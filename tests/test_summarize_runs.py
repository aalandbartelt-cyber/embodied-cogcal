from __future__ import annotations

import json

import pandas as pd

from analysis.scripts.summarize_runs import load_episode_records, summarize_success


def test_summarize_success_groups_by_condition_and_calibration_variant(tmp_path):
    path = tmp_path / "episodes.jsonl"
    rows = [
        {"calibration_variant": "raw", "semantic_condition": "neutral", "execution_condition": "nominal", "task_success": True},
        {"calibration_variant": "raw", "semantic_condition": "neutral", "execution_condition": "nominal", "task_success": False},
        {"calibration_variant": "eccbf", "semantic_condition": "conflict", "execution_condition": "perturbed", "task_success": True},
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    summary = summarize_success(load_episode_records(path))

    assert isinstance(summary, pd.DataFrame)
    raw = summary.query("calibration_variant == 'raw'").iloc[0]
    assert raw["n"] == 2
    assert raw["successes"] == 1
    assert raw["success_rate"] == 0.5


def test_load_episode_records_rejects_missing_success_field(tmp_path):
    path = tmp_path / "episodes.jsonl"
    path.write_text('{"calibration_variant": "raw"}\n', encoding="utf-8")

    try:
        list(load_episode_records(path))
    except ValueError as exc:
        assert "task_success" in str(exc)
    else:
        raise AssertionError("missing task_success should be rejected")
