#!/usr/bin/env python3
"""E3b post-hoc sensitivity (NOT preregistered; reported separately).

Two questions raised by the E3b primary endpoint:

1. The registered 5-point slope mixes in delta=10, whose 10-deg cells are the
   lowest in the reach-safe set.  What is the slope over delta in {2,4,6,8}?
2. The E3 secondary GEE interaction was positive (+0.458 under its own
   centering); E3b's is negative.  Does the sign depend on the reach-limited
   delta=14 column?  Refit with one common centering so coefficients are
   comparable across delta windows.

Nothing here changes PREREG_E3B.md decisions; it is labelled post-hoc in
RESULTS_E3B.md. Run with the sim env python.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze_e3 as e3  # noqa: E402

SEEDS = list(range(12920, 12940))
YAWS = (0, 5, 10, 15)
RNG = np.random.default_rng(20261118 + 7)
N_BOOT = 10_000


def load_cell(tag: str, yaw: int, delta: int) -> dict[int, dict]:
    run = HERE / "runs" / f"{tag}-y{yaw}-d{delta}"
    rows = [json.loads(line) for line in
            (run / "episodes.jsonl").read_text().splitlines() if line.strip()]
    return {int(row["seed"]): row for row in rows}


def cells_for(deltas: list[int]) -> dict[tuple[int, int], dict[int, dict]]:
    return {(yaw, delta): load_cell("e3" if delta in (2, 8, 14) else "e3b", yaw, delta)
            for delta in deltas for yaw in YAWS}


def rates(cells, deltas, idx) -> dict[tuple[int, int], float]:
    return {(yaw, delta): sum(bool(cells[(yaw, delta)][SEEDS[i]]["task_success"])
                              for i in idx) / len(idx)
            for delta in deltas for yaw in YAWS}


def theta_hat(rates_by_cell, delta: int):
    col = {yaw: rates_by_cell[(yaw, delta)] for yaw in YAWS}
    if col[0] < 0.5 or col[15] >= 0.5:
        return None
    return e3.theta_star(col)


def slope_report(deltas: list[int]) -> None:
    cells = cells_for(deltas)
    point = rates(cells, deltas, list(range(len(SEEDS))))
    thetas = [theta_hat(point, d) for d in deltas]
    slope = e3.ols_slope(deltas, thetas)
    boots = []
    while len(boots) < N_BOOT:
        idx = list(RNG.integers(0, len(SEEDS), size=len(SEEDS)))
        rates_b = rates(cells, deltas, idx)
        ts = [theta_hat(rates_b, d) for d in deltas]
        if any(t is None for t in ts):
            continue
        boots.append(e3.ols_slope(deltas, ts))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    print(f"slope over delta={deltas}: s={slope:+.4f} deg/mm "
          f"CI95=[{lo:+.4f}, {hi:+.4f}] boot n={len(boots)} "
          f"theta*={[round(t, 3) for t in thetas]}")


def gee_report(deltas: list[int]) -> None:
    cells = cells_for(deltas)
    X, y, groups = [], [], []
    for delta in deltas:
        for yaw in YAWS:
            for i, seed in enumerate(SEEDS):
                theta_c = (yaw - 7.5) / 7.5
                delta_c = (delta - 6.0) / 4.0          # common centering here
                X.append([1.0, theta_c, delta_c, theta_c * delta_c])
                y.append(float(bool(cells[(yaw, delta)][seed]["task_success"])))
                groups.append(i)
    fit = e3.gee_exchangeable(np.asarray(X, float), np.asarray(y, float),
                              np.asarray(groups))
    beta = np.asarray(fit["beta"])
    se = np.sqrt(np.diag(np.asarray(fit["cov"])))
    z_int = float(beta[3] / se[3])
    p_less = 0.5 * math.erfc(-z_int / math.sqrt(2))  # P(interaction < 0)
    print(f"GEE delta={deltas}: n={len(y)} beta={[round(float(b), 3) for b in beta]} "
          f"se={[round(float(s), 3) for s in se]} z_int={z_int:+.2f} "
          f"p(int<0)={p_less:.3g} alpha={fit['alpha']:.3f}")


def main() -> int:
    print("post-hoc sensitivity (not preregistered)")
    slope_report([2, 4, 6, 8, 10])
    slope_report([2, 4, 6, 8])
    gee_report([2, 8])
    gee_report([2, 8, 14])
    gee_report([4, 6, 10])
    gee_report([2, 4, 6, 8, 10])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
