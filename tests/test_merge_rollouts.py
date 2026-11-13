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
