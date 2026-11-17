"""Read-only audit of existing E8 paired outputs; no simulator or inference.

Run from the repository root. Verifies stored aggregate predicates, byte hashes,
recorded initial conditions and physics-derived contact/release counters;
cannot establish unrecorded RNG state or independently measure contacts.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def verify_row(row):
    vals = (row['goal_error_xy_m'], row['longest_two_finger_lift_s'],
            row['max_object_robot_penetration_m'], *row['final_object_xyz_m'])
    if not all(math.isfinite(x) for x in vals):
        raise ValueError('non-finite outcome')
    pos, goal = row['final_object_xyz_m'], row['goal_xyz_m']
    dist = math.dist(pos[:2], goal[:2])
    if not math.isclose(dist, row['goal_error_xy_m'], abs_tol=1e-12):
        raise ValueError('distance mismatch')
    placed = dist <= .035 and abs(pos[2] - .014) <= .012
    if row['placed'] != placed:
        raise ValueError('placement mismatch')
    expected = (placed and row['released'] and row['longest_two_finger_lift_s'] >= .5
                and row['max_object_robot_penetration_m'] <= .0015)
    if row['task_success'] != expected:
        raise ValueError('success mismatch')
    if row['controls'] != 330 or row['object_pose_writes_during_rollout'] != 0:
        raise ValueError('episode contract mismatch')


def verify_physics(path, row):
    with np.load(path, allow_pickle=False) as data:
        xyz = data['xyz']
        time = data['time']
        masks = data['finger_mask']
        contacts = data['robot_contact']
        pen = data['penetration']
        if len(time) < 2 or any(len(x) != len(time) for x in (xyz, masks, contacts, pen)):
            raise ValueError('physics lengths mismatch')
        dt = float(time[1] - time[0])
        if not np.allclose(np.diff(time), dt, rtol=1e-8, atol=1e-12):
            raise ValueError('nonuniform physics time')
        held = (masks == 3) & (xyz[:, 2] > row['source_xyz_m'][2] + .05)
        longest = current = 0
        for value in held:
            current = current + 1 if value else 0
            longest = max(longest, current)
        free = 0
        for value in contacts[::-1]:
            if value:
                break
            free += 1
        if not math.isclose(longest * dt, row['longest_two_finger_lift_s'], abs_tol=1e-9):
            raise ValueError('held duration mismatch')
        if (free * dt >= .1) != row['released']:
            raise ValueError('release mismatch')
        if not math.isclose(float(np.max(pen)), row['max_object_robot_penetration_m'], abs_tol=1e-12):
            raise ValueError('penetration mismatch')
        if not np.allclose(xyz[-1], row['final_object_xyz_m'], atol=1e-12, rtol=0):
            raise ValueError('final position mismatch')


def read_arm(root, base, name):
    arm = base / 'runs' / name
    rows = [json.loads(line) for line in (arm / 'episodes.jsonl').read_text().splitlines()]
    if len(rows) != 20 or {r['seed'] for r in rows} != set(range(12850,12870)):
        raise ValueError(f'{name}: missing or duplicate seeds')
    result = {}
    for r in rows:
        verify_row(r)
        physics = root / r['physics_path']
        trace = arm / f"{r['seed']}.trace.jsonl"
        if digest(physics) != r['physics_sha256'] or digest(trace) != r['trace_sha256']:
            raise ValueError(f'{name}/{r["seed"]}: hash mismatch')
        verify_physics(physics, r)
        with trace.open() as f:
            records = [json.loads(line) for line in f]
        if len(records) != 330 or [x['control_step'] for x in records] != list(range(330)):
            raise ValueError(f'{name}/{r["seed"]}: trace steps mismatch')
        result[r['seed']] = (r, records[0])
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, default=Path.cwd())
    args = ap.parse_args()
    root = args.repo.resolve()
    base = root / 'experiments/discovery/e8-theta-estimator-20261118'
    names = ['nocomp-15', 'diag-15-neg7p5', 'est-15']
    arms = {n: read_arm(root, base, n) for n in names}
    for seed in range(12850,12870):
        reference, ref0 = arms[names[0]][seed]
        for name in names[1:]:
            row, initial = arms[name][seed]
            for key in ('delta_mm', 'source_xyz_m', 'goal_xyz_m', 'yaw_deg'):
                if row[key] != reference[key]:
                    raise ValueError(f'{seed}/{name}: mismatch {key}')
            for key in ('q_before_rad','rgb_sha256'):
                if initial[key] != ref0[key]:
                    raise ValueError(f'{seed}/{name}: initial mismatch {key}')
    print('PASS: 60 E8 rows, per-arm hashes, physics-derived outcome and recorded initial pairing; RNG state not independently validated')


if __name__ == '__main__':
    main()
