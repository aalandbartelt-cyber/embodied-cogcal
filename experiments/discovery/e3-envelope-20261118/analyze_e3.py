"""Analyze E3 (PREREG.md): 12-cell rates, boundary theta*(delta), slope with
cluster bootstrap, cluster-robust (GEE exchangeable) logistic interaction, and
the stage decomposition.

Reads runs/e3-y{yaw}-d{delta}/episodes.jsonl. Writes analysis.json and prints
the tables quoted in RESULTS.md. No episode is dropped. E2/E1' anchors are
copied from their committed documents, never re-run or pooled.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
YAWS = (0, 5, 10, 15)
DELTAS = (2, 8, 14)
SEED_START, SEED_COUNT = 12920, 20
N_BOOT = 10_000
RNG_SEED = 20261118
LIFT_THRESHOLD_S = 0.5

# Committed anchors (quoted, not re-run).
E2_D1 = {0: 19, 2: 18, 5: 18, 10: 14, 15: 1}            # E2 RESULTS.md, delta ~ U(0.5,1.5), seeds 12850-12869
E1P_B0 = (18, 20)                                         # E1' bin b0 (median 1.12 mm), E1P_RESULT.md
E1P_B02 = (55, 60)                                        # b0+b1+b2 pooled (1.12/4.67/7.55 mm)
E1P_B4 = (16, 20)                                         # b4 (13.8 mm)
E1P_B5 = (8, 20)                                          # b5 (17.2 mm)


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def theta_star(rates: dict[int, float]) -> float | None:
    """Linear interpolation of the 0.5 crossing between the largest theta with
    p_hat >= 0.5 and its successor; None when censored (PREREG section 4)."""
    ths = sorted(rates)
    above = [t for t in ths if rates[t] >= 0.5]
    if not above:
        return None
    lo = max(above)
    i = ths.index(lo)
    if i == len(ths) - 1:
        return None
    hi = ths[i + 1]
    p_lo, p_hi = rates[lo], rates[hi]
    return lo + (p_lo - 0.5) / (p_lo - p_hi) * (hi - lo)


def ols_slope(xs: list[float], ys: list[float]) -> float:
    x = np.asarray(xs, float)
    y = np.asarray(ys, float)
    return float(((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum())


def gee_exchangeable(X: np.ndarray, y: np.ndarray, groups: np.ndarray, max_iter: int = 300,
                     tol: float = 1e-10) -> dict | None:
    """Logistic GEE with exchangeable within-cluster working correlation.

    Seeds are clusters (12 paired cells each). Estimating equations use the
    canonical D = A X form: U = sum_g X' A V^-1 (y - mu), bread = sum_g X' A
    V^-1 A X. Returns beta, cluster-robust sandwich covariance and alpha.
    """
    n, p = X.shape
    _, inv = np.unique(groups, return_inverse=True)
    n_clusters = int(inv.max()) + 1
    beta = np.zeros(p)
    beta[0] = math.log(y.mean() / (1 - y.mean()))

    def blocks(beta: np.ndarray, alpha: float):
        mu = 1.0 / (1.0 + np.exp(-(X @ beta)))
        v = mu * (1.0 - mu)
        out = []
        for g in range(n_clusters):
            idx = np.where(inv == g)[0]
            m = idx.size
            R = np.full((m, m), alpha)
            np.fill_diagonal(R, 1.0)
            A = np.diag(np.sqrt(v[idx]))
            V = A @ R @ A
            out.append((idx, X[idx], A, np.linalg.inv(V), mu[idx]))
        return mu, v, out

    def alpha_hat(mu: np.ndarray, v: np.ndarray) -> float:
        z = (y - mu) / np.sqrt(v)
        num = 0.0
        den = 0.0
        for g in range(n_clusters):
            zg = z[inv == g]
            m = zg.size
            num += zg.sum() ** 2 - (zg ** 2).sum()
            den += m * (m - 1)
        return float(num / den) if den else 0.0

    alpha = 0.0
    for _ in range(max_iter):
        mu, v, blk = blocks(beta, alpha)
        alpha = alpha_hat(mu, v)
        mu, v, blk = blocks(beta, alpha)
        bread = np.zeros((p, p))
        score = np.zeros(p)
        for idx, Xg, A, Vinv, mug in blk:
            DtV = (A @ Xg).T @ Vinv
            bread += DtV @ (A @ Xg)
            score += DtV @ (y[idx] - mug)
        step = np.linalg.solve(bread, score)
        beta = beta + step
        if np.max(np.abs(step)) < tol:
            break
    mu, v, blk = blocks(beta, alpha)
    bread = np.zeros((p, p))
    meat = np.zeros((p, p))
    for idx, Xg, A, Vinv, mug in blk:
        D = A @ Xg
        DtV = D.T @ Vinv
        bread += DtV @ D
        s = DtV @ (y[idx] - mug)
        meat += np.outer(s, s)
    bread_inv = np.linalg.inv(bread)
    return {"beta": beta.tolist(), "cov": (bread_inv @ meat @ bread_inv).tolist(),
            "alpha": alpha}


def main() -> int:
    rows: list[dict] = []
    for yaw in YAWS:
        for delta in DELTAS:
            run = HERE / "runs" / f"e3-y{yaw}-d{delta}" / "episodes.jsonl"
            rows.extend(json.loads(line) for line in run.read_text().splitlines() if line.strip())
    assert len(rows) == len(YAWS) * len(DELTAS) * SEED_COUNT, len(rows)

    by_cell: dict[tuple[int, int], list[dict]] = {}
    for row in rows:
        by_cell.setdefault((int(row["yaw_deg"]), int(row["delta_mm"])), []).append(row)
    success = {(y, d): np.array([bool(r["task_success"]) for r in sorted(by_cell[(y, d)], key=lambda r: r["seed"])])
               for y in YAWS for d in DELTAS}
    cells = []
    rates_by_delta = {}
    for yaw in YAWS:
        for delta in DELTAS:
            s = success[(yaw, delta)]
            k, n = int(s.sum()), int(s.size)
            lo, hi = wilson(k, n)
            cells.append({"yaw_deg": yaw, "delta_mm": delta, "k": k, "n": n,
                          "rate": k / n, "wilson95": [lo, hi]})
            rates_by_delta.setdefault(delta, {})[yaw] = k / n

    thetas = {delta: theta_star(rates_by_delta[delta]) for delta in DELTAS}
    slope = None
    if all(v is not None for v in thetas.values()):
        slope = ols_slope(list(DELTAS), [thetas[d] for d in DELTAS])

    # Cluster bootstrap over the 20 paired seed indices, all cells jointly.
    rng = np.random.default_rng(RNG_SEED)
    null_boot = np.vstack([success[(y, d)] for y in YAWS for d in DELTAS])
    boot = []
    boot_theta = {d: [] for d in DELTAS}
    boot_28 = []
    skipped = 0
    for _ in range(N_BOOT):
        idx = rng.integers(0, SEED_COUNT, SEED_COUNT)
        drawn = null_boot[:, idx].mean(axis=1).reshape(len(YAWS), len(DELTAS))
        th = {d: theta_star({y: float(drawn[i, j]) for i, y in enumerate(YAWS)})
              for j, d in enumerate(DELTAS)}
        for d in DELTAS:
            if th[d] is not None:
                boot_theta[d].append(th[d])
        if any(v is None for v in th.values()):
            skipped += 1
            continue
        boot.append(ols_slope(list(DELTAS), [th[d] for d in DELTAS]))
        # Post-hoc, two-point slope over the reach-safe columns (delta in {2, 8}).
        boot_28.append((th[DELTAS[1]] - th[DELTAS[0]]) / (DELTAS[1] - DELTAS[0]))
    boot_arr = np.asarray(boot)
    boot_ci = [float(np.percentile(boot_arr, 2.5)), float(np.percentile(boot_arr, 97.5))]
    boot_theta_ci = {str(d): {"ci95": [float(np.percentile(np.asarray(boot_theta[d]), 2.5)),
                                      float(np.percentile(np.asarray(boot_theta[d]), 97.5))],
                             "n": len(boot_theta[d])} for d in DELTAS}
    slope_28 = (thetas[DELTAS[1]] - thetas[DELTAS[0]]) / (DELTAS[1] - DELTAS[0])
    slope_28_ci = ([float(np.percentile(np.asarray(boot_28), 2.5)),
                    float(np.percentile(np.asarray(boot_28), 97.5))] if boot_28 else None)

    # Secondary: cluster-robust logistic interaction (GEE exchangeable, seed clusters).
    theta_c = np.array([(int(r["yaw_deg"]) - 7.5) / 7.5 for r in rows])
    delta_c = np.array([(int(r["delta_mm"]) - 8.0) / 6.0 for r in rows])
    y = np.array([bool(r["task_success"]) for r in rows], float)
    X = np.column_stack([np.ones_like(theta_c), theta_c, delta_c, theta_c * delta_c])
    groups = np.array([int(r["seed"]) for r in rows])
    gee = gee_exchangeable(X, y, groups)
    if gee is not None:
        beta = np.asarray(gee["beta"])
        se = np.sqrt(np.diag(np.asarray(gee["cov"])))
        z = beta / se
        # Pre-registered direction is interaction < 0, so the one-sided p for
        # that hypothesis is Phi(z); sf(z) is the p for interaction > 0.
        p_less = float(stats.norm.cdf(z[3]))
        p_greater = float(stats.norm.sf(z[3]))
        gee = {"terms": ["intercept", "theta", "delta", "theta:delta"], "beta": beta.tolist(),
               "robust_se": se.tolist(), "z": z.tolist(),
               "interaction_one_sided_p_less": p_less,
               "interaction_one_sided_p_greater": p_greater,
               "alpha": gee["alpha"]}

    # Stage decomposition.
    stage = {}
    for yaw in YAWS:
        for delta in DELTAS:
            rs = sorted(by_cell[(yaw, delta)], key=lambda r: r["seed"])
            lift = [r["longest_two_finger_lift_s"] >= LIFT_THRESHOLD_S for r in rs]
            placed = [bool(r["placed"]) for r in rs]
            released = [bool(r["released"]) for r in rs]
            ok = [bool(r["task_success"]) for r in rs]
            reasons = Counter(r["failure_reason"] for r in rs if r["failure_reason"])
            stage[f"{yaw}-{delta}"] = {
                "lifted": int(sum(lift)), "placed": int(sum(placed)), "released": int(sum(released)),
                "successes": int(sum(ok)),
                "success_given_lift": (sum(1 for l, o in zip(lift, ok) if l and o) / sum(lift)) if sum(lift) else None,
                "failure_reasons": dict(reasons),
            }

    # Per-seed paired pattern (delta-major order: d2 th0..15, d8, d14).
    pattern = Counter()
    for seed in range(SEED_START, SEED_START + SEED_COUNT):
        bits = ""
        for delta in DELTAS:
            for yaw in YAWS:
                r = next(x for x in by_cell[(yaw, delta)] if x["seed"] == seed)
                bits += "1" if r["task_success"] else "0"
        pattern[bits] += 1

    # Anchor comparisons (quoted counts, Fisher exact, two-sided).
    def fisher(k1: int, n1: int, k2: int, n2: int) -> float:
        return float(stats.fisher_exact([[k1, n1 - k1], [k2, n2 - k2]], alternative="two-sided")[1])

    anchors = {
        "e2_y15_vs_e3_15_2": {"e2": [E2_D1[15], 20], "e3": [int(success[(15, 2)].sum()), 20],
                              "p_two_sided": fisher(int(success[(15, 2)].sum()), 20, E2_D1[15], 20)},
        "e1p_b0_vs_e3_0_2": {"e1p": list(E1P_B0), "e3": [int(success[(0, 2)].sum()), 20],
                             "p_two_sided": fisher(int(success[(0, 2)].sum()), 20, *E1P_B0)},
        "e1p_b02_vs_e3_0_2": {"e1p": list(E1P_B02), "e3": [int(success[(0, 2)].sum()), 20],
                              "p_two_sided": fisher(int(success[(0, 2)].sum()), 20, *E1P_B02)},
        "e1p_b4_vs_e3_0_14": {"e1p": list(E1P_B4), "e3": [int(success[(0, 14)].sum()), 20],
                              "p_two_sided": fisher(int(success[(0, 14)].sum()), 20, *E1P_B4)},
        "e1p_b4_b5_note": {"b4": list(E1P_B4), "b5": list(E1P_B5)},
    }

    result = {
        "cells": cells,
        "theta_star_deg": thetas,
        "slope_deg_per_mm": slope,
        "bootstrap": {"n": len(boot), "skipped": skipped, "ci95": boot_ci,
                      "theta_star_ci": boot_theta_ci,
                      "samples": [float(v) for v in boot_arr[:200]]},
        "posthoc_two_point_slope_2_8": {"slope": slope_28, "ci95": slope_28_ci,
                                        "n_boot": len(boot_28)},
        "gee": gee,
        "stages": stage,
        "patterns": dict(pattern),
        "anchors": anchors,
        "n_episodes": len(rows),
    }
    (HERE / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")

    print("cell      k/20  rate  wilson95")
    for c in cells:
        print(f"theta={c['yaw_deg']:>2} d={c['delta_mm']:>2}  {c['k']:>2}/20  {c['rate']:.3f}  "
              f"[{c['wilson95'][0]:.2f}, {c['wilson95'][1]:.2f}]")
    print()
    print("theta* (deg):", thetas)
    print("theta* bootstrap 95% CIs:", {k: [round(a, 2), round(b, 2)] for k, (a, b) in
                                         ((d, v["ci95"]) for d, v in boot_theta_ci.items())})
    print(f"slope: {slope if slope is None else round(slope, 4)} deg/mm; "
          f"bootstrap 95% CI {boot_ci[0]:.3f}..{boot_ci[1]:.3f} (skipped {skipped}/{N_BOOT})")
    print(f"post-hoc slope over delta in {{{DELTAS[0]}, {DELTAS[1]}}}: {slope_28:.4f} deg/mm"
          + (f"; bootstrap 95% CI {slope_28_ci[0]:.3f}..{slope_28_ci[1]:.3f}" if slope_28_ci else ""))
    if gee is not None:
        print("GEE interaction beta=%.4f (robust SE %.4f, z %.2f; one-sided p(interaction<0)=%.4g, "
              "p(>0)=%.4g; alpha %.3f)"
              % (gee["beta"][3], gee["robust_se"][3], gee["z"][3],
                 gee["interaction_one_sided_p_less"], gee["interaction_one_sided_p_greater"], gee["alpha"]))
    print()
    print("stage (cell: lift placed released success | success|lift)")
    for key, s in stage.items():
        sl = "n/a" if s["success_given_lift"] is None else f"{s['success_given_lift']:.2f}"
        print(f"  {key:>5}: {s['lifted']:>2} {s['placed']:>2} {s['released']:>2} {s['successes']:>2} | {sl}  {s['failure_reasons']}")
    print()
    print("patterns:", dict(pattern))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
