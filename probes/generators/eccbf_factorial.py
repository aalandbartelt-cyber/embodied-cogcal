"""Generate deterministic ECCBF four-cell episode metadata.

The generator creates public scene metadata only. It does not load MuJoCo,
models, evaluator labels, target poses, or privileged simulator state.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml

DEFAULT_DEFINITION = Path(__file__).resolve().parents[1] / "definitions" / "eccbf_factorial.yaml"
TASK_IDS = ("so101_pick_place", "so101_target_selection")
FORBIDDEN_FIELDS = {
    "evaluator_target_pose",
    "hidden_success_label",
    "privileged_scene_state",
}


def load_definition(path: str | Path = DEFAULT_DEFINITION) -> dict[str, Any]:
    """Load and validate the four-cell probe definition."""

    definition = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    conditions = definition.get("conditions", [])
    required_conditions = {
        "neutral_nominal",
        "conflict_nominal",
        "neutral_perturbed",
        "conflict_perturbed",
    }
    if {condition["id"] for condition in conditions} != required_conditions:
        raise ValueError("ECCBF definition must contain exactly four factorial conditions")
    forbidden = set(definition.get("runtime_inputs", {}).get("forbidden", []))
    if forbidden != FORBIDDEN_FIELDS:
        raise ValueError("ECCBF definition forbidden runtime inputs changed unexpectedly")
    return definition


def _scene_metadata(rng: np.random.Generator, scene_index: int, seed: int) -> dict[str, Any]:
    """Create metadata observable by a policy without exposing evaluator state."""

    colors = tuple(rng.choice(np.array(["red", "blue", "green", "yellow"]), size=2, replace=False))
    return {
        "scene_id": f"scene-{scene_index:04d}",
        "scene_seed": int(rng.integers(0, 2**31 - 1)),
        "layout_bucket": int(rng.integers(0, 8)),
        "object_colors": list(colors),
        "distractor_count": int(rng.integers(1, 4)),
        "generator_seed": seed,
    }


def generate_records(
    definition_path: str | Path = DEFAULT_DEFINITION,
    *,
    num_scenes: int,
    seed: int,
) -> list[dict[str, Any]]:
    """Generate four matched records for each deterministic scene."""

    if num_scenes < 1:
        raise ValueError("num_scenes must be positive")
    definition = load_definition(definition_path)
    rng = np.random.default_rng(seed)
    conditions = definition["conditions"]
    records: list[dict[str, Any]] = []

    for scene_index in range(num_scenes):
        scene = _scene_metadata(rng, scene_index, seed)
        task_id = TASK_IDS[scene_index % len(TASK_IDS)]
        for condition in conditions:
            record = {
                "probe_id": definition["id"],
                "episode_id": f"{scene['scene_id']}__{condition['id']}",
                "task_id": task_id,
                "scene_id": scene["scene_id"],
                "seed": seed + scene_index,
                "condition_id": condition["id"],
                "semantic_condition": condition["semantic_condition"],
                "execution_condition": condition["execution_condition"],
                "scene_metadata": scene,
                "runtime_input_names": sorted(definition["runtime_inputs"]["allowed"]),
                "expected_outputs": list(definition["episode_outputs"]),
            }
            records.append(record)

    _assert_no_forbidden_fields(records)
    return records


def _assert_no_forbidden_fields(records: list[dict[str, Any]]) -> None:
    encoded = json.dumps(records, ensure_ascii=False)
    for field in FORBIDDEN_FIELDS:
        if field in encoded:
            raise ValueError(f"forbidden runtime field emitted: {field}")


def write_jsonl(records: list[dict[str, Any]], output: str | Path) -> None:
    """Write records in stable-key JSONL format."""

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--definition", type=Path, default=DEFAULT_DEFINITION)
    parser.add_argument("--num-scenes", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = generate_records(args.definition, num_scenes=args.num_scenes, seed=args.seed)
    write_jsonl(records, args.output)
    print(f"wrote {len(records)} matched episodes to {args.output}")


if __name__ == "__main__":
    main()
