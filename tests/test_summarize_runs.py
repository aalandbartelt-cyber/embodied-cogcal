from __future__ import annotations

import json
import sys

import pandas as pd
import pytest

from analysis.scripts.summarize_runs import load_episode_records, main, summarize_success


def _episode(**values):
    return {
        "calibration_variant": "raw",
        "semantic_condition": "neutral",
        "execution_condition": "nominal",
        "task_success": True,
        **values,
    }


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


@pytest.mark.parametrize("success", ["false", "true", None, 2, -1, 0.0, 1.0, [], {}])
@pytest.mark.parametrize("load_from_file", [False, True])
def test_summary_rejects_nonbinary_success_labels(tmp_path, success, load_from_file):
    record = _episode(task_success=success)
    path = tmp_path / "episodes.jsonl"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="task_success.*boolean.*0/1"):
        if load_from_file:
            list(load_episode_records(path))
        else:
            summarize_success([record])


def test_summary_accepts_booleans_and_binary_integers():
    summary = summarize_success([_episode(task_success=value) for value in [True, False, 0, 1]])

    assert summary.iloc[0]["n"] == 4
    assert summary.iloc[0]["successes"] == 2
    assert summary.iloc[0]["success_rate"] == 0.5


@pytest.mark.parametrize("marker", [{"step": 0}, {"failure_reason": "scripted_plumbing_smoke_only"}])
@pytest.mark.parametrize("load_from_file", [False, True])
def test_summary_rejects_step_and_scripted_smoke_records(tmp_path, marker, load_from_file):
    record = _episode(**marker)
    path = tmp_path / "episodes.jsonl"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="episode.*step|smoke"):
        if load_from_file:
            list(load_episode_records(path))
        else:
            summarize_success([record])


@pytest.mark.parametrize("marker", [{"record_type": "step"}, {"experiment_kind": "plumbing_smoke"}])
@pytest.mark.parametrize("load_from_file", [False, True])
def test_summary_rejects_explicit_nonpaper_records_before_missing_success(tmp_path, marker, load_from_file):
    record = _episode(**marker)
    del record["task_success"]
    path = tmp_path / "episodes.jsonl"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="not a paper episode"):
        if load_from_file:
            list(load_episode_records(path))
        else:
            summarize_success([record])


@pytest.mark.parametrize("field", ["domain", "domain_id", "model", "model_id", "model_name", "task", "task_id"])
def test_summary_keeps_available_domain_model_and_task_groups_separate(field):
    summary = summarize_success([
        _episode(**{field: "first"}),
        _episode(**{field: "second"}, task_success=False),
        _episode(task_success=False),
    ])

    assert len(summary) == 3
    assert summary["n"].tolist() == [1, 1, 1]
    assert summary.loc[summary[field] == "first", "success_rate"].item() == 1.0
    assert summary.loc[summary[field].isna(), "success_rate"].item() == 0.0


