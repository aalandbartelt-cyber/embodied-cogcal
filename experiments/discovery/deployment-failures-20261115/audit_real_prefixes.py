"""Describe fixed real-rollout prefixes; no detector training or causal attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DATA = ROOT / "data/discovery/deployment-failures-20261115"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit() -> dict:
    selection_path = HERE / "real-rollout-selection.json"
    selection = json.loads(selection_path.read_text())
    info_path = DATA / "armnet-meta-info.json"
    info = json.loads(info_path.read_text())
    assert info["fps"] == 20
    assert info["features"]["action"]["names"] == info["features"]["observation.state"]["names"]
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in [selection_path, info_path]}
    tables = {}
    episodes = []
    for episode in selection["episodes"]:
        chunk, file = episode["data/chunk_index"], episode["data/file_index"]
        filename = f"armnet-data-chunk{chunk:03d}-file{file:03d}.parquet"
        path = DATA / filename
        if filename not in tables:
            tables[filename] = pq.read_table(path, columns=[
                "episode_index", "timestamp", "frame_index", "index", "task_index",
                "action", "observation.state", "next.done", "next.reward",
            ]).to_pylist()
            inputs[str(path.relative_to(ROOT))] = sha(path)
        rows = [r for r in tables[filename] if r["episode_index"] == episode["episode_index"]]
        assert len(rows) == episode["length"]
        assert [r["frame_index"] for r in rows] == list(range(len(rows)))
        indices = [r["index"] for r in rows]
        assert indices == list(range(episode["dataset_from_index"], episode["dataset_to_index"]))
        times = np.asarray([r["timestamp"] for r in rows])
        max_time_error = float(np.max(np.abs(times - np.arange(len(rows)) / info["fps"])))
        assert max_time_error < 1e-5
        assert len({r["task_index"] for r in rows}) == 1
        assert all(not r["next.done"] for r in rows[:-1]) and rows[-1]["next.done"]
        actions = np.asarray([r["action"] for r in rows], dtype=float)
        states = np.asarray([r["observation.state"] for r in rows], dtype=float)
        assert actions.shape == states.shape == (len(rows), 6)
        assert np.isfinite(actions).all() and np.isfinite(states).all()
        prefixes = {}
        for seconds in (1, 3):
            # Integer frame indices avoid float32 boundary drift at exactly 1s/3s.
            count = min(len(rows), seconds * info["fps"])
            a, q = actions[:count], states[:count]
            assert len(a) >= 2
            prefixes[str(seconds)] = {
                "rows": count,
                "same_frame_mean_abs_command_state_difference": np.mean(np.abs(a - q), axis=0).tolist(),
                "next_sample_mean_abs_command_state_difference": np.mean(np.abs(a[:-1] - q[1:]), axis=0).tolist(),
                "action_step_increment_rms": np.sqrt(np.mean(np.diff(a, axis=0) ** 2, axis=0)).tolist(),
                "state_step_increment_rms": np.sqrt(np.mean(np.diff(q, axis=0) ** 2, axis=0)).tolist(),
            }
        episodes.append({
            "episode_index": episode["episode_index"], "outcome_label": episode["success_class"],
            "rows": len(rows), "max_nominal_time_error_seconds": max_time_error,
            "last_reward": rows[-1]["next.reward"], "prefixes": prefixes,
        })
    metrics = [k for k in episodes[0]["prefixes"]["1"] if k != "rows"]
    summary = {}
    for seconds in ("1", "3"):
        summary[seconds] = {}
        for label in ("successful", "failure"):
            selected = [r for r in episodes if r["outcome_label"] == label]
            summary[seconds][label] = {
                "episodes": len(selected),
                "episode_medians": {
                    metric: np.median([r["prefixes"][seconds][metric] for r in selected], axis=0).tolist()
                    for metric in metrics
                },
            }
    inputs[str(Path(__file__).resolve().relative_to(ROOT))] = sha(Path(__file__).resolve())
    return {
        "claim": "descriptive native-unit prefix measurements only; not actuator error, prediction or causality",
        "input_sha256": inputs,
        "feature_order": info["features"]["action"]["names"],
        "episodes": episodes, "summary": summary,
        "limits": [
            "Units have not been independently resolved; do not call values degrees or millimetres.",
            "Timestamp is the nominal 20Hz frame clock, not separate command-send or motor-read times.",
            "Same-frame and next-sample differences mix intended motion, servo response and observation timing.",
            "Outcome-stratified selection is not an unbiased prevalence or success estimate.",
            "Initial object poses are unmatched; joint telemetry does not establish grasp, object motion or insertion.",
            "No significance test, selected threshold, trained predictor or new policy evaluation.",
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
    print(json.dumps({
        "episodes": len(result["episodes"]),
        "full_rows_verified": sum(r["rows"] for r in result["episodes"]),
        "summary_3s": result["summary"]["3"],
    }))
