"""Exact Gaussian OT flow check of finite-grid VFD; no robot/VLA trials."""

from __future__ import annotations

import abc
import argparse
import ast
import hashlib
import itertools
import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import scipy
import torch
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CACHE = ROOT / "data/discovery/vfd-quadrature-20261115"
SIGMAS = [.01, .03, .1, .3, 1., 3.]
DELTAS = [0., .001, .003, .01, .03, .1, .3, 1.]
COUNTS = [5, 10, 20, 50, 100, 500]
PRESET = tuple(i * .1 for i in range(10)) + (.95,)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integrand(t, sigma, delta):
    variance = (1 - t) ** 2 + sigma ** 2 * t ** 2
    return delta ** 2 * t * (1 - t) / variance ** 2


def mi_reference(sigma, delta):
    if delta == 0:
        return 0., 0.
    ratio = delta / sigma

    def entropy(z):
        llr = ratio ** 2 / 2 + ratio * z
        return math.exp(-z * z / 2) / math.sqrt(2 * math.pi) * np.logaddexp(0., -llr)

    conditional, error = quad(entropy, -12., 12., epsabs=1e-11, epsrel=1e-11, limit=500)
    return math.log(2) - conditional, error


def definitions(namespace, filename, names):
    path = CACHE / filename
    tree = ast.parse(path.read_text())
    chosen = [node for node in tree.body
              if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
    if {node.name for node in chosen} != set(names):
        raise ValueError("missing inspected definitions")
    future = ast.parse("from __future__ import annotations").body
    module = ast.Module(body=[*future, *chosen], type_ignores=[])
    exec(compile(module, str(path), "exec"), namespace)


def source_component():
    records = json.loads((HERE / "primary-sources.json").read_text())["sources"]
    records += json.loads((HERE / "implementation-sources.json").read_text())["sources"]
    records += [json.loads((HERE / "path-source.json").read_text())]
    for entry in records:
        if digest(ROOT / entry["cache"]) != entry["sha256"]:
            raise ValueError("fixed source content changed")
    namespace = {"torch": torch, "Tensor": torch.Tensor, "abc": abc, "ABC": abc.ABC}
    definitions(namespace, "active_learning__src__lerobot__policies__common__flow_matching__conditional_probability_path.py",
                ["CondProbPath", "OTCondProbPath"])
    definitions(namespace, "active_learning__src__lerobot__policies__common__flow_matching__ode_solver.py",
                ["select_ode_states"])
    definitions(namespace, "active_learning__src__lerobot__uncertainty__uncertainty_scoring__scoring_metrics.py",
                ["UncertaintyMetric", "InterVelDiff"])
    times = torch.tensor([*PRESET, 1.], dtype=torch.float64)
    sampler = SimpleNamespace(device=torch.device("cpu"), dtype=torch.float64, env_action_dim=1,
                              sampling_ode_solver=None, sampling_time_grid=times,
                              cond_vf_config={"type": "ot", "sigma_min": 0.})
    metric = namespace["InterVelDiff"](SimpleNamespace(velocity_eval_times=PRESET), sampler)
    generator = torch.Generator().manual_seed(20261115)
    noise = torch.randn((8, 1, 1), generator=generator, dtype=torch.float64)
    return metric, times, noise, records


def make_velocity(mu, sigma):
    def velocity(x_t, t):
        variance = (1 - t) ** 2 + sigma ** 2 * t ** 2
        rate = t * sigma ** 2 - (1 - t)
        return mu + rate / variance * (x_t - t * mu)
    return velocity


def source_score(metric, times, noise, sigma, delta):
    t = times.reshape(-1, 1, 1, 1)
    variance = (1 - t) ** 2 + sigma ** 2 * t ** 2
    states_a = -t * delta / 2 + torch.sqrt(variance) * noise.unsqueeze(0)
    states_b = t * delta / 2 + torch.sqrt(variance) * noise.unsqueeze(0)
    a, b = make_velocity(-delta / 2, sigma), make_velocity(delta / 2, sigma)
    scores = []
    for states in [states_a, states_b]:
        scores.append(metric(ref_ode_states=states, ref_velocity_fn=a,
                             cmp_ode_states=states, cmp_velocity_fn=b))
    scores = torch.stack(scores)
    return float(scores.mean()), float(scores.max() - scores.min())


def rank_report(rows, method, reference):
    considered = inversions = score_ties = 0
    first = None
    for i, j in itertools.combinations(range(len(rows)), 2):
        a, b = rows[i][reference], rows[j][reference]
        if reference == "epistemic_mi_nats_reference":
            tied = abs(a - b) <= 1e-9
        else:
            tied = math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-14)
        if tied:
            continue
        considered += 1
        sa, sb = rows[i]["scores"][method], rows[j]["scores"][method]
        if math.isclose(sa, sb, rel_tol=1e-10, abs_tol=1e-14):
            score_ties += 1
        elif (sa - sb) * (a - b) < 0:
            inversions += 1
            if first is None:
                first = [i, j]
    return {"strict_reference_pairs": considered, "strict_inversions": inversions,
            "estimated_score_ties": score_ties, "first_inversion_row_indices": first}


