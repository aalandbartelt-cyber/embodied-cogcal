# TPSC learned-policy pilot implementation plan

Goal: execute the user-approved 20-episode pilot with a real learned checkpoint on the local RTX 5070 Ti, preserving the original manifests and experiment records.

Architecture: keep MuJoCo 4.0.1 in cogcal-sim (Python 3.12); policy inference in an isolated Python 3.10 GPU environment. Only RGB, six measured joints, instruction and a registered random seed cross the process boundary. Evaluator object/goal state never crosses it.

1. [x] Review and commit original carrier, scene and scripted assets with review limitations (`af47281`).
2. [x] Freeze the specified dataset/model revisions; inspect gripper range, normalizer and camera features. Download to ignored directories.
3. [x] Write and run contract regressions for all-six-degree simulation adapter, unique repeated pairs, missing/duplicate rejection and capability gating.
4. [x] Implement a minimal policy worker that returns full action chunks and runtime statistics; run a real CUDA inference on the specified carrier sample before simulation.
5. [ ] Implement a simulation driver using the unchanged 20-row manifest, bounded actuator targets, clip counts and separate trace/result files. Original scripted JSON stays unchanged.
6. [ ] Run capability pilot. Preserve all rows, saved chunks, qpos and failures. Pair comparisons retain all ten repeats and common random seeds. Distinguish natural RGB differences from same-input language queries.
7. [ ] Assess go/no-go. If capability fails or units/cameras remain unverified, mark shared-prefix and uniform-separation damage as not identifiable. Do not implement outcome-conditioned support.
8. [ ] Update handoff, README, NEXT_A100_TPSC, progress/task plan; verify and commit.

Validation: pure contract tests, real checkpoint forward pass with shape/finiteness/resource measurements, simulation tests and a complete episode identity audit. Heavy public carrier training is distinct from TPSC paired-task evaluation. Twenty episodes are a capability screen, not a statistical power guarantee.
