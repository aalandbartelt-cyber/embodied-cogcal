"""Audit completed episode identities, traces and sampled robot joints.

Distances are descriptive; no correct-prefix or semantic-effect inference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from analysis.tpsc_prefix import paired_report  # noqa: E402


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh audit output required")
    episodes = read_rows(args.run / "episodes.jsonl")
    manifest = read_rows(args.manifest)
    expected = {row["episode_id"] for row in manifest}
    ids = [row["episode_id"] for row in episodes]
    if len(ids) != 20 or len(set(ids)) != len(ids) or set(ids) != expected:
        raise ValueError("incomplete or duplicate episode identities")
    traces = {}
    episode_metrics = []
    for row in episodes:
        trace = read_rows(args.run / (row["episode_id"] + ".trace.jsonl"))
        if len(trace) != 30 or [t["step"] for t in trace] != list(range(0, 300, 10)):
            raise ValueError("incomplete fixed-budget chunk trace")
        targets = np.asarray([a for t in trace for a in t["executed_targets_rad"]])
        if targets.shape != (300, 6) or not np.isfinite(targets).all():
            raise ValueError("invalid executed commands")
        if not np.array_equal(targets, row["executed_targets_rad"]):
            raise ValueError("episode and trace commands disagree")
        previous = None
        q = []
        times = [0]
        tracking = []
        for t in trace:
            before = np.asarray(t["qpos_robot_before_rad"])
            after = np.asarray(t["qpos_robot_rad"])
            chunk = np.asarray(t["action_chunk_rad"])
            if before.shape != (6,) or after.shape != (6,) or chunk.shape != (50, 6):
                raise ValueError("invalid joint/chunk shape")
            if not all(np.isfinite(v).all() for v in [before, after, chunk]):
                raise ValueError("nonfinite joints/chunks")
            if previous is None:
                q.append(before)
            elif not np.array_equal(previous, before):
                raise ValueError("discontinuous measured joint trace")
            if t["episode_id"] != row["episode_id"] or t["action_seed"] != 42 + t["step"]:
                raise ValueError("trace identity or random seed mismatch")
            if abs(t["sim_time_s"] - (t["step"] + 10) / 30) > 0.0021:
                raise ValueError("simulation clock does not match fixed control budget")
            q.append(after)
            times.append(t["step"] + 10)
            tracking.append(float(np.max(np.abs(after - t["executed_targets_rad"][-1]))))
            previous = after
        traces[row["episode_id"]] = (trace, np.asarray(q), times)
        episode_metrics.append({
            "episode_id": row["episode_id"],
            "task_success": row["task_success"],
            "failure_reason": row["failure_reason"],
            "clip_events": row["clip_events"],
            "chunks": len(trace),
            "joint_observations": len(q),
            "mean_inference_s": float(np.mean([t["inference_s"] for t in trace])),
            "sampled_end_of_chunk_max_abs_tracking_error_rad": max(tracking),
        })
    result = paired_report(episodes)
    manifest_by_id = {r["episode_id"]: r for r in manifest}
    by_case = {}
    for row in episodes:
        by_case.setdefault(row["case_id"], {})[row["branch"]] = row
    for pair in result["pairs"]:
        left, right = (by_case[pair["case_id"]][b] for b in ["left", "right"])
        lt, lq, times = traces[left["episode_id"]]
        rt, rq, right_times = traces[right["episode_id"]]
        if times != right_times:
            raise ValueError("joint sampling clocks differ")
        distances = np.linalg.norm(lq - rq, axis=1)
        indices = np.flatnonzero(distances > result["distance_threshold_rad"])
        k = int(indices[0]) if len(indices) else None
        pair.update({
            "same_initial_measured_q": bool(np.array_equal(lq[0], rq[0])),
            "same_initial_rgb": lt[0]["input_rgb_sha256"] == rt[0]["input_rgb_sha256"],
            "same_initial_action_seed": lt[0]["action_seed"] == rt[0]["action_seed"],
            "language_changed": manifest_by_id[left["episode_id"]]["task_text"]
                != manifest_by_id[right["episode_id"]]["task_text"],
            "sampled_q_l2_mean_rad": float(distances.mean()),
            "sampled_q_l2_max_rad": float(distances.max()),
            "first_measured_q_divergence_seen_at_control_step": times[k] if k is not None else None,
            "measured_q_divergence_interval_open_left_closed_right":
                [times[k - 1], times[k]] if k is not None and k > 0 else None,
        })
    result.update({
        "audit_kind": "complete_run_and_sampled_joint_audit_not_tpsc_effect",
        "episode_metrics": episode_metrics,
        "failure_counts": dict(Counter(r["failure_reason"] for r in episodes)),
        "lift_observed_episodes": sum(r["lift_observed"] for r in episodes),
        "placement_successes": sum(r["placement_success"] for r in episodes),
        "clip_events_total": sum(r["clip_events"] for r in episodes),
        "total_chunks": sum(r["chunks"] for r in episode_metrics),
        "total_executed_control_steps": len(episodes) * 300,
        "per_episode_mean_inference_median_s": float(np.median([
            r["mean_inference_s"] for r in episode_metrics
        ])),
        "capability_gate": "not_established_task_success_0_and_unverified_camera_adapter"
            if not result["task_successes"] else "requires_independent_validation",
        "manifest_sha256": hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
        "episodes_sha256": hashlib.sha256((args.run / "episodes.jsonl").read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "limitations_extra": [
            "Measured robot q is logged every ten controls; earliest physical divergence is an interval.",
            "Executed target commands are distinct from measured robot motion.",
            "RGB changes along with language in every natural pair; no causal language attribution.",
            "Inference pauses simulation stepping; nominal 30Hz is simulation time, not real-time deployment.",
            "All failures remain in this descriptive screen; no frame-wise significance or population CI.",
        ],
    })
    with args.out.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({k: result[k] for k in [
        "episodes", "task_successes", "failure_counts", "clip_events_total", "total_chunks"
    ]}))


if __name__ == "__main__":
    main()
