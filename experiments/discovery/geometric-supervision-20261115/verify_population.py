"""Independent optimizer and bracketing checks of the saved population diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from check_population import Geometry
from scipy.optimize import brentq, minimize_scalar
from scipy.special import expit, ndtri


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    saved = json.loads(args.input.read_text())
    g = Geometry()
    # Independent bounded minimizer evaluates the actual MuJoCo/SO3 loss.
    optimizer_rows = []
    for p in [.5, .7, 1.]:
        m, t = 2 * p - 1, .5

        def conditional_objective(y, mean=m, posterior=p, time=t):
            return ((y - mean) ** 2 + 1 - mean ** 2) / time ** 2 + (
                .15 / (.25 + .001)) * g.fk_loss(y, posterior)

        result = minimize_scalar(conditional_objective, bounds=(-1, 1), method="bounded",
                                 options={"xatol": 1e-13})
        computed = float(g.optimum(p, t)[0])
        difference = abs(result.x - computed)
        if not result.success or difference > 1e-7:
            raise ValueError("independent original-FK optimization disagrees")
        optimizer_rows.append({"posterior_plus": p, "independent_minimizer": result.x,
                               "runner_minimizer": computed, "absolute_difference": difference})
    # Independent Brent solver, not runner Newton; reruns all 10-step quantiles.
    bracketing_rows = []
    for prior in [.5, .7]:
        x = ndtri((np.arange(1024) + .5) / 1024)
        for i in range(10):
            t = (10 - i) / 10
            posterior = expit(np.log(prior / (1 - prior)) + 2 * (1 - t) * x / t ** 2)
            w = 0. if t <= .05 else min(10., 1. / (t ** 2 + .001))
            y = []
            for p in posterior:
                if p == 0. or p == 1.:
                    optimum = 2 * p - 1
                else:
                    def derivative(value, probability=p, time=t, weighting=w):
                        return 2 * (value - (2 * probability - 1)) / time ** 2 + (
                            .15 * weighting * g.geo_dy(value, probability))

                    optimum = brentq(derivative, -1., 1., xtol=1e-14, rtol=1e-14)
                y.append(optimum)
            x -= (x - np.array(y)) / (10 * t)
        reference = next(row for row in saved["sampling"] if row["prior_plus"] == prior
                         and row["steps"] == 10 and row["field"].startswith("paired_"))
        difference = float(np.max(np.abs(x - reference["endpoint"])))
        distance = np.minimum(np.abs(x - 1), np.abs(x + 1))
        indices = np.flatnonzero(distance > .1).tolist()
        if difference > 1e-10:
            raise ValueError("independent bracketing rollout disagrees")
        bracketing_rows.append({"prior_plus": prior, "max_endpoint_discrepancy": difference,
                                "indices_outside_preregistered_band": indices,
                                "endpoints_at_these_indices": x[indices].tolist()})
    report = {"input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
              "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "independent_original_fk_optimizer": optimizer_rows,
              "brent_full_10_step_checks": bracketing_rows,
              "claim": "Numerical validation only; no new robot episodes or task evidence."}
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
