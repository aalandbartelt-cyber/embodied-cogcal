# E3 PREREG — two-dimensional (yaw, lateral offset) tolerance envelope

Registered before any E3 rollout (smoke included; the smoke run is a harness
check, not data). Parent direction: `docs/direction-20261118-pose-prior/DIRECTION.md`
§4 "E3"; inputs: E2 `RESULTS.md` (yaw sweep at δ ~ U(0.5, 1.5) mm), E1′
`E1P_RESULT.md` (δ sweep at yaw 0). Instrument: `rollout_e3.py`, derived from
E2's audited runner with the δ jitter removed.

## 0. Question

Two one-dimensional tolerance curves exist for the frozen ACT policy:

- yaw at δ ≈ 1 mm: 19/20, 18/20, 18/20, 14/20, 1/20 at 0/2/5/10/15° (E2);
- offset at yaw 0: ≈ all success up to 10.3 mm, 16/20 at 13.8 mm, 8/20 at
  17.2 mm (E1′ bins b0–b5, per-axis shift convention).

The 2-D surface is unmeasured. E3 asks whether orientation tolerance is a
function of lateral offset: does the collapse angle θ\* shrink as δ grows
(interaction: one shared tolerance budget, boundary tilts), or is θ\* invariant
over the tested δ range (separable axes: orientation is its own failure axis,
E2's rejection of "θ ≡ δ" holds even at large δ)? This is the support test for
direction claim T3 ("(δ, θ) 二维包络").

δ convention is inherited unchanged: `shift = (δ, δ, 0)/1000 m`, i.e. δ is the
per-axis shift and the Euclidean lateral offset is δ√2. Labels are comparable
with E1′/E2 only under this convention.

## 1. Design

Grid 4 × 3, 20 paired seeds per cell (12920–12939), 240 episodes:

| | δ = 2 mm | δ = 8 mm | δ = 14 mm |
|---|---|---|---|
| θ = 0° | (0,2) | (0,8) | (0,14) |
| θ = 5° | (5,2) | (5,8) | (5,14) |
| θ = 10° | (10,2) | (10,8) | (10,14) |
| θ = 15° | (15,2) | (15,8) | (15,14) |

- δ is **exact per cell** (no uniform jitter): E2's 1 mm jitter made δ a nuisance
  draw inside every cell; E3 removes it so δ is a design variable and cells are
  comparable at fixed δ. Everything else is identical to E2/E4: frozen
  `official-act-20261116/final-20000.pt`, surviving carrier bytecode, 30 Hz,
  285 control steps, chunk 100 / execute 30, inputs `current_two_RGB` +
  `current_measured_q_rad`.
- Rotation is E2's mechanism: the free-joint quaternion is set at reset, so body
  and rendered image rotate together (natural scene; E4's `both` condition).
  No variant trees, no appearance manipulation.
- All 12 cells share the same 20 seeds (paired across cells). No episode
  exclusions, no interim stopping, no seed extension.

**Why these levels.** δ = 2 mm sits just above E2's baseline; δ = 8 mm sits near
E1′ b2 (19/20); δ = 14 mm sits near E1′ b4 (16/20), i.e. the steep part of the
offset curve, where an interaction has room to show. θ levels are E2's own.

## 2. Pre-run checks

1. `python -m py_compile rollout_e3.py`; contract records `kind =
   e3_yaw_delta_envelope_not_method`, yaw, exact δ, `prereg_sha256`,
   `control_budget = 285`, frozen XML sha, carrier pyc sha.
2. Smoke: 1 seed per cell (12 episodes), tag `smoke`. Pass requires per cell:
   no exception, 285 controls, 10 ACT queries, `reset_quat_wxyz` equal to
   `[cos(θ/2), 0, 0, sin(θ/2)]` within 1e-9, `delta_mm` recorded exactly, npz
   written and hashed. Any failure aborts E3 as a harness failure.
3. Workspace check at (0,14) and (0,2): the shift must not interpenetrate the
   robot at reset (`initial_penetrations()` is asserted by the runner) and the
   arm must reach: if the smoke cell (0,14) reports a reach/placement failure
   with `longest_two_finger_lift_s = 0`, δ = 14 is out of the reliable workspace
   and the grid is replaced by {2, 6, 10} mm for all cells, recorded here as
   amendment §2.1 before the full run; θ levels are not changed.

## 3. Predictions

- **H_inter** (interaction): θ\*(δ) decreases with δ; working guess
  θ\*(2) ≈ 11°, θ\*(8) ≈ 9°, θ\*(14) ≈ 6–7°.
- **H_sep** (separable): θ\*(δ) flat within ±2°; orientation collapse is not
  shifted by a 2 → 14 mm lateral offset.
- **Stage**: at (5,14) and (10,8) failures should mix pre-lift push-out and
  post-lift placement; at (15,·) lift failures dominate (E2: 13/20 closed
  without lifting); at (10,2) placement failures dominate among lifts.

## 4. Decision rules (registered)

Primary endpoint: rate per cell (`task_success`), Wilson 95% intervals, and the
boundary angle θ\*(δ) from linear interpolation of the cell rate between the
largest θ with p̂ ≥ 0.5 and its successor (crossing of 0.5). If p̂(0°) < 0.5 or
p̂(15°) ≥ 0.5 in a column, θ\* is censored for that column and no slope is
estimated.

Slope s = OLS of θ\* on δ (3 points). Uncertainty: 10⁴ cluster-bootstrap
resamples of the 20 seed indices, all 12 cells resampled jointly at the same
indices (pairing preserved); 2.5/97.5 percentiles.

- **PASS-E3a (interactive boundary)** iff s < 0 and the bootstrap 95% CI upper
  bound < 0.
- **PASS-E3b (separable)** iff the CI lies entirely inside ±2°/12 mm-equivalent
  (i.e. |s| < 2°/12 mm even at the CI edge).
- Otherwise **inconclusive**: report the surface and the CI; no 2-D claim is
  added, and the T3 claim stays as it is in DIRECTION.md §2 (flagged as
  unmeasured) rather than being silently upgraded.
- Secondary, supporting only (not a gate): logistic `success ~ θ_c + δ_c +
  θ_c:δ_c` fitted by GEE with seed clusters and exchangeable working
  correlation; interaction coefficient negative at one-sided p < 0.05.
- Stage decomposition: lift (`longest_two_finger_lift_s` ≥ 0.5), placed,
  released; per-cell counts, no model.

## 5. Controls and comparability

- (0,2) is the internal negative control: expected 0.85–0.95 (E1′ b0/b1 at
  θ = 0). If ≤ 0.60 the run is non-comparable and is reported as such.
- (15,2) vs E2 y15 (1/20): reference only, different seeds; a drift of more than
  5/20 is reported, not hidden.
- Any non-monotonicity in θ within a δ column (p̂(10°) < p̂(15°) by ≥ 5/20) is
  reported as measured; no cell is dropped or re-labeled.

## 6. Budget and boundaries

240 episodes, inference only, CPU, ≈15–25 min wall at 12-way parallelism with
`OMP_NUM_THREADS=2`. No GPU training, no checkpoint change, no seed extension,
no parameter search. E5′ (command-side q5 compensation) and E6 (external
validity point) are **not** authorized by this registration.

## 7. Analysis plan

1. Cell rates + Wilson 95% (12 rows), per-seed 12-bit pattern table.
2. θ\*(δ) per §4, slope + cluster bootstrap.
3. GEE interaction as secondary.
4. Stage table per cell.
5. E2/E1′ anchors quoted from their committed RESULTS with seeds/dates; not
   re-run and not pooled into E3 rates.
6. All 240 episodes used; verify_e3.py must pass before analysis is reported.
