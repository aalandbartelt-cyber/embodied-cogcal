"""E1' analysis: does pre-closure object displacement keep within-bin signal?

Reads the ten bin directories, reconstructs obj_pre at the gripper closure from the
recorded physics, and reports (a) a success-weighted stratified AUC of obj_pre, its
seeded bootstrap interval, (b) the same for |delta| inside a bin, and (c) the
success rate per bin. No physics is stepped here; nothing is refitted.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "runs"
THRESHOLD = 0.20
BINS = 10
BOOTSTRAP = 10000
BOOTSTRAP_SEED = 20261117
SEEDS = list(range(12800, 12820))


def auc(score: np.ndarray, label: np.ndarray) -> float:
    score, label = np.asarray(score, float), np.asarray(label, float)
    pos, neg = score[label > 0], score[label <= 0]
    if not pos.size or not neg.size:
        return float("nan")
    d = pos[:, None] - neg[None, :]
    return float(((d > 0).sum() + 0.5 * (d == 0).sum()) / (pos.size * neg.size))


def closure_index(npz_path: Path) -> int:
    z = np.load(npz_path)
    g = z["q"][:, 5]
    idx = np.flatnonzero(g <= THRESHOLD)
    return int(idx[0]) if idx.size else int(len(g) - 1)


def load_bin(bin_index: int) -> list[dict]:
    run = OUT / f"e1p-b{bin_index}"
    physics = OUT / f"e1p-b{bin_index}-physics"
    rows = [json.loads(l) for l in (run / "episodes.jsonl").read_text().splitlines() if l.strip()]
    out = []
    for row in rows:
        seed = int(row["seed"])
        z = np.load(physics / f"{seed}.npz")
        i = closure_index(physics / f"{seed}.npz")
        drift = (z["xyz"][i] - z["xyz"][0]) * 1000.0
        out.append({
            "bin": bin_index, "seed": seed, "delta_mm": float(row["delta_mm"]),
            "success": bool(row["task_success"]),
            "abs_delta_mm": float(np.hypot(*(np.asarray(row["source_xyz_m"])[:2])) * 1000.0),
            "obj_pre_mm": float(np.linalg.norm(drift)),
            "obj_pre_xy_mm": float(np.linalg.norm(drift[:2])),
        })
    return out


def stratified_auc(rows: list[dict], key: str, sign: float = -1.0) -> tuple[float, list[tuple[int, int]]]:
    """Weighted mean of within-bin AUCs, weighted by n_pos*n_neg. Also returns weights."""
    total_w, acc, parts = 0.0, 0.0, []
    for b in range(BINS):
        sub = [r for r in rows if r["bin"] == b]
        y = np.array([r["success"] for r in sub], float)
        s = sign * np.array([r[key] for r in sub], float)
        n_pos, n_neg = int(y.sum()), int((1 - y).sum())
        if n_pos < 3 or n_neg < 3:
            parts.append((0, 0))
            continue
        w = n_pos * n_neg
        acc += w * auc(s, y)
        total_w += w
        parts.append((n_pos, n_neg))
    return (acc / total_w if total_w else float("nan")), parts


def main() -> int:
    rows = [r for b in range(BINS) for r in load_bin(b)]
    by_bin = {}
    for b in range(BINS):
        sub = [r for r in rows if r["bin"] == b]
        succ = sum(r["success"] for r in sub)
        by_bin[b] = {
            "n": len(sub), "success": succ,
            "delta_mm_median": float(np.median([r["delta_mm"] for r in sub])),
            "obj_pre_median_mm": float(np.median([r["obj_pre_mm"] for r in sub])),
            "auc_obj_pre": auc(-np.array([r["obj_pre_mm"] for r in sub]),
                               np.array([r["success"] for r in sub], float)),
            "auc_abs_delta": auc(-np.array([r["abs_delta_mm"] for r in sub]),
                                 np.array([r["success"] for r in sub], float)),
        }
    strat_pre, parts = stratified_auc(rows, "obj_pre_mm")
    strat_delta, _ = stratified_auc(rows, "abs_delta_mm")
    effective = [b for b in range(BINS) if parts[b][0] >= 3 and parts[b][1] >= 3]

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    boot, boot_diff = [], []
    index = {s: [i for i, r in enumerate(rows) if r["seed"] == s] for s in SEEDS}
    for _ in range(BOOTSTRAP):
        take = rng.choice(SEEDS, size=len(SEEDS), replace=True)
        sample = [rows[i] for s in take for i in index[s]]
        value, _ = stratified_auc(sample, "obj_pre_mm")
        other, _ = stratified_auc(sample, "abs_delta_mm")
        if np.isfinite(value):
            boot.append(value)
        if np.isfinite(value) and np.isfinite(other):
            boot_diff.append(value - other)
    lo, hi = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))) if boot else (float("nan"),) * 2
    diff_lo, diff_hi = ((float(np.percentile(boot_diff, 2.5)), float(np.percentile(boot_diff, 97.5)))
                        if boot_diff else (float("nan"),) * 2)

    verdict = ("PASS" if np.isfinite(strat_pre) and strat_pre >= 0.75 and lo > 0.5 and len(effective) >= 2
               else "FAIL" if not np.isfinite(strat_pre) or strat_pre < 0.65 or lo <= 0.5
               else "INCONCLUSIVE")
    result = {
        "kind": "e1p_analysis", "threshold_rad": THRESHOLD, "bootstrap": BOOTSTRAP,
        "per_bin": {str(b): by_bin[b] for b in range(BINS)}, "effective_bins": effective,
        "stratified_auc_obj_pre": strat_pre, "stratified_auc_ci": [lo, hi],
        "stratified_auc_abs_delta": strat_delta,
        "delta_auc_vs_abs_delta": strat_pre - strat_delta,
        "delta_auc_ci": [diff_lo, diff_hi],
        "verdict_G1p": verdict,
        "note": "within-bin only; no tau variation, no collapse claim",
        "rows": rows,
    }
    (HERE / "e1p_result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in [
        "stratified_auc_obj_pre", "stratified_auc_ci", "stratified_auc_abs_delta",
        "delta_auc_vs_abs_delta", "delta_auc_ci", "effective_bins", "verdict_G1p"]}, indent=2))
    for b in range(BINS):
        v = by_bin[b]
        print(f"b{b}  n={v['n']} succ={v['success']}  delta={v['delta_mm_median']:.2f}mm "
              f"pre={v['obj_pre_median_mm']:.2f}mm  auc(pre)={v['auc_obj_pre']:.2f} "
              f"auc(|d|)={v['auc_abs_delta']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
