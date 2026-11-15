"""Read-only qualification of public telemetry; no policy or detector execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CACHE = ROOT / "data/discovery/vfd-assets-20261115"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    source = json.loads((HERE / "drishti-db-source.json").read_text())
    db_path = ROOT / source["cache"]
    if digest(db_path) != source["sha256"]:
        raise ValueError("source database hash changed")
    connection = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    integrity = [tuple(row) for row in connection.execute("PRAGMA integrity_check")]
    if integrity != [("ok",)]:
        raise ValueError(f"SQLite integrity failure: {integrity}")
    runs = [dict(row) for row in connection.execute("SELECT * FROM runs ORDER BY run_id")]
    steps = [dict(row) for row in connection.execute("SELECT * FROM steps ORDER BY run_id, step_idx")]
    frames = [dict(row) for row in connection.execute("SELECT * FROM frames ORDER BY id")]
    tables = {row["name"]: row["sql"] for row in connection.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table'")}
    connection.close()
    if digest(db_path) != source["sha256"]:
        raise ValueError("read-only audit modified source")
    run_ids = {r["run_id"] for r in runs}
    if any(row["run_id"] not in run_ids for row in steps + frames):
        raise ValueError("orphan telemetry row")
    tree = json.loads((CACHE / "drishti-tree.json").read_text())
    blobs = {e["path"] for e in tree["tree"] if e["type"] == "blob"}
    embeddings = sorted(p for p in blobs if p.startswith("data/demo/blobs/") and p.endswith(".npy"))
    embedding_runs = {p.split("/")[3] for p in embeddings}
    frame_runs = {row["run_id"] for row in frames}
    missing_frames = [r["blob_path"] for r in frames if "data/demo/blobs/" + r["blob_path"] not in blobs]
    if missing_frames:
        raise ValueError("frame references missing from fixed repository tree")
    per_run = []
    coverage = Counter()
    vector_lengths = {name: Counter() for name in ["observation_state", "action", "action_head_mean", "action_head_std"]}
    for row in steps:
        for name in vector_lengths:
            if row[name] is None:
                continue
            value = json.loads(row[name])
            if value is None:
                continue
            if not isinstance(value, list) or any(not math.isfinite(v) for v in value):
                raise ValueError(f"invalid numeric vector: {name}, step id {row['id']}")
            vector_lengths[name][len(value)] += 1
            coverage[name] += 1
        for name in ["smd", "rnd", "ace", "latency_ms"]:
            coverage[name] += row[name] is not None
    for run in runs:
        selected = [s for s in steps if s["run_id"] == run["run_id"]]
        meta = json.loads(run["meta"] or "{}")
        if run["success_rate"] not in [0., 1.]:
            raise ValueError("unknown episode label encoding")
        per_run.append({"run_id": run["run_id"], "model_id": run["model_id"],
                        "recorded_success": bool(run["success_rate"]), "steps": len(selected),
                        "declared_steps": run["n_steps"],
                        "contiguous_zero_based_steps": [s["step_idx"] for s in selected] == list(range(len(selected))),
                        "cube_xy_recorded": meta.get("cube_xy"), "meta_keys": sorted(meta),
                        "embeddings_in_tree": run["run_id"] in embedding_runs,
                        "images_in_tree": run["run_id"] in frame_runs,
                        "logged_t_equals_step_index": all(s["t"] == float(s["step_idx"]) for s in selected)})
    summary = {"runs": len(runs), "steps": len(steps), "frame_rows": len(frames),
               "embedding_files_in_tree_not_downloaded": len(embeddings),
               "success_labels": sum(r["recorded_success"] for r in per_run),
               "failure_labels": sum(not r["recorded_success"] for r in per_run),
               "runs_with_embeddings_in_tree": len(embedding_runs), "runs_with_images_in_tree": len(frame_runs),
               "embedding_subset_success": sum(r["recorded_success"] for r in per_run if r["embeddings_in_tree"]),
               "embedding_subset_failure": sum(not r["recorded_success"] for r in per_run if r["embeddings_in_tree"]),
               "model_id_counts": dict(Counter(r["model_id"] for r in runs)),
               "success_runs_under_20_steps": sum(r["recorded_success"] and r["steps"] < 20 for r in per_run),
               "declared_step_count_mismatches": sum(r["steps"] != r["declared_steps"] for r in per_run),
               "noncontiguous_runs": sum(not r["contiguous_zero_based_steps"] for r in per_run),
               "runs_with_t_equal_step_index": sum(r["logged_t_equals_step_index"] for r in per_run),
               "metadata_key_run_counts": dict(Counter(k for r in per_run for k in r["meta_keys"])),
               "available_step_vectors": {k: dict(v) for k, v in vector_lengths.items()},
               "non_null_step_field_counts": dict(coverage)}
    report = {"kind": "public_telemetry_qualification_not_reproduced_robot_success_or_vfd", "summary": summary,
              "per_run": per_run, "table_schemas": tables, "source_database_sha256": source["sha256"],
              "source_tree_sha256": digest(CACHE / "drishti-tree.json"),
              "audit_script_sha256": digest(Path(__file__)), "plan_sha256": digest(HERE / "data-contract-plan.md"),
              "scope": {"database_opened_read_only": True, "database_integrity_ok": True,
                        "frame_blobs_checked_against_tree_only": True, "upstream_code_executed": False,
                        "policy_weights_downloaded": False},
              "missing_for_vfd": ["Bound policy weight hash and training/data revisions", "Independent trained ensemble member",
                                  "Full action chunks and intermediate ODE states/velocities at common points"],
              "missing_for_physical_outcome_recomputation": ["Per-step cube state and finger contacts", "Complete reset qpos/qvel and historical scene binding"]}
    with args.out.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
