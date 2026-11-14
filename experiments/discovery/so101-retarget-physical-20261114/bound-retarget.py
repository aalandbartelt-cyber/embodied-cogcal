"""Two ordinary bounded IK baselines; no learned model or new method."""

from __future__ import annotations

import mujoco
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

ANCHOR_INDICES = [41, 80, 149, 197, 233]
MODES = ["full_pose", "task_direction"]


def commands_from_anchors(carrier, anchors):
    up = carrier.upstream
    above, grasp, lift, carry, place = anchors
    schedule = [
        (up.HOME, up.APPROACH_Q, .4), (above, up.APPROACH_Q, 1.),
        (grasp, up.APPROACH_Q, 1.3), (grasp, up.CLOSE_Q, 1.),
        (lift, up.CLOSE_Q, 1.3), (carry, up.CLOSE_Q, 1.6),
        (place, up.CLOSE_Q, 1.2), (place, up.APPROACH_Q, .8),
        (lift, up.APPROACH_Q, .9),
    ]
    actions = []
    for step in range(285):
        elapsed = step / 30
        previous = np.r_[up.HOME, up.APPROACH_Q]
        for arm, grip, seconds in schedule:
            target = np.r_[arm, grip]
            if elapsed < seconds:
                progress = np.clip(elapsed / (seconds * .6), 0, 1)
                blend = progress * progress * (3 - 2 * progress)
                actions.append(previous + (target - previous) * blend)
                break
            elapsed -= seconds
            previous = target
        else:
            actions.append(previous)
    return np.asarray(actions)


def generate(carrier, source_actions, object_delta, goal_delta, mode):
    if mode not in MODES:
        raise ValueError("unknown IK mode")
    model = carrier.model
    scratch = mujoco.MjData(model)
    site = model.site(carrier.upstream.PINCH_SITE).id
    body = int(model.site_bodyid[site])
    low = np.maximum(model.jnt_range[:5, 0], carrier.low[:5])
    high = np.minimum(model.jnt_range[:5, 1], carrier.high[:5])
    source_anchors = source_actions[ANCHOR_INDICES, :5]
    reconstructed = commands_from_anchors(carrier, source_anchors)
    reconstruction_error = float(np.abs(reconstructed - source_actions).max())
    if reconstruction_error > 1e-12:
        raise ValueError("anchor schedule differs from original teacher")
    previous = carrier.upstream.HOME.copy()
    solutions, diagnostics = [], []
    for index, source in enumerate(source_anchors):
        scratch.qpos[:5] = source
        scratch.qpos[5] = carrier.upstream.APPROACH_Q
        mujoco.mj_forward(model, scratch)
        delta = object_delta if index < 3 else goal_delta
        position = scratch.site_xpos[site].copy() + delta
        rotation = scratch.site_xmat[site].reshape(3, 3).copy()
        approach = -scratch.xmat[body].reshape(3, 3)[:, 2].copy()
        attempts = []
        for seed in [source, previous]:
            calls = 0

            def residual(q, position=position, rotation=rotation, approach=approach, source=source):
                nonlocal calls
                calls += 1
                scratch.qpos[:5] = q
                mujoco.mj_forward(model, scratch)
                error_p = scratch.site_xpos[site] - position
                if mode == "full_pose":
                    current = scratch.site_xmat[site].reshape(3, 3)
                    error_r = Rotation.from_matrix(rotation.T @ current).as_rotvec()
                else:
                    current = -scratch.xmat[body].reshape(3, 3)[:, 2]
                    error_r = current - approach
                return np.r_[error_p, .1 * error_r, .001 * (q - source)]

            fit = least_squares(residual, np.clip(seed, low + 1e-10, high - 1e-10),
                                bounds=(low, high), max_nfev=150,
                                ftol=1e-10, xtol=1e-10, gtol=1e-10)
            attempts.append({"q": fit.x.copy(), "cost": float(fit.cost), "nfev": fit.nfev,
                             "residual_calls_including_numeric_jacobian": calls,
                             "optimizer_success": bool(fit.success), "status": int(fit.status)})
        chosen = min(attempts, key=lambda row: row["cost"])
        previous = chosen["q"].copy()
        scratch.qpos[:5] = previous
        mujoco.mj_forward(model, scratch)
        fitted_r = scratch.site_xmat[site].reshape(3, 3)
        fitted_a = -scratch.xmat[body].reshape(3, 3)[:, 2]
        diagnostics.append({
            "anchor_index": index, "q_rad": previous.tolist(),
            "target_xyz_m": position.tolist(), "target_rotation": rotation.tolist(),
            "position_error_m": float(np.linalg.norm(scratch.site_xpos[site] - position)),
            "rotation_error_rad": float(np.linalg.norm(Rotation.from_matrix(rotation.T @ fitted_r).as_rotvec())),
            "approach_error_deg": float(np.degrees(np.arccos(np.clip(approach @ fitted_a, -1, 1)))),
            "attempts": [{k: v for k, v in attempt.items() if k != "q"} for attempt in attempts],
        })
        solutions.append(previous)
    return commands_from_anchors(carrier, solutions), {
        "mode": mode, "anchors": diagnostics,
        "source_schedule_reconstruction_max_error_rad": reconstruction_error,
        "reference": "source command FK, not measured executed FK",
        "orientation_length_m": .1, "source_joint_prior_m_per_rad": .001,
        "bounds_rad": {"low": low.tolist(), "high": high.tolist()},
    }
