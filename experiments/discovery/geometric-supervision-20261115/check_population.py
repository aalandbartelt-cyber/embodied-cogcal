"""Bounded one-coordinate population diagnostic, not GRASP/policy replication."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import mujoco
import numpy as np
import scipy
from scipy.spatial.transform import Rotation
from scipy.special import expit, ndtri

ROOT = Path(__file__).resolve().parents[3]
MODEL = ROOT / "third_party/SO-ARM100/Simulation/SO101/so101_new_calib.xml"
STATS = ROOT / "data/tpsc-carrier/meta/stats.json"
REVISION = "a758567c3978dfeefe282ede0500085a48fe8f78"
JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]
LAMBDA, CP, CR = .15, .5 + .1, .5 * .3 + .1 * .1


def weight(t):
    return 0. if t <= .05 else min(10., 1. / (t * t + .001))


class Geometry:
    def __init__(self):
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=MODEL.parents[2], text=True).strip()
        if revision != REVISION:
            raise ValueError("uninspected official model revision")
        stats = json.loads(STATS.read_text())
        self.mu = float(np.deg2rad(stats["action"]["mean"][0]))
        self.scale = float(np.deg2rad(stats["action"]["std"][0]))
        self.model = mujoco.MjModel.from_xml_path(str(MODEL))
        self.data = mujoco.MjData(self.model)
        ids = np.array([self.model.joint(n).id for n in JOINTS])
        self.addresses = self.model.jnt_qposadr[ids]
        self.fixed = self.model.jnt_range[ids].mean(1)
        self.data.qpos[self.addresses] = self.fixed
        self.pose(0.)
        axis = self.data.xaxis[ids[0]].copy()
        offset = self.data.site("gripperframe").xpos - self.data.xanchor[ids[0]]
        self.radius = float(np.linalg.norm(offset - axis * (axis @ offset)))
        self.limit = self.model.jnt_range[ids[0]].copy()
        if not np.all((self.mu + self.scale * np.array([-1., 1.]) > self.limit[0])
                      & (self.mu + self.scale * np.array([-1., 1.]) < self.limit[1])):
            raise ValueError("modes outside official pan range")
        if 2 * self.scale >= np.pi:
            raise ValueError("orientation quadratic reduction would wrap")

    def pose(self, y):
        self.data.qpos[self.addresses[0]] = self.mu + self.scale * y
        mujoco.mj_forward(self.model, self.data)
        return (self.data.site("gripperframe").xpos.copy(),
                self.data.site("gripperframe").xmat.reshape(3, 3).copy())

    def fk_loss(self, y, p, affine=False):
        pred_p, pred_r = self.pose(y)
        value = 0.
        for target, prob in [(-1., 1 - p), (1., p)]:
            true_p, true_r = self.pose(target)
            # Affine negative control uses the tangent at conditional mean.
            if affine:
                position = self.radius ** 2 * self.scale ** 2 * (y - target) ** 2
            else:
                position = float(np.sum((pred_p - true_p) ** 2))
            angle = float(Rotation.from_matrix(pred_r @ true_r.T).magnitude())
            value += prob * (CP * position + CR * angle ** 2)
        return value

    def geo(self, y, p):
        s = self.scale
        position = 2 * self.radius ** 2 * (
            1 - p * np.cos(s * (y - 1)) - (1 - p) * np.cos(s * (y + 1)))
        angle2 = s ** 2 * (p * (y - 1) ** 2 + (1 - p) * (y + 1) ** 2)
        return CP * position + CR * angle2

    def geo_dy(self, y, p, affine=False):
        m, s = 2 * p - 1, self.scale
        pos = (2 * self.radius ** 2 * s ** 2 * (y - m) if affine else
               2 * self.radius ** 2 * s *
               (p * np.sin(s * (y - 1)) + (1 - p) * np.sin(s * (y + 1))))
        return CP * pos + 2 * CR * s ** 2 * (y - m)

    def optimum(self, p, t, lam=LAMBDA):
        """Unique minimizer y in [-1,1]; residual scaled to y units."""
        m, s = 2 * p - 1, self.scale
        a = 1 / t ** 2 + lam * weight(t) * CR * s ** 2
        b = lam * weight(t) * CP * self.radius ** 2 * s / a
        # derivative of normalized root >= 1-|b*s| on the whole real line.
        lower = 1 - abs(b * s)
        if lower <= 0:
            raise ValueError("global convexity not established")
        y = np.array(m, dtype=np.float64, copy=True)
        for _ in range(12):
            sine = p * np.sin(s * (y - 1)) + (1 - p) * np.sin(s * (y + 1))
            cosine = p * np.cos(s * (y - 1)) + (1 - p) * np.cos(s * (y + 1))
            residual = y - m + b * sine
            if np.max(np.abs(residual)) < 1e-14:
                break
            y -= residual / (1 + b * s * cosine)
        residual = y - m + b * (
            p * np.sin(s * (y - 1)) + (1 - p) * np.sin(s * (y + 1)))
        error = float(np.max(np.abs(residual)))
        if error > 1e-12 or np.max(np.abs(y)) > 1 + 1e-12:
            raise ValueError("minimizer failed its residual/range check")
        return y, error, lower


def gradient_checks(g):
    rows = []
    h = 1e-5
    for p, t, lam, affine, label in [
        (.7, .5, LAMBDA, False, "asymmetric_two_mode"),
        (.5, .5, LAMBDA, False, "symmetric_single_coordinate_control"),
        (1., .5, LAMBDA, False, "deterministic_control"),
        (.7, .5, LAMBDA, True, "affine_fk_control"),
        (.7, .5, 0., False, "no_geometric_loss_control"),
        (.7, .05, LAMBDA, False, "weight_switch_off_control"),
        (.7, .050001, LAMBDA, False, "just_above_weight_switch"),
    ]:
        m = 2 * p - 1
        analytic = -t * lam * weight(t) * g.geo_dy(m, p, affine)
        # Central difference evaluates MuJoCo FK + scipy SO(3), independently.
        numeric = lam * weight(t) * (
            g.fk_loss(m - t * h, p, affine) - g.fk_loss(m + t * h, p, affine)) / (2 * h)
        if abs(analytic - numeric) > 2e-9:
            raise ValueError("independent FK central difference disagrees")
        rows.append({"condition": label, "posterior_plus": p, "t": t,
                     "lambda": lam, "weight": weight(t), "mean_action": m,
                     "geo_gradient_wrt_velocity_at_cfm": float(analytic),
                     "independent_fd_gradient": float(numeric),
                     "absolute_gradient_check_error": abs(float(analytic - numeric))})
    return rows


def sample(g, prior, steps, geometric):
    initial = ndtri((np.arange(1024, dtype=np.float64) + .5) / 1024)
    x = initial.copy()
    max_residual, min_convexity = 0., 1.
    log_odds = np.log(prior / (1 - prior))
    for i in range(steps):
        t = (steps - i) / steps
        posterior = expit(log_odds + 2 * (1 - t) * x / t ** 2)
        if geometric:
            y, error, lower = g.optimum(posterior, t)
            max_residual, min_convexity = max(max_residual, error), min(min_convexity, lower)
        else:
            y = 2 * posterior - 1
        # Euler from noise t=1 to actual data endpoint t=0.
        x -= (x - y) / (steps * t)
    distance = np.minimum(np.abs(x - 1), np.abs(x + 1))
    return {"prior_plus": prior, "steps": steps,
            "field": "paired_geometric_population_optimum" if geometric else "ordinary_cfm_exact",
            "quadrature_points_not_episodes": len(initial),
            "legal_support_fraction_at_band_0_1": float(np.mean(distance <= .1)),
            "positive_mode_fraction": float(np.mean(x > 0)),
            "max_distance_from_either_mode": float(distance.max()),
            "max_normalized_root_residual": max_residual,
            "min_normalized_hessian_lower_bound": min_convexity,
            "endpoint": x.tolist()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    g = Geometry()
    fk_errors = [abs(g.fk_loss(y, p) - g.geo(y, p))
                 for y in [-1., 0., .4, 1.] for p in [.5, .7, 1.]]
    if max(fk_errors) > 1e-12:
        raise ValueError("circle reduction differs from actual FK/SO3 loss")
    gradients = gradient_checks(g)
    rows, paired = [], []
    for prior in [.5, .7]:
        for steps in [10, 100, 1000]:
            baseline, augmented = sample(g, prior, steps, False), sample(g, prior, steps, True)
            diff = np.array(augmented["endpoint"]) - np.array(baseline["endpoint"])
            paired.append({"prior_plus": prior, "steps": steps,
                           "max_absolute_paired_endpoint_difference": float(np.abs(diff).max()),
                           "support_fraction_change": augmented["legal_support_fraction_at_band_0_1"]
                           - baseline["legal_support_fraction_at_band_0_1"],
                           "positive_mode_fraction_change": augmented["positive_mode_fraction"]
                           - baseline["positive_mode_fraction"]})
            rows.extend([baseline, augmented])
    report = {
        "kind": "one_coordinate_population_diagnostic_not_robot_task_or_grasp_replication",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "plan_sha256": hashlib.sha256(Path(__file__).with_name("PLAN.md").read_bytes()).hexdigest(),
        "model_revision": REVISION, "model_xml_sha256": hashlib.sha256(MODEL.read_bytes()).hexdigest(),
        "stats_sha256": hashlib.sha256(STATS.read_bytes()).hexdigest(),
        "versions": {"mujoco": mujoco.__version__, "numpy": np.__version__, "scipy": scipy.__version__},
        "geometry": {"fixed_joint_order": JOINTS, "fixed_midpoints_rad": g.fixed.tolist(),
                     "active_coordinate": "normalized shoulder_pan only; others held fixed",
                     "mean_rad": g.mu, "rad_per_normalized_action": g.scale,
                     "tcp_circle_radius_m": g.radius, "pan_limit_rad": g.limit.tolist(),
                     "position_loss_coefficient": CP, "angle_squared_coefficient": CR,
                     "lambda": LAMBDA, "max_fk_reduction_error": max(fk_errors)},
        "gradient_checks": gradients, "paired_sampling": paired, "sampling": rows,
        "limits": ["Exact conditional field, no finite model, fitting, RGB/language or robot rollout.",
                   "Both legal modes are assumed task goals; not independently successful robot continuations.",
                   "1024 deterministic Gaussian quadrature points are not 1024 independent robot episodes.",
                   "No inference that full GRASP, other geometries or policies cannot suffer harm.",
                   "Nonzero training-objective gradient is not itself sampled task harm or novelty."]}
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"gradients": gradients, "paired_sampling": paired,
                      "max_fk_reduction_error": max(fk_errors)}))


if __name__ == "__main__":
    main()