@pytest.mark.parametrize("contents", ["", "\n  \n"])
def test_loader_rejects_empty_input(tmp_path, contents):
    path = tmp_path / "episodes.jsonl"
    path.write_text(contents, encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        list(load_episode_records(path))


def test_summary_rejects_empty_records():
    with pytest.raises(ValueError, match="at least one episode"):
        summarize_success([])


@pytest.mark.parametrize("contents", ["[]\n", "null\n", '"record"\n', "invalid\n"])
def test_loader_reports_malformed_records_with_source_line(tmp_path, contents):
    path = tmp_path / "episodes.jsonl"
    path.write_text("\n" + contents, encoding="utf-8")

    with pytest.raises(ValueError, match=r"episodes.jsonl:2"):
        list(load_episode_records(path))


def test_summary_validates_required_fields_for_direct_call():
    with pytest.raises(ValueError, match="missing required fields.*task_success"):
        summarize_success([{"calibration_variant": "raw"}])


@pytest.mark.parametrize("alias", ["same", "symlink", "hardlink"])
def test_summary_cli_rejects_output_aliasing_input(tmp_path, monkeypatch, alias):
    source = tmp_path / "episodes.jsonl"
    source.write_text(json.dumps(_episode()) + "\n", encoding="utf-8")
    original = source.read_bytes()
    output = source if alias == "same" else tmp_path / "summary.csv"
    if alias == "symlink":
        output.symlink_to(source)
    elif alias == "hardlink":
        output.hardlink_to(source)
    monkeypatch.setattr(sys, "argv", ["summarize_runs", str(source), "--output", str(output)])

    with pytest.raises(ValueError, match="output.*input"):
        main()

    assert source.read_bytes() == original


def test_summary_failed_write_preserves_output_and_removes_temporary_file(tmp_path, monkeypatch):
    source = tmp_path / "episodes.jsonl"
    source.write_text(json.dumps(_episode()) + "\n", encoding="utf-8")
    output = tmp_path / "summary.csv"
    output.write_text("previous result\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["summarize_runs", str(source), "--output", str(output)])

    def fail_write(self, handle, **kwargs):
        if hasattr(handle, "write"):
            handle.write("partial output")
        else:
            handle.write_text("partial output", encoding="utf-8")
        raise OSError("write failed")

    monkeypatch.setattr(pd.DataFrame, "to_csv", fail_write)
    with pytest.raises(OSError, match="write failed"):
        main()

    assert output.read_text(encoding="utf-8") == "previous result\n"
    assert {path.name for path in tmp_path.iterdir()} == {"episodes.jsonl", "summary.csv"}


def test_summary_cli_writes_csv_without_modifying_source(tmp_path, monkeypatch):
    source = tmp_path / "episodes.jsonl"
    source.write_text(json.dumps(_episode(task_success=0, domain="simulation")) + "\n", encoding="utf-8")
    original = source.read_bytes()
    output = tmp_path / "summary.csv"
    output.write_text("previous result\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["summarize_runs", str(source), "--output", str(output)])

    main()

    summary = pd.read_csv(output)
    assert summary.iloc[0]["domain"] == "simulation"
    assert summary.iloc[0]["n"] == 1
    assert summary.iloc[0]["successes"] == 0
    assert source.read_bytes() == original
    assert {path.name for path in tmp_path.iterdir()} == {"episodes.jsonl", "summary.csv"}


@pytest.mark.parametrize("changed_fields", [{}, {"task_id": "other_task"}, {"semantic_condition": "conflict"}])
def test_summary_rejects_duplicate_episode_identity_even_across_task_or_condition(changed_fields):
    first = _episode(episode_id="scene-0000__neutral_nominal", task_id="pick")
    second = {**first, **changed_fields, "task_success": False}

    with pytest.raises(ValueError, match="duplicate episode_id"):
        summarize_success([first, second])


@pytest.mark.parametrize("missing_id", [{}, {"episode_id": None}, {"episode_id": ""}])
def test_summary_requires_valid_id_on_every_record_once_any_id_is_provided(missing_id):
    records = [_episode(episode_id="scene-0000__neutral_nominal"), _episode(**missing_id)]

    with pytest.raises(ValueError, match="episode_id.*every record"):
        summarize_success(records)


@pytest.mark.parametrize("identity_field", ["calibration_variant", "domain", "domain_id", "model", "model_id", "model_name"])
def test_summary_allows_shared_episode_id_across_variants_domains_and_models(identity_field):
    records = [
        _episode(episode_id="shared", **{identity_field: "first"}),
        _episode(episode_id="shared", task_success=False, **{identity_field: "second"}),
    ]

    summary = summarize_success(records)

    assert len(summary) == 2
    assert summary["n"].tolist() == [1, 1]
    assert summary["successes"].tolist() == [1, 0]


def test_summary_retains_legacy_records_with_no_episode_ids():
    summary = summarize_success([_episode(task_success=True), _episode(task_success=False)])

    assert summary.iloc[0]["n"] == 2
    assert summary.iloc[0]["success_rate"] == 0.5
