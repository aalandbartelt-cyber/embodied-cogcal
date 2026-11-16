"""Analyze the E2 yaw sweep (PREREG.md v2): P1-P4 and the frozen decision rule.

Reads runs/e2-y{0,2,5,10,15}-d1/episodes.jsonl. Writes analysis.json and prints a
summary table. No episode is dropped.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import optimize, stats

HERE = Path(__file__).resolve().parent
YAWS = (0, 2, 5, 10, 15)
WEIGHTS = np.array(YAWS, dtype=float)
E1P_RATE = (37, 40)  # E1' bins b1+b2 pooled: 18+19 successes of 20+20


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def newcombe(k1: int, n1: int, k2: int, n2: int) -> tuple[float, float]:
    """Newcombe hybrid-score interval for p1 - p2 (method 10, no continuity fix)."""
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    d = p1 - p2
    lo = d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return (lo, hi)


def paired_bootstrap(success: dict[int, dict[int, bool]], a: int, b: int,
                     draws: int = 10_000, seed: int = 20261118) -> tuple[float, float]:
    seeds = sorted(success[a])
    xa = np.array([success[a][s] for s in seeds], dtype=float)
    xb = np.array([success[b][s] for s in seeds], dtype=float)
    rng = np.random.default_rng(seed)
    diffs = np.empty(draws)
    n = len(seeds)
    for i in range(draws):
        idx = rng.integers(0, n, n)
        diffs[i] = xa[idx].mean() - xb[idx].mean()
    return (float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5)))


def cochran_armitage(counts: np.ndarray, n: np.ndarray, weights: np.ndarray) -> tuple[float, float]:
    """One-sided CA trend z and p for a decreasing trend (negative z favours decay)."""
    total_n = n.sum()
    total_x = counts.sum()
    p_hat = total_x / total_n
    num = np.sum(weights * (counts - n * p_hat))
    var = p_hat * (1 - p_hat) * (np.sum(n * weights ** 2) - np.sum(n * weights) ** 2 / total_n)
    z = num / math.sqrt(var)
    return float(z), float(stats.norm.sf(-z))  # H1: decreasing -> z negative -> p small


def logistic_fit(yaw: np.ndarray, counts: np.ndarray, n: np.ndarray) -> dict | None:
    """Binomial logistic regression p(yaw) = sigmoid(a + b*yaw), b < 0 allowed."""
    def nll(params):
        a, b = params
        eta = a + b * yaw
        p = 1.0 / (1.0 + np.exp(-eta))
        p = np.clip(p, 1e-9, 1 - 1e-9)
        return -np.sum(counts * np.log(p) + (n - counts) * np.log1p(-p))

    best = None
    for a0 in (-4.0, -2.0, 0.0, 2.0, 4.0):
        for b0 in (-1.0, -0.2, 0.0, 0.2):
            res = optimize.minimize(nll, x0=[a0, b0], method="Nelder-Mead",
                                          options={"maxiter": 4000, "xatol": 1e-8})
            if res.success and (best is None or res.fun < best.fun):
                best = res
    if best is None:
        return None
    a, b = (float(v) for v in best.x)
    yaw50 = -a / b if b != 0 else float("inf")
    return {"intercept": a, "slope_per_deg": b, "yaw50_deg": yaw50,
            "neg_log_likelihood": float(best.fun)}


def main() -> None:
    success: dict[int, dict[int, bool]] = {}
    counts: dict[int, int] = {}
    ns: dict[int, int] = {}
    for yaw in YAWS:
        path = HERE / "runs" / f"e2-y{yaw}-d1" / "episodes.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        success[yaw] = {int(r["seed"]): bool(r["task_success"]) for r in rows}
        counts[yaw] = sum(success[yaw].values())
        ns[yaw] = len(rows)

    rates = {y: counts[y] / ns[y] for y in YAWS}
    p1_k, p1_n = counts[0], ns[0]
    p15_k, p15_n = counts[15], ns[15]
    table = [[p1_k, p1_n - p1_k], [p15_k, p15_n - p15_k]]
    fisher_p = float(stats.fisher_exact(table, alternative="greater")[1])
    diff = rates[0] - rates[15]
    ci = newcombe(p1_k, p1_n, p15_k, p15_n)
    boot = paired_bootstrap(success, 0, 15)

    z, p_trend = cochran_armitage(np.array([counts[y] for y in YAWS]),
                                  np.array([ns[y] for y in YAWS]), WEIGHTS)

    fit = logistic_fit(np.array(YAWS, float),
                       np.array([counts[y] for y in YAWS], float),
                       np.array([ns[y] for y in YAWS], float))

    p4_k, p4_n = E1P_RATE
    p4 = float(stats.fisher_exact([[p15_k, p15_n - p15_k], [p4_k, p4_n - p4_k]],
                                  alternative="less")[1])

    if diff >= 0.5 and fisher_p < 0.05 and p_trend < 0.10:
        verdict = "COLLAPSE"
    elif rates[15] >= 0.70:
        verdict = "COLLINEAR"
    else:
        verdict = "INCONCLUSIVE"

    out = {
        "prereg": "PREREG.md (v2 yaw sweep)",
        "yaws_deg": list(YAWS),
        "per_condition": {str(y): {"successes": counts[y], "episodes": ns[y],
                                   "rate": rates[y], "wilson95": wilson(counts[y], ns[y])}
                          for y in YAWS},
        "P1": {"diff": diff, "fisher_one_sided_p": fisher_p,
               "newcombe95": ci, "paired_bootstrap95": boot,
               "table": table},
        "P2": {"ca_z": z, "ca_one_sided_p": p_trend, "weights": WEIGHTS.tolist()},
        "P3": {"logistic": fit},
        "P4": {"yaw15_vs_e1p_b1b2": {"yaw15_rate": rates[15],
                                      "e1p_rate": p4_k / p4_n,
                                      "fisher_one_sided_p": p4}},
        "decision": verdict,
    }
    (HERE / "analysis.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"{'yaw':>4} {'succ':>5} {'n':>3} {'rate':>6}  wilson95")
    for y in YAWS:
        lo, hi = wilson(counts[y], ns[y])
        print(f"{y:>4} {counts[y]:>5} {ns[y]:>3} {rates[y]:>6.2f}  [{lo:.2f}, {hi:.2f}]")
    print(f"P1 diff(0-15)={diff:+.3f} fisher_p={fisher_p:.3g} newcombe={ci} boot={boot}")
    print(f"P2 CA z={z:.3f} p={p_trend:.3g}")
    if fit:
        print(f"P3 yaw50={fit['yaw50_deg']:.2f} deg slope={fit['slope_per_deg']:.3f}")
    print(f"P4 yaw15 vs E1' b1+b2 p={p4:.3g}")
    print(f"DECISION: {verdict}")


if __name__ == "__main__":
    main()
