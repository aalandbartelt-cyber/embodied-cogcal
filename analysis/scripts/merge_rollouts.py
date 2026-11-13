"""Merge probe metadata and one calibration variant's rollout JSONL by episode_id."""

from __future__ import annotations

import argparse
import json
import tempfile
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
        if "step" in row or row.get("record_type") == "step":
            raise ValueError(f"not a paper episode (step trace) in {label}: {episode_id}")
        if (
            row.get("experiment_kind") == "plumbing_smoke"
            or row.get("failure_reason") == "scripted_plumbing_smoke_only"
        ):
            raise ValueError(f"not a paper episode (plumbing smoke) in {label}: {episode_id}")
        if "task_success" in row:
            success = row["task_success"]
            if not isinstance(success, bool) and not (
                isinstance(success, int) and success in (0, 1)
            ):
                raise ValueError("task_success must be a boolean or integer 0/1")
        if episode_id in indexed:
            raise ValueError(
                f"duplicate episode_id in {label}: {episode_id}; "
                "require one rollout per episode and one calibration variant per file"
            )
        indexed[episode_id] = row
    if not indexed:
        raise ValueError(f"{label} input is empty")
    return indexed


def _assert_no_privileged(rows: Iterable[dict[str, object]]) -> None:
    pending: list[object] = list(rows)
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            found = PRIVILEGED_FIELDS.intersection(value)
            if found:
                names = ", ".join(sorted(found))
                raise ValueError(f"privileged fields are forbidden in merged records: {names}")
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)


def merge_jsonl(metadata_path: str | Path, rollout_path: str | Path, output_path: str | Path) -> int:
    """Merge one rollout per episode, with one calibration variant per file.

    Validate the complete join before atomically replacing the output. Run this
    separately for each calibration variant; episode_id alone is the join key.
    """

    output = Path(output_path)
    for input_path in (Path(metadata_path), Path(rollout_path)):
        if output.resolve() == input_path.resolve() or (
            output.exists() and input_path.exists() and output.samefile(input_path)
        ):
            raise ValueError("output path must differ from every input path")

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

    merged_rows = []
    for episode_id in metadata:
        merged = dict(metadata[episode_id])
        overlap = set(merged).intersection(rollouts[episode_id]) - {"episode_id"}
        if overlap:
            fields = ", ".join(sorted(overlap))
            raise ValueError(f"metadata/rollout fields overlap: {fields}")
        merged.update(rollouts[episode_id])
        merged_rows.append(merged)

    variants = [row["calibration_variant"] for row in merged_rows if "calibration_variant" in row]
    if variants and any(variant != variants[0] for variant in variants[1:]):
        raise ValueError("merge requires one calibration variant per file")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=output.parent, prefix=f".{output.name}.", delete=False
        ) as handle:
            temporary = Path(handle.name)
            for merged in merged_rows:
                handle.write(json.dumps(merged, ensure_ascii=False, sort_keys=True) + "\n")
        temporary.replace(output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
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
