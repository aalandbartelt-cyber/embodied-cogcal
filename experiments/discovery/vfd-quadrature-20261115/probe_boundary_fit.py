"""Finite-fit path perturbations with identical exact terminal action maps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from run_probe import COUNTS, PRESET, digest, make_velocity, source_component
from scipy.integrate import quad

HERE = Path(__file__).resolve().parent
EPSILONS = [0., 1e-6, 1e-4, .01, .1, 1.]
CUTOFFS = [.9, .99, .999, .9999, .99999]


def eta(t):
    variance = (1 - t) ** 2 + t ** 2
    return (variance - np.sqrt(variance)) / 2


def density(t, epsilon):
    return 4 * epsilon ** 2 * (t - .5) ** 2 * t / (1 - t)


def perturbed_velocity(epsilon, sign):
    base = make_velocity(0., 1.)

    def velocity(x_t, t):
        return base(x_t, t) + sign * epsilon * (t - .5)
    return velocity


@torch.no_grad()
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    metric, times, noise, sources = source_component()
    step = 1e-6
    rows = []
    for epsilon in EPSILONS:
        max_ode_error = 0.
        for sign in [-1, 1]:
            for t in [.05, .25, .5, .75, .95]:
                for z in noise.numpy().ravel():
                    def trajectory(s, z=z, sign=sign, epsilon=epsilon):
                        return np.sqrt((1 - s) ** 2 + s ** 2) * z + sign * epsilon * eta(s)
                    derivative = (trajectory(t + step) - trajectory(t - step)) / (2 * step)
                    field = ((2 * t - 1) * trajectory(t) / ((1 - t) ** 2 + t ** 2)
                             + sign * epsilon * (t - .5))
                    max_ode_error = max(max_ode_error, abs(derivative - field))
        if max_ode_error > 1e-7:
            raise ValueError("closed-form trajectories fail independent ODE derivative check")
        t = times.reshape(-1, 1, 1, 1)
        variance = (1 - t) ** 2 + t ** 2
        mean_shift = epsilon * (variance - torch.sqrt(variance)) / 2
        score_samples = []
        for sign in [-1, 1]:
            states = torch.sqrt(variance) * noise.unsqueeze(0) + sign * mean_shift
            if not torch.equal(states[-1], noise):
                raise ValueError("terminal maps differ")
            score_samples.append(metric(
                ref_ode_states=states, ref_velocity_fn=perturbed_velocity(epsilon, 1),
                cmp_ode_states=states, cmp_velocity_fn=perturbed_velocity(epsilon, -1)))
        original = float(torch.stack(score_samples).mean())
        expected = float(np.diff([*PRESET, 1.]) @ density(np.asarray(PRESET), epsilon))
        if not np.isclose(original, expected, rtol=1e-10, atol=1e-14):
            raise ValueError("original scorer and independent formula disagree")
        discrete = []
        for n in COUNTS:
            uniform = float(density(np.arange(n) / n, epsilon).mean())
            closed = epsilon ** 2 * (sum(1 / j for j in range(1, n + 1)) - 1
                                      - 2 * (n - 1) * (2 * n - 1) / (3 * n ** 2))
            if not np.isclose(uniform, closed, rtol=1e-11, atol=1e-16):
                raise ValueError("finite harmonic-sum identity failed")
            nodes, weights = np.polynomial.legendre.leggauss(n)
            gauss = float(weights @ density((nodes + 1) / 2, epsilon) / 2)
            discrete.append({"n": n, "uniform_left": uniform,
                             "uniform_left_exact_harmonic_sum": closed, "gauss_legendre": gauss})
        truncated = []
        for cutoff in CUTOFFS:
            closed = epsilon ** 2 * (-4 * cutoff ** 3 / 3 - cutoff - np.log1p(-cutoff))
            unit_value, unit_error = quad(density, 0., cutoff, args=(1.,),
                                          epsabs=1e-11, epsrel=1e-11, limit=500)
            value, error = epsilon ** 2 * unit_value, epsilon ** 2 * unit_error
            if not np.isclose(value, closed, rtol=1e-10, atol=1e-13):
                raise ValueError("truncated integral identity failed")
            truncated.append({"cutoff": cutoff, "closed_form": float(closed),
                              "adaptive_quad": value, "quad_error_estimate": error})
        rows.append({"epsilon": epsilon, "exact_terminal_pairwise_kl": 0., "exact_epistemic_mi": 0.,
                     "terminal_maps_identical_for_every_noise": True,
                     "population_cfm_excess_mse_per_member": epsilon ** 2 / 12,
                     "max_ode_finite_difference_error": float(max_ode_error),
                     "source_default_score": original, "independent_default_formula": expected,
                     "discrete": discrete, "truncated_integrals": truncated,
                     "continuous_vfd_integral": "zero" if epsilon == 0 else "diverges_to_positive_infinity"})
    result = {"kind": "analytic_finite_fit_boundary_probe_not_neural_model_or_robot_failure",
              "conditions": len(rows), "rows": rows,
              "source_files_verified": len(sources), "source_revision": "bcc2433d2549afee27bf5d0a73ae528375bca686",
              "source_sha256": digest(Path(__file__)), "plan_sha256": digest(HERE / "PLAN-boundary-fit.md"),
              "limits": ["These perturbed fields do not obey exact population-optimal OT marginals.",
                         "This does not contradict the original continuous theorem under its assumptions.",
                         "No actual trained VLA, empirical risk ranking or robot task tested."]}
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"conditions": len(rows), "rows": [
        {"epsilon": r["epsilon"], "true_kl": 0., "source_default_score": r["source_default_score"],
         "excess_cfm_mse": r["population_cfm_excess_mse_per_member"],
         "uniform_n500": r["discrete"][-1]["uniform_left"]} for r in rows]}))


if __name__ == "__main__":
    main()
