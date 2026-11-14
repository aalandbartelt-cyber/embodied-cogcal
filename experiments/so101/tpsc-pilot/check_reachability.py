"""Loose reachability check for TPSC manifest object/goal points.

Randomly samples the six SO-101 joint ranges, forwards kinematics, and reports
the minimum distance from the gripper body to each object/goal point.  This is
a geometry proxy, not proof that a policy can grasp or place; collisions,
dynamics, and camera visibility are not checked.

Run in the simulation environment:

    env -u PYTHONPATH PYTHONNOUSERSITE=1 PYTHONPATH=. \
      /home/mary/miniconda3/envs/cogcal-sim/bin/python \
      experiments/so101/tpsc-pilot/check_reachability.py \
      --manifest experiments/so101/tpsc-pilot/manifest-full.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from simulation.so101.scene import JOINT_NAMES
from simulation.so101.tpsc_scene import load_tpsc_scene


def _load(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--threshold", type=float, default=0.05)
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("reachability.json"))
    args = parser.parse_args()

    import mujoco

    records = _load(args.manifest)
    model, data = load_tpsc_scene(mujoco_module=mujoco)
    rng = np.random.default_rng(args.seed)
    addresses = [int(model.jnt_qposadr[model.joint(name).id]) for name in JOINT_NAMES]
    lows = np.array([float(model.joint(name).range[0]) for name in JOINT_NAMES])
    highs = np.array([float(model.joint(name).range[1]) for name in JOINT_NAMES])
    samples = rng.uniform(lows, highs, size=(args.samples, len(JOINT_NAMES)))

    points = []
    for q in samples:
        data.qpos[addresses] = q
        mujoco.mj_forward(model, data)
        points.append(data.body("gripper").xpos.copy())
    points = np.asarray(points)

    targets: list[dict[str, Any]] = []
    for record in records:
        target_key = f"{record['target_object']}_pose"
        for kind, key in (("target_object", target_key), ("goal", "goal_pose")):
            value = record.get(key)
            if value is not None:
                targets.append({
                    "episode_id": record["episode_id"],
                    "kind": kind,
                    "position": np.asarray(value, dtype=float),
                })
    results = []
    for target in targets:
        distance = float(np.min(np.linalg.norm(points - target["position"], axis=1)))
        results.append({
            "episode_id": target["episode_id"],
            "kind": target["kind"],
            "position": target["position"].tolist(),
            "min_gripper_distance_m": distance,
            "reachable_proxy": distance <= args.threshold,
        })
    unreachable = [r for r in results if not r["reachable_proxy"]]
    output = {
        "kind": "tpsc_reachability_proxy_not_policy_result",
        "manifest": str(args.manifest),
        "samples": args.samples,
        "seed": args.seed,
        "threshold_m": args.threshold,
        "points": len(results),
        "unreachable": len(unreachable),
        "ok": not unreachable,
        "results": results,
    }
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "output": str(args.out),
        "samples": args.samples,
        "targets": len(results),
        "unreachable": len(unreachable),
        "worst": sorted(results, key=lambda x: -x["min_gripper_distance_m"])[:5],
    }, ensure_ascii=False))
    return 0 if not unreachable else 1


if __name__ == "__main__":
    raise SystemExit(main())
