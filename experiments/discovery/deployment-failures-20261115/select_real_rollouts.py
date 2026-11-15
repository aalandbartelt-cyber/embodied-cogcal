"""Freeze a label-stratified sample before reading frame-level measurements."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
META = ROOT / "data/discovery/deployment-failures-20261115/armnet-episodes.parquet"
TASK = "Insert the colourful ring into the central wooden peg"


def select() -> dict:
    rows = pq.read_table(META).to_pylist()
    pool = [r for r in rows if TASK in r["tasks"] and r["policy_type"] == "pi0.5"]
    policies = sorted({r["policy_repo_id"] for r in pool})
    assert policies and policies[0]
    policy = policies[0]
    pool = [r for r in pool if r["policy_repo_id"] == policy]
    selected = []
    for label in ("successful", "failure"):
        group = sorted(
            [r for r in pool if r["success_class"] == label],
            key=lambda r: r["episode_index"],
        )
        assert group, (policy, label)
        for row in group[:6]:
            keys = [
                "episode_index", "length", "success", "success_class", "policy_type",
                "policy_repo_id", "data/chunk_index", "data/file_index",
                "dataset_from_index", "dataset_to_index",
            ]
            keys += [k for k in row if k.startswith("videos/")]
            selected.append({k: row[k] for k in keys})
    return {
        "purpose": "fixed real-rollout discovery sample, not an unbiased success estimate",
        "dataset": "armnet/armnetbench_v01_lerobot_so101",
        "revision": "1db69c82b589c7172ee31a6b8f7ef58d1fc2c663",
        "metadata_sha256": hashlib.sha256(META.read_bytes()).hexdigest(),
        "task": TASK, "policy_type": "pi0.5", "candidate_policy_repo_ids": policies,
        "selected_policy_repo_id": policy, "pool_counts": dict(Counter(
            r["success_class"] for r in pool
        )),
        "rule": "lexicographically first policy id; first six episode indices per outcome",
        "episodes": sorted(selected, key=lambda r: r["episode_index"]),
        "limits": [
            "Single-operator outcome labels, not independently relabelled physics truth.",
            "No matched initial object poses or action causality claim.",
            "No frame measurements, video inspection, or failure mechanism used for selection.",
            "Camera, frame time, motor-read time and command-send time are not interchangeable.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    result = select()
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "pool_counts": result["pool_counts"],
        "episode_indices": [r["episode_index"] for r in result["episodes"]],
        "data_files": sorted({(r["data/chunk_index"], r["data/file_index"])
                              for r in result["episodes"]}),
    }))
