"""Parameterised success predicate.

One implementation, many thresholds.  The gold standard is
``experiments/discovery/official-act-20261116/audit_act.py::predicate`` — the
function the frozen audits were run with.  This module must reproduce it exactly
at the default parameters; ``--selfcheck`` proves that on real physics archives
before any threshold grid is allowed to draw conclusions.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np

PLACE_XY_M = 0.035
PLACE_Z_M = 0.014
PLACE_DZ_M = 0.012
RELEASE_S = 0.1
LIFT_S = 0.5
LIFT_CLEARANCE_M = 0.05
PENETRATION_M = 0.0015

GRID = {
    'place_xy_m': (0.030, 0.035, 0.040),
    'release_s': (0.05, 0.10, 0.15),
    'lift_s': (0.3, 0.5, 0.7),
    'penetration_m': (0.0010, 0.0015, 0.0020),
    'budget': (285, 320, 330),
}


def longest_run(values):
    """Longest consecutive True run; identical to the gold standard."""
    padded = np.r_[False, np.asarray(values, dtype=bool), False].astype(np.int8)
    starts = np.flatnonzero(np.diff(padded) == 1)
    ends = np.flatnonzero(np.diff(padded) == -1)
    return int(np.max(ends - starts)) if len(starts) else 0


def predicate(physics, dt, source_z, goal, *,
              place_xy_m=PLACE_XY_M, place_z_m=PLACE_Z_M, place_dz_m=PLACE_DZ_M,
              release_s=RELEASE_S, lift_s=LIFT_S, penetration_m=PENETRATION_M):
    """Recompute one episode verdict from per-tick physics, with free thresholds."""
    xyz = physics["xyz"]
    held = (physics["finger_mask"] == 3) & (xyz[:, 2] > source_z + LIFT_CLEARANCE_M)
    held_s = longest_run(held) * dt
    contact = np.asarray(physics["robot_contact"], dtype=bool)
    last_contact = np.flatnonzero(contact)
    release_ticks = len(contact) - 1 - last_contact[-1] if len(last_contact) else len(contact)
    final = xyz[-1]
    distance = float(np.linalg.norm(final[:2] - np.asarray(goal)[:2]))
    placed = bool(distance <= place_xy_m and abs(final[2] - place_z_m) <= place_dz_m)
    released = bool(release_ticks * dt >= release_s)
    max_penetration = float(np.max(physics["penetration"]))
    return {"task_success": bool(placed and released and held_s >= lift_s and max_penetration <= penetration_m),
            "placed": placed, "released": released, "longest_two_finger_lift_s": held_s,
            "goal_error_xy_m": distance, "max_object_robot_penetration_m": max_penetration,
            "max_object_z_m": max(source_z, float(xyz[:, 2].max())),
            "final_object_xyz_m": final.tolist()}


def load_physics(path):
    with np.load(Path(path), allow_pickle=False) as data:
        payload = {key: np.asarray(data[key]) for key in
                   ('control_step', 'time', 'xyz', 'q', 'finger_mask', 'robot_contact', 'penetration')}
    lengths = {len(value) for value in payload.values()}
    if len(lengths) != 1:
        raise ValueError(f'inconsistent array lengths in {path}: {sorted(lengths)}')
    times = payload['time']
    if len(times) < 2:
        raise ValueError(f'too few ticks in {path}')
    steps = np.diff(times)
    if not np.allclose(steps, steps[0], rtol=1e-6, atol=1e-9):
        raise ValueError(f'non-uniform timestamps in {path}')
    payload['dt'] = float(steps[0])
    return payload


def truncate(physics, budget):
    """Slice a tick archive to the first ``budget`` control steps."""
    if budget is None:
        return physics
    mask = physics['control_step'] < int(budget)
    if not np.any(mask):
        return None
    sliced = {key: value[mask] for key, value in physics.items() if isinstance(value, np.ndarray)}
    sliced['dt'] = physics.get('dt')
    return sliced


def resolve_physics_path(root, experiment_root, raw):
    """Physics paths appear relative to the repo, the experiment, or ``data/``."""
    root = Path(root)
    candidates = [root / raw, Path(experiment_root) / raw, root / 'data' / raw,
                  root / str(raw).lstrip('./')]
    for candidate in candidates:
        try:
            if candidate.is_file():
                return candidate.resolve()
        except OSError:
            continue
    return None


def _gold_predicate():
    root = Path(__file__).resolve().parents[2]
    source = root / 'experiments/discovery/official-act-20261116/audit_act.py'
    spec = importlib.util.spec_from_file_location('audit_act_gold', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.predicate


def selfcheck(root, limit=None):
    """Compare against the gold predicate on real episodes.  Returns a summary."""
    root = Path(root).resolve()
    gold = _gold_predicate()
    checked = 0
    mismatches = []
    for episodes in sorted((root / 'experiments/discovery').rglob('episodes.jsonl')):
        if any(part in {'smoke', 'audit'} for part in episodes.parts):
            continue
        for line in episodes.read_text(encoding='utf-8', errors='replace').splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            raw = row.get('physics_path')
            goal = row.get('goal_xyz_m')
            source = row.get('source_xyz_m')
            if not raw or not goal or not source:
                continue
            path = resolve_physics_path(root, episodes.parent.parent, raw)
            if path is None:
                continue
            physics = load_physics(path)
            args = (physics, physics['dt'], float(source[2]), goal)
            expected = gold(*args)
            actual = predicate(*args)
            for key, value in expected.items():
                if isinstance(value, bool):
                    same = value == actual[key]
                elif isinstance(value, (int, float)):
                    same = abs(float(value) - float(actual[key])) <= 1e-12
                else:
                    same = value == actual[key]
                if not same:
                    mismatches.append({'episode': f"{episodes.parent.name}/{row.get('seed')}", 'key': key})
            checked += 1
            if limit and checked >= limit:
                return {'checked': checked, 'mismatches': mismatches}
    return {'checked': checked, 'mismatches': mismatches}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selfcheck', action='store_true')
    parser.add_argument('--root', default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()
    if not args.selfcheck:
        parser.error('nothing to do; pass --selfcheck')
    summary = selfcheck(args.root, args.limit or None)
    print(json.dumps({'checked': summary['checked'], 'mismatches': len(summary['mismatches'])}))
    for item in summary['mismatches'][:5]:
        print('  mismatch', item)
    return 0 if not summary['mismatches'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
