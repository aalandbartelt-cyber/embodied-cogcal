"""Read-only local kinematic premise audit, not a manipulation experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "third_party/SO-ARM100"
REVISION = "a758567c3978dfeefe282ede0500085a48fe8f78"
JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]


def world_angular_derivative(plus, minus, center, step):
    omega = ((plus - minus) / (2 * step)) @ center.T
    return np.array([omega[2, 1] - omega[1, 2], omega[0, 2] - omega[2, 0],
                     omega[1, 0] - omega[0, 1]]) / 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=SOURCE, text=True).strip()
    if revision != REVISION:
        raise ValueError("uninspected model revision")
    xml = SOURCE / "Simulation/SO101/so101_new_calib.xml"
    model = mujoco.MjModel.from_xml_path(str(xml))
    data = mujoco.MjData(model)
    joint_ids = np.array([model.joint(n).id for n in JOINTS])
    addresses = model.jnt_qposadr[joint_ids]
    dofs = model.jnt_dofadr[joint_ids]
    limits = model.jnt_range[joint_ids]
    site = model.site("gripperframe").id
    rng = np.random.default_rng(20261114)
    configurations = limits.mean(1) + rng.uniform(-.3, .3, (24, 5)) * np.diff(limits, axis=1).ravel()
    step = 1e-6
    rows = []
    max_p_error = max_r_error = 0.
    for index, q in enumerate(configurations):
        data.qpos[addresses] = q
        mujoco.mj_forward(model, data)
        rotation = data.site_xmat[site].reshape(3, 3).copy()
        jp, jr = np.zeros((3, model.nv)), np.zeros((3, model.nv))
        mujoco.mj_jacSite(model, data, jp, jr, site)
        jp, jr = jp[:, dofs], jr[:, dofs]
        fd_p, fd_r = [], []
        for j, address in enumerate(addresses):
            data.qpos[address] = q[j] + step
            mujoco.mj_forward(model, data)
            pp, rp = data.site_xpos[site].copy(), data.site_xmat[site].reshape(3, 3).copy()
            data.qpos[address] = q[j] - step
            mujoco.mj_forward(model, data)
            pm, rm = data.site_xpos[site].copy(), data.site_xmat[site].reshape(3, 3).copy()
            data.qpos[address] = q[j]
            fd_p.append((pp - pm) / (2 * step))
            fd_r.append(world_angular_derivative(rp, rm, rotation, step))
        max_p_error = max(max_p_error, float(np.abs(np.array(fd_p).T - jp).max()))
        max_r_error = max(max_r_error, float(np.abs(np.array(fd_r).T - jr).max()))
        scales = []
        for length in [.05, .1, .2]:
            jac = np.vstack([jp, length * jr])
            u, singular, _ = np.linalg.svd(jac, full_matrices=True)
            missing = u[:, -1]
            # Block rotation puts both twist blocks in the same tool frame.
            missing_tool = np.r_[rotation.T @ missing[:3], rotation.T @ missing[3:]]
            ratios = []
            for axis in range(3):
                desired = np.r_[np.zeros(3), length * rotation[:, axis]]
                fitted = jac @ np.linalg.lstsq(jac, desired, rcond=None)[0]
                ratios.append(float(np.linalg.norm(desired - fitted) / np.linalg.norm(desired)))
            scales.append({"characteristic_length_m": length,
                           "rank_at_absolute_1e_9": int(np.linalg.matrix_rank(jac, tol=1e-9)),
                           "singular_values_scaled": singular.tolist(),
                           "left_null_tool_scaled": missing_tool.tolist(),
                           "pure_tool_rotation_relative_ls_residual_xyz": ratios})
        rows.append({"index": index, "q_rad": q.tolist(), "scales": scales,
                     "wrist_roll_angular_axis_tool": (rotation.T @ jr[:, -1]).tolist(),
                     "wrist_roll_site_translation_m_per_rad": float(np.linalg.norm(jp[:, -1]))})
    if max_p_error > 1e-7 or max_r_error > 1e-7:
        raise ValueError("analytic Jacobian fails independent finite difference")
    report = {"kind": "local_geometric_audit_not_task_reachability_or_method_novelty",
              "model_revision": revision, "model_xml_sha256": hashlib.sha256(xml.read_bytes()).hexdigest(),
              "audit_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "mujoco": mujoco.__version__, "numpy": np.__version__, "seed": 20261114,
              "sample": "24 configurations, middle 60 percent of each arm joint range, no task/collision filter",
              "joint_order": JOINTS, "site": "gripperframe", "finite_difference_step_rad": step,
              "max_finite_difference_translation_error_m_per_rad": max_p_error,
              "max_finite_difference_angular_error_rad_per_rad": max_r_error, "rows": rows,
              "limits": ["Configuration samples are not independent task episodes.",
                         "Local rank does not prove a global pose unreachable or task impossible.",
                         "No retargeted trajectory, policy rollout, compensation or hardware trial run.",
                         "A blog model may have different frames; our model does not prove their implementation wrong."]}
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"configurations": len(rows), "max_fd_position": max_p_error,
                      "max_fd_rotation": max_r_error,
                      "ranks": sorted({s["rank_at_absolute_1e_9"] for r in rows for s in r["scales"]}),
                      "first_wrist_axis_tool": rows[0]["wrist_roll_angular_axis_tool"]}))


if __name__ == "__main__":
    main()
