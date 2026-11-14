"""Audit a real public SO-101 LeRobot dataset against the project SO-101 XML.

This is a range/unit audit, not a policy result.  It downloads the small
per-episode parquet files (no videos), computes action/state ranges, and
compares them to the actuator ctrlrange in the official SO-101 XML used by
this project.

The default dataset is ``kristaqp/so101-pick-place`` at a pinned revision:
50 episodes, 30 Hz, two cameras, Apache-2.0, ``robot_type=so101_follower``.
It was created on 2025-06-14, before LeRobot v0.3.2, so its body values are
dataset-era degrees ([-180, 180]) and its gripper is 0--100.

Run in the ``cogcal`` environment (needs pandas + pyarrow):

    /home/mary/miniconda3/envs/cogcal/bin/python \
      experiments/so101/smolvla-interface-preflight/audit_real_so101_range.py
"""

from __future__ import annotations

import argparse
import io
import json
import math
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REPO = "kristaqp/so101-pick-place"
DEFAULT_REVISION = "994aa6d4f68e33ac93c410085eca4beb9cc14aea"
DEFAULT_EPISODES = 50
DEFAULT_XML = ROOT / "third_party/SO-ARM100/Simulation/SO101/so101_new_calib.xml"
JOINT_NAMES = (
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
    "gripper",
)


def scene_ctrlrange(xml_path: Path) -> dict[str, list[float]]:
    """Read actuator ctrlrange values from the SO-101 XML (radians)."""
    tree = ET.parse(xml_path)
    ranges: dict[str, list[float]] = {}
    for actuator in tree.iter("actuator"):
        for item in actuator:
            name = item.get("name")
            ctrl = item.get("ctrlrange")
            if name and ctrl:
                ranges[name] = [float(x) for x in ctrl.split()]
    missing = [name for name in JOINT_NAMES if name not in ranges]
    if missing:
        raise ValueError(f"missing actuator ctrlrange for {missing} in {xml_path}")
    return {name: ranges[name] for name in JOINT_NAMES}


def read_episode(repo: str, revision: str, episode: int) -> pd.DataFrame:
    url = (
        f"https://huggingface.co/datasets/{repo}/resolve/{revision}/"
        f"data/chunk-000/episode_{episode:06d}.parquet"
    )
    with urllib.request.urlopen(url, timeout=60) as response:
        return pd.read_parquet(io.BytesIO(response.read()))


def audit(repo: str, revision: str, episodes: int, xml_path: Path) -> dict[str, Any]:
    action_mins: list[np.ndarray] = []
    action_maxs: list[np.ndarray] = []
    state_mins: list[np.ndarray] = []
    state_maxs: list[np.ndarray] = []
    frames = 0
    for episode in range(episodes):
        frame = read_episode(repo, revision, episode)
        if "action" not in frame or "observation.state" not in frame:
            raise ValueError(f"episode {episode} lacks action/observation.state: {list(frame.columns)}")
        action = np.stack(frame["action"].values)
        state = np.stack(frame["observation.state"].values)
        action_mins.append(action.min(axis=0))
        action_maxs.append(action.max(axis=0))
        state_mins.append(state.min(axis=0))
        state_maxs.append(state.max(axis=0))
        frames += len(frame)

    action_low = np.min(np.stack(action_mins), axis=0)
    action_high = np.max(np.stack(action_maxs), axis=0)
    state_low = np.min(np.stack(state_mins), axis=0)
    state_high = np.max(np.stack(state_maxs), axis=0)

    scene = scene_ctrlrange(xml_path)
    scene_low = np.array([scene[name][0] for name in JOINT_NAMES])
    scene_high = np.array([scene[name][1] for name in JOINT_NAMES])
    scene_low_deg = np.degrees(scene_low)
    scene_high_deg = np.degrees(scene_high)

    def as_list(values: np.ndarray) -> list[float]:
        return [float(x) for x in values]

    return {
        "kind": "public_real_so101_range_audit_not_policy_result",
        "dataset": {
            "repo": repo,
            "revision": revision,
            "episodes_read": episodes,
            "frames_read": frames,
            "robot_type": "so101_follower",
            "created_at": "2025-06-14",
            "license": "apache-2.0",
            "task": "Pick the red object and place it in the box",
            "cameras": ["observation.images.side", "observation.images.wrist.left"],
            "units": "dataset-era degrees ([-180,180]); gripper 0--100; no calibration file in the dataset",
        },
        "action_range_public": as_list(action_low) + as_list(action_high),
        "state_range_public": as_list(state_low) + as_list(state_high),
        "action_min_deg": as_list(action_low),
        "action_max_deg": as_list(action_high),
        "scene_ctrlrange_rad": scene,
        "scene_ctrlrange_deg_low": as_list(scene_low_deg),
        "scene_ctrlrange_deg_high": as_list(scene_high_deg),
        "overflow_deg": {
            "low": as_list(np.maximum(0.0, scene_low_deg - action_low)),
            "high": as_list(np.maximum(0.0, action_high - scene_high_deg)),
        },
        "finding": (
            "A real so101_follower dataset reaches elbow_flex=100.0 deg, reproducing "
            "the +3.17 deg overflow against the XML upper limit 96.83 deg; wrist_flex "
            "max is 86.1 deg in this task, so the svla 99.49 deg wrist overflow is not "
            "reproduced here.  The XML elbow limit is therefore conservative relative "
            "to observed real SO-101 use, not necessarily a SO-100-only artifact."
        ),
        "limitations": [
            "No calibration file is included, so the dataset's zero/range cannot be mapped exactly onto the project SO-101.",
            "This is one real SO-101 dataset and one task; it does not prove the mechanical limit of all SO-101 units.",
            "No weights were loaded and no policy action was executed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--revision", default=DEFAULT_REVISION)
    parser.add_argument("--episodes", type=int, default=DEFAULT_EPISODES)
    parser.add_argument("--xml", type=Path, default=DEFAULT_XML)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("real-so101-reference.json"))
    args = parser.parse_args()
    result = audit(args.repo, args.revision, args.episodes, args.xml)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "output": str(args.output),
        "episodes": result["dataset"]["episodes_read"],
        "frames": result["dataset"]["frames_read"],
        "overflow_deg": result["overflow_deg"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
