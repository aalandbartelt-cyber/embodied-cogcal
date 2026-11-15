# VFD finite-grid analytic mechanism figure

Figure ID: `vfd_grid_analytic_20261115`.

Core conclusion: fixed finite-time VFD quadrature can reverse disagreement order for exact Gaussian OT flows;
the continuous identity holds and ordinary quadrature is an essential control.

Evidence: `experiments/discovery/vfd-quadrature-20261115/analytic-results.json`, 48 prescribed conditions,
original scorer definition replay and independent Gaussian formulas. Archetype: mechanism / failure boundary.

| Panel | Source / metric | Visual argument |
|---|---|---|
| a | Exact normalized integrand for the two conditions from the first reported inversion | Mass can concentrate between the final default evaluation and endpoint |
| b | All positive-δ rows, median estimate/exact KL at each σ | Width-dependent error is not a uniform scale correction |
| c | All 1,062 MI-resolvable condition pairs | Include midpoint/Gauss–Legendre controls and all prescribed evaluation counts |
| d | First lexicographic default-grid inversion in the saved result | True pairwise KL and its finite-grid estimate change order; MI has the same true ordering here |

Panel d is an explanatory post-result display selected by a documented deterministic rule, not an independent confirmatory trial.
No model training, robot episodes, empirical failure risk, timing advantage, confidence intervals or independent-pair sample size are claimed.
MI and KL remain distinct quantities; panel d plots KL rather than putting MI on the estimator's scale.
Quadrature controls match integrand calls only, not neural ODE evaluations.

Export: double column 17.8 × 10.5 cm; SVG/PDF plus PNG preview; DejaVu Sans, editable SVG text, PDF TrueType.
Source manifest: `.research/figures/source_data_manifest.json`.
