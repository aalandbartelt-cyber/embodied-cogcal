"""Supplementary mechanism analysis for E2 (post-hoc, label-free where possible).

Two questions the preregistered endpoints do not answer:

1. Does the jaw stop width track W_eff(theta) = W(|cos|+|sin|)?  The gripper joint
   angle at full closure (q5) is blocked by the object, so it is an independent
   kinematic read-out of the across-jaws width -- computed without the success label.
2. Given that the cube was lifted, does placement still work?  Splitting failures
   by stage separates "gripper never held it" from "held it but released wrong".

Writes mechanism.json. This is descriptive: no endpoint, no decision.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import interpolate, stats

HERE = Path(__file__).resolve().parent
YAWS = (0, 2, 5, 10, 15)
CUBE_MM = 28.0
# Pad-centre gap vs gripper joint angle, measured on the frozen model (PREREG section 2).
CALIB = np.array([[-0.17453297762778586, 9.43], [0.0, 21.24], [0.5, 60.34],
                  [1.0, 96.39], [1.5, 126.57], [1.7453291995659765, 138.61]])
GAP_MM = interpolate.interp1d(CALIB[:, 0], CALIB[:, 1], kind="linear")
LIFT_Z = 0.05  # metres; comfortably above the 0.019 m "never got hold of it" ceiling and below 0.08 m lifts


def w_eff(yaw: float) -> float:
    t = np.radians(yaw)
    return CUBE_MM * (abs(np.cos(t)) + abs(np.sin(t)))


def main() -> None:
    rows = []
    for yaw in YAWS:
        for line in (HERE / "runs" / f"e2-y{yaw}-d1" / "episodes.jsonl").read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            npz = np.load(HERE / "runs" / f"e2-y{yaw}-d1-physics" / f"{row['seed']}.npz",
                          allow_pickle=True)
            t = npz["time"]
            q5 = npz["q"][:, 5]
            xyz = npz["xyz"]
            if xyz.dtype == object:
                xyz = np.array([v if v is not None else np.full(3, np.nan) for v in xyz.tolist()], float)
            window = (t >= 2.6) & (t <= 4.4)
            start = xyz[np.argmin(np.abs(t - 0.2))]
            end = xyz[np.argmin(np.abs(t - 4.4))]
            rows.append({
                "yaw_deg": yaw,
                "seed": row["seed"],
                "success": bool(row["task_success"]),
                "q5_min": float(q5[window].min()),
                "stop_gap_mm": float(GAP_MM(q5[window].min())),
                "max_object_z_m": float(np.nanmax(xyz[:, 2])),
                "xy_displacement_mm": float(np.linalg.norm(end[:2] - start[:2]) * 1000),
                "failure_reason": row["failure_reason"],
            })

    per_yaw = {}
    for yaw in YAWS:
        group = [r for r in rows if r["yaw_deg"] == yaw]
        lifted = [r for r in group if r["max_object_z_m"] > LIFT_Z]
        # Stage split is by the objective z read-out, not by a fitted closure threshold:
        # seed 12862 (yaw 5 deg) succeeds with q5_min = 0.1547, i.e. below the 0.160 that
        # nominal episodes show, so any q5 cut near there mislabels it as "never held".
        closed = lifted
        per_yaw[str(yaw)] = {
            "n": len(group),
            "successes": sum(r["success"] for r in group),
            "w_eff_mm": w_eff(yaw),
            "stop_gap_mm_median": float(np.median([r["stop_gap_mm"] for r in group])),
            "stop_gap_mm_median_when_lifted": (
                float(np.median([r["stop_gap_mm"] for r in lifted])) if lifted else None),
            "lifted": len(lifted),
            "successes_given_lift": sum(r["success"] for r in lifted),
            "never_lifted": len(group) - len(lifted),
        }

    trend = stats.linregress([w_eff(y) for y in YAWS],
                             [per_yaw[str(y)]["stop_gap_mm_median_when_lifted"] for y in YAWS])
    lifted_stops = [r["q5_min"] for r in rows if r["max_object_z_m"] > LIFT_Z]
    dropped_stops = [r["q5_min"] for r in rows if r["max_object_z_m"] <= LIFT_Z]
    y0_lift = per_yaw["0"]["successes_given_lift"], per_yaw["0"]["lifted"]
    y15_lift = per_yaw["15"]["successes_given_lift"], per_yaw["15"]["lifted"]
    placement = stats.fisher_exact([[y0_lift[0], y0_lift[1] - y0_lift[0]],
                                    [y15_lift[0], y15_lift[1] - y15_lift[0]]])

    out = {
        "note": "post-hoc mechanism supplement; not a preregistered endpoint",
        "yaw": per_yaw,
        "stop_gap_vs_w_eff": {"slope_mm_per_mm": float(trend.slope),
                              "r2": float(trend.rvalue ** 2)},
        "closure_depth_by_stage": {"lifted_q5_range": [float(min(lifted_stops)), float(max(lifted_stops))],
                                   "never_lifted_q5_range": [float(min(dropped_stops)), float(max(dropped_stops))]},
        "placement_given_lift_y0_vs_y15": {
            "y0": f"{y0_lift[0]}/{y0_lift[1]}", "y15": f"{y15_lift[0]}/{y15_lift[1]}",
            "fisher_one_sided_p": float(placement[1])},
        "episodes": rows,
    }
    (HERE / "mechanism.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"{'yaw':>4} {'W_eff':>6} {'stop_gap':>9} {'lifted':>6} {'succ|lift':>9} {'dropped':>7}")
    for yaw in YAWS:
        d = per_yaw[str(yaw)]
        print(f"{yaw:>4} {d['w_eff_mm']:>6.2f} {d['stop_gap_mm_median_when_lifted']:>9.2f} "
              f"{d['lifted']:>6} {d['successes_given_lift']:>9} {d['never_lifted']:>7}")
    print(f"stop gap vs W_eff: slope={trend.slope:.2f} R2={trend.rvalue ** 2:.2f}")
    print(f"q5 by stage: lifted {min(lifted_stops):.3f}-{max(lifted_stops):.3f}, "
          f"never lifted {min(dropped_stops):.3f}-{max(dropped_stops):.3f}")
    print(f"placement given lift y0 {y0_lift[0]}/{y0_lift[1]} vs y15 {y15_lift[0]}/{y15_lift[1]}: "
          f"fisher p={placement[1]:.3g}")


if __name__ == "__main__":
    main()
