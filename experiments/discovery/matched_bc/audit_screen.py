"""Read-only evidence checks for the fixed BC screen and validation diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/discovery/matched-bc-lowrate-20261114"
DIAG = ROOT / "experiments/discovery/matched-bc-horizon-diagnostic-20261114"


def read(path):
    return json.loads(path.read_text(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def rows(path):
    return [json.loads(line, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
            for line in path.read_text().splitlines()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_trace(path, execute, low, high, diagnostic=False):
    trace = rows(path)
    assert len(trace) == 285
    history = deque([trace[0]["q_before_rad"] for _ in range(8)], maxlen=8)
    chunk, count, clips = None, 0, 0
    for step, row in enumerate(trace):
        assert row["step" if diagnostic else "control_step"] == step
        if step:
            assert row["q_before_rad"] == trace[step - 1]["q_after_rad"]
        if step % execute == 0:
            chunk = np.asarray(row["chunk_rad"])
            assert chunk.shape == (30, 6) and np.isfinite(chunk).all()
            assert row["q_history_input_rad"] == list(history)
            assert len(row["rgb_sha256"]) == 64
            count += 1
        else:
            assert "chunk_rad" not in row
        raw = chunk[step % execute]
        command = np.asarray(row["command_rad"])
        assert np.array_equal(command, np.clip(raw, low, high))
        assert np.isfinite(row["q_after_rad"]).all()
        clips += int(np.any(raw != command))
        history.append(row["q_after_rad"])
    if not diagnostic:
        assert abs(trace[-1]["sim_time_s"] - 9.5) <= 0.0005
    return count, clips


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh audit output required")
    protected = {
        "experiments/so101/smolvla-interface-preflight/summary-degree-assumption.json":
            "48fce62e85353a8dc0c81214bd8c6f8963ca8e5745226c2b40824af85b4b3a81",
        "experiments/so101/tpsc-pilot/manifest-pilot.jsonl":
            "2b351ca811adbe9672973cebe17597827b902a1f1be12210ae5030eda2baf883",
        "experiments/so101/tpsc-pilot/manifest-full.jsonl":
            "ced15f2b419275c89cff76516e17d2468324512eb7b32e10002a4148f6be39e5",
    }
    for path, expected in protected.items():
        assert sha(ROOT / path) == expected, path
    recorded_sources = read(RUN / "pipeline-source-hashes.json")
    for name, expected in recorded_sources.items():
        assert sha(Path(__file__).with_name(name)) == expected, name
    events = rows(RUN / "pipeline-events.jsonl")
    assert [e["stage"] for e in events if e["event"] == "stage_exit"] == ["collection", "training", "test"]
    assert all(e["exit_code"] == 0 for e in events if e["event"] == "stage_exit")
    assert events[-1]["event"] == "complete" and not events[-1]["capability_gate"]

    demonstrations = rows(RUN / "collection/episodes.jsonl")
    train = {r["seed"] for r in demonstrations if r["split"] == "train"}
    val = {r["seed"] for r in demonstrations if r["split"] == "val"}
    assert train == set(range(4100, 4124)) and val == set(range(5100, 5108))
    assert len(demonstrations) == 32 and all(r["task_success"] is True for r in demonstrations)
    assert not (train & val)
    for row in demonstrations:
        path = Path(row["path"])
        assert sha(path) == row["sha256"]
        with np.load(path) as data:
            rgb = data["rgb"]
            assert rgb.shape == (285, 2, 128, 128, 3)
            assert rgb.dtype == np.uint8
            assert data["q"].shape == data["action"].shape == (285, 6)
            assert np.isfinite(data["q"]).all() and np.isfinite(data["action"]).all()
            assert np.array_equal(data["rgb_age_control_steps"], np.arange(285) % 6)
            for i in range(285):
                assert np.array_equal(rgb[i], rgb[i - i % 6])
    training = read(RUN / "training/completed.json")
    assert training["step"] == 2000 and training["test_used"] is False
    assert sha(Path(training["checkpoint"])) == training["checkpoint_sha256"]
    assert [r["step"] for r in rows(RUN / "training/updates.jsonl")] == list(range(100, 2001, 100))
    identity = read(RUN / "model-identity-postrun.json")
    low, high = np.asarray(identity["actuator_low_rad"]), np.asarray(identity["actuator_high_rad"])
    test = rows(RUN / "test/episodes.jsonl")
    assert [r["seed"] for r in test] == list(range(6100, 6120))
    assert all(r["task_success"] is False and r["longest_two_finger_lift_s"] == 0 for r in test)
    chunks = clips = 0
    for row in test:
        n, c = check_trace(RUN / f"test/{row['seed']}.trace.jsonl", 6, low, high)
        assert row["clip_events"] == c and row["controls"] == 285
        chunks += n
        clips += c
    assert chunks == 960 and clips == 2828

    diagnostic = rows(DIAG / "episodes.jsonl")
    assert len(diagnostic) == 16
    for execute in [6, 30]:
        group = [r for r in diagnostic if r["execute"] == execute]
        assert [r["seed"] for r in group] == list(range(5100, 5108))
        assert sum(r["task_success"] for r in group) == (0 if execute == 6 else 4)
        for row in group:
            _, c = check_trace(DIAG / f"e{execute}-s{row['seed']}.trace.jsonl",
                               execute, low, high, diagnostic=True)
            assert c == row["clip_events"]
        if execute == 30:
            assert all(r["placed"] and r["longest_two_finger_lift_s"] >= 0.5 for r in group)
            assert all(not r["released"] for r in group if not r["task_success"])
        else:
            assert all(not r["placed"] for r in group)
    primary = read(ROOT / "experiments/so101/vla-open-source-audit/history-compensation-primary-sources.json")
    for source in primary["sources"]:
        assert sha(ROOT / source["local_cache"]) == source["sha256"]
    result = {
        "kind": "raw_evidence_integrity_not_method_or_novelty_validation", "passed": True,
        "protected_originals": protected, "pipeline_sources_unchanged": len(recorded_sources),
        "demonstrations": 32, "demonstration_frames": 9120,
        "test_episodes": 20, "test_successes": 0, "test_commands": 5700,
        "test_chunks": chunks, "test_vector_clip_events": clips,
        "validation_diagnostic_episodes": 16, "primary_cache_hashes": len(primary["sources"]),
        "auditor_sha256": sha(Path(__file__)),
        "limits": ["Does not prove task competence, physical calibration, a failure mechanism or novelty.",
                   "Model identity was recorded after the run, not monitored continuously."],
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
