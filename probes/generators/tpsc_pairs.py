"""Generate TPSC paired-task episode manifests for the SO-101 pilot.

This is evaluator-side metadata only: no policy, no success label leakage into
observations, no TPSC method.  The pilot mode emits exactly one shared-prefix
pair (2 branches x 10 episodes = 20 records).  Full mode emits 3 families x
2 pairs x 2 branches x 10 episodes = 120 records.

Run:

    python -m probes.generators.tpsc_pairs --mode pilot \
      --output experiments/so101/tpsc-pilot/manifest-pilot.jsonl

The scene is ``simulation/so101/tpsc_scene.xml``; see
``experiments/so101/tpsc-data-protocol.md``.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
PARKED_Y = 0.36
OBJECT_Z = 0.036
GOAL_Z = 0.003


def _jitter(rng: random.Random, value: float, scale: float) -> float:
    return value + rng.uniform(-scale, scale)


def _pose(x: float, y: float, z: float) -> list[float]:
    return [float(x), float(y), float(z)]


def _record(
    *,
    episode_id: str,
    pair_id: str,
    family: str,
    branch: str,
    task_text: str,
    red_pose: list[float],
    blue_pose: list[float],
    goal_pose: list[float],
    target_object: str,
    barrier_pose: list[float] | None,
    barrier_size: list[float] | None,
    preferred_route: str | None,
    pilot: bool,
    seed: int,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "tpsc_manifest_record_not_policy_result",
        "episode_id": episode_id,
        "pair_id": pair_id,
        "family": family,
        "branch": branch,
        "task_text": task_text,
        "red_pose": red_pose,
        "blue_pose": blue_pose,
        "goal_pose": goal_pose,
        "target_object": target_object,
        "success_predicate": f"{target_object}_object_in_goal",
        "barrier_pose": barrier_pose,
        "barrier_size": barrier_size,
        "preferred_route": preferred_route,
        "pilot": pilot,
        "seed": seed,
    }


def _shared_pair(
    rng: random.Random,
    *,
    pair_id: str,
    object_nominal: tuple[float, float],
    goal_left: tuple[float, float],
    goal_right: tuple[float, float],
    episodes_per_branch: int,
    pilot: bool,
    seed: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    blue_parked = _pose(0.14, PARKED_Y, OBJECT_Z)
    for index in range(episodes_per_branch):
        red = _pose(
            _jitter(rng, object_nominal[0], 0.01),
            _jitter(rng, object_nominal[1], 0.02),
            OBJECT_Z,
        )
        left = _pose(
            _jitter(rng, goal_left[0], 0.01),
            _jitter(rng, goal_left[1], 0.02),
            GOAL_Z,
        )
        right = _pose(
            _jitter(rng, goal_right[0], 0.01),
            _jitter(rng, goal_right[1], 0.02),
            GOAL_Z,
        )
        for branch, goal, text in (
            ("left", left, "把红色方块放到左边盒子。"),
            ("right", right, "把红色方块放到右边盒子。"),
        ):
            records.append(
                _record(
                    episode_id=f"{pair_id}_{index:04d}_{branch}",
                    pair_id=pair_id,
                    family="shared_prefix",
                    branch=branch,
                    task_text=text,
                    red_pose=red,
                    blue_pose=blue_parked,
                    goal_pose=goal,
                    target_object="red",
                    barrier_pose=None,
                    barrier_size=None,
                    preferred_route=None,
                    pilot=pilot,
                    seed=seed,
                )
            )
    return records


def _no_common_pair(
    rng: random.Random,
    *,
    pair_id: str,
    red_nominal: tuple[float, float],
    blue_nominal: tuple[float, float],
    goal_red: tuple[float, float],
    goal_blue: tuple[float, float],
    episodes_per_branch: int,
    pilot: bool,
    seed: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    red_parked = _pose(0.14, -PARKED_Y, OBJECT_Z)
    blue_parked = _pose(0.14, PARKED_Y, OBJECT_Z)
    for index in range(episodes_per_branch):
        red = _pose(
            _jitter(rng, red_nominal[0], 0.01),
            _jitter(rng, red_nominal[1], 0.02),
            OBJECT_Z,
        )
        blue = _pose(
            _jitter(rng, blue_nominal[0], 0.01),
            _jitter(rng, blue_nominal[1], 0.02),
            OBJECT_Z,
        )
        red_goal = _pose(
            _jitter(rng, goal_red[0], 0.01),
            _jitter(rng, goal_red[1], 0.02),
            GOAL_Z,
        )
        blue_goal = _pose(
            _jitter(rng, goal_blue[0], 0.01),
            _jitter(rng, goal_blue[1], 0.02),
            GOAL_Z,
        )
        records.append(
            _record(
                episode_id=f"{pair_id}_{index:04d}_red",
                pair_id=pair_id,
                family="no_common_prefix",
                branch="red",
                task_text="把红色方块放到左边盒子。",
                red_pose=red,
                blue_pose=blue_parked,
                goal_pose=red_goal,
                target_object="red",
                barrier_pose=None,
                barrier_size=None,
                preferred_route=None,
                pilot=pilot,
                seed=seed,
            )
        )
        records.append(
            _record(
                episode_id=f"{pair_id}_{index:04d}_blue",
                pair_id=pair_id,
                family="no_common_prefix",
                branch="blue",
                task_text="把蓝色方块放到右边盒子。",
                red_pose=red_parked,
                blue_pose=blue,
                goal_pose=blue_goal,
                target_object="blue",
                barrier_pose=None,
                barrier_size=None,
                preferred_route=None,
                pilot=pilot,
                seed=seed,
            )
        )
    return records


def _multi_valid_pair(
    rng: random.Random,
    *,
    pair_id: str,
    object_nominal: tuple[float, float],
    goal_nominal: tuple[float, float],
    barrier_nominal: tuple[float, float],
    barrier_size: tuple[float, float, float],
    episodes_per_branch: int,
    pilot: bool,
    seed: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    blue_parked = _pose(0.14, PARKED_Y, OBJECT_Z)
    for index in range(episodes_per_branch):
        red = _pose(
            _jitter(rng, object_nominal[0], 0.01),
            _jitter(rng, object_nominal[1], 0.02),
            OBJECT_Z,
        )
        goal = _pose(
            _jitter(rng, goal_nominal[0], 0.01),
            _jitter(rng, goal_nominal[1], 0.02),
            GOAL_Z,
        )
        barrier = _pose(
            _jitter(rng, barrier_nominal[0], 0.01),
            _jitter(rng, barrier_nominal[1], 0.02),
            0.04,
        )
        barrier_size_list = [float(x) for x in barrier_size]
        for route in ("left", "right"):
            records.append(
                _record(
                    episode_id=f"{pair_id}_{index:04d}_{route}",
                    pair_id=pair_id,
                    family="multi_valid",
                    branch=route,
                    task_text="把红色方块放到中间盒子。",
                    red_pose=red,
                    blue_pose=blue_parked,
                    goal_pose=goal,
                    target_object="red",
                    barrier_pose=barrier,
                    barrier_size=barrier_size_list,
                    preferred_route=route,
                    pilot=pilot,
                    seed=seed,
                )
            )
    return records


def waypoint_targets(record: dict[str, Any]) -> list[tuple[str, list[float]]]:
    """Task-space waypoints used by the scripted prefix smoke.

    The shared segment is above_object -> grasp -> lift.  Shared-prefix pairs
    have identical waypoints there; no-common pairs differ from above_object;
    multi-valid pairs share the prefix and differ at the route waypoint.
    """
    target = record["target_object"]
    obj = [float(x) for x in record[f"{target}_pose"]]
    goal = [float(x) for x in record["goal_pose"]]
    waypoints: list[tuple[str, list[float]]] = [
        ("above_object", [obj[0], obj[1], obj[2] + 0.12]),
        ("grasp", [obj[0], obj[1], obj[2] + 0.02]),
        ("lift", [obj[0], obj[1], obj[2] + 0.15]),
    ]
    if record["family"] == "multi_valid":
        sign = 1.0 if record["branch"] == "left" else -1.0
        waypoints.append(("route", [goal[0] - 0.09, goal[1] + sign * 0.12, 0.15]))
    waypoints.extend(
        [
            ("above_goal", [goal[0], goal[1], goal[2] + 0.15]),
            ("place", [goal[0], goal[1], goal[2] + 0.04]),
            ("retreat", [goal[0], goal[1], goal[2] + 0.15]),
        ]
    )
    return waypoints


def generate_records(
    *,
    mode: str = "pilot",
    seed: int = 42,
    episodes_per_branch: int = 10,
) -> list[dict[str, Any]]:
    """Generate deterministic pilot/full TPSC manifests."""
    if mode not in {"pilot", "full"}:
        raise ValueError("mode must be pilot or full")
    if episodes_per_branch < 1:
        raise ValueError("episodes_per_branch must be positive")
    rng = random.Random(seed)
    pilot = mode == "pilot"

    shared_specs = [
        {
            "pair_id": "shared_left_right",
            "object_nominal": (0.14, 0.0),
            "goal_left": (0.30, 0.18),
            "goal_right": (0.30, -0.18),
        },
        {
            "pair_id": "shared_left_right_02",
            "object_nominal": (0.12, 0.02),
            "goal_left": (0.28, 0.15),
            "goal_right": (0.28, -0.15),
        },
    ]
    no_common_specs = [
        {
            "pair_id": "no_common_red_blue",
            "red_nominal": (0.14, -0.12),
            "blue_nominal": (0.14, 0.12),
            "goal_red": (0.30, -0.18),
            "goal_blue": (0.30, 0.18),
        },
        {
            "pair_id": "no_common_red_blue_02",
            "red_nominal": (0.16, -0.10),
            "blue_nominal": (0.16, 0.10),
            "goal_red": (0.28, -0.14),
            "goal_blue": (0.28, 0.14),
        },
    ]
    multi_specs = [
        {
            "pair_id": "multi_valid_center",
            "object_nominal": (0.12, 0.0),
            "goal_nominal": (0.31, 0.0),
            "barrier_nominal": (0.19, 0.0),
            "barrier_size": (0.02, 0.06, 0.04),
        },
        {
            "pair_id": "multi_valid_offset",
            "object_nominal": (0.12, 0.02),
            "goal_nominal": (0.31, -0.02),
            "barrier_nominal": (0.19, 0.02),
            "barrier_size": (0.02, 0.05, 0.04),
        },
    ]

    records: list[dict[str, Any]] = []
    for spec in shared_specs if mode == "full" else shared_specs[:1]:
        records.extend(
            _shared_pair(
                rng,
                pair_id=spec["pair_id"],
                object_nominal=spec["object_nominal"],
                goal_left=spec["goal_left"],
                goal_right=spec["goal_right"],
                episodes_per_branch=episodes_per_branch,
                pilot=pilot,
                seed=seed,
            )
        )
    if mode == "full":
        for spec in no_common_specs:
            records.extend(
                _no_common_pair(
                    rng,
                    pair_id=spec["pair_id"],
                    red_nominal=spec["red_nominal"],
                    blue_nominal=spec["blue_nominal"],
                    goal_red=spec["goal_red"],
                    goal_blue=spec["goal_blue"],
                    episodes_per_branch=episodes_per_branch,
                    pilot=pilot,
                    seed=seed,
                )
            )
        for spec in multi_specs:
            records.extend(
                _multi_valid_pair(
                    rng,
                    pair_id=spec["pair_id"],
                    object_nominal=spec["object_nominal"],
                    goal_nominal=spec["goal_nominal"],
                    barrier_nominal=spec["barrier_nominal"],
                    barrier_size=spec["barrier_size"],
                    episodes_per_branch=episodes_per_branch,
                    pilot=pilot,
                    seed=seed,
                )
            )
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("pilot", "full"), default="pilot")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--episodes-per-branch", type=int, default=10)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = generate_records(
        mode=args.mode,
        seed=args.seed,
        episodes_per_branch=args.episodes_per_branch,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "mode": args.mode,
                "records": len(records),
                "families": sorted({record["family"] for record in records}),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
