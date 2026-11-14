"""Verify fixed episode identities and task predicates from saved raw traces."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    contract = json.loads((args.run / "contract.json").read_text())
    summary = json.loads((args.run / "summary.json").read_text())
    assert summary["status"] == "completed", "not a completed 15-episode screen"
    assert contract["plan_sha256"] == digest(args.run / "plan-before-execution.md")
    for name, expected in contract["bindings_sha256"].items():
        assert digest(ROOT / name) == expected
        assert digest(args.run / f"bound-{Path(name).name}") == expected
    for name, expected in contract["model_xml_sha256"].items():
        assert digest(ROOT / name) == expected
    modes = ["full_pose", "task_direction"]
    expected_names = ["witness-source", *[f"witness-target-{i}" for i in range(4)],
                      *[f"identity-{mode}" for mode in modes],
                      *[f"retarget-{i}-{mode}" for i in range(4) for mode in modes]]
    assert [row["name"] for row in summary["rows"]] == expected_names
    assert summary["episodes_completed"] == summary["attempts"] == 15
    traces, checked = {}, []
    for row in summary["rows"]:
        name = row["name"]
        trace = [json.loads(line) for line in (args.run / f"{name}.trace.jsonl").read_text().splitlines()]
        assert len(trace) == row["controls"] == 285
        assert [r["control_step"] for r in trace] == list(range(285))
        requested = np.asarray([r["requested_rad"] for r in trace])
        sent = np.asarray([r["sent_rad"] for r in trace])
        before = np.asarray([r["q_before_rad"] for r in trace])
        after = np.asarray([r["q_after_rad"] for r in trace])
        assert requested.shape == sent.shape == before.shape == after.shape == (285, 6)
        assert all(np.isfinite(array).all() for array in [requested, sent, before, after])
        assert np.array_equal(before[1:], after[:-1])
        assert row["clip_events"] == sum(np.any(a != b) for a, b in zip(requested, sent, strict=True))
        assert all(r["object_pose_writes_during_rollout"] == 0 for r in trace)
        ticks = np.asarray([r["physics_ticks"] for r in trace])
        dt = contract["physics_timestep_s"]
        assert np.array_equal(ticks, np.rint(np.arange(1, 286) / (30 * dt)).astype(int))
        assert np.max(np.abs(np.array([r["time_s"] for r in trace]) - ticks * dt)) < 1e-9
        final = trace[-1]
        xyz = np.asarray(final["object_xyz_m_evaluator_only"])
        distance = float(np.linalg.norm(xyz[:2] - np.asarray(row["goal_xyz_m"])[:2]))
        assert abs(distance - row["goal_error_xy_m"]) < 1e-12
        assert np.array_equal(xyz, row["final_object_xyz_m"])
        placed = bool(distance <= .035 and abs(xyz[2] - .014) <= .012)
        released = bool(final["release_run_physics_ticks"] * dt >= .1)
        held = final["longest_held_run_physics_ticks"] * dt
        penetration = final["max_penetration_m_to_date"]
        assert np.all(np.diff([r["longest_held_run_physics_ticks"] for r in trace]) >= 0)
        assert np.all(np.diff([r["max_penetration_m_to_date"] for r in trace]) >= 0)
        success = bool(placed and released and held >= .5 and penetration <= .0015)
        assert success is row["task_success"]
        assert placed is row["placed"] and released is row["released"]
        assert held == row["longest_two_finger_lift_s"]
        assert penetration == row["max_object_robot_penetration_m"]
        traces[name] = trace
        checked.append({"name": name, "task_success_recomputed": success,
                        "controls": len(trace), "final_goal_error_m": distance})
    source = np.asarray([r["requested_rad"] for r in traces["witness-source"]])
    for mode in modes:
        commands = np.asarray([r["requested_rad"] for r in traces[f"identity-{mode}"]])
        assert np.abs(commands - source).max() <= 1e-5
    ik_attempts = 0
    for path in args.run.glob("*.ik.json"):
        diagnostic = json.loads(path.read_text())
        assert len(diagnostic["anchors"]) == 5
        assert diagnostic["source_schedule_reconstruction_max_error_rad"] <= 1e-12
        for anchor in diagnostic["anchors"]:
            assert len(anchor["attempts"]) == 2
            for attempt in anchor["attempts"]:
                assert attempt["nfev"] <= 150
                assert attempt["residual_calls_including_numeric_jacobian"] >= attempt["nfev"]
                ik_attempts += 1
    assert ik_attempts == 100
    protected = {
        "experiments/so101/smolvla-interface-preflight/summary-degree-assumption.json":
        "48fce62e85353a8dc0c81214bd8c6f8963ca8e5745226c2b40824af85b4b3a81",
        "experiments/so101/tpsc-pilot/manifest-pilot.jsonl":
        "2b351ca811adbe9672973cebe17597827b902a1f1be12210ae5030eda2baf883",
        "experiments/so101/tpsc-pilot/manifest-full.jsonl":
        "ced15f2b419275c89cff76516e17d2468324512eb7b32e10002a4148f6be39e5",
    }
    for name, expected in protected.items():
        assert digest(ROOT / name) == expected
    report = {"kind": "trace_integrity_and_predicate_audit_not_novelty_or_vla_validation",
              "passed": True, "episodes": len(checked), "controls": sum(r["controls"] for r in checked),
              "ik_optimizer_attempts": ik_attempts, "rows": checked,
              "protected_original_sha256": protected, "audit_source_sha256": digest(Path(__file__))}
    with args.out.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"passed": True, "episodes": len(checked), "controls": report["controls"]}))


if __name__ == "__main__":
    main()
