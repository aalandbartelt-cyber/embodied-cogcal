from __future__ import annotations

import json

import pytest

from analysis.scripts.merge_rollouts import merge_jsonl


def _write(path, rows):
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_merge_rollouts_joins_by_episode_id_and_preserves_conditions(tmp_path):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    output = tmp_path / "merged.jsonl"
    _write(
        metadata,
        [
            {
                "episode_id": "scene-0000__neutral_nominal",
                "task_id": "so101_pick_place",
                "scene_id": "scene-0000",
                "semantic_condition": "neutral",
                "execution_condition": "nominal",
            }
        ],
    )
    _write(rollout, [{"episode_id": "scene-0000__neutral_nominal", "task_success": True}])

    count = merge_jsonl(metadata, rollout, output)

    assert count == 1
    merged = json.loads(output.read_text(encoding="utf-8"))
    assert merged["task_id"] == "so101_pick_place"
    assert merged["task_success"] is True


def test_merge_rollouts_rejects_missing_or_duplicate_episode_ids(tmp_path):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    output = tmp_path / "merged.jsonl"
    _write(metadata, [{"episode_id": "a"}, {"episode_id": "b"}])
    _write(rollout, [{"episode_id": "a", "task_success": True}])
    with pytest.raises(ValueError, match="missing rollout"):
        merge_jsonl(metadata, rollout, output)

    _write(rollout, [{"episode_id": "a", "task_success": True}, {"episode_id": "a", "task_success": False}])
    with pytest.raises(ValueError, match="duplicate"):
        merge_jsonl(metadata, rollout, output)


def test_merge_rollouts_rejects_privileged_fields(tmp_path):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    output = tmp_path / "merged.jsonl"
    _write(metadata, [{"episode_id": "a", "evaluator_target_pose": [0, 0, 0]}])
    _write(rollout, [{"episode_id": "a", "task_success": True}])

    with pytest.raises(ValueError, match="privileged"):
        merge_jsonl(metadata, rollout, output)


@pytest.mark.parametrize("existing_output", [False, True])
def test_merge_overlap_does_not_truncate_or_create_output(tmp_path, existing_output):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    output = tmp_path / "merged.jsonl"
    _write(metadata, [{"episode_id": "a"}, {"episode_id": "b", "task_id": "pick"}])
    _write(rollout, [{"episode_id": "a"}, {"episode_id": "b", "task_id": "other"}])
    if existing_output:
        output.write_text("previous result\n", encoding="utf-8")

    with pytest.raises(ValueError, match="overlap"):
        merge_jsonl(metadata, rollout, output)

    if existing_output:
        assert output.read_text(encoding="utf-8") == "previous result\n"
    else:
        assert not output.exists()


@pytest.mark.parametrize("source_name", ["metadata", "rollout"])
@pytest.mark.parametrize("alias", ["same", "symlink", "hardlink"])
def test_merge_rejects_output_aliasing_either_input(tmp_path, source_name, alias):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    _write(metadata, [{"episode_id": "a"}])
    _write(rollout, [{"episode_id": "a", "task_success": True}])
    source = {"metadata": metadata, "rollout": rollout}[source_name]
    output = source if alias == "same" else tmp_path / "output.jsonl"
    if alias == "symlink":
        output.symlink_to(source)
    elif alias == "hardlink":
        output.hardlink_to(source)
    original = source.read_bytes()

    with pytest.raises(ValueError, match="output.*input"):
        merge_jsonl(metadata, rollout, output)

    assert source.read_bytes() == original


@pytest.mark.parametrize("source_name", ["metadata", "rollout"])
@pytest.mark.parametrize("field", ["evaluator_target_pose", "hidden_success_label", "privileged_scene_state"])
def test_merge_rejects_privileged_fields_nested_in_lists(tmp_path, source_name, field):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    rows = {"metadata": {"episode_id": "a"}, "rollout": {"episode_id": "a"}}
    rows[source_name]["observations"] = [{"nested": {field: 1}}]
    _write(metadata, [rows["metadata"]])
    _write(rollout, [rows["rollout"]])
    output = tmp_path / "merged.jsonl"

    with pytest.raises(ValueError, match="privileged"):
        merge_jsonl(metadata, rollout, output)

    assert not output.exists()


