#!/usr/bin/env python3
"""Recompute E4 (appearance vs contact decoupling) statistics from saved records.

Read-only over ``runs/e4-<condition>/episodes.jsonl``.  The registered contrast
``success(visual) - success(collision)`` flips *two* factors at once, so this
script also estimates the 2x2 factorial main effects that the design supports:

    factor A (appearance) : rendered / image yaw 0 -> 15 deg
    factor C (contact)    : collision yaw        0 -> 15 deg

    deg0      A0 C0
    visual    A1 C0
    collision A0 C1
    both      A1 C1

Usage:
    python3 recompute_e4_pairs.py [--repo PATH] [--json OUT]
"""
from __future__ import annotations

import argparse
import json
import math
from itertools import product
from pathlib import Path

CONDITIONS = ("deg0", "visual", "collision", "both")
CELLS = {"deg0": (0, 0), "visual": (1, 0), "collision": (0, 1), "both": (1, 1)}


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def _hypergeom_tail(a: int, row1: int, col1: int, total: int) -> float:
    """P(X >= a) for X ~ Hypergeometric(total, col1, row1)."""
    def pmf(x: int) -> float:
        return (math.comb(col1, x) * math.comb(total - col1, row1 - x)) / math.comb(total, row1)

    upper = min(row1, col1)
    return sum(pmf(x) for x in range(a, upper + 1))


def fisher_one_sided(a: int, b: int, c: int, d: int) -> float:
    """One-sided Fisher exact p for H1: first row has the higher success rate.

    Table is [[a, b], [c, d]] with a/c successes and b/d failures.
    """
    return min(1.0, _hypergeom_tail(a, a + b, a + c, a + b + c + d))


def mcnemar_exact(discordant_1_0: int, discordant_0_1: int) -> float:
    """Two-sided exact McNemar p on paired binary outcomes."""
    n = discordant_1_0 + discordant_0_1
    if n == 0:
        return 1.0
    k = min(discordant_1_0, discordant_0_1)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def _stratified(success: dict[str, dict[int, bool]], seeds: list[int],
                pair_a: tuple[str, str], pair_b: tuple[str, str]) -> dict:
    """Stratified McNemar over the two strata that isolate one factor.

    ``pair_a`` and ``pair_b`` are (baseline, treatment) condition pairs taken at
    the other factor's level 0 and 1.
    """
    gained = lost = 0
    for baseline, treatment in (pair_a, pair_b):
        for seed in seeds:
            if success[treatment][seed] and not success[baseline][seed]:
                gained += 1
            elif success[baseline][seed] and not success[treatment][seed]:
                lost += 1
    total = gained + lost
    p_gain = _hypergeom_p(gained, total) if total else 1.0
    p_loss = _hypergeom_p(lost, total) if total else 1.0
    return {
        "discordant_gained": gained,
        "discordant_lost": lost,
        "p_one_sided_gain": round(min(1.0, p_gain), 12),
        "p_one_sided_loss": round(min(1.0, p_loss), 12),
        "p_two_sided": round(min(1.0, 2 * min(p_gain, p_loss)), 12),
    }


def _hypergeom_p(k: int, n: int) -> float:
    """One-sided sign-test p: P(X >= k) with X ~ Binomial(n, 1/2)."""
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n


def load(repo: Path) -> dict[str, dict[int, dict]]:
    base = repo / "experiments/discovery/e4-appearance-contact-20261118/runs"
    out: dict[str, dict[int, dict]] = {}
    for cond in CONDITIONS:
        path = base / f"e4-{cond}" / "episodes.jsonl"
        rows: dict[int, dict] = {}
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                rows[int(row["seed"])] = row
        out[cond] = rows
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--json", default=None)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    data = load(repo)

    seeds = sorted(set.intersection(*(set(rows) for rows in data.values())))
    problems: list[str] = []
    for cond, rows in data.items():
        if len(rows) != 20:
            problems.append(f"{cond}: {len(rows)} episodes, expected 20")
        if sorted(rows) != seeds:
            problems.append(f"{cond}: seed set differs from the common set")
        for seed, row in rows.items():
            if float(row["delta_mm"]) <= 0:
                problems.append(f"{cond}/{seed}: non-positive delta_mm")

    deltas: dict[int, set[float]] = {}
    for seed in seeds:
        deltas[seed] = {round(float(data[cond][seed]["delta_mm"]), 9) for cond in CONDITIONS}
    for seed, values in deltas.items():
        if len(values) != 1:
            problems.append(f"seed {seed}: delta_mm differs across conditions: {sorted(values)}")

    success = {cond: {seed: bool(data[cond][seed]["task_success"]) for seed in seeds} for cond in CONDITIONS}
    counts = {cond: sum(success[cond].values()) for cond in CONDITIONS}

    patterns: dict[str, int] = {}
    for seed in seeds:
        key = "".join("1" if success[cond][seed] else "0" for cond in CONDITIONS)
        patterns[key] = patterns.get(key, 0) + 1

    summary = {
        "n_per_condition": len(seeds),
        "seeds": seeds,
        "successes": counts,
        "wilson95": {cond: [round(x, 4) for x in wilson(counts[cond], len(seeds))] for cond in CONDITIONS},
        "paired_patterns(deg0,visual,collision,both)": dict(sorted(patterns.items(), key=lambda kv: -kv[1])),
        "registered_contrast_visual_minus_collision": counts["visual"] - counts["collision"],
        "registered_fisher_one_sided_p": fisher_one_sided(
            counts["visual"], len(seeds) - counts["visual"],
            counts["collision"], len(seeds) - counts["collision"]),
        "single_factor": {
            "appearance_only_deg0_to_visual": {
                "delta_success": counts["visual"] - counts["deg0"],
                "fisher_one_sided_p": fisher_one_sided(
                    counts["visual"], len(seeds) - counts["visual"],
                    counts["deg0"], len(seeds) - counts["deg0"]),
                "mcnemar_exact_p": mcnemar_exact(
                    sum(1 for s in seeds if success["visual"][s] and not success["deg0"][s]),
                    sum(1 for s in seeds if success["deg0"][s] and not success["visual"][s])),
            },
            "contact_only_deg0_to_collision": {
                "delta_success": counts["collision"] - counts["deg0"],
                "fisher_one_sided_p": fisher_one_sided(
                    counts["deg0"], len(seeds) - counts["deg0"],
                    counts["collision"], len(seeds) - counts["collision"]),
                "mcnemar_exact_p": mcnemar_exact(
                    sum(1 for s in seeds if success["deg0"][s] and not success["collision"][s]),
                    sum(1 for s in seeds if success["collision"][s] and not success["deg0"][s])),
            },
        },
        "factorial_main_effects": {
            "appearance_A_avg_over_contact": round(
                ((counts["visual"] - counts["deg0"]) + (counts["both"] - counts["collision"])) / 2, 3),
            "contact_C_avg_over_appearance": round(
                ((counts["collision"] - counts["deg0"]) + (counts["both"] - counts["visual"])) / 2, 3),
            "difference_of_differences": (counts["both"] - counts["collision"]) - (counts["visual"] - counts["deg0"]),
        },
        "stratified_main_effect_tests": {
            "appearance": _stratified(success, seeds, ("deg0", "visual"), ("collision", "both")),
            "contact": _stratified(success, seeds, ("deg0", "collision"), ("visual", "both")),
        },
        "consistency_problems": problems,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.json:
        Path(args.json).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
