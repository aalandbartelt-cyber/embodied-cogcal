#!/usr/bin/env python3
"""Threshold sensitivity of the success predicate.

Recomputes every registered contrast on a 243-cell grid of endpoint thresholds
(placement window, release window, lift duration, penetration ceiling, control
budget) from the archived physics — no simulation is run.  A claim is robust
only if no cell changes its verdict.

    python3 analysis/threshold_sensitivity.py --check          # predicate vs episodes
    python3 analysis/threshold_sensitivity.py --run            # write JSON + report
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/live-panel'))
import success_predicate as sp  # noqa: E402

CONTRASTS = ROOT / 'analysis/threshold_contrasts.json'
OUT_JSON = ROOT / 'analysis/threshold_sensitivity.json'
OUT_MD = ROOT / 'docs/report/THRESHOLD_SENSITIVITY_20261117.md'
DEFAULT_CELL = {'place_xy_m': 0.035, 'release_s': 0.10, 'lift_s': 0.5,
                'penetration_m': 0.0015, 'budget': 330}
RULE = {'min_delta': 0.10, 'alpha': 0.05}


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(0, min(b, c) + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def load_arm(root, experiment, arm):
    folder = Path(root) / 'experiments/discovery' / experiment / 'runs' / arm
    episodes = folder / 'episodes.jsonl'
    if not episodes.is_file():
        raise SystemExit(f'missing episodes: {episodes}')
    rows = {}
    for line in episodes.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        path = sp.resolve_physics_path(Path(root), folder.parent.parent, row['physics_path'])
        if path is None:
            raise SystemExit(f"unresolved physics for {arm} seed {row.get('seed')}")
        rows[str(row['seed'])] = (row, sp.load_physics(path))
    return rows


def episode_metrics(row, physics):
    source_z = float(row['source_xyz_m'][2])
    goal = row['goal_xyz_m']
    out = {'dist': float(math.dist(physics['xyz'][-1][:2], goal[:2])),
           'final_z': float(physics['xyz'][-1][2]),
           'max_pen': float(physics['penetration'].max()),
           'held_s': {}, 'free_s': {}}
    for budget in sp.GRID['budget']:
        sliced = sp.truncate(physics, budget)
        if sliced is None:
            out['held_s'][budget] = None
            out['free_s'][budget] = None
            continue
        dt = sliced['dt']
        held = (sliced['finger_mask'] == 3) & (sliced['xyz'][:, 2] > source_z + sp.LIFT_CLEARANCE_M)
        out['held_s'][budget] = sp.longest_run(held) * dt
        contact = sliced['robot_contact'].astype(bool)
        last = contact.nonzero()[0]
        release_ticks = len(contact) - 1 - last[-1] if len(last) else len(contact)
        out['free_s'][budget] = release_ticks * dt
    return out


def judge(metrics, cell):
    held = metrics['held_s'].get(cell['budget'])
    free = metrics['free_s'].get(cell['budget'])
    if held is None or free is None:
        return None
    placed = metrics['dist'] <= cell['place_xy_m'] and abs(metrics['final_z'] - sp.PLACE_Z_M) <= sp.PLACE_DZ_M
    released = free >= cell['release_s']
    return bool(placed and released and held >= cell['lift_s'] and metrics['max_pen'] <= cell['penetration_m'])


def contrast_stats(paired, cell):
    a_wins = b_wins = 0
    n = 0
    for metrics_a, metrics_b in paired:
        va, vb = judge(metrics_a, cell), judge(metrics_b, cell)
        if va is None or vb is None:
            continue
        n += 1
        if va and not vb:
            a_wins += 1
        elif vb and not va:
            b_wins += 1
    if n == 0:
        return None
    delta = (a_wins - b_wins) / n
    p = mcnemar_exact(a_wins, b_wins)
    if delta >= RULE['min_delta'] and p < RULE['alpha']:
        verdict = 'A>B'
    elif delta <= -RULE['min_delta'] and p < RULE['alpha']:
        verdict = 'B>A'
    else:
        verdict = 'tie'
    return {'n': n, 'a_only': a_wins, 'b_only': b_wins, 'delta': round(delta, 4),
            'p': round(p, 6), 'verdict': verdict}


def run(root, out_json, out_md):
    root = Path(root)
    contrasts = json.loads(CONTRASTS.read_text(encoding='utf-8')) if CONTRASTS.is_file() else {'contrasts': []}
    results = []
    for item in contrasts.get('contrasts', []):
        experiment, arm_a, arm_b = item['experiment'], item['arm_a'], item['arm_b']
        rows_a, rows_b = load_arm(root, experiment, arm_a), load_arm(root, experiment, arm_b)
        shared = sorted(set(rows_a) & set(rows_b))
        paired = []
        for seed in shared:
            row_a, phys_a = rows_a[seed]
            row_b, phys_b = rows_b[seed]
            paired.append((episode_metrics(row_a, phys_a), episode_metrics(row_b, phys_b)))
        keys = list(sp.GRID)
        cells = []
        for values in itertools.product(*(sp.GRID[key] for key in keys)):
            cell = dict(zip(keys, values))
            stats = contrast_stats(paired, cell)
            if stats:
                stats['cell'] = cell
                cells.append(stats)
        baseline = next((c for c in cells if all(c['cell'][k] == DEFAULT_CELL[k] for k in DEFAULT_CELL)), None)
        flips = [c for c in cells if baseline and c['verdict'] != baseline['verdict']]
        by_param = {}
        for key in keys:
            others = [c for c in cells if all(c['cell'][k] == DEFAULT_CELL[k] for k in DEFAULT_CELL if k != key)]
            by_param[key] = sorted({c['verdict'] for c in others})
        results.append({'experiment': experiment, 'arm_a': arm_a, 'arm_b': arm_b,
                        'paired': len(paired), 'baseline': baseline['verdict'] if baseline else None,
                        'baseline_stats': baseline, 'cells': len(cells),
                        'flips': len(flips), 'flipped_to': sorted({c['verdict'] for c in flips}),
                        'by_param': by_param,
                        'verdict_robust': baseline is not None and not flips,
                        'sensitive_param': max(by_param, key=lambda k: len(by_param[k])) if by_param else None})
    payload = {'grid': {k: list(v) for k, v in sp.GRID.items()}, 'rule': RULE,
               'defaults': DEFAULT_CELL, 'contrasts': results}
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(out_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')

    lines = ['# 端点阈值敏感性（首个科研动作）', '',
             f'网格：{len(list(itertools.product(*sp.GRID.values())))} 格；'
             f'判定：|Δ| ≥ {RULE["min_delta"]} 且 McNemar p < {RULE["alpha"]}。', '',
             '## 结论', '']
    for item in results:
        state = '稳健' if item['verdict_robust'] else f"翻转 {item['flips']} 格"
        lines.append(f"- **{item['experiment']}** `{item['arm_a']}` vs `{item['arm_b']}`："
                     f"基线 {item['baseline']}，{state}；配对 {item['paired']} 集。")
    lines += ['', '## 逐对比明细', '',
              '| 实验 | 对比 | 配对 | 基线裁决 | 翻转格数 | 裁决集合 | 最敏感参数 |',
              '|---|---|---|---|---|---|---|']
    for item in results:
        verdicts = ' / '.join(sorted({v for values in item['by_param'].values() for v in values}))
        lines.append(f"| {item['experiment']} | {item['arm_a']} vs {item['arm_b']} | {item['paired']} | "
                     f"{item['baseline']} | {item['flips']} | {verdicts} | {item['sensitive_param']} |")
    lines += ['', '## 方法边界（必须与结论同时引用）', '',
              '1. z 容差（±12 mm）与桌面参考高度（14 mm）不在网格内：它们描述"物体落在桌面上"这一物理事实，不是可调判据。',
              '2. 预算格 330 对 285 步的运行是 `undefined` 而非失败；undefined 不计入翻转。',
              '3. `released` 采用与冻结审计相同的正向尾部计数；参数化实现已与 `audit_act.predicate` 逐集比对（见 `--check`）。',
              '4. `lift_s` 只改"持续多久算抬起"，不改"+0.05 m 才算抬起"这一常数。', '',
              '## 复现', '', '```bash',
              'python3 analysis/threshold_sensitivity.py --check',
              'python3 analysis/threshold_sensitivity.py --run', '```']
    Path(out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(out_md).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return payload


def check(root, limit=None):
    root = Path(root)
    checked = mismatches = 0
    for episodes in sorted((root / 'experiments/discovery').rglob('episodes.jsonl')):
        if any(part in {'smoke', 'audit'} for part in episodes.parts):
            continue
        folder = episodes.parent
        for line in episodes.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            path = sp.resolve_physics_path(root, folder.parent.parent, row.get('physics_path', ''))
            if path is None:
                continue
            metrics = episode_metrics(row, sp.load_physics(path))
            verdict = judge(metrics, DEFAULT_CELL)
            if verdict is None:
                continue
            checked += 1
            if verdict != bool(row.get('task_success')):
                mismatches += 1
                if mismatches <= 5:
                    print('mismatch', folder.name, row.get('seed'))
            if limit and checked >= limit:
                return checked, mismatches
    return checked, mismatches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(ROOT))
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--out', default=str(OUT_JSON))
    parser.add_argument('--report', default=str(OUT_MD))
    args = parser.parse_args()
    if args.check:
        checked, mismatches = check(args.root, args.limit or None)
        print(json.dumps({'episodes': checked, 'mismatches': mismatches}))
        return 0 if mismatches == 0 else 1
    if args.run:
        payload = run(args.root, args.out, args.report)
        print(json.dumps({'contrasts': len(payload['contrasts']),
                          'robust': sum(1 for c in payload['contrasts'] if c['verdict_robust'])}))
        return 0
    parser.error('pass --check or --run')


if __name__ == '__main__':
    raise SystemExit(main())
