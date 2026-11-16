# E4 PREREG — appearance vs collision decoupling at one fixed yaw

Registered before any E4 rollout. Parent direction:
`docs/direction-20261118-pose-prior/DIRECTION.md` §4 "E4"; background: E2
`RESULTS.md` §5 and `ANCHOR_PROBE.md` §5. Instrument: `make_variants.py` plus
`check_variants.py`, whose JSON evidence is committed alongside this file.

## 0. Question

At object yaw 15° and lateral offset δ ~ U(0.5, 1.5) mm, E2 measured 1/20
successes against 19/20 at 0°. Yaw changed two things at once: what the frozen
ACT policy sees (a rotated cube, off its demonstration distribution) and what the
jaw pads physically hit (rotated faces, effective width W(|cos t| + |sin t|)).
E4 asks which channel carries the failure. It is the confirm/kill test for the
contact-geometry claim C2 and the highest-priority experiment in DIRECTION.md §4.

## 1. Instrument

`variant-source` gives the cube body two coincident boxes:

| geom | role | group | mass | contype | rendered |
|---|---|---|---|---|---|
| `cube_look` | appearance | 0 | 0 | 0 | yes (mjv_defaultOption keeps groups 0–2) |
| `cube_visual` | collision | 3 | 0.020 | 2 | no (group 3 hidden) |

A cube's inertia is isotropic: 15° about z moves no mass, so the physics is the
same rigid body however the yaw is represented.

**Rotation is E2's mechanism.** Real object rotation is written into the free-joint
quaternion at reset (`+15°`), exactly as in E2's θ sweep, so the physical state
stays on E2's numerical path (cube `body_simple=1`, `body_iquat` identity,
isotropic inertia). That mechanism is what makes `both` identical to E2's θ=15 by
construction.

**Appearance is cancelled where needed in the compiled XML.** `cube_look`'s frame
gets a quat in the variant trees (runtime writes to `model.geom_quat` do not reach
the compiled frame in MuJoCo 4.0.1; verified on a minimal model). It is a massless,
non-colliding geom, so its frame cannot enter the dynamics: only the rendered
image changes. `check_variants.py` proves that empirically by replaying E2's
recorded θ=15 command traces step by step (max cube-pose difference 0.0 m over
285 control steps, 2 seeds, contact-rich), so "collision" differs from "both" in
appearance only, and "visual" from "deg0" in appearance only.

Condition table (each 20 paired seeds 12880–12899):

| condition | tree | body yaw | `cube_look` geom yaw | rendered yaw | collision yaw |
|---|---|---|---|---|---|
| `deg0` | deg0 | 0° | 0° | 0° | 0° |
| `visual` | visual | 0° | +15° | 15° | 0° |
| `collision` | collision | +15° | −15° | 0° | 15° |
| `both` | deg0 | +15° | 0° | 15° | 15° |

Sampling identical to E2: frozen `official-act-20261116/final-20000.pt`, surviving
carrier bytecode, 30 Hz control, 285 control steps, chunk 100 / execute 30; δ
drawn once per seed (keyed by seed only) and reused in all four conditions with
the same shift applied to the seed-randomized reset pose. Inference only; no
policy, checkpoint, or controller change.

## 2. Pre-run instrumentation checks (all passed; see `variants_check.json`)

1. Compiled `cube_look` quat and world frames carry the intended yaw per
   condition; `cube_visual` world yaw equals the body yaw.
2. `rgb(deg0)` == `rgb(upstream single-geom training model)` at the same state.
3. `rgb(collision)` == `rgb(deg0)` even though the object is rotated 15°: the
   appearance is the one the policy was trained on while the contact geometry
   is not.
4. `rgb(visual)` == `rgb(both)`: the visual condition renders exactly E2's θ=15
   appearance; and `rgb(visual)` != `rgb(deg0)`.
5. Physics-defining model arrays (mass, inertia, geom size/pos/contact params,
   pairs, joints, actuators) are equal across trees; differences are confined to
   `cube_look`'s compiled frame bookkeeping (`geom_quat`, `geom_sameframe`,
   names-buffer offsets); cube `body_simple=1` and `body_iquat` identity in all.
6. Open-loop replay of E2's θ=15 traces: the harness reproduces E2's recorded
   joint trajectory exactly; `both` vs `collision` and `deg0` vs `visual` agree
   on cube pose to 0.0 over 285 control steps (2 seeds).

Any failure here aborts E4 as an instrumentation failure, not as science.

## 3. Predictions

- **H_contact (C2)**: `collision` fails like `both`; `visual` succeeds like
  `deg0`. The failure is carried by contact geometry; appearance is not
  sufficient.
- **H_visual**: `visual` fails like `both`; `collision` succeeds like `deg0`.
  Behaviour is disturbed by the unseen orientation; C2 is downgraded to "visual
  sensitivity" per DIRECTION.md §4 kill criteria.
- **H_mixed**: intermediate cells; both channels contribute and C2 must be
  reported as a quantified mixture, not as the sole mechanism.

## 4. Decision rules (registered)

Counts of `task_success` per condition, 20 each.

- C2 **supported** iff `success(visual) − success(collision) ≥ 8` and a
  one-sided Fisher exact test on (visual, collision) gives p < 0.01.
- C2 **downgraded to visual sensitivity** iff `success(collision) −
  success(visual) ≥ 8` and the same one-sided Fisher criterion holds.
- Otherwise **mixed**: report cell counts with Wilson 95% intervals, the
  per-seed paired pattern across the four conditions, and the mixture explicitly.
- `both` is the internal positive control (E2's θ=15 ≈ 1/20), `deg0` the
  negative control (≈ 19/20). A control drifting by more than 5/20 from E2 makes
  the run non-comparable; it is then reported as such, not as a mechanism result.

## 5. Budget and boundaries

80 episodes, inference only, CPU, ≈10–15 min wall; no GPU training, no seed
extension, no policy change, no parameter search. E5′ (command-side yaw
compensation) is **not** authorized by this registration; it stays a separate,
user-approved decision (DIRECTION.md §6.2).
