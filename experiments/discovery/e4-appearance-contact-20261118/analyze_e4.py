"""E4 analysis: Wilson intervals, one-sided Fisher exact on the registered
contrast, and the per-seed paired pattern across the four conditions.

Decision rule is fixed in PREREG.md section 4 and implemented here verbatim.
"""

from __future__ import annotations

import json
import math
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CONDITIONS = ("deg0", "visual", "collision", "both")
N = 20


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def fisher_one_sided(a: int, n1: int, c: int, n2: int) -> float:
    """P(X >= a) under the hypergeometric null, row totals fixed."""
    total = n1 + n2
    hits = a + c

    def prob(x: int) -> float:
        return (math.comb(hits, x) * math.comb(total - hits, n1 - x)
                / math.comb(total, n1))

    return sum(prob(x) for x in range(a, min(n1, hits) + 1))


def main() -> int:
    rows = {}
    for condition in CONDITIONS:
        summary = json.loads((HERE / f"runs/e4-{condition}/summary.json").read_text())
        rows[condition] = {row["seed"]: row for row in summary["rows"]}
    seeds = sorted(rows["deg0"])
    if len(seeds) != N or any(sorted(rows[c]) != seeds for c in CONDITIONS):
        raise ValueError("conditions do not share the registered seed set")

    successes = {c: sum(rows[c][s]["task_success"] for s in seeds) for c in CONDITIONS}
    intervals = {c: wilson(successes[c], N) for c in CONDITIONS}

    contrast_p = fisher_one_sided(successes["visual"], N, successes["collision"], N)
    reverse_p = fisher_one_sided(successes["collision"], N, successes["visual"], N)
    contrast = successes["visual"] - successes["collision"]
    if contrast >= 8 and contrast_p < 0.01:
        verdict = "C2 supported: appearance alone does not carry the failure; contact geometry does"
    elif -contrast >= 8 and reverse_p < 0.01:
        verdict = "C2 downgraded to visual sensitivity"
    else:
        verdict = "mixed: both channels contribute"

    control_both = successes["both"] / N
    control_deg0 = successes["deg0"] / N
    comparability = ("both control outside 1/20+-5/20 or deg0 outside 19/20+-5/20: report as non-comparable"
                     if abs(control_both - 0.05) > 0.25 or abs(control_deg0 - 0.95) > 0.25
                     else "controls within the registered drift band")

    patterns = {}
    for seed in seeds:
        pattern = tuple(rows[c][seed]["task_success"] for c in CONDITIONS)
        patterns[pattern] = patterns.get(pattern, 0) + 1

    out = {
        "n_per_condition": N, "seeds": seeds,
        "successes": successes,
        "wilson95": {c: [round(v[0], 4), round(v[1], 4)] for c, v in intervals.items()},
        "contrast_visual_minus_collision": contrast,
        "fisher_one_sided_visual_gt_collision_p": contrast_p,
        "fisher_one_sided_collision_gt_visual_p": reverse_p,
        "verdict": verdict,
        "comparability": comparability,
        "paired_patterns(deg0,visual,collision,both)": {"".join("1" if v else "0" for v in k): v
                                                        for k, v in sorted(patterns.items(), key=lambda kv: -kv[1])},
        "delta_mm_by_seed": {s: rows["deg0"][s]["delta_mm"] for s in seeds},
        "per_seed": {c: {str(s): rows[c][s]["task_success"] for s in seeds} for c in CONDITIONS},
    }
    (HERE / "analysis.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"{'condition':10s} success  Wilson95")
    for c in CONDITIONS:
        lo, hi = intervals[c]
        print(f"{c:10s} {successes[c]:2d}/{N}    [{lo:.3f}, {hi:.3f}]")
    print(f"visual - collision = {contrast:+d}  Fisher p = {contrast_p:.4g}  "
          f"(reverse p = {reverse_p:.4g})")
    print(f"controls: both {successes['both']}/{N}, deg0 {successes['deg0']}/{N} -> {comparability}")
    print(f"paired patterns: {out['paired_patterns(deg0,visual,collision,both)']}")
    print(f"verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
