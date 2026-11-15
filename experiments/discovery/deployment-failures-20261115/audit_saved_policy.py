"""Describe saved outputs and processors without policy inference or simulator execution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from safetensors.numpy import load_file

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/so101/tpsc-pilot/runs/local-5070ti/pilot-20k"
CHECKPOINT = ROOT / "checkpoints/tpsc-carrier-20k/checkpoints/020000/pretrained_model"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def describe(values: np.ndarray, stats: dict) -> dict:
    assert values.ndim == 2 and values.shape[1] == 6
    assert np.isfinite(values).all()
    std = values.std(axis=0)
    span = np.quantile(values, 0.99, axis=0) - np.quantile(values, 0.01, axis=0)
    return {
        "numeric_source_std": std.tolist(),
        "numeric_source_p01_p99_span": span.tolist(),
        "std_over_dataset_std": (std / np.asarray(stats["std"])).tolist(),
        "p01_p99_span_over_dataset_minmax": (
            span / (np.asarray(stats["max"]) - np.asarray(stats["min"]))
        ).tolist(),
    }


def audit() -> dict:
    sources = {}
    manifest = RUN.parent / "pilot-20k-checkpoint.json"
    source_manifest = json.loads(manifest.read_text())
    for row in source_manifest["files"]:
        path = ROOT / row["path"]
        assert path.stat().st_size == row["bytes"]
        assert sha(path) == row["sha256"], path
        sources[row["path"]] = row["sha256"]

    stats_path = ROOT / "data/tpsc-carrier/meta/stats.json"
    dataset_stats = json.loads(stats_path.read_text())
    comparisons = []
    for filename in [
        "policy_preprocessor_step_5_normalizer_processor.safetensors",
        "policy_postprocessor_step_0_unnormalizer_processor.safetensors",
    ]:
        tensors = load_file(CHECKPOINT / filename)
        for feature in ("action", "observation.state"):
            for moment in ("mean", "std"):
                actual = tensors[f"{feature}.{moment}"]
                expected = np.asarray(dataset_stats[feature][moment])
                assert actual.shape == expected.shape == (6,)
                assert np.allclose(actual, expected, atol=1e-6, rtol=1e-6)
                comparisons.append({
                    "file": filename, "feature": feature, "moment": moment,
                    "max_abs_difference": float(np.max(np.abs(actual - expected))),
                    "equals_dataset_after_float32_cast": bool(
                        np.array_equal(actual, expected.astype(np.float32))
                    ),
                })

    episodes_path = RUN / "episodes.jsonl"
    episodes = [json.loads(x) for x in episodes_path.read_text().splitlines() if x.strip()]
    assert len(episodes) == len({x["episode_id"] for x in episodes}) == 20
    rows = []
    for episode in episodes:
        path = RUN / f"{episode['episode_id']}.trace.jsonl"
        trace = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
        assert all(x["episode_id"] == episode["episode_id"] for x in trace)
        chunks = np.concatenate([x["action_chunk_rad"] for x in trace], axis=0)
        executed = np.concatenate([x["executed_targets_rad"] for x in trace], axis=0)
        assert np.array_equal(executed, episode["executed_targets_rad"])
        assert np.array_equal(trace[0]["action_chunk_rad"], episode["first_chunk_rad"])
        rows.append({
            "episode_id": episode["episode_id"],
            "task_success": episode["task_success"],
            "queries": len(trace), "recorded_chunk_rows": len(chunks),
            "executed_control_rows": len(executed),
            "recorded_chunk": describe(np.rad2deg(chunks), dataset_stats["action"]),
            "executed_target": describe(np.rad2deg(executed), dataset_stats["action"]),
        })
        sources[str(path.relative_to(ROOT))] = sha(path)

    summary = {}
    for kind in ("recorded_chunk", "executed_target"):
        values = np.asarray([r[kind]["std_over_dataset_std"] for r in rows])
        summary[kind] = {
            "episode_std_ratio_min": values.min(axis=0).tolist(),
            "episode_std_ratio_median": np.median(values, axis=0).tolist(),
            "episode_std_ratio_max": values.max(axis=0).tolist(),
        }
    for path in (manifest, stats_path, episodes_path, Path(__file__).resolve()):
        sources[str(path.relative_to(ROOT))] = sha(path)
    return {
        "claim": "read-only processor and saved-output audit, not a causal or task-recovery result",
        "input_sha256": sources, "processor_checks": comparisons,
        "episodes": rows, "summary": summary,
        "counts": {
            "episodes": len(rows), "task_successes": sum(r["task_success"] for r in rows),
            "queries": sum(r["queries"] for r in rows),
            "recorded_chunk_rows": sum(r["recorded_chunk_rows"] for r in rows),
            "executed_control_rows": sum(r["executed_control_rows"] for r in rows),
        },
        "limits": [
            "Both processors match current pinned dataset stats, not evidence of a beneficial normalization scheme.",
            "Saved trace adapter uses six numeric degree-to-radian channels; physical gripper semantics remain unverified.",
            "Predicted chunk tails include actions never executed; execution may include clipping.",
            "Frames and chunks are not independent replications; no collapse cutoff was selected.",
            "No comparison of task-matched demonstration conditional distributions or causal training intervention.",
            "No policy loaded, new rollout executed, model trained, or normalizer changed.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    result = audit()
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"counts": result["counts"], "summary": result["summary"]}))
