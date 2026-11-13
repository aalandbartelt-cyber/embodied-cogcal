"""Summarize episode JSONL without editing the raw source data."""

from __future__ import annotations

import argparse
import json
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


def load_episode_records(path: str | Path) -> Iterator[dict[str, object]]:
    """Yield validated JSONL records while preserving the raw file."""

    path = Path(path)
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            missing = REQUIRED_FIELDS.difference(record)
            if missing:
                names = ", ".join(sorted(missing))
                raise ValueError(f"line {line_number} is missing required fields: {names}")
            yield record


def summarize_success(records: Iterable[Mapping[str, object]]) -> pd.DataFrame:
    """Aggregate success rate and Wilson interval by experimental condition."""

    frame = pd.DataFrame(list(records))
    if frame.empty:
        raise ValueError("at least one episode record is required")

    group_columns = [
        "calibration_variant",
        "semantic_condition",
        "execution_condition",
    ]
    grouped = (
        frame.assign(task_success=frame["task_success"].astype(bool))
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
    summary = summarize_success(load_episode_records(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
