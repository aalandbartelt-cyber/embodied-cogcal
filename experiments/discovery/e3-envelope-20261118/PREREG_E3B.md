# E3b supplement -- pre-registration: is the yaw window constant over reach-safe offsets?

Frozen before execution. This file is hashed into every E3b contract
(`prereg_sha256`), so it must not be edited after the first episode is run.

Parent: `PREREG.md` (E3, sha256 `129c4081...`), `RESULTS.md` (E3, commit 22806f7).

## 1. Why this supplement

E3 registered a 3-column design (delta in {2,8,14} mm). Its registered primary
outcome met PASS-E3a only literally: the 3-point slope was s = -0.982 deg/mm,
CI [-1.019, -0.243], but

1. the whole slope is carried by the delta=14 column, where the 0-deg baseline
   is 10/20 = 0.50 and the failures are lift/reach failures
   (`two_finger_lift_not_established`), not tilt failures; theta*(14) is pinned
   at the lower grid edge 0 deg and 39.3% of bootstrap draws are censored;
2. the two reach-safe columns delta in {2,8} give theta* 11.79 vs 11.67 deg,
   post-hoc slope -0.020 deg/mm, CI [-0.162, +0.282].

So E3 cannot distinguish "window shrinks with offset" from "window is a fixed
~11.7 deg and the delta=14 column merely runs out of reach margin". This
supplement measures theta*(delta) on five reach-safe offsets with the same
paired seeds, which turns that ambiguity into a testable slope.

## 2. Design

- New cells: yaw in {0,5,10,15} deg x per-axis delta in {4,6,10} mm
  (= 12 cells x 20 paired seeds = 240 episodes), tag `e3b`,
  seeds 12920-12939 (identical to E3).
- Reused cells: E3's delta in {2,8} columns, tag `e3`, same seeds
  12920-12939, same frozen config. They stay in `runs/e3-y*-d{2,8}` and are
  read, not re-run. Rationale: same policy, same carrier, same control budget,
  same seed set; re-running would only duplicate.
- Everything else identical to E3: frozen ACT checkpoint, surviving carrier
  bytecode, control budget 285 @ 30 fps, horizon/execute as in E3, fixed exact
  per-axis shift (Euclidean offset = delta*sqrt(2) mm), yaw via free-joint
  quaternion at reset, natural scene (body and render rotate together).
- Reuse of E3 columns across two contract hashes is fine: pairing requires only
  identical seeds, and the frozen configuration (`kind`, checkpoint, carrier,
  budget, w_eff formula) is byte-identical except the tag/prereg hash.

## 3. Endpoints (registered)

Primary: per-cell success rate (task_success) with Wilson 95%, and
theta*(delta) with E3's estimator verbatim: linear interpolation between the
largest yaw with p_hat >= 0.5 and its successor. Censoring rule identical: a
column with p_hat(0 deg) < 0.5 or p_hat(15 deg) >= 0.5 is censored and
contributes no theta*.

Slope: OLS of theta* on delta over the five columns {2,4,6,8,10} mm.
Uncertainty: 10^4 cluster-bootstrap resamples of the 20 seed indices, all 20
cells (5 delta x 4 yaw, E3 and E3b together) resampled jointly at the same
indices; 2.5/97.5 percentiles. Bootstrap draws in which any included column is
censored are skipped and the skip count is reported (E3 had 39.3% skips).

Decision categories (registered):
- **SHRINK** iff s < 0 and the 95% CI upper bound < 0 (window shrinks inside
  the reach-safe zone; this would overturn the E3 reading in RESULTS.md §2).
- **FLAT** iff the CI lies entirely inside +/- 2 deg / 12 mm equivalent
  (|s| < 0.1667 deg/mm at the CI edge, same threshold as E3b in the parent
  prereg).
- **INCONCLUSIVE** otherwise: report the surface and the CI; the paper claim
  becomes "constant within the CI", quantified, not "exactly constant".

Prediction (registered, may be wrong): SHRINK is not supported and the point
estimate is small (|s| < 0.15 deg/mm). Positional prediction: theta*(10) >=
10 deg, and the FLAT test is expected to be the borderline case -- with 5
columns of 20 episodes the per-column theta* bootstrap SD is about 0.5 deg, so
the slope CI half-width is expected near 0.15 deg/mm; a CI of about
[-0.15, +0.15] would land just inside the FLAT threshold.

## 4. Controls (registered)

- **(0,10) is the reach control**: E1' b4 (13.8 mm) is 16/20 and E3 (0,14) is
  10/20, so delta=10 mm is expected near 0.8-1.0. If (0,10) < 0.60, the
  delta=10 column is declared mechanism-contaminated (reach-limited) and is
  excluded from the slope; all cells are still reported and the exclusion is
  stated explicitly. If (0,10) is in [0.60, 0.75), the column stays in the
  registered slope but the reach caveat is reported.
- **(15,*) must stay <= 0.15** in every new column (E3: 1/20, 2/20 at delta
  2/8). A single violation above 0.25 is a protocol alarm (report and inspect
  traces); it is not silently discarded.
- **(0,4)/(0,6)/(0,8)/(0,10)** are expected monotone non-decreasing in delta
  up to reach; no statistical gate, report only.
- Monotonicity in yaw per column is checked with the E3 rule (a rise of >= 5/20
  between consecutive yaw is flagged and reported; E3 had one +1/20 at delta=2).

## 5. Secondary (supporting only, not a gate)

- GEE logistic `success ~ theta_c + delta_c + theta_c:delta_c` with seed
  clusters and exchangeable working correlation, over the pooled 20 cells
  (400 observations), theta_c=(theta-7.5)/7.5, delta_c=(delta-6)/4.
  The interaction coefficient is the "does the yaw sensitivity depend on
  offset" read-out; positive = yaw cliff steeper at small offsets, negative =
  boundary shrinks with offset. Report beta, cluster-robust SE, z, and both
  one-sided p-values.
- Stage decomposition: lift (longest_two_finger_lift_s >= 0.5), placed,
  released per cell; specifically report lift failures at (0,10) and (15,10) to
  document whether failures are reach or placement.
- Anchors (quoted, not pooled): (0,2)/(15,2) vs E1'/E2 already in E3 RESULTS
  §5; new cells have no external anchor, only internal cross-checks against
  E3's delta=2/8 columns via the shared seeds.

## 6. Verification and artifacts

- `verify_e3b.py` must pass: contract kind `e3b_envelope_supplement_not_method`,
  yaw/delta/tag/w_eff/budget/prereg hash/seeds, per-row controls 285, reset
  quaternion yaw < 1e-6, success == placed & released, failure_reason/success
  consistency, npz existence and sha256, source_sha256 drift (this prereg,
  `rollout_e3b.py`, the official rollout/worker/interface files, carrier pyc).
- Analysis output `analysis_e3b.json` with per-cell rates + Wilson,
  theta*(delta) + CIs, slope + bootstrap CI + skip count, GEE, stage table.
- RESULTS_E3B.md reports every cell, both decision categories, the registered
  prediction, and the reach-control outcome; no exclusion beyond the
  registered (0,10) rule; any deviation is listed.

## 7. Deviation policy

No post-hoc cell addition, no relabeling, no seed changes. If an episode
crashes, the run script refuses to overwrite and the crash is reported; the
cell is re-run only after the cause is fixed and disclosed. `rollout_e3b.py`
must not change after the first episode: its sha256 is embedded in every
contract and `verify_e3b.py` rejects a drift. If a change is unavoidable, all
E3b cells are re-run under the new script and the old ones are deleted.
