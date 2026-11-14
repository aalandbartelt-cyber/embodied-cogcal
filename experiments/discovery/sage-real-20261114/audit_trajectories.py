"""Read-only descriptive audit of three fixed public SO-101 recordings.

No success labels, VLA inputs, paired simulator output or causal mechanical
parameters are inferred. Gripper position is normalized, not a sixth radian.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]


def load(path, keys):
    with path.open() as stream:
        rows = list(csv.DictReader(stream))
    times = np.asarray([float(r["timestamp"]) / 1e6 for r in rows])
    if len(times) < 2 or not np.isfinite(times).all() or not np.all(np.diff(times) > 0):
        raise ValueError("finite strictly increasing microsecond timestamps required")
    values = {}
    for key in keys:
        array = np.asarray([ast.literal_eval(r[key]) for r in rows], dtype=float)
        if array.shape != (len(rows), 6) or not np.isfinite(array).all():
            raise ValueError("six finite channels required")
        values[key] = array
    return times, values, list(rows[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    source = json.loads(Path(__file__).with_name("source-inventory.json").read_text())
    for file in source["files"]:
        if hashlib.sha256((ROOT / file["cache"]).read_bytes()).hexdigest() != file["sha256"]:
            raise ValueError("source content changed")
    results = []
    for motion in source["selected_before_data_read"]:
        folder = ROOT / "data/discovery/sage-real-readonly-20261114" / motion
        control_time, control, control_columns = load(folder / "control.csv", ["positions"])
        state_time, state, state_columns = load(folder / "state_motor.csv", ["positions", "velocities", "torques"])
        names = (folder / "joint_list.txt").read_text().splitlines()
        if len(names) != 6:
            raise ValueError("unexpected joint order")
        # Available timestamps permit descriptive row matching only. The collector
        # stamps the post-command serial read with the earlier loop-start time.
        equal_clock = np.array_equal(control_time, state_time)
        same_length = len(control_time) == len(state_time)
        if not (equal_clock and same_length):
            raise ValueError("reported equal-clock assumption does not hold")
        residual = state["positions"] - control["positions"]
        periods = np.diff(control_time)
        with (folder / "event.csv").open() as stream:
            events = list(csv.DictReader(stream))
        results.append({
            "motion": motion, "rows": len(control_time), "joint_order": names,
            "columns": {"control": control_columns, "state": state_columns},
            "duration_s": float(control_time[-1] - control_time[0]),
            "period_s_quantiles_p0_p50_p95_p100": np.quantile(periods, [0, .5, .95, 1]).tolist(),
            "descriptive_median_hz": float(1 / np.median(periods)),
            "exact_equal_command_state_timestamps": bool(equal_clock),
            "arm_command_min_rad": control["positions"][:, :5].min(0).tolist(),
            "arm_command_max_rad": control["positions"][:, :5].max(0).tolist(),
            "arm_state_min_rad": state["positions"][:, :5].min(0).tolist(),
            "arm_state_max_rad": state["positions"][:, :5].max(0).tolist(),
            "row_matched_arm_residual_mean_rad": residual[:, :5].mean(0).tolist(),
            "row_matched_arm_residual_rmse_rad": np.sqrt((residual[:, :5] ** 2).mean(0)).tolist(),
            "row_matched_gripper_residual_rmse_normalized": float(np.sqrt((residual[:, 5] ** 2).mean())),
            "gripper_command_range_normalized": [float(control["positions"][:, 5].min()),
                                                   float(control["positions"][:, 5].max())],
            "gripper_state_range_normalized": [float(state["positions"][:, 5].min()),
                                                 float(state["positions"][:, 5].max())],
            "events": events, "success_labels_present": False,
        })
    result = {
        "kind": "public_real_data_descriptive_not_our_hardware_or_vla_mechanism",
        "source_revision": source["revision"], "rows": results,
        "recordings": len(results), "frames_total_descriptive_only": sum(r["rows"] for r in results),
        "causal_delay_estimate": "not_identifiable_from_shared_loop_start_timestamps",
        "readout_note": "Same-row q-command error includes unresolved sensing/dispatch timing; not isolated mechanics.",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "limits": ["Three preselected recordings, not independent frame-level replications.",
                   "No RGB/task success/closed-loop policy trace; motion filename is not a successful task label.",
                   "No matched sim output, so no sim-real gap is computed.",
                   "Estimated torques are not calibrated force measurements.",
                   "Current collector snapshot does not establish historical recording provenance."],
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"recordings": result["recordings"], "frames": result["frames_total_descriptive_only"],
                      "motion_rows_hz": [(r["motion"], r["rows"], r["descriptive_median_hz"]) for r in results]}))


if __name__ == "__main__":
    main()
