"""E3b analysis: theta*(delta) on five reach-safe offsets.

Reads E3's delta in {2,8} cells (tag e3) and E3b's delta in {4,6,10} cells
(tag e3b), all on seeds 12920-12939, and runs the registered estimators:
per-cell rates + Wilson, theta*(delta) with E3's interpolation, 5-point OLS
slope, cluster bootstrap over the shared seed indices, GEE interaction, stage
decomposition. Writes analysis_e3b.json.

Registered decision (PREREG_E3B.md section 3):
  SHRINK iff slope<0 and CI upper<0; FLAT iff CI inside +/- 0.1667 deg/mm;
  otherwise INCONCLUSIVE.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats

import analyze_e3 as e3

HERE = Path(__file__).resolve().parent
YAWS = (0, 5, 10, 15)
DELTAS = (2, 4, 6, 8, 10)  # 2 and 8 from E3, 4/6/10 from E3b
SEEDS = list(range(12920, 12940))
FLAT_EDGE = 2.0 / 12.0  # deg/mm, PREREG_E3B.md section 3
N_BOOT = 10000
RNG = np.random.default_rng(20261117)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cells() -> dict[tuple[int, int], list[dict]]:
    cells: dict[tuple[int, int], list[dict]] = {}
    for delta in DELTAS:
        tag = "e3" if delta in (2, 8) else "e3b"
        for yaw in YAWS:
            run = HERE / "runs" / f"{tag}-y{yaw}-d{delta}"
            rows = [json.loads(line) for line in
                    (run / "episodes.jsonl").read_text().splitlines() if line.strip()]
            assert len(rows) == 20, f"{run}: {len(rows)} rows"
            seeds = sorted(int(r["seed"]) for r in rows)
            assert seeds == SEEDS, f"{run}: seed set mismatch"
            contract = json.loads((run / "contract.json").read_text())
            assert contract["tag"] == tag, f"{run}: tag {contract['tag']} != {tag}"
            assert contract["yaw_deg"] == yaw and contract["delta_mm"] == delta, run
            prefer = sha(HERE / ("PREREG.md" if tag == "e3" else "PREREG_E3B.md"))
            assert contract["prereg_sha256"] == prefer, f"{run}: prereg hash drift"
            by_seed = {int(r["seed"]): r for r in rows}
            cells[(yaw, delta)] = [by_seed[s] for s in SEEDS]
    return cells


def rates_from(cells: dict[tuple[int, int], list[dict]], idx: list[int]) -> dict[tuple[int, int], float]:
    out = {}
    for (yaw, delta), rows in cells.items():
        out[(yaw, delta)] = sum(bool(rows[i]["task_success"]) for i in idx) / len(idx)
    return out


def theta_star_column(cells, delta: int, idx: list[int]) -> float | None:
    rates = {yaw: sum(bool(cells[(yaw, delta)][i]["task_success"]) for i in idx) / len(idx)
             for yaw in YAWS}
    if rates[0] < 0.5 or rates[15] >= 0.5:
        return None
    return e3.theta_star(rates)


def stage_counts(cells, yaw: int, delta: int) -> dict:
    rows = cells[(yaw, delta)]
    return {
        "n": len(rows),
        "lifted": sum(r["longest_two_finger_lift_s"] >= 0.5 for r in rows),
        "placed": sum(bool(r["placed"]) for r in rows),
        "released": sum(bool(r["released"]) for r in rows),
        "success": sum(bool(r["task_success"]) for r in rows),
        "failure_reasons": {
            reason: sum(r["failure_reason"] == reason for r in rows)
            for reason in sorted({r["failure_reason"] for r in rows} - {None})
        },
    }


def main() -> int:
    cells = load_cells()
    n = len(SEEDS)
    all_idx = list(range(n))

    # ---- rates ----
    rates = {}
    for (yaw, delta), rows in sorted(cells.items()):
        k = sum(bool(r["task_success"]) for r in rows)
        rates[f"{yaw}-{delta}"] = {
            "yaw_deg": yaw, "delta_mm": delta, "k": k, "n": len(rows),
            "rate": k / len(rows), "wilson95": e3.wilson(k, len(rows)),
        }

    # ---- theta* and slope ----
    theta_hat: dict[int, float | None] = {}
    for delta in DELTAS:
        theta_hat[delta] = theta_star_column(cells, delta, all_idx)
    usable = [d for d in DELTAS if theta_hat[d] is not None]
    slope = e3.ols_slope([d for d in usable], [theta_hat[d] for d in usable])

    # ---- joint cluster bootstrap over the 20 shared seed indices ----
    boot = []
    skipped = 0
    attempts = 0
    while len(boot) < N_BOOT and attempts < 4 * N_BOOT:
        attempts += 1
        idx = list(RNG.integers(0, n, size=n))
        ts = {d: theta_star_column(cells, d, idx) for d in DELTAS}
        if any(v is None for v in ts.values()):
            skipped += 1
            continue
        boot.append(e3.ols_slope(list(DELTAS), [ts[d] for d in DELTAS]))
    boot_s = np.asarray(boot)
    ci = (float(np.percentile(boot_s, 2.5)), float(np.percentile(boot_s, 97.5)))
    theta_ci = {}
    for delta in DELTAS:
        samples = []
        for _ in range(2000):
            idx = list(RNG.integers(0, n, size=n))
            v = theta_star_column(cells, delta, idx)
            if v is not None:
                samples.append(v)
        theta_ci[delta] = (float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5)))

    # ---- GEE over pooled 20 cells (400 obs) ----
    X, y, groups = [], [], []
    for si, _seed in enumerate(SEEDS):
        for yaw in YAWS:
            for delta in DELTAS:
                row = cells[(yaw, delta)][si]
                X.append([1.0, (yaw - 7.5) / 7.5, (delta - 6.0) / 4.0,
                          ((yaw - 7.5) / 7.5) * ((delta - 6.0) / 4.0)])
                y.append(bool(row["task_success"]))
                groups.append(si)
    gee = e3.gee_exchangeable(np.asarray(X, float), np.asarray(y, float), np.asarray(groups))
    beta = np.asarray(gee["beta"])
    se = np.sqrt(np.diag(np.asarray(gee["cov"])))
    z = beta / se
    gee_summary = {
        "terms": ["intercept", "theta", "delta", "theta:delta"],
        "beta": beta.tolist(), "robust_se": se.tolist(), "z": z.tolist(),
        "interaction_one_sided_p_less": float(stats.norm.cdf(z[3])),
        "interaction_one_sided_p_greater": float(stats.norm.sf(z[3])),
        "alpha": gee["alpha"],
    }

    # ---- stages ----
    stages = {f"{yaw}-{delta}": stage_counts(cells, yaw, delta)
              for yaw in YAWS for delta in DELTAS}

    # ---- controls / monotonicity ----
    controls = {f"0-{delta}": rates[f"0-{delta}"]["rate"] for delta in DELTAS}
    reach_control = {
        "cell": "0-10", "rate": controls["0-10"],
        "status": ("contaminated" if controls["0-10"] < 0.60
                   else "caveat" if controls["0-10"] < 0.75 else "ok"),
    }
    y15_alarm = {f"15-{delta}": rates[f"15-{delta}"]["rate"] for delta in DELTAS}
    mono_flags = []
    for delta in DELTAS:
        for a, b in zip(YAWS, YAWS[1:]):
            rise = rates[f"{b}-{delta}"]["rate"] - rates[f"{a}-{delta}"]["rate"]
            if rise >= 5 / 20:
                mono_flags.append({"delta": delta, "from": a, "to": b, "rise": rise})

    # ---- decision ----
    lo, hi = ci
    if slope < 0 and hi < 0:
        decision = "SHRINK"
    elif -FLAT_EDGE < lo and hi < FLAT_EDGE:
        decision = "FLAT"
    else:
        decision = "INCONCLUSIVE"
    prediction = {
        "registered": "not SHRINK and |point slope| < 0.15 deg/mm",
        "shrinks_supported": slope < 0 and hi < 0,
        "point_within_0.15": abs(slope) < 0.15,
    }
    prediction["met"] = (not prediction["shrinks_supported"]) and prediction["point_within_0.15"]

    result = {
        "prereg": "PREREG_E3B.md",
        "design": {"yaws": list(YAWS), "deltas": list(DELTAS), "seeds": SEEDS,
                   "cells": len(cells), "episodes": len(SEEDS) * len(cells)},
        "rates": rates,
        "theta_star_deg": {str(d): theta_hat[d] for d in DELTAS},
        "theta_star_ci95": {str(d): theta_ci[d] for d in DELTAS},
        "slope_deg_per_mm": slope,
        "slope_ci95": ci,
        "bootstrap": {"n": len(boot_s), "skipped_censored": skipped,
                      "attempts": attempts,
                      "samples_summary": {"mean": float(boot_s.mean()),
                                          "sd": float(boot_s.std(ddof=1))}},
        "decision": decision,
        "flat_threshold_deg_per_mm": FLAT_EDGE,
        "prediction": prediction,
        "controls": controls,
        "reach_control": reach_control,
        "yaw15_alarm": y15_alarm,
        "monotonicity_flags": mono_flags,
        "gee": gee_summary,
        "stages": stages,
    }
    (HERE / "analysis_e3b.json").write_text(json.dumps(result, indent=2) + "\n")

    # ---- report ----
    print(f"cells: {len(cells)}  episodes: {len(SEEDS) * len(cells)}")
    print("rate table (yaw x delta):")
    for yaw in YAWS:
        print("  " + "  ".join(f"d{d}:{rates[f'{yaw}-{d}']['k']}/20={rates[f'{yaw}-{d}']['rate']:.2f}"
                               for d in DELTAS))
    print("\ntheta* (deg):", {d: (None if theta_hat[d] is None else round(theta_hat[d], 3)) for d in DELTAS})
    print("theta* ci95    :", {d: tuple(round(v, 2) for v in theta_ci[d]) for d in DELTAS})
    print(f"slope = {slope:.4f} deg/mm  CI95 [{lo:.4f}, {hi:.4f}] "
          f"(boot n={len(boot_s)}, skipped={skipped}/{attempts})")
    print(f"decision = {decision}  (FLAT edge {FLAT_EDGE:.4f})  prediction met={prediction['met']}")
    print("controls:", {k: round(v, 3) for k, v in controls.items()},
          " reach_control:", reach_control["status"])
    print("(15,*):", {k: round(v, 3) for k, v in y15_alarm.items()})
    print("GEE:", {t: round(b, 3) for t, b in zip(gee_summary["terms"], gee_summary["beta"])},
          "p(interaction<0):", f"{gee_summary['interaction_one_sided_p_less']:.3g}",
          "p(greater):", f"{gee_summary['interaction_one_sided_p_greater']:.3g}")
    print("stages (lift/placed/released/success, P(success|lift)):")
    for yaw in YAWS:
        for delta in DELTAS:
            s = stages[f"{yaw}-{delta}"]
            p = f"{s['success'] / s['lifted']:.2f}" if s["lifted"] else "-"
            print(f"  {yaw}-{delta}: {s['lifted']:2d} {s['placed']:2d} {s['released']:2d} "
                  f"{s['success']:2d} | {p} {s['failure_reasons']}")
    if mono_flags:
        print("monotonicity flags:", mono_flags)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
