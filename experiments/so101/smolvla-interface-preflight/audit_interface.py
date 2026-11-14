"""Audit the public SmolVLA/SO-101 interface against this MuJoCo scene.

This is an interface audit, not a policy evaluation.  The public LeRobot
dataset exposes six joint positions in its public motor convention: body
joints in degrees (the SO follower default) and gripper in 0--100.  The
project MuJoCo scene exposes six actuator targets in radians, with a hinge
gripper.  The audit makes the conversion explicit and reports range overlap.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import mujoco

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from simulation.so101.scene import JOINT_NAMES, load_scene


DATASET_JOINT_NAMES = [
    "shoulder_pan.pos",
    "shoulder_lift.pos",
    "elbow_flex.pos",
    "wrist_flex.pos",
    "wrist_roll.pos",
    "gripper.pos",
]

# Provenance for the *dataset-era* unit convention.  The dataset was created
# on 2025-05-23, before LeRobot v0.3.2 (released 2025-08-01) changed the
# SO100 follower default from degrees to RANGE_M100_100.  The old manipulator
# documentation says rotations are in degrees in [-180, 180] and the gripper
# is in [0, 100].  This is an evidence record, not a claim that the public
# dataset is mechanically identical to this project's SO-101.
DATASET_PROVENANCE = {
    "created_at": "2025-05-23",
    "lerobot_commit_at_creation": "6163daaaa4fa193d0e37468a94d90e07ef3c95ce",
    "unit_evidence": {
        "manipulator.py:294-297": "Rotations are expressed in degrees in nominal range of [-180, 180], and linear motions (like gripper of Aloha) in nominal range of [0, 100].",
        "feetech_calibration.py:490": "Joints with rotational motions are expressed in degrees in nominal range of [-180, 180].",
        "later_change": "LeRobot v0.3.2 (2025-08-01) introduced use_degrees=False as the SO100 default; the current default True is documented as backward compatibility with previous policies/datasets.",
    },
    "robot_type": "so100_follower",
    "same_body_so101": False,
    "same_body_reason": "metadata says so100_follower; public elbow/wrist reach 100/99.49 degrees and exceed the SO-101 XML limits; the dataset does not include its calibration file.",
}


def audit(info_path: Path, stats_path: Path) -> dict[str, Any]:
    info = json.loads(info_path.read_text())
    stats = json.loads(stats_path.read_text())
    features = info["features"]
    action_names = features["action"]["names"]
    state_names = features["observation.state"]["names"]
    if action_names != DATASET_JOINT_NAMES or state_names != DATASET_JOINT_NAMES:
        raise ValueError(f"unexpected feature order: action={action_names}, state={state_names}")

    model, _ = load_scene()
    scene_ranges: dict[str, list[float]] = {}
    dataset_ranges_public: dict[str, list[float]] = {}
    dataset_ranges_scene: dict[str, list[float]] = {}
    in_scene: dict[str, bool] = {}
    range_overflow: dict[str, dict[str, float]] = {}
    for index, joint_name in enumerate(JOINT_NAMES):
        action_key = f"{joint_name}.pos"
        # stats.json is keyed by feature, while the feature order is the
        # authoritative mapping to the six-dimensional action vector.
        mins = stats["action"]["min"]
        maxs = stats["action"]["max"]
        low, high = float(mins[index]), float(maxs[index])
        dataset_ranges_public[action_key] = [low, high]
        actuator = model.actuator(joint_name)
        scene_low, scene_high = map(float, model.actuator_ctrlrange[actuator.id])
        scene_ranges[action_key] = [scene_low, scene_high]
        if index < 5:
            converted = [math.radians(low), math.radians(high)]
        else:
            # LeRobot's public gripper convention is a percentage; map it to
            # the scene hinge range for this audit only.
            converted = [scene_low + low / 100.0 * (scene_high - scene_low),
                         scene_low + high / 100.0 * (scene_high - scene_low)]
        dataset_ranges_scene[action_key] = converted
        in_scene[action_key] = converted[0] >= scene_low and converted[1] <= scene_high
        low_overflow = max(0.0, scene_low - converted[0])
        high_overflow = max(0.0, converted[1] - scene_high)
        range_overflow[action_key] = {
            "low_rad": low_overflow,
            "high_rad": high_overflow,
            "low_deg": math.degrees(low_overflow),
            "high_deg": math.degrees(high_overflow),
        }

    return {
        "kind": "smolvla_so101_interface_preflight_not_policy_result",
        "dataset": {
            "robot_type": info["robot_type"],
            "dataset_name": "svla_so101_pickplace",
            "dataset_robot_type_warning": "metadata says so100_follower; do not assume SO-101 mechanical identity without calibration evidence",
            "codebase_version": info["codebase_version"],
            "total_episodes": info["total_episodes"],
            "total_frames": info["total_frames"],
            "fps": info["fps"],
            "action_shape": features["action"]["shape"],
            "state_shape": features["observation.state"]["shape"],
            "action_names": action_names,
            "state_names": state_names,
            "public_units": {
                "body_joints": "degrees (dataset-era LeRobot calibration; rotations in [-180,180])",
                "gripper": "0..100",
            },
            "lerobot_source_commit_audited": "fe1c54594f6ba275fccf210b9f7b11f0e2324b89",
            "lerobot_source_evidence": {
                "current_config": "src/lerobot/robots/so_follower/config_so_follower.py:use_degrees=True (current default; documented as backward compatibility with previous policies/datasets)",
                "dataset_era_config": "old lerobot/common/robot_devices/robots/manipulator.py:294-297 (2025-05-23): rotations in degrees [-180,180], gripper [0,100]",
                "later_change": "v0.3.2 (2025-08-01) introduced use_degrees=False as the SO100 default, after this dataset was created",
            },
            "dataset_provenance": DATASET_PROVENANCE,
        },
        "scene": {
            "mujoco_version": mujoco.__version__,
            "joint_names": list(JOINT_NAMES),
            "public_interface": "six radian hinge position targets",
            "actuator_ctrlrange_rad": scene_ranges,
        },
        "dataset_action_range_public": dataset_ranges_public,
        "dataset_action_range_mapped_to_scene": dataset_ranges_scene,
        "mapped_range_inside_scene": in_scene,
        "range_overflow": range_overflow,
        "decision": {
            "same_body_so101_claim": False,
            "reason": "metadata says so100_follower; public elbow_flex/wrist_flex reach 100.0/99.49 degrees and exceed the SO-101 XML upper limits (96.83/95.01 degrees) by 3.17/4.49 degrees; the dataset does not include its calibration file.",
            "allowed_use": "carrier smoke test only, with an explicit degree->radian and gripper adapter; count and report every clip event.",
            "not_allowed_use": "same-body SO-101 training/evaluation, or attributing A100/VLA failures to TPSC before the interface is resolved.",
            "required_before_tpsc": [
                "collect project-owned SO-101 demonstrations with the project's calibration and record the calibration file/revision",
                "or obtain a public dataset that declares robot_type=so101_follower and includes calibration metadata",
                "re-run this audit with the actual calibration range, not a range-matching assumption",
            ],
        },
        "required_adapter": [
            "Record the dataset-era degree convention (created 2025-05-23, before LeRobot v0.3.2) and re-check it for any newer dataset.",
            "Convert the first five public joint values from degrees to radians.",
            "Map the public gripper 0..100 convention to the scene hinge range; do not pass it as radians.",
            "Do not silently clip elbow_flex/wrist_flex; count and report any clip events.",
            "Resolve the SO-100 vs SO-101 body/calibration mismatch before claiming same-body simulation; prefer project-owned SO-101 data for TPSC.",
        ],
        "limitations": [
            "Degree values are relative to the dataset's own calibration; without the calibration file they do not identify the project SO-101 zero/range.",
            "The public dataset is a SO-100 carrier (metadata), not a same-body SO-101 dataset.",
            "Range conversion does not prove kinematic or dynamic equivalence.",
            "The public dataset contains one task_index only; it is a carrier smoke-test asset, not the TPSC task matrix.",
            "No weights were loaded and no policy action was executed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--info", type=Path, default=Path(__file__).with_name("dataset-info.json"))
    parser.add_argument("--stats", type=Path, default=Path(__file__).with_name("dataset-stats.json"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("summary.json"))
    args = parser.parse_args()
    result = audit(args.info, args.stats)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "mapped_range_inside_scene": result["mapped_range_inside_scene"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
