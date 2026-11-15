"""Matched-data, initialization-only CFM optimization in a two-parameter model."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from probe_finite_data import ENDPOINT_GAIN, PAIRS, SIZES, population, raw_score
from run_probe import digest, mi_reference, source_component

HERE = Path(__file__).resolve().parent
STEPS = [32, 128, 512]


def train(design, target, initial):
    coefficient = initial.copy()
    saved = {}
    for step in range(1, max(STEPS) + 1):
        gradient = 2 * (design.T @ (design @ coefficient - target)) / len(target)
        coefficient -= .4 * gradient
        if step in STEPS:
            saved[step] = coefficient.copy()
    return saved


@torch.no_grad()
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    torch.set_num_threads(1)
    metric, times, noise, sources = source_component()
    rows = []
    for n in SIZES:
        for pair in range(PAIRS):
            data_seed = 3036111500 + n * 100 + pair
            rng = np.random.default_rng(data_seed)
            t, x0, x1 = rng.uniform(size=n), rng.normal(size=n), rng.normal(size=n)
            x = (1 - t) * x0 + t * x1
            design = np.stack([np.ones(n), t - .5], axis=1)
            target = x1 - x0 - population(t, x)
            data_hash = hashlib.sha256(design.tobytes() + target.tobytes()).hexdigest()
            optimum = np.linalg.lstsq(design, target, rcond=None)[0]
            minimum_loss = float(np.mean((design @ optimum - target) ** 2))
            initials, snapshots, init_seeds = [], [], []
            for member in [0, 1]:
                init_seed = 4046111500 + n * 100 + 2 * pair + member
                initial = np.random.default_rng(init_seed).normal(scale=.1, size=2)
                fitted = train(design, target, initial)
                repeated = train(design, target, initial)
                if any(not np.array_equal(fitted[k], repeated[k]) for k in STEPS):
                    raise ValueError("identical initialization does not reproduce")
                initials.append(initial)
                snapshots.append(fitted)
                init_seeds.append(init_seed)
            for step in STEPS:
                c0, c1 = [snapshots[m][step] for m in [0, 1]]
                delta = abs(ENDPOINT_GAIN * (c0[0] - c1[0]))
                score = raw_score(metric, times, noise, c0, c1)
                mi, mi_error = mi_reference(1., delta)
                members = []
                for m, coefficient in enumerate([c0, c1]):
                    loss = float(np.mean((design @ coefficient - target) ** 2))
                    members.append({"data_sha256": data_hash, "initialization_seed": init_seeds[m],
                                    "initial_coefficient": initials[m].tolist(),
                                    "coefficient": coefficient.tolist(), "empirical_loss": loss,
                                    "loss_minus_ols_minimum": max(0., loss - minimum_loss),
                                    "population_excess_cfm_mse": float(coefficient[0] ** 2 + coefficient[1] ** 2 / 12)})
                rows.append({"n": n, "pair_index": pair, "updates": step, "data_seed": data_seed,
                             "ols_optimum": optimum.tolist(), "ols_empirical_loss": minimum_loss,
                             "members": members, "exact_pairwise_kl": float(.5 * delta ** 2),
                             "epistemic_mi_reference": mi, "mi_reference_error_estimate": mi_error,
                             "original_default_vfd": score})
    summary = {}
    for n in SIZES:
        for step in STEPS:
            subset = [r for r in rows if r["n"] == n and r["updates"] == step]
            kl = np.asarray([r["exact_pairwise_kl"] for r in subset])
            score = np.asarray([r["original_default_vfd"] for r in subset])
            gap = [m["loss_minus_ols_minimum"] for r in subset for m in r["members"]]
            summary[f"n{n}_updates{step}"] = {
                "model_pairs": len(subset), "median_exact_kl": float(np.median(kl)),
                "maximum_exact_kl": float(kl.max()), "median_vfd": float(np.median(score)),
                "maximum_vfd": float(score.max()), "maximum_empirical_loss_gap_to_ols": max(gap),
                "all_pairs_with_true_kl_below_1e_minus_12": bool(np.all(kl < 1e-12))}
    report = {"kind": "same_data_finite_optimization_probe_not_neural_vla",
              "distinct_data_pools": len(SIZES) * PAIRS, "model_fits": len(SIZES) * PAIRS * 2,
              "all_reported_endpoints": len(rows), "rows": rows, "summary": summary,
              "source_sha256": digest(Path(__file__)), "plan_sha256": digest(HERE / "PLAN-same-data.md"),
              "external_source_files_verified": len(sources),
              "limits": ["Artificial population velocity basis; not trained neural/VLA action expert.",
                         "Scores become tiny with convergence; absolute scales must not be hidden.",
                         "No empirical robot risk ordering or impact on demonstration choices measured."]}
    with args.out.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"model_fits": report["model_fits"], "endpoints": len(rows), "summary": summary}))


if __name__ == "__main__":
    main()
