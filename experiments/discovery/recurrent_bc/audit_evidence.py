"""Check complete carry/reset/initial-RGB-feature BC evidence without rerunning."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/discovery/matched_bc"))
from audit_screen import check_trace  # noqa: E402

RECURRENT = ROOT / "experiments/discovery/recurrent-bc-20261114"
ANCHOR = ROOT / "experiments/discovery/anchor-bc-20261114"


def read(path):
    return json.loads(path.read_text(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    original = read(ROOT / "experiments/discovery/matched-bc-lowrate-20261114/evidence-audit.json")
    for name, expected in original["protected_originals"].items():
        assert sha(ROOT / name) == expected
    source_counts = {}
    for directory in [RECURRENT, ANCHOR]:
        sources = read(directory / "source-hashes.json")
        for name, expected in sources.items():
            assert sha(ROOT / name) == expected, name
        source_counts[str(directory.relative_to(ROOT))] = len(sources)
        events = rows(directory / "pipeline-events.jsonl")
        exits = [r for r in events if r["event"] == "stage_exit"]
        assert len(exits) == (4 if directory == RECURRENT else 2)
        assert all(r["exit_code"] == 0 for r in exits)
        assert events[-1]["event"] == "complete"
    trained = [read(RECURRENT / f"train-{m}/completed.json") for m in ["carry", "reset"]]
    for key in ["initial_parameter_sha256", "sample_indices_sha256", "parameters"]:
        assert trained[0][key] == trained[1][key], key
    anchor_training = read(ANCHOR / "training/completed.json")
    assert anchor_training["sample_indices_sha256"] == trained[0]["sample_indices_sha256"]
    for run, training in [(RECURRENT / "train-carry", trained[0]),
                          (RECURRENT / "train-reset", trained[1]),
                          (ANCHOR / "training", anchor_training)]:
        assert training["step"] == 2000 and training["test_used"] is False
        assert sha(Path(training["checkpoint"])) == training["checkpoint_sha256"]
        assert [r["step"] for r in rows(run / "updates.jsonl")] == list(range(200, 2001, 200))
    identity = read(ROOT / "experiments/discovery/matched-bc-lowrate-20261114/model-identity-postrun.json")
    low, high = np.asarray(identity["actuator_low_rad"]), np.asarray(identity["actuator_high_rad"])
    totals = {}
    settings = [(RECURRENT / "test-carry", 7100, 11), (RECURRENT / "test-reset", 7100, 4),
                (ANCHOR / "test", 8100, 15)]
    for run, first, expected in settings:
        episodes = rows(run / "episodes.jsonl")
        assert [r["seed"] for r in episodes] == list(range(first, first + 20))
        assert len(episodes) == 20 and sum(r["task_success"] for r in episodes) == expected
        summary = read(run / "summary.json")
        assert summary["rows"] == episodes and summary["successes"] == expected
        commands = chunks = clip_events = 0
        for episode in episodes:
            trace_path = run / f"{episode['seed']}.trace.jsonl"
            count, clips = check_trace(trace_path, 6, low, high)
            assert clips == episode["clip_events"] and episode["controls"] == 285
            trace = rows(trace_path)
            previous_hidden = None
            anchor_hash = None
            for row in trace:
                assert len(row["object_xyz_m_evaluator_only"]) == 3
                if "memory" not in row:
                    continue
                state = row["memory"]
                assert np.isfinite(state["hidden_output_l2"]) and state["hidden_output_l2"] >= 0
                if row["control_step"] == 0:
                    assert state["reset_requested"] is True and state["hidden_input_l2"] == 0
                else:
                    assert state["reset_requested"] is False
                    assert state["hidden_input_l2"] == (0 if run.name == "test-reset" else previous_hidden)
                previous_hidden = state["hidden_output_l2"]
                if run.parent == ANCHOR:
                    current = state["initial_color_feature_sha256"]
                    anchor_hash = current if anchor_hash is None else anchor_hash
                    assert current == anchor_hash
            goal_error = np.linalg.norm(np.asarray(episode["final_object_xyz_m"])[:2] -
                                        np.asarray(episode["goal_xyz_m"])[:2])
            assert np.isclose(goal_error, episode["goal_error_xy_m"], atol=1e-12)
            assert np.allclose(trace[-1]["object_xyz_m_evaluator_only"], episode["final_object_xyz_m"], atol=1e-12)
            placed = goal_error <= .035 and abs(episode["final_object_xyz_m"][2] - .014) <= .012
            assert bool(placed) == episode["placed"]
            success = (placed and episode["released"] and episode["longest_two_finger_lift_s"] >= .5 and
                       episode["max_object_robot_penetration_m"] <= .0015)
            assert bool(success) == episode["task_success"]
            chunks += count
            commands += len(trace)
            clip_events += clips
        totals[str(run.relative_to(ROOT))] = {
            "episodes": 20, "successes": expected, "capability_gate": expected >= 16,
            "commands": commands, "chunks": chunks, "clip_events": clip_events,
            "failure_counts": dict(Counter(r["failure_reason"] or "success" for r in episodes)),
        }
    carry, reset = (read(RECURRENT / f"test-{m}/summary.json")["rows"] for m in ["carry", "reset"])
    paired = Counter(f"carry_{int(a['task_success'])}_reset_{int(b['task_success'])}"
                     for a, b in zip(carry, reset, strict=True))
    observational = read(RECURRENT / "training-observability.json")
    assert observational["training_episodes"] == 24 and len(observational["rows"]) == 48
    assert all(not x["exact_same_input"] for r in observational["rows"] for x in r["nearest_five_by_q_distance"])
    new_sources = read(ROOT / "experiments/so101/vla-open-source-audit/feedback-memory-followup-sources.json")
    for source in new_sources["sources"]:
        assert sha(ROOT / source["cache"]) == source["sha256"]
    report = {"kind": "scoped_raw_evidence_integrity_not_scientific_completion", "passed": True,
              "unchanged_bound_sources": source_counts, "runs": totals,
              "paired_success_table": dict(paired), "initialization_and_sampling_matched": True,
              "all_capability_gates_failed": True, "compensation_interventions": 0,
              "primary_cache_hashes": len(new_sources["sources"]),
              "auditor_sha256": sha(Path(__file__)),
              "limits": ["Single training seed and conservative single task; no population advantage claim.",
                         "Sparse traces do not independently recompute continuous dual-contact duration.",
                         "No physical calibration, scientific novelty or mechanism established."]}
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in {"unchanged_bound_sources", "limits"}}))


if __name__ == "__main__":
    main()
