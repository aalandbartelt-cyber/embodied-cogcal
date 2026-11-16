"""Zero-cost anchor probe on the E2 yaw sweep (no new episodes).

Measures the policy's *orientation response gain* alpha = d(phi_close)/d(theta),
where phi_close is the horizontal direction of the gripper's closing axis at the
moment the jaws begin to close. Two independent readings:

  * phi_cmd  -- forward kinematics of the commanded joint target (raw_target_rad),
                i.e. what the policy asks for (immune to servo lag);
  * phi_meas -- forward kinematics of the measured joints (q_after_rad).

Also reports, per yaw condition: wrist_roll by stage, the pre-close fingertip
contact timing and the object drift it causes, and the cross-condition spread of
the commanded end-effector position (to contrast translation gain with rotation
gain).  Writes anchor_probe.json next to this file.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import mujoco
import numpy as np

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
XML = HERE.parents[2] / "third_party/SO-ARM100/Simulation/SO101/so101_new_calib.xml"

CONDITIONS = {
    "e2-y0-d1": 0.0,
    "e2-y2-d1": 2.0,
    "e2-y5-d1": 5.0,
    "e2-y10-d1": 10.0,
    "e2-y15-d1": 15.0,
    "smoke-y30-d1": 30.0,
    "smoke-y45-d1": 45.0,
}

STAGES = {
    "approach": (35, 60),
    "close": (65, 85),
    "lift": (90, 130),
    "place": (150, 280),
}


def load_rows(tag: str) -> list[dict]:
    return [json.loads(line) for line in (RUNS / tag / "episodes.jsonl").read_text().splitlines() if line.strip()]


def load_trace(tag: str, seed: int) -> list[dict]:
    path = RUNS / tag / f"{seed}.trace.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def closing_angle(model, data, body_id, q) -> float:
    """Angle of the gripper body's local y axis (closing axis proxy) in the world xy plane."""
    data.qpos[:6] = q
    mujoco.mj_forward(model, data)
    y = data.xmat[body_id].reshape(3, 3)[:, 1]
    return math.degrees(math.atan2(y[1], y[0]))


def ee_pose(model, data, body_id, q):
    data.qpos[:6] = q
    mujoco.mj_forward(model, data)
    return data.xpos[body_id].copy(), data.xmat[body_id].reshape(3, 3).copy()


def main() -> None:
    model = mujoco.MjModel.from_xml_path(str(XML))
    data = mujoco.MjData(model)
    gid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "gripper")

    out: dict = {"xml": str(XML), "body": "gripper", "conditions": {}}
    all_phi_cmd, all_phi_meas, all_theta = [], [], []

    for tag, theta in CONDITIONS.items():
        rows = load_rows(tag)
        phi_cmd_by_step = {s: [] for s in (50, 60, 70, 80)}
        phi_cmd_close, phi_meas_close, wrist_by_stage = [], [], {k: [] for k in STAGES}
        ee_by_step = {50: [], 60: [], 70: []}
        early, first_ct, close_t, drift = [], [], [], []
        servo = []

        for row in rows:
            tr = load_trace(tag, row["seed"])
            if len(tr) < 90:
                continue
            q = np.array([t["q_after_rad"] for t in tr])
            tgt = np.array([t["raw_target_rad"] for t in tr])
            g = q[:, 5]
            idx = [i for i in range(40, min(285, len(tr))) if g[i] < 0.26]
            close = idx[0] if idx else 150

            for s in phi_cmd_by_step:
                if s < len(tgt):
                    phi_cmd_by_step[s].append(closing_angle(model, data, gid, tgt[s]))
            phi_cmd_close.append(closing_angle(model, data, gid, tgt[close]))
            phi_meas_close.append(closing_angle(model, data, gid, q[close]))
            servo.append(abs(phi_cmd_close[-1] - phi_meas_close[-1]))

            for s in ee_by_step:
                if s < len(tgt):
                    ee_by_step[s].append(ee_pose(model, data, gid, tgt[s])[0])

            for name, (a, b) in STAGES.items():
                b = min(b, len(q) - 1)
                if b > a:
                    wrist_by_stage[name].append(float(np.median(q[a:b, 4])))

            phys = np.load(row["physics_path"])
            t, xyz, fm = phys["time"], phys["xyz"], phys["finger_mask"]
            c_t = tr[close]["sim_time_s"]
            close_t.append(c_t)
            has = bool((fm > 0).any())
            ft = float(t[np.argmax(fm > 0)]) if has else float("nan")
            first_ct.append(ft)
            early.append(bool(has and ft < c_t - 0.02))
            pre = xyz[t < c_t]
            drift.append(float(np.linalg.norm(pre[-1][:2] - pre[0][:2]) * 1000) if len(pre) > 1 else 0.0)

        ee_spread = {}
        for s, pts in ee_by_step.items():
            if len(pts) > 1:
                arr = np.stack(pts)
                ee_spread[s] = float(np.sqrt(np.mean(np.var(arr, axis=0))) * 1000)

        out["conditions"][tag] = {
            "theta_deg": theta,
            "n": len(phi_cmd_close),
            "phi_cmd_close_deg": float(np.median(phi_cmd_close)),
            "phi_meas_close_deg": float(np.median(phi_meas_close)),
            "phi_cmd_by_step_deg": {str(s): float(np.median(v)) for s, v in phi_cmd_by_step.items() if v},
            "servo_gap_deg": float(np.median(servo)),
            "wrist_roll_by_stage_rad": {k: float(np.median(v)) for k, v in wrist_by_stage.items() if v},
            "early_contact_frac": float(np.mean(early)),
            "median_first_contact_s": float(np.nanmedian(first_ct)),
            "median_close_onset_s": float(np.median(close_t)),
            "median_preclose_drift_mm": float(np.median(drift)),
        }
        all_phi_cmd.extend(phi_cmd_close)
        all_phi_meas.extend(phi_meas_close)
        all_theta.extend([theta] * len(phi_cmd_close))

    theta = np.array(all_theta)
    for key, vals in (("alpha_cmd", all_phi_cmd), ("alpha_meas", all_phi_meas)):
        slope = float(np.polyfit(theta, np.array(vals), 1)[0])
        out[key] = slope
    out["ee_spread_step_mm"] = ee_spread

    (HERE / "anchor_probe.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
