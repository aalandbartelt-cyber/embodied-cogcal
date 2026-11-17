"""Job templates for the console.

v0 is deliberately a *planner*: it turns a template plus validated arguments
into the exact command, output directory and expected duration, and reports GPU
headroom.  It does not start anything; execution stays behind an explicit flag
so the console keeps its read-only contract until that is reviewed.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

E8 = 'experiments/discovery/e8-theta-estimator-20261118'

TEMPLATES = {
    'eval-e8-arm': {
        'label': '评估 E8 单臂（逐集记录）',
        'script': f'{E8}/rollout_e8.py',
        'summary': '按既有 runner 跑一个剂量臂，产出新的 attempt 目录，不覆盖历史运行。',
        'arms': ['est15', 'est0', 'est-15', 'nocomp15', 'nocomp-15'],
        'seed_min': 12850,
        'seed_max': 12999,
        'count_max': 40,
        'seconds_per_episode': 4.2,
    },
    'gate-e7b': {
        'label': '能力门（E7B 判据）',
        'script': f'experiments/discovery/e7b-second-seed-20261118/rollout_e7b.py',
        'summary': '跑 y0_none 臂核对 ≥16/20 能力门；失败即判 CHECKPOINT_INELIGIBLE。',
        'arms': ['y0-none'],
        'seed_min': 13050,
        'seed_max': 13199,
        'count_max': 20,
        'seconds_per_episode': 4.0,
    },
}


def _gpu():
    try:
        out = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.used,memory.total,utilization.gpu',
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=3, check=False)
        line = (out.stdout or '').strip().splitlines()
        if not line:
            return None
        name, used, total, util = [part.strip() for part in line[0].split(',')]
        return {'name': name, 'used_mb': int(float(used)), 'total_mb': int(float(total)),
                'util': int(float(util))}
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def plan(root: Path, template: str, arm: str, seed: int, count: int) -> dict:
    item = TEMPLATES.get(template)
    if item is None:
        raise ValueError('未知模板')
    if arm not in item['arms']:
        raise ValueError('臂不在白名单内')
    if not (item['seed_min'] <= int(seed) <= item['seed_max']):
        raise ValueError('种子超出允许区间')
    if not (1 <= int(count) <= item['count_max']):
        raise ValueError(f'集数需在 1–{item["count_max"]} 之间')
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    out = f'{E8}/attempts/{stamp}-{template}-{arm}'
    argv = ['python3', item['script'], '--arm', arm, '--seed-start', str(seed),
            '--count', str(count), '--out', out]
    return {'template': template, 'label': item['label'], 'argv': argv,
            'out': out, 'eta_min': round(int(count) * item['seconds_per_episode'] / 60, 1),
            'exists': (Path(root) / out).exists(), 'gpu': _gpu(),
            'executable': False,
            'note': 'v0 只生成命令与目录，不启动进程；执行开关待评审后启用。'}


def catalog(root: Path) -> dict:
    root = Path(root).resolve()
    attempts = []
    for base in (root / E8 / 'attempts',):
        if base.is_dir():
            attempts = sorted((p.name for p in base.iterdir() if p.is_dir()), reverse=True)[:8]
    return {'templates': [dict(id=key, **{k: v for k, v in item.items() if k != 'script'},
                               script=item['script']) for key, item in TEMPLATES.items()],
            'attempts': attempts, 'gpu': _gpu()}
