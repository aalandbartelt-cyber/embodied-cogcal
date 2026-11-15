"""Ordinary two-parameter finite-data CFM fit with exact Gaussian endpoints."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import torch
from run_probe import PRESET, digest, mi_reference, source_component

HERE = Path(__file__).resolve().parent
SIZES = [256, 1024, 4096]
PAIRS = 24
ENDPOINT_GAIN = np.sqrt(2) * np.arcsinh(1)


def population(t, x):
    return (2 * t - 1) * x / ((1 - t) ** 2 + t ** 2)


def fit(n, seed):
    rng = np.random.default_rng(seed)
    t, x0, x1 = rng.uniform(size=n), rng.normal(size=n), rng.normal(size=n)
    x = (1 - t) * x0 + t * x1
    target = x1 - x0 - population(t, x)
    design = np.stack([np.ones(n), t - .5], axis=1)
    coefficient = np.linalg.lstsq(design, target, rcond=None)[0]
    orthogonality = float(np.abs(design.T @ (target - design @ coefficient)).max() / n)
    if orthogonality > 1e-10:
        raise ValueError("OLS normal equations fail")
    return coefficient, {"seed": seed, "samples": n, "coefficient": coefficient.tolist(),
                         "empirical_residual_mse": float(np.mean((target - design @ coefficient) ** 2)),
                         "population_excess_cfm_mse": float(coefficient[0] ** 2 + coefficient[1] ** 2 / 12),
                         "normal_equation_max_per_sample": orthogonality}


def trajectory(t, z, coefficient):
    variance = (1 - t) ** 2 + t ** 2
    scale = np.sqrt(variance)
    integral = (np.arcsinh(2 * t - 1) + np.arcsinh(1)) / np.sqrt(2)
    eta = (variance - scale) / 2
    return scale * z + coefficient[0] * scale * integral + coefficient[1] * eta


def velocity(coefficient):
    def value(x_t, t):
        return population(t, x_t) + coefficient[0] + coefficient[1] * (t - .5)
    return value


def raw_score(metric, times, noise, c0, c1):
    states = torch.stack([torch.from_numpy(trajectory(float(t), noise.numpy(), c0)) for t in times])
    scores = metric(ref_ode_states=states, ref_velocity_fn=velocity(c0),
                    cmp_ode_states=states, cmp_velocity_fn=velocity(c1))
    return float(scores.mean())


def inversions(rows, score):
    considered = flips = 0
    first = None
    for a, b in itertools.combinations(rows, 2):
        difference = a["exact_pairwise_kl"] - b["exact_pairwise_kl"]
        if abs(difference) <= 1e-12:
            continue
        considered += 1
        if difference * (a[score] - b[score]) < 0:
            flips += 1
            if first is None:
                first = [a["pair_index"], b["pair_index"]]
    return {"strict_kl_pairs": considered, "inversions": flips, "first_inversion_indices": first}


@torch.no_grad()
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    torch.set_num_threads(1)
    metric, times, noise, sources = source_component()
    default = np.asarray(PRESET)
    weights = np.diff([*PRESET, 1.]) * default / (1 - default)
    rows = []
    max_derivative = max_endpoint = max_source_formula = 0.
    for n in SIZES:
        for index in range(PAIRS):
            coefficients, records = [], []
            for member in [0, 1]:
                seed = 2026111500 + n * 100 + 2 * index + member
                coefficient, record = fit(n, seed)
                coefficients.append(coefficient)
                records.append(record)
                z = noise.numpy()
                terminal = trajectory(1., z, coefficient)
                max_endpoint = max(max_endpoint, float(np.abs(terminal - z - ENDPOINT_GAIN * coefficient[0]).max()))
                for t in [.05, .25, .5, .75, .95]:
                    derivative = (trajectory(t + 1e-6, z, coefficient)
                                  - trajectory(t - 1e-6, z, coefficient)) / 2e-6
                    target = population(t, trajectory(t, z, coefficient)) + coefficient[0] + coefficient[1] * (t - .5)
                    max_derivative = max(max_derivative, float(np.abs(derivative - target).max()))
            c0, c1 = coefficients
            difference = c0 - c1
            score = raw_score(metric, times, noise, c0, c1)
            formula = float(weights @ (difference[0] + difference[1] * (default - .5)) ** 2)
            max_source_formula = max(max_source_formula, abs(score - formula))
            if not np.isclose(score, formula, rtol=1e-10, atol=1e-12):
                raise ValueError("raw source and formula differ")
            endpoint_only = float(weights.sum() * difference[0] ** 2)
            projected0, projected1 = c0.copy(), c1.copy()
            projected0[1] = projected1[1] = 0
            projected_source = raw_score(metric, times, noise, projected0, projected1)
            if not np.isclose(projected_source, endpoint_only, rtol=1e-10, atol=1e-12):
                raise ValueError("oracle terminal-equivalent score mismatch")
            delta = abs(ENDPOINT_GAIN * difference[0])
            mi, mi_error = mi_reference(1., delta)
            rows.append({"n": n, "pair_index": index, "members": records,
                         "exact_terminal_means": [float(ENDPOINT_GAIN * c[0]) for c in coefficients],
                         "exact_pairwise_kl": float(.5 * delta ** 2), "epistemic_mi_reference": mi,
                         "mi_reference_error_estimate": mi_error,
                         "raw_source_default_vfd": score, "oracle_zero_time_term_score": endpoint_only,
                         "oracle_projected_source_score": projected_source,
                         "coefficient_difference": difference.tolist()})
    if max_endpoint > 1e-12 or max_derivative > 1e-7:
        raise ValueError("independent exact endpoint or ODE checks fail")
    summary = {str(n): {"pairs": PAIRS, "raw": inversions([r for r in rows if r["n"] == n], "raw_source_default_vfd"),
                        "oracle_zero_time_term": inversions([r for r in rows if r["n"] == n], "oracle_zero_time_term_score")}
               for n in SIZES}
    report = {"kind": "finite_data_two_parameter_cfm_not_vla_or_robot_experiment", "model_pairs": len(rows),
              "model_fits": len(rows) * 2, "rows": rows, "summary": summary,
              "checks": {"max_endpoint_mean_formula_error": max_endpoint,
                         "max_ode_central_difference_error": max_derivative,
                         "max_source_vs_formula_score_error": max_source_formula},
              "source_sha256": digest(Path(__file__)), "plan_sha256": digest(HERE / "PLAN-finite-data.md"),
              "external_source_files_verified": len(sources),
              "limits": ["Known population velocity basis and two fitted time coefficients; not a neural VLA.",
                         "Members use independent finite datasets from the same law, unlike same-data training-seed ensembles.",
                         "Oracle removal of the null-terminal term is a diagnostic, not a deployable new method.",
                         "Pairwise ranking counts are dependent comparisons; no statistical significance claimed.",
                         "No action-risk, demonstration-acquisition or hardware performance gain established."]}
    with args.out.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"model_pairs": len(rows), "model_fits": len(rows) * 2, "summary": summary,
                      "checks": report["checks"]}))


if __name__ == "__main__":
    main()
