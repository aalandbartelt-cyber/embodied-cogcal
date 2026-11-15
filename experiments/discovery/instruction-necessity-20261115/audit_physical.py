"""Audit every saved command/physical trace and compare the fresh replay."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    run = HERE / "physical"
    contract = json.loads((run / "contract.json").read_text())
    for name, expected in contract["bindings"].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"bound source changed: {name}")
    if digest(run / "scene-override.xml") != contract["scene_override_sha256"]:
        raise ValueError("executed scene changed")
    summary = json.loads((run / "summary.json").read_text())
    if summary != json.loads((args.replay / "summary.json").read_text()):
        raise ValueError("fresh physics replay summary differs")
    checked, totals = [], 0
    for result in summary["rows"]:
        name = result["case"]
        if "error" in result:
            raise ValueError("a physical case failed; audit must not hide it")
        commands = np.load(run / f"{name}.commands.npy", allow_pickle=False)
        replay = np.load(args.replay / f"{name}.commands.npy", allow_pickle=False)
        if not np.array_equal(commands, replay):
            raise ValueError("replay command stream differs")
        trace_path = run / f"{name}.trace.jsonl"
        if digest(trace_path) != digest(args.replay / trace_path.name):
            raise ValueError("fresh replay physical trace differs")
        trace = [json.loads(line) for line in trace_path.read_text().splitlines()]
        if len(trace) != result["controls"] or commands.shape != (len(trace), 6):
            raise ValueError("command/trace count mismatch")
        max_lift = {n: 0. for n in ["A", "B"]}
        sampled_longest = {n: 0 for n in ["A", "B"]}
        streak = sampled_longest.copy()
        proximity_both = 0
        for i, row in enumerate(trace):
            if row["control_index"] != i or abs(row["time_s"] - (i + 1) / 30) > .00051:
                raise ValueError("physical clock mismatch")
            if not np.array_equal(commands[i], row["requested_rad"]) or not np.array_equal(commands[i], row["sent_rad"]):
                raise ValueError("requested/sent command mismatch")
            distances = []
            for object_name, obj in row["objects"].items():
                height = obj["xyz_m"][2] - contract["initial_xyz_m"][object_name][2]
                max_lift[object_name] = max(max_lift[object_name], height)
                valid = obj["fingers"] == 2 and height > .05
                streak[object_name] = streak[object_name] + 1 if valid else 0
                sampled_longest[object_name] = max(sampled_longest[object_name], streak[object_name])
                distances.append(float(np.linalg.norm(np.asarray(row["tcp_xyz_m"]) - obj["xyz_m"])))
                if obj["max_penetration_m"] > .0015:
                    raise ValueError("penetration gate failed")
            proximity_both += max(distances) < .2
        completes = result["ever_physical_completion"]
        expected = {n: n in result["order"] for n in ["A", "B"]}
        if completes != expected:
            raise ValueError("physical positive/negative control failed")
        for n, expected_lift in expected.items():
            if expected_lift and (sampled_longest[n] < 15 or max_lift[n] < .05):
                raise ValueError("saved control-rate contacts do not support lift witness")
        if result["clip_vectors"] != 0 or result["object_pose_writes_after_reset"] != 0:
            raise ValueError("command clipping or object-state write recorded")
        checked.append({"case": name, "controls": len(trace), "command_sha256": digest(run / f"{name}.commands.npy"),
                        "trace_sha256": digest(trace_path), "max_lift_above_initial_m": max_lift,
                        "longest_consecutive_contact_samples_at_30hz": sampled_longest,
                        "samples_both_within_0p2_m": proximity_both,
                        "ever_completed": completes, "first_completion_matches": result["first_completion_matches"]})
        totals += len(trace)
    inventory = {str(p.relative_to(ROOT)): digest(p) for p in sorted(run.iterdir()) if p.is_file()}
    for scan, single in [("scan_AB", "single_A"), ("scan_BA", "single_B")]:
        scan_commands = np.load(run / f"{scan}.commands.npy", allow_pickle=False)
        single_commands = np.load(run / f"{single}.commands.npy", allow_pickle=False)
        if not np.array_equal(scan_commands[:len(single_commands)], single_commands):
            raise ValueError("single-target command stream differs from matching scan prefix")
        scan_trace = (run / f"{scan}.trace.jsonl").read_bytes().splitlines()
        single_trace = (run / f"{single}.trace.jsonl").read_bytes().splitlines()
        if scan_trace[:len(single_trace)] != single_trace:
            raise ValueError("single-target physical states differ from matching scan prefix")
    output = {"kind": "all_record_audit_and_same_code_physics_replay_not_hardware_or_novelty",
              "cases": checked, "total_controls": totals, "cases_checked": len(checked),
              "fresh_physics_replay_trace_bytes_identical": True, "inventory": inventory,
              "single_target_and_scan_prefix_commands_and_traces_identical": True,
              "audit_script_sha256": digest(Path(__file__)),
              "limits": ["Contact durations at physical rate are recorded by the runner; this audit independently checks control-rate contact runs.",
                         "Fresh replay verifies numerical reproducibility, not statistical independence.",
                         "0.2m proximity diagnostic is post-result and not the full Isaac checker."]}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"cases": len(checked), "controls": totals, "replay_identical": True,
                      "per_case_sampled_two_finger_lift": {r["case"]: r["longest_consecutive_contact_samples_at_30hz"] for r in checked}}))


if __name__ == "__main__":
    main()
