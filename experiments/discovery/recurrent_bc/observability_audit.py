"""Descriptive training-only input distances; no identifiability theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RECORDS = ROOT / "experiments/discovery/matched-bc-lowrate-20261114/collection/episodes.jsonl"


def inspect(row, query_only):
    path = Path(row["path"])
    if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
        raise ValueError("data changed")
    with np.load(path) as data:
        q, actions, rgb = data["q"], data["action"], data["rgb"]
    times = np.arange(0, 256, 6 if query_only else 1)
    history = q[np.maximum(times[:, None] - np.arange(7, -1, -1), 0)]
    chunks = actions[times[:, None] + np.arange(30)]
    distance = np.max(np.abs(history[:, None] - history[None, :]), axis=(2, 3))
    gap = np.max(np.abs(chunks[:, None] - chunks[None, :]), axis=(2, 3))
    allowed = (times[None, :] - times[:, None] >= 8) & (gap > .02)
    distance[~allowed] = np.inf
    nearest = []
    for index in np.argsort(distance.ravel()):
        i, j = np.unravel_index(index, distance.shape)
        if not np.isfinite(distance[i, j]):
            break
        rgb_delta = np.abs(rgb[times[i]].astype(float) - rgb[times[j]].astype(float))
        nearest.append({"i": int(times[i]), "j": int(times[j]),
                        "history_max_abs_rad": float(distance[i, j]),
                        "chunk_max_abs_gap_rad": float(gap[i, j]),
                        "rgb_mean_abs_255": float(np.mean(rgb_delta)),
                        "rgb_different_values": int(np.count_nonzero(rgb_delta)),
                        "exact_same_input": bool(distance[i, j] == 0 and not rgb_delta.any())})
        if len(nearest) == 5:
            break
    return {"seed": row["seed"], "query_only": query_only,
            "considered_times": times.tolist(), "candidate_pairs": int(allowed.sum()),
            "nearest_five_by_q_distance": nearest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("new output required")
    rows = [json.loads(line) for line in RECORDS.read_text().splitlines()]
    train = [r for r in rows if r["split"] == "train"]
    assert len(train) == 24
    results = [inspect(r, query_only) for r in train for query_only in [False, True]]
    report = {
        "kind": "posthoc_descriptive_training_observability_not_new_failure_mechanism",
        "choices": "after first two exact-RGB searches returned zero, inspect continuous distances; no pass gate",
        "filter": "within same episode, at least 8 controls apart, chunk max gap>.02rad, full 30-step labels",
        "ranking": "five smallest measured q-history distances per episode; RGB distances reported without threshold",
        "training_episodes": 24, "test_or_val_used": False, "rows": results,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "limits": ["Approximate equality does not prove exact aliasing or an irreducible loss floor.",
                   "Frame pairs are descriptive, not independent statistical replicates.",
                   "Does not identify the cause of closed-loop failures or establish novelty."],
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"training_episodes": 24, "scope_rows": len(results),
                      "exact_same_inputs_among_nearest": sum(x["exact_same_input"] for r in results
                                                             for x in r["nearest_five_by_q_distance"])}))


if __name__ == "__main__":
    main()
