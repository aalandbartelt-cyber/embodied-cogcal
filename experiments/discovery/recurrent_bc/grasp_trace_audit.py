"""Read-only FK of logged states; evaluator truth never enters the policy."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/discovery/matched_bc"))
from carrier import Carrier  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("new output required")
    summary = json.loads((args.run / "summary.json").read_text())
    carrier = Carrier()
    scratch = mujoco.MjData(carrier.model)
    site = carrier.model.site(carrier.upstream.PINCH_SITE).id
    rows = []
    for episode in summary["rows"]:
        trace = [json.loads(line) for line in
                 (args.run / f"{episode['seed']}.trace.jsonl").read_text().splitlines()]
        close = next((r for r in trace if r["command_rad"][5] <= .2), None)
        record = {"seed": episode["seed"], "task_success": episode["task_success"],
                  "failure_reason": episode["failure_reason"], "source_xyz_m": episode["source_xyz_m"]}
        if close is not None:
            scratch.qpos[:6] = close["q_after_rad"]
            mujoco.mj_forward(carrier.model, scratch)
            tcp = scratch.site_xpos[site].copy()
            obj = np.asarray(close["object_xyz_m_evaluator_only"])
            axis = scratch.site_xmat[site].reshape(3, 3)[:, 2]
            direction_error = np.degrees(np.arccos(np.clip(axis @ carrier.upstream.DOWN, -1, 1)))
            record.update({"first_command_le_0p2_rad_step": close["control_step"],
                           "pinch_xyz_m_at_logged_after_state": tcp.tolist(),
                           "object_xyz_m_at_same_after_state": obj.tolist(),
                           "pinch_object_xy_error_m": float(np.linalg.norm(tcp[:2] - obj[:2])),
                           "pinch_object_z_error_m": float(tcp[2] - obj[2]),
                           "pinch_down_direction_error_deg": float(direction_error)})
        rows.append(record)
    groups = {}
    for success in [False, True]:
        group = [r for r in rows if r["task_success"] is success]
        errors = [r["pinch_object_xy_error_m"] for r in group if "pinch_object_xy_error_m" in r]
        groups[str(success)] = {"episodes": len(group), "with_close_event": len(errors),
                                "median_xy_error_m": float(np.median(errors)) if errors else None}
    report = {"kind": "posthoc_logged_state_fk_diagnostic_not_causal_failure_proof",
              "groups_by_final_success": groups, "rows": rows,
              "definition": "first command gripper<=.2rad; FK and object from same after-control state",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "limits": ["Threshold selected for descriptive investigation after observing failures.",
                         "Contact may already have displaced the object; does not identify perception error.",
                         "FK scratch writes are offline only; no rollout is altered."]}
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(groups))


if __name__ == "__main__":
    main()
