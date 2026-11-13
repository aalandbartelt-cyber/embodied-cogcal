"""Summarize episode JSONL without editing the raw source data.

Legacy files with no episode_id are accepted, but their uniqueness cannot be verified.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path

import pandas as pd

from cogcal.metrics import wilson_interval

REQUIRED_FIELDS = {
    "calibration_variant",
    "semantic_condition",
    "execution_condition",
    "task_success",
}
EPISODE_CONTEXT_FIELDS = ("domain", "domain_id", "model", "model_id", "model_name")
OPTIONAL_GROUP_FIELDS = (*EPISODE_CONTEXT_FIELDS, "task", "task_id")


def _validate_record(record: object, source: str) -> None:
    if not isinstance(record, Mapping):
        raise ValueError(f"record at {source} must be an object")
    if "step" in record or record.get("record_type") == "step":
        raise ValueError(f"not a paper episode (step trace) at {source}")
    if (
        record.get("experiment_kind") == "plumbing_smoke"
        or record.get("failure_reason") == "scripted_plumbing_smoke_only"
    ):
        raise ValueError(f"not a paper episode (plumbing smoke) at {source}")
    missing = REQUIRED_FIELDS.difference(record)
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"record at {source} is missing required fields: {names}")
    success = record["task_success"]
    if not isinstance(success, bool) and not (isinstance(success, int) and success in (0, 1)):
        raise ValueError(f"task_success at {source} must be a boolean or integer 0/1")


def load_episode_records(path: str | Path) -> Iterator[dict[str, object]]:
    """Yield validated JSONL records while preserving the raw file."""

    path = Path(path)
    count = 0
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            source = f"{path}:{line_number}"
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at {source}") from exc
            _validate_record(record, source)
            count += 1
            yield record
    if not count:
        raise ValueError(f"episode input is empty: {path}")


def summarize_success(records: Iterable[Mapping[str, object]]) -> pd.DataFrame:
    """Aggregate success rate and Wilson interval by experimental condition.

    When IDs are provided, require one row per episode, calibration variant and
    available domain/model context. Task, condition and seed fields do not make
    repeated IDs independent episodes. Legacy rows may all omit episode_id.
    """

    rows = list(records)
    for number, record in enumerate(rows, start=1):
        _validate_record(record, f"record {number}")
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise ValueError("at least one episode record is required")

    if "episode_id" in frame.columns:
        if any(
            not isinstance(record.get("episode_id"), str) or not record["episode_id"]
            for record in rows
        ):
            raise ValueError("episode_id must be a nonempty string on every record when provided")
        identity_columns = [field for field in EPISODE_CONTEXT_FIELDS if field in frame.columns]
        identity_columns += ["calibration_variant", "episode_id"]
        duplicates = frame.duplicated(subset=identity_columns)
        if duplicates.any():
            episode_id = frame.loc[duplicates, "episode_id"].iloc[0]
            raise ValueError(f"duplicate episode_id within calibration variant and domain/model: {episode_id}")

    group_columns = [field for field in OPTIONAL_GROUP_FIELDS if field in frame.columns] + [
        "calibration_variant",
        "semantic_condition",
        "execution_condition",
    ]
    grouped = (
        frame.assign(task_success=frame["task_success"].astype(int))
        .groupby(group_columns, dropna=False)["task_success"]
        .agg(n="size", successes="sum")
        .reset_index()
    )
    intervals = grouped.apply(
        lambda row: wilson_interval(int(row["successes"]), int(row["n"])), axis=1
    )
    grouped["success_rate"] = grouped["successes"] / grouped["n"]
    grouped["ci_low"] = [interval[0] for interval in intervals]
    grouped["ci_high"] = [interval[1] for interval in intervals]
    return grouped.sort_values(group_columns).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="raw episode JSONL")
    parser.add_argument("--output", type=Path, required=True, help="summary CSV path")
    args = parser.parse_args()
    if args.output.resolve() == args.input.resolve() or (
        args.output.exists() and args.input.exists() and args.output.samefile(args.input)
    ):
        raise ValueError("output path must differ from the input path")
    summary = summarize_success(load_episode_records(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=args.output.parent,
            prefix=f".{args.output.name}.", delete=False,
        ) as handle:
            temporary = Path(handle.name)
            summary.to_csv(handle, index=False)
        temporary.replace(args.output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
