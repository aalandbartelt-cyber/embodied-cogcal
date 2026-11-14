"""Validate a TPSC pilot/full manifest without running MuJoCo or a policy.

Checks counts, pair matching, task-family geometry and table bounds.  This is a
geometry/schema audit, not evidence that the tasks are reachable or that TPSC
works.

Run:

    python experiments/so101/tpsc-pilot/validate_manifest.py \
      --manifest experiments/so101/tpsc-pilot/manifest-pilot.jsonl --mode pilot
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = {
    "schema_version",
    "kind",
    "episode_id",
    "pair_id",
    "family",
    "branch",
    "task_text",
    "red_pose",
    "blue_pose",
    "goal_pose",
    "target_object",
    "success_predicate",
    "barrier_pose",
    "barrier_size",
    "preferred_route",
    "pilot",
    "seed",
}
FAMILIES = {"shared_prefix", "no_common_prefix", "multi_valid"}


def _load(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        records.append(record)
    return records


def _pose(record: dict[str, Any], key: str) -> tuple[float, float, float]:
    value = record[key]
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{record['episode_id']}: {key} must be a 3-vector")
    pose = tuple(float(x) for x in value)
    if not all(math.isfinite(x) for x in pose):
        raise ValueError(f"{record['episode_id']}: {key} must be finite")
    return pose


def _check_bounds(record: dict[str, Any], errors: list[str]) -> None:
    eid = record.get("episode_id", "?")
    red = _pose(record, "red_pose")
    blue = _pose(record, "blue_pose")
    goal = _pose(record, "goal_pose")
    for name, pose in (("red", red), ("blue", blue)):
        if not (0.05 <= pose[0] <= 0.40 and -0.40 <= pose[1] <= 0.40):
            errors.append(f"{eid}: {name} object outside table bounds: {pose}")
        if abs(pose[2] - 0.036) > 1e-6:
            errors.append(f"{eid}: {name} object z must be 0.036, got {pose[2]}")
    if not (0.10 <= goal[0] <= 0.40 and -0.30 <= goal[1] <= 0.30):
        errors.append(f"{eid}: goal outside table bounds: {goal}")
    if abs(goal[2] - 0.003) > 1e-6:
        errors.append(f"{eid}: goal z must be 0.003, got {goal[2]}")
    barrier = record.get("barrier_pose")
    if barrier is not None:
        b = _pose(record, "barrier_pose")
        if not (0.10 <= b[0] <= 0.35 and -0.30 <= b[1] <= 0.30):
            errors.append(f"{eid}: barrier outside allowed bounds: {b}")
        if abs(b[2] - 0.04) > 1e-6:
            errors.append(f"{eid}: barrier z must be 0.04, got {b[2]}")


def _check_shared(records: list[dict[str, Any]], errors: list[str]) -> None:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_pair[record["pair_id"]].append(record)
    for pair_id, pair_records in by_pair.items():
        branches = {record["branch"] for record in pair_records}
        if branches != {"left", "right"}:
            errors.append(f"{pair_id}: shared pair branches must be left/right, got {branches}")
            continue
        by_index: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        for record in pair_records:
            index = record["episode_id"].rsplit("_", 1)[0]
            by_index[index][record["branch"]] = record
        for index, pair in by_index.items():
            if set(pair) != {"left", "right"}:
                errors.append(f"{pair_id}/{index}: missing branch")
                continue
            left, right = pair["left"], pair["right"]
            for key in ("red_pose", "blue_pose"):
                if left[key] != right[key]:
                    errors.append(f"{pair_id}/{index}: {key} must match across branches")
            if left["goal_pose"] == right["goal_pose"]:
                errors.append(f"{pair_id}/{index}: goals must differ across branches")
            if abs(left["goal_pose"][1] - right["goal_pose"][1]) <= 0.20:
                errors.append(f"{pair_id}/{index}: shared goals are too close: {left['goal_pose']} vs {right['goal_pose']}")
            if left["target_object"] != "red" or right["target_object"] != "red":
                errors.append(f"{pair_id}/{index}: shared pair must target red in both branches")


def _check_no_common(records: list[dict[str, Any]], errors: list[str]) -> None:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_pair[record["pair_id"]].append(record)
    for pair_id, pair_records in by_pair.items():
        branches = {record["branch"] for record in pair_records}
        if branches != {"red", "blue"}:
            errors.append(f"{pair_id}: no-common branches must be red/blue, got {branches}")
            continue
        by_index: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        for record in pair_records:
            index = record["episode_id"].rsplit("_", 1)[0]
            by_index[index][record["branch"]] = record
        for index, pair in by_index.items():
            if set(pair) != {"red", "blue"}:
                errors.append(f"{pair_id}/{index}: missing branch")
                continue
            red, blue = pair["red"], pair["blue"]
            if red["target_object"] != "red" or blue["target_object"] != "blue":
                errors.append(f"{pair_id}/{index}: branch/target mismatch")
            if red["red_pose"] == blue["red_pose"]:
                errors.append(f"{pair_id}/{index}: red object pose must differ between branches")
            if red["blue_pose"] == blue["blue_pose"]:
                errors.append(f"{pair_id}/{index}: blue object pose must differ between branches")
            if abs(red["goal_pose"][1] - blue["goal_pose"][1]) <= 0.20:
                errors.append(f"{pair_id}/{index}: no-common goals are too close")


def _check_multi(records: list[dict[str, Any]], errors: list[str]) -> None:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_pair[record["pair_id"]].append(record)
    for pair_id, pair_records in by_pair.items():
        branches = {record["branch"] for record in pair_records}
        if branches != {"left", "right"}:
            errors.append(f"{pair_id}: multi-valid branches must be left/right, got {branches}")
            continue
        by_index: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        for record in pair_records:
            index = record["episode_id"].rsplit("_", 1)[0]
            by_index[index][record["branch"]] = record
        for index, pair in by_index.items():
            if set(pair) != {"left", "right"}:
                errors.append(f"{pair_id}/{index}: missing branch")
                continue
            left, right = pair["left"], pair["right"]
            for key in ("red_pose", "blue_pose", "goal_pose", "barrier_pose", "barrier_size"):
                if left[key] != right[key]:
                    errors.append(f"{pair_id}/{index}: {key} must match across routes")
            if left["preferred_route"] != "left" or right["preferred_route"] != "right":
                errors.append(f"{pair_id}/{index}: preferred_route mismatch")
            if left["barrier_pose"] is None:
                errors.append(f"{pair_id}/{index}: multi-valid requires a barrier")


def validate(records: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    errors: list[str] = []
    if not records:
        return {"records": 0, "errors": ["empty manifest"]}
    for record in records:
        missing = REQUIRED_FIELDS - set(record)
        if missing:
            errors.append(f"{record.get('episode_id', '?')}: missing fields {sorted(missing)}")
            continue
        if record["family"] not in FAMILIES:
            errors.append(f"{record['episode_id']}: unknown family {record['family']}")
        if record["kind"] != "tpsc_manifest_record_not_policy_result":
            errors.append(f"{record['episode_id']}: unexpected kind {record['kind']}")
        if not record["task_text"]:
            errors.append(f"{record['episode_id']}: empty task_text")
        _check_bounds(record, errors)

    counts = Counter(record["family"] for record in records)
    pair_counts = Counter((record["family"], record["pair_id"]) for record in records)
    if mode == "pilot":
        if len(records) != 20:
            errors.append(f"pilot must have 20 records, got {len(records)}")
        if counts != {"shared_prefix": 20}:
            errors.append(f"pilot must be shared_prefix only, got {dict(counts)}")
        if pair_counts != {("shared_prefix", "shared_left_right"): 20}:
            errors.append(f"pilot pair counts unexpected: {dict(pair_counts)}")
        _check_shared(records, errors)
    else:
        if len(records) != 120:
            errors.append(f"full must have 120 records, got {len(records)}")
        for family in FAMILIES:
            if counts.get(family, 0) != 40:
                errors.append(f"full family {family} must have 40 records, got {counts.get(family, 0)}")
        _check_shared([r for r in records if r["family"] == "shared_prefix"], errors)
        _check_no_common([r for r in records if r["family"] == "no_common_prefix"], errors)
        _check_multi([r for r in records if r["family"] == "multi_valid"], errors)

    return {
        "records": len(records),
        "mode": mode,
        "families": dict(counts),
        "pairs": {f"{family}/{pair}": count for (family, pair), count in sorted(pair_counts.items())},
        "errors": errors,
        "ok": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--mode", choices=("pilot", "full"), default="pilot")
    args = parser.parse_args()
    records = _load(args.manifest)
    result = validate(records, args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
