# E4 RESULTS — appearance vs collision decoupling at one fixed yaw

> 勘误（2026-11-17，未改动本文件结论段）：注册对比 `visual − collision` 为同时翻转两个因素的双重差分，且 `both` 实为 1/20 而非全失败。见 [E4_DECOUPLING_AUDIT_20261117.md](E4_DECOUPLING_AUDIT_20261117.md)。

Status: **run complete, verified**. 80 episodes, inference only, frozen ACT
checkpoint, same carrier bytecode and control budget as E2. Registration:
`PREREG.md` (unchanged since before the 20-seed runs; its sha is recorded in
every `contract.json`). Instrument: `make_variants.py`, `check_variants.py`
(evidence in `variants.json`, `variants_check.json`). Outputs: `runs/e4-*`,
`analysis.json`, `verify_e4.json`.

## 1. Result

Object yaw 15°, lateral offset δ ~ U(0.5, 1.5) mm, 20 paired seeds 12880–12899.

| condition | tree | body yaw | rendered yaw | collision yaw | success | Wilson 95% |
|---|---|---|---|---|---|---|
| `deg0` | deg0 | 0° | 0° | 0° | **18/20** | [0.699, 0.972] |
| `visual` | visual | 0° | 15° | 0° | **20/20** | [0.839, 1.000] |
| `collision` | collision | 15° | 0° | 15° | **0/20** | [0.000, 0.161] |
| `both` | deg0 | 15° | 15° | 15° | **1/20** | [0.009, 0.236] |

Registered contrast `success(visual) − success(collision) = +20`, one-sided
Fisher exact p = 7.3e-12 → **C2 supported**. Reverse contrast p = 1.0.

Paired patterns (deg0, visual, collision, both): `1100` ×17, `0100` ×2,
`1101` ×1. Every seed fails `collision` and `both`; no seed fails `visual` or
fails `deg0` while passing `collision`.

### Controls

`both` reproduces E2's θ=15 cell exactly (1/20 here; 1/20 in E2) and `deg0`
lands at 18/20 against E2's 19/20: the positive control is on the nose and the
negative control is inside the registered ±5/20 drift band (Δ = −1/20), so the
run is comparable to E2 by the pre-registered rule.

### Interpretation

At W(15°) ≈ 1.32× the face width and δ ≈ 1 mm:

- The frozen policy is **not** disturbed by a 15°-rotated cube in its input:
  given an appearance-only rotation it succeeds 20/20, statistically
  indistinguishable from 0°. Its behaviour is carried by the object's *position*
  in the image, not by its in-plane appearance.
- The failure is carried by **contact geometry**: rotate only the rigid body
  under an identity-looking cube and the cell collapses to 0/20 — exactly where
  `both` sits. Note 17/20 seeds show the full `1100` pattern: the split is not a
  marginal effect but a per-seed determinism, driven by where the jaw pads land
  relative to the rotated faces.
- C2 therefore survives its kill test in the strongest form DIRECTION.md §4
  allowed: appearance is *not* the channel, contact geometry *is*. C2's earlier
  "visual sensitivity" downgrade path is now closed.

One caveat to carry forward rather than bury: `visual` = 20/20 is a ceiling
cell; it constrains the appearance channel only at 15°. It says nothing about
larger appearance rotations, and nothing about whether the policy uses
orientation at low contrast — only that at this angle the rendered orientation
is not what breaks the transfer.

## 2. Validity gates (all green)

- Instrumentation: 842/842 checks in `verify_e4.py`; `check_variants.py` passed
  before the run, including open-loop replay of E2's θ=15 traces with cube-pose
  difference exactly 0.0 over 285 control steps (2 seeds).
- Registered contract: every condition compiled the registered XML
  (`model_xml_sha256`), used seeds 12880–12899, δ identical across conditions per
  seed, same checkpoint/carrier/training contract hash, prereg and instrumentation
  hashes unchanged.
- Rendering: at step 0 of every seed `rgb(collision) == rgb(deg0)` and
  `rgb(visual) == rgb(both)`, while `rgb(visual) != rgb(deg0)`: each condition
  renders exactly what its cell says it renders.
- Episodes: 285 control steps, 9.5 s sim each, `object_pose_writes_during_rollout
  == 0`, artifacts hash-checked, all physics arrays finite.
- 2-seed smoke runs per condition (`smoke/`, tag `smoke`) exercised the pipeline
  before the registered runs; they are excluded from every number above.

## 3. What this changes

- DIRECTION.md §4's C2 kill/confirm test is answered: **confirm**. The
  appearance-vs-contact split is clean at 20/20 vs 0/20 with a per-seed pattern,
  not an aggregate coincidence.
- The measurement case (C3) is unaffected; E5′ (command-side yaw compensation)
  now has a defined target mechanism: compensate the *grasp geometry* rather than
  the image, and its 15° success bar (>50%) is still the registered kill rule for
  C4.
- E3 (δ-only sweep) remains the natural next cell: E4 fixes δ ~ U(0.5, 1.5) and
  one angle; E3 asks how the collision channel scales with δ at fixed yaw.

Next decisions (awaiting the user, per DIRECTION.md §6): run E3 now; whether E5′
may touch `rollout_e2.py`'s command side with its 20–40 episode budget; and
whether to price E6 (price only, no execution).
