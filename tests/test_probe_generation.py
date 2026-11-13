from __future__ import annotations

import json
from pathlib import Path

from probes.generators.eccbf_factorial import generate_records, write_jsonl

DEFINITION = Path(__file__).resolve().parents[1] / "probes/definitions/eccbf_factorial.yaml"


def test_generator_creates_four_matched_conditions_per_scene():
    records = generate_records(DEFINITION, num_scenes=3, seed=7)

    assert len(records) == 12
    for scene_id in {record["scene_id"] for record in records}:
        scene_records = [record for record in records if record["scene_id"] == scene_id]
        assert {record["condition_id"] for record in scene_records} == {
            "neutral_nominal",
            "conflict_nominal",
            "neutral_perturbed",
            "conflict_perturbed",
        }
        assert len({(record["task_id"], record["seed"]) for record in scene_records}) == 1


def test_generator_is_deterministic_for_same_seed():
    first = generate_records(DEFINITION, num_scenes=4, seed=11)
    second = generate_records(DEFINITION, num_scenes=4, seed=11)
    assert first == second


def test_generator_does_not_emit_privileged_runtime_inputs(tmp_path):
    records = generate_records(DEFINITION, num_scenes=1, seed=3)
    forbidden = {
        "evaluator_target_pose",
        "hidden_success_label",
        "privileged_scene_state",
    }

    def walk(value):
        if isinstance(value, dict):
            yield from value.keys()
            for child in value.values():
                yield from walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from walk(child)

    assert forbidden.isdisjoint(set(walk(records)))

    output = tmp_path / "episodes.jsonl"
    write_jsonl(records, output)
    loaded = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert loaded == records
