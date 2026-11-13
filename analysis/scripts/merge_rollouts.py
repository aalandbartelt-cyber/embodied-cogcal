"""Merge probe metadata and model rollout JSONL by episode_id."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path

PRIVILEGED_FIELDS = {
    "evaluator_target_pose",
    "hidden_success_label",
    "privileged_scene_state",
}


def _read(path: str | Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at {path}:{line_number}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"JSONL row at {path}:{line_number} must be an object")
            rows.append(row)
    return rows


def _index(rows: Iterable[dict[str, object]], label: str) -> dict[str, dict[str, object]]:
    indexed: dict[str, dict[str, object]] = {}
    for row in rows:
        episode_id = row.get("episode_id")
        if not isinstance(episode_id, str) or not episode_id:
            raise ValueError(f"{label} row is missing episode_id")
        if episode_id in indexed:
            raise ValueError(f"duplicate episode_id in {label}: {episode_id}")
        indexed[episode_id] = row
    return indexed


def _assert_no_privileged(rows: Iterable[dict[str, object]]) -> None:
    for row in rows:
        found = PRIVILEGED_FIELDS.intersection(row)
        if found:
            names = ", ".join(sorted(found))
            raise ValueError(f"privileged fields are forbidden in merged records: {names}")


def merge_jsonl(metadata_path: str | Path, rollout_path: str | Path, output_path: str | Path) -> int:
    """Strictly merge metadata and rollout records and return row count."""

    metadata = _index(_read(metadata_path), "metadata")
    rollouts = _index(_read(rollout_path), "rollout")
    _assert_no_privileged(metadata.values())
    _assert_no_privileged(rollouts.values())

    missing = sorted(set(metadata) - set(rollouts))
    extra = sorted(set(rollouts) - set(metadata))
    if missing:
        raise ValueError(f"missing rollout records: {missing}")
    if extra:
        raise ValueError(f"rollout records have no metadata: {extra}")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for episode_id in metadata:
            merged = dict(metadata[episode_id])
            overlap = set(merged).intersection(rollouts[episode_id]) - {"episode_id"}
            if overlap:
                fields = ", ".join(sorted(overlap))
                raise ValueError(f"metadata/rollout fields overlap: {fields}")
            merged.update(rollouts[episode_id])
            handle.write(json.dumps(merged, ensure_ascii=False, sort_keys=True) + "\n")
    return len(metadata)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metadata", type=Path)
    parser.add_argument("rollout", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    count = merge_jsonl(args.metadata, args.rollout, args.output)
    print(f"merged {count} episodes into {args.output}")


if __name__ == "__main__":
    main()