@pytest.mark.parametrize("empty_source", ["metadata", "rollout", "both"])
def test_merge_rejects_empty_input_without_replacing_output(tmp_path, empty_source):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    _write(metadata, [] if empty_source in {"metadata", "both"} else [{"episode_id": "a"}])
    _write(rollout, [] if empty_source in {"rollout", "both"} else [{"episode_id": "a"}])
    output = tmp_path / "merged.jsonl"
    output.write_text("previous result\n", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        merge_jsonl(metadata, rollout, output)

    assert output.read_text(encoding="utf-8") == "previous result\n"


@pytest.mark.parametrize("success", ["false", "true", None, 2, -1, 0.0, 1.0, [], {}])
def test_merge_rejects_nonbinary_success_labels(tmp_path, success):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    _write(metadata, [{"episode_id": "a"}])
    _write(rollout, [{"episode_id": "a", "task_success": success}])

    with pytest.raises(ValueError, match="task_success.*boolean.*0/1"):
        merge_jsonl(metadata, rollout, tmp_path / "merged.jsonl")


@pytest.mark.parametrize("marker", [{"step": 0}, {"failure_reason": "scripted_plumbing_smoke_only"}])
def test_merge_rejects_step_and_scripted_smoke_records(tmp_path, marker):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    _write(metadata, [{"episode_id": "a"}])
    _write(rollout, [{"episode_id": "a", "task_success": False, **marker}])

    with pytest.raises(ValueError, match="episode.*step|smoke"):
        merge_jsonl(metadata, rollout, tmp_path / "merged.jsonl")


@pytest.mark.parametrize("marker", [{"record_type": "step"}, {"experiment_kind": "plumbing_smoke"}])
def test_merge_rejects_explicit_nonpaper_records_without_success(tmp_path, marker):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    _write(metadata, [{"episode_id": "a"}])
    _write(rollout, [{"episode_id": "a", **marker}])

    with pytest.raises(ValueError, match="not a paper episode"):
        merge_jsonl(metadata, rollout, tmp_path / "merged.jsonl")


def test_merge_requires_one_variant_per_file(tmp_path):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    _write(metadata, [{"episode_id": "a"}, {"episode_id": "b"}])
    _write(rollout, [
        {"episode_id": "a", "calibration_variant": "raw"},
        {"episode_id": "b", "calibration_variant": "eccbf"},
    ])

    with pytest.raises(ValueError, match="one calibration variant per file"):
        merge_jsonl(metadata, rollout, tmp_path / "merged.jsonl")


def test_merge_duplicate_rollout_explains_variant_file_contract(tmp_path):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    _write(metadata, [{"episode_id": "a"}])
    _write(rollout, [
        {"episode_id": "a", "calibration_variant": "raw"},
        {"episode_id": "a", "calibration_variant": "eccbf"},
    ])

    with pytest.raises(ValueError, match="one calibration variant per file"):
        merge_jsonl(metadata, rollout, tmp_path / "merged.jsonl")


def test_merge_accepts_single_variant_with_boolean_and_integer_outcomes(tmp_path):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    output = tmp_path / "merged.jsonl"
    values = [True, False, 0, 1]
    _write(metadata, [{"episode_id": str(number)} for number in range(len(values))])
    _write(rollout, [
        {"episode_id": str(number), "calibration_variant": "raw", "task_success": value}
        for number, value in enumerate(values)
    ])
    originals = (metadata.read_bytes(), rollout.read_bytes())
    output.write_text("previous result\n", encoding="utf-8")

    assert merge_jsonl(metadata, rollout, output) == len(values)

    merged = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert [row["task_success"] for row in merged] == values
    assert {row["calibration_variant"] for row in merged} == {"raw"}
    assert (metadata.read_bytes(), rollout.read_bytes()) == originals
    assert {path.name for path in tmp_path.iterdir()} == {
        "metadata.jsonl", "rollout.jsonl", "merged.jsonl"
    }


def test_merge_failed_replace_preserves_output_and_removes_temporary_file(tmp_path, monkeypatch):
    metadata = tmp_path / "metadata.jsonl"
    rollout = tmp_path / "rollout.jsonl"
    output = tmp_path / "merged.jsonl"
    _write(metadata, [{"episode_id": "a"}])
    _write(rollout, [{"episode_id": "a", "task_success": True}])
    output.write_text("previous result\n", encoding="utf-8")

    def fail_replace(self, target):
        raise OSError("replacement failed")

    monkeypatch.setattr(type(output), "replace", fail_replace)
    with pytest.raises(OSError, match="replacement failed"):
        merge_jsonl(metadata, rollout, output)

    assert output.read_text(encoding="utf-8") == "previous result\n"
    assert {path.name for path in tmp_path.iterdir()} == {
        "metadata.jsonl", "rollout.jsonl", "merged.jsonl"
    }
