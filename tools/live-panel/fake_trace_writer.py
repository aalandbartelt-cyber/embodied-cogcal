#!/usr/bin/env python3
"""Write a synthetic trace at a controlled rate to exercise the live console.

This is a test fixture, not a simulation: it fabricates joint angles so the
console's tail-window reader, growth detection and follow logic can be checked
without starting MuJoCo or touching any experiment record.

Usage:
    python3 fake_trace_writer.py --root /tmp/lp-fixture --experiment demo \
        --run live --seeds 11 12 13 --steps 330 --fps 82
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--experiment', default='demo')
    parser.add_argument('--run', default='live')
    parser.add_argument('--seeds', nargs='+', type=int, default=[11])
    parser.add_argument('--steps', type=int, default=330)
    parser.add_argument('--fps', type=float, default=82.0)
    parser.add_argument('--start-at', type=int, default=0,
                        help='skip this many control steps before writing (resume look-alike)')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    folder = root / 'experiments/discovery' / args.experiment / 'runs' / args.run
    folder.mkdir(parents=True, exist_ok=True)

    contract = {'kind': 'fake-fixture', 'seeds': args.seeds, 'control_budget': args.steps,
                'fps': args.fps, 'note': 'synthetic trace for console checks'}
    (folder / 'contract.json').write_text(json.dumps(contract), encoding='utf-8')
    episodes = folder / 'episodes.jsonl'
    episodes.write_text('', encoding='utf-8')
    (folder / 'episodes.jsonl').open('a', encoding='utf-8').close()

    delay = 1.0 / max(args.fps, 1.0)
    for seed in args.seeds:
        trace = folder / f'{seed}.trace.jsonl'
        with trace.open('w', encoding='utf-8') as handle:
            for step in range(args.start_at, args.steps):
                phase = step / 40.0 + seed * 0.01
                q = [0.02 * math.sin(phase), -0.55 + 0.05 * math.cos(phase),
                     0.95 + 0.08 * math.sin(phase * 0.7), 0.78,
                     0.01 * math.cos(phase), 0.28 + 0.02 * math.sin(phase)]
                row = {'seed': seed, 'control_step': step,
                       'sim_time_s': round(step / args.fps, 4),
                       'q_after_rad': q,
                       'command_rad': [value + 0.004 for value in q]}
                handle.write(json.dumps(row) + '\n')  # no flush on purpose
                time.sleep(delay)
        with episodes.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps({'seed': seed, 'task_success': seed % 2 == 1,
                                     'wall_s': round(args.steps / args.fps, 3)}) + '\n')
            handle.flush()
        print(f'finished seed {seed}', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
