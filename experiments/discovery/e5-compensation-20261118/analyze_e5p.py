#!/usr/bin/env python3
"""Analyse E5': A (theta=15, q5 bias +15) vs B (theta=0, q5 bias +15) and the E2
references. Implements the pre-registered endpoints P1-P6, plus descriptive
cross-checks. Writes analysis_e5p.json and prints a compact report.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E2 = HERE.parent / "e2-size-tolerance-20261118"
SEEDS = list(range(12850, 12870))
RNG = np.random.default_rng(20261117)


def load_episodes(path: Path) -> dict[int, dict]:
    return {r["seed"]: r for r in (json.loads(line) for line in path.read_text().splitlines() if line.strip())}


def fisher_greater(a_succ: int, a_n: int, b_succ: int, b_n: int) -> float:
    from scipy.stats import fisher_exact

    return float(fisher_exact([[a_succ, a_n - a_succ], [b_succ, b_n - b_succ]], alternative="greater")[1])


def fisher_less(a_succ: int, a_n: int, b_succ: int, b_n: int) -> float:
    from scipy.stats import fisher_exact

    return float(fisher_exact([[a_succ, a_n - a_succ], [b_succ, b_n - b_succ]], alternative="less")[1])


def fisher_two(a_succ: int, a_n: int, b_succ: int, b_n: int) -> float:
    from scipy.stats import fisher_exact

    return float(fisher_exact([[a_succ, a_n - a_succ], [b_succ, b_n - b_succ]], alternative="two-sided")[1])


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def paired_bootstrap(a: dict[int, dict], b: dict[int, dict], n_boot: int = 10000) -> dict:
    seeds = np.array(SEEDS)
    av = np.array([bool(a[s]["task_success"]) for s in seeds], dtype=float)
    bv = np.array([bool(b[s]["task_success"]) for s in seeds], dtype=float)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        pick = RNG.integers(0, len(seeds), len(seeds))
        diffs[i] = av[pick].mean() - bv[pick].mean()
    return {
        "n_boot": n_boot,
        "observed_diff": float(av.mean() - bv.mean()),
        "ci95": [float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))],
        "p_diff_le_0": float(np.mean(diffs <= 0.0)),
        "p_diff_ge_0": float(np.mean(diffs >= 0.0)),
    }


def mcnemar_exact(a: dict[int, dict], b: dict[int, dict]) -> dict:
    b01 = sum(1 for s in SEEDS if a[s]["task_success"] and not b[s]["task_success"])
    b10 = sum(1 for s in SEEDS if not a[s]["task_success"] and b[s]["task_success"])
    n = b01 + b10
    # exact two-sided binomial with p=0.5
    if n == 0:
        p = 1.0
    else:
        k = min(b01, b10)
        p = min(1.0, 2.0 * sum(math.comb(n, i) for i in range(0, k + 1)) / (2.0**n))
    return {"a_only": b01, "b_only": b10, "p_two_sided": p}


def paired_interaction(a: dict[int, dict], e15: dict[int, dict], b: dict[int, dict], e0: dict[int, dict], n_boot: int = 10000) -> dict:
    """Difference-in-differences: (A - E2 y15) - (B - E2 y0), resampling seeds."""
    av = np.array([bool(a[s]["task_success"]) for s in SEEDS], dtype=float)
    ev = np.array([bool(e15[s]["task_success"]) for s in SEEDS], dtype=float)
    bv = np.array([bool(b[s]["task_success"]) for s in SEEDS], dtype=float)
    zv = np.array([bool(e0[s]["task_success"]) for s in SEEDS], dtype=float)
    observed = (av.mean() - ev.mean()) - (bv.mean() - zv.mean())
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        pick = RNG.integers(0, len(SEEDS), len(SEEDS))
        diffs[i] = (av[pick].mean() - ev[pick].mean()) - (bv[pick].mean() - zv[pick].mean())
    return {
        "observed": float(observed),
        "ci95": [float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))],
        "p_le_0": float(np.mean(diffs <= 0.0)),
    }


def release_modes(base: Path, rows: dict[int, dict]) -> dict:
    """Classify placed episodes by how the release phase ended (trace q6 + physics contact)."""
    from collections import Counter

    modes = []
    for r in rows.values():
        if not r["placed"]:
            continue
        seed = r["seed"]
        t = [json.loads(line) for line in (base / f"{seed}.trace.jsonl").read_text().splitlines() if line.strip()]
        q6 = np.array([x["q_after_rad"][5] for x in t])
        phys = np.load(base.parent / f"{base.name}-physics/{seed}.npz")
        rc = phys["robot_contact"]
        cs = phys["control_step"]
        last_contact = int(cs[np.where(rc)[0].max()]) if rc.any() else -1
        # release must follow a close: find the first close, then the first re-open
        closes = [i for i in range(40, len(q6)) if q6[i] < 0.24]
        first_close = closes[0] if closes else None
        opens = ([i for i in range(first_close + 1, len(q6)) if q6[i] > 0.24]
                 if first_close is not None else [])
        if first_close is None:
            mode = "never_closed"
        elif not opens:
            mode = "stuck_closed"
        elif last_contact >= len(q6) - 1:
            mode = "contact_at_end"
        elif opens[0] >= 278:
            mode = "late_open"
        else:
            mode = "opened_clean"
        modes.append({"seed": seed, "mode": mode, "first_open": opens[0] if opens else None,
                      "last_contact_control_step": last_contact, "success": r["task_success"]})
    return {"counts": dict(Counter(m["mode"] for m in modes)), "episodes": modes}


def stages(rows: dict[int, dict]) -> dict:
    from collections import Counter

    c = Counter(r["failure_reason"] for r in rows.values())
    return {
        "success": sum(r["task_success"] for r in rows.values()),
        "failure_reason": {k: v for k, v in sorted(c.items(), key=lambda kv: str(kv[0]))},
        "two_finger_lift_run_ge_0.5s": sum(r["longest_two_finger_lift_s"] >= 0.5 for r in rows.values()),
        "placed": sum(r["placed"] for r in rows.values()),
        "released": sum(r["released"] for r in rows.values()),
        "median_held_s_success": float(np.median([r["longest_two_finger_lift_s"] for r in rows.values() if r["task_success"]]))
        if any(r["task_success"] for r in rows.values())
        else 0.0,
        "median_goal_error_mm_success": float(
            np.median([r["goal_error_xy_m"] * 1000 for r in rows.values() if r["task_success"]])
        )
        if any(r["task_success"] for r in rows.values())
        else 0.0,
    }


def main() -> None:
    a = load_episodes(HERE / "runs/e5p-y15-b15/episodes.jsonl")
    b = load_episodes(HERE / "runs/e5p-y0-b15/episodes.jsonl")
    e2_15 = load_episodes(E2 / "runs/e2-y15-d1/episodes.jsonl")
    e2_0 = load_episodes(E2 / "runs/e2-y0-d1/episodes.jsonl")
    verify = json.loads((HERE / "verify_e5p.json").read_text())

    kA, kB, k15, k0 = (sum(r["task_success"] for r in d.values()) for d in (a, b, e2_15, e2_0))
    n = 20
    out: dict = {
        "n_per_arm": n,
        "rates": {
            "A_y15_b15": {"k": kA, "n": n, "rate": kA / n, "wilson95": list(wilson(kA, n))},
            "B_y0_b15": {"k": kB, "n": n, "rate": kB / n, "wilson95": list(wilson(kB, n))},
            "E2_y15_b0": {"k": k15, "n": n, "rate": k15 / n, "wilson95": list(wilson(k15, n))},
            "E2_y0_b0": {"k": k0, "n": n, "rate": k0 / n, "wilson95": list(wilson(k0, n))},
        },
        "tests": {
            "P1_A_vs_E2y15_greater": fisher_greater(kA, n, k15, n),
            "P2_B_vs_E2y0_less": fisher_less(kB, n, k0, n),
            "A_vs_B_greater": fisher_greater(kA, n, kB, n),
            "A_vs_E2y0_two_sided": fisher_two(kA, n, k0, n),
            "B_vs_E2y15_two_sided": fisher_two(kB, n, k15, n),
        },
        "paired": {
            "A_vs_E2y15": paired_bootstrap(a, e2_15),
            "A_vs_E2y0": paired_bootstrap(a, e2_0),
            "B_vs_E2y0": paired_bootstrap(b, e2_0),
            "mcnemar_A_vs_E2y15": mcnemar_exact(a, e2_15),
            "mcnemar_A_vs_E2y0": mcnemar_exact(a, e2_0),
            "mcnemar_B_vs_E2y0": mcnemar_exact(b, e2_0),
            "mcnemar_A_vs_B": mcnemar_exact(a, b),
        },
        "stages": {
            "A_y15_b15": stages(a),
            "B_y0_b15": stages(b),
            "E2_y15_b0": stages(e2_15),
            "E2_y0_b0": stages(e2_0),
        },
        "held_lift": {
            "A": {"k": sum(r["longest_two_finger_lift_s"] >= 0.5 for r in a.values()), "n": n},
            "B": {"k": sum(r["longest_two_finger_lift_s"] >= 0.5 for r in b.values()), "n": n},
            "E2_y15": {"k": sum(r["longest_two_finger_lift_s"] >= 0.5 for r in e2_15.values()), "n": n},
            "E2_y0": {"k": sum(r["longest_two_finger_lift_s"] >= 0.5 for r in e2_0.values()), "n": n},
            "p_A_vs_E2y15": fisher_greater(
                sum(r["longest_two_finger_lift_s"] >= 0.5 for r in a.values()), n,
                sum(r["longest_two_finger_lift_s"] >= 0.5 for r in e2_15.values()), n),
            "p_B_vs_E2y0": fisher_less(
                sum(r["longest_two_finger_lift_s"] >= 0.5 for r in b.values()), n,
                sum(r["longest_two_finger_lift_s"] >= 0.5 for r in e2_0.values()), n),
        },
        "interaction": paired_interaction(a, e2_15, b, e2_0),
        "release_modes": {
            "A": release_modes(HERE / "runs/e5p-y15-b15", a),
            "B": release_modes(HERE / "runs/e5p-y0-b15", b),
            "E2_y15": release_modes(E2 / "runs/e2-y15-d1", e2_15),
            "E2_y0": release_modes(E2 / "runs/e2-y0-d1", e2_0),
        },
        "P5": verify["P5"],
        "P6": verify["P6"],
        "per_seed": [
            {
                "seed": s,
                "delta_mm": a[s]["delta_mm"],
                "A_y15_b15": a[s]["task_success"],
                "B_y0_b15": b[s]["task_success"],
                "E2_y15_b0": e2_15[s]["task_success"],
                "E2_y0_b0": e2_0[s]["task_success"],
                "A_failure": a[s]["failure_reason"],
                "B_failure": b[s]["failure_reason"],
            }
            for s in SEEDS
        ],
    }

    # pre-registered verdict
    p5_ok = verify["P5"]["A"]["ok"]
    if not p5_ok:
        verdict = "INVALID (P5)"
    elif kA >= 11 and out["tests"]["P1_A_vs_E2y15_greater"] < 0.01:
        verdict = "COMPENSATION-SUPPORTED"
    elif kA <= 6:
        verdict = "NULL"
    else:
        verdict = "INCONCLUSIVE"
    out["verdict"] = verdict
    out["verdict_rule"] = "A>=11/20 and P1 p<0.01 and P5 pass; NULL if A<=6/20; else INCONCLUSIVE"
    out["specificity_note"] = (
        "B (0 deg cube, +15 deg wrist) is harmed by the same constant offset, so the offset cannot be applied "
        "without knowing theta; but the sign of the relative mismatch differs between B and E2 y15, so B is a "
        "deployment control, not a geometric mirror of E2 y15."
    )

    (HERE / "analysis_e5p.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"A (15,+15): {kA}/20  wilson {out['rates']['A_y15_b15']['wilson95']}")
    print(f"B ( 0,+15): {kB}/20  wilson {out['rates']['B_y0_b15']['wilson95']}")
    print(f"E2 y15    : {k15}/20")
    print(f"E2 y0     : {k0}/20")
    print(f"P1 A vs E2 y15 one-sided Fisher p = {out['tests']['P1_A_vs_E2y15_greater']:.3e}")
    print(f"P2 B vs E2 y0  one-sided Fisher p = {out['tests']['P2_B_vs_E2y0_less']:.3e}")
    print(f"A vs B p = {out['tests']['A_vs_B_greater']:.3e}; A vs E2 y0 p = {out['tests']['A_vs_E2y0_two_sided']:.3f}")
    print(f"paired A-E2y15 diff = {out['paired']['A_vs_E2y15']['observed_diff']:+.3f} CI {out['paired']['A_vs_E2y15']['ci95']}")
    print(f"McNemar A vs E2y15: {out['paired']['mcnemar_A_vs_E2y15']}")
    print(f"McNemar B vs E2y0: {out['paired']['mcnemar_B_vs_E2y0']}; A vs B: {out['paired']['mcnemar_A_vs_B']}")
    print(f"held>=0.5: A {out['held_lift']['A']['k']}/20, B {out['held_lift']['B']['k']}/20, E2y15 {out['held_lift']['E2_y15']['k']}/20")
    print(f"interaction DiD = {out['interaction']['observed']:+.3f} CI {out['interaction']['ci95']}")
    print("release modes:", {k: v["counts"] for k, v in out["release_modes"].items()})
    print(f"P5 A ok = {p5_ok}; P6 cross median = {verify['P6']['cross_condition_deg']['median']:.3f} deg")
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