@torch.no_grad()
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    torch.set_num_threads(1)
    metric, times, noise, sources = source_component()
    grids = {}
    for n in COUNTS:
        grids[f"paper_left_{n}"] = (np.arange(n) / n, np.full(n, 1 / n))
        grids[f"midpoint_{n}"] = ((np.arange(n) + .5) / n, np.full(n, 1 / n))
        points, weights = np.polynomial.legendre.leggauss(n)
        grids[f"gauss_legendre_{n}"] = ((points + 1) / 2, weights / 2)
    grids["source_default_11"] = (np.asarray(PRESET), np.diff([*PRESET, 1.]))
    rows = []
    max_agreement = max_integral_error = max_noise_range = 0.
    for sigma, delta in itertools.product(SIGMAS, DELTAS):
        truth = delta ** 2 / (2 * sigma ** 2)
        integral, error = quad(integrand, 0., 1., args=(sigma, delta),
                               epsabs=1e-11, epsrel=1e-11, limit=500)
        normalized_error = abs(integral - truth) / (1 + truth)
        if normalized_error > 1e-8:
            raise ValueError("continuous KL identity failed independent quadrature")
        mi, mi_error = mi_reference(sigma, delta)
        scores = {name: float(weights @ integrand(points, sigma, delta))
                  for name, (points, weights) in grids.items()}
        original, noise_range = source_score(metric, times, noise, sigma, delta)
        if not math.isclose(original, scores["source_default_11"], rel_tol=1e-10, abs_tol=1e-12):
            raise ValueError("original source scorer and independent formula disagree")
        if noise_range > 1e-8 * (1 + abs(original)):
            raise ValueError("unexpected noise dependence in equal-variance Gaussian probe")
        max_agreement = max(max_agreement, abs(original - scores["source_default_11"]))
        max_integral_error = max(max_integral_error, normalized_error)
        max_noise_range = max(max_noise_range, noise_range)
        rows.append({"sigma": sigma, "mean_separation_delta": delta,
                     "exact_pairwise_kl_nats": truth, "continuous_quad_kl": integral,
                     "continuous_quad_error_estimate": error,
                     "epistemic_mi_nats_reference": mi, "mi_reference_quad_error_estimate": mi_error,
                     "source_function_score": original, "source_score_sample_range": noise_range,
                     "scores": scores})
    summaries = {}
    for name in grids:
        relative = [abs(row["scores"][name] - row["exact_pairwise_kl_nats"]) /
                    row["exact_pairwise_kl_nats"] for row in rows if row["exact_pairwise_kl_nats"] > 0]
        summaries[name] = {"median_relative_kl_error": float(np.median(relative)),
                           "maximum_relative_kl_error": max(relative),
                           "kl_ranking": rank_report(rows, name, "exact_pairwise_kl_nats"),
                           "mi_ranking": rank_report(rows, name, "epistemic_mi_nats_reference")}
    result = {
        "kind": "analytic_population_OT_component_probe_not_robot_or_learned_policy",
        "conditions": len(rows), "rows": rows, "summary": summaries,
        "source_revision": "bcc2433d2549afee27bf5d0a73ae528375bca686",
        "source_definition_loading": "unchanged inspected AST definitions, analytic model adapters, no full runtime",
        "checks": {"max_original_source_formula_absolute_error": max_agreement,
                   "max_continuous_identity_error_divided_by_1_plus_kl": max_integral_error,
                   "max_noise_sample_score_range": max_noise_range},
        "code_sha256": digest(Path(__file__)), "plan_sha256": digest(HERE / "PLAN.md"),
        "source_files_verified": len(sources),
        "runtime": {"torch": torch.__version__, "numpy": np.__version__, "scipy": scipy.__version__,
                    "device": "cpu", "dtype": "float64", "noise_seed": 20261115, "noise_samples": 8},
        "limits": ["Synthetic distribution conditions, not episodes or empirical model failures.",
                   "Continuous population theorem remains valid; only finite-grid approximation is probed.",
                   "Classical controls match integrand calls only, not neural ODE NFE or latency.",
                   "No failure risk, task harm, active-learning gain or SO101 deployment established."]}
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"conditions": len(rows), "checks": result["checks"],
                      "paper_left_10": summaries["paper_left_10"],
                      "source_default_11": summaries["source_default_11"]}))


if __name__ == "__main__":
    main()
