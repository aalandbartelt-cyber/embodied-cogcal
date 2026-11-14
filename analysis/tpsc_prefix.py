"""Episode-level TPSC carrier diagnostics; no method or success claim from distance."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np


def simulation_degrees_to_rad(action: Any) -> np.ndarray:
    """Explicit *simulation-only* convention: all six channels are angular.

    This is not the real LeRobot motor-percentage gripper convention. Choosing
    this adapter remains an experimental assumption until carrier source or
    calibration proves it. It is recorded by the runner, never inferred at run time.
    """
    vector = np.asarray(action, dtype=float)
    if vector.ndim < 1 or vector.shape[-1] != 6 or not np.isfinite(vector).all():
        raise ValueError("finite six-channel simulation joint angles required")
    return np.deg2rad(vector)


def paired_report(episodes: list[dict], threshold_rad: float = 0.01) -> dict:
    if not np.isfinite(threshold_rad) or threshold_rad <= 0:
        raise ValueError("positive finite threshold required")
    if not episodes:
        raise ValueError("no episodes")
    ids: set[str] = set()
    groups: dict[str, dict] = defaultdict(dict)
    for row in episodes:
        if row["episode_id"] in ids or row["branch"] in groups[row["case_id"]]:
            raise ValueError("duplicate episode or branch")
        if type(row["task_success"]) is not bool:
            raise ValueError("task_success must be Boolean")
        ids.add(row["episode_id"])
        groups[row["case_id"]][row["branch"]] = row
    comparisons = []
    for case_id, pair in sorted(groups.items()):
        if set(pair) != {"left", "right"}:
            raise ValueError(f"{case_id}: missing paired branch")
        left, right = pair["left"], pair["right"]
        if left["action_seed"] != right["action_seed"]:
            raise ValueError(f"{case_id}: random seeds differ")
        a, b = (np.asarray(r["first_chunk_rad"], dtype=float) for r in [left, right])
        if a.shape != b.shape or a.ndim != 2 or a.shape[1] != 6 or not len(a):
            raise ValueError("paired chunks must have matching (H, 6) shape")
        if not np.isfinite(a).all() or not np.isfinite(b).all():
            raise ValueError("non-finite chunk")
        per_step = np.linalg.norm(a - b, axis=1)
        indices = np.flatnonzero(per_step > threshold_rad)
        onset = left.get("branch_onset_step")
        if onset != right.get("branch_onset_step"):
            raise ValueError("independent branch onset mismatch")
        if onset is not None and (type(onset) is not int or not 0 < onset <= len(a)):
            raise ValueError("branch onset must index the first chunk")
        executed_divergence = None
        executed_mean = None
        if any("executed_targets_rad" in row for row in [left, right]):
            if not all("executed_targets_rad" in row for row in [left, right]):
                raise ValueError("missing executed targets in one paired branch")
            executed_a, executed_b = (
                np.asarray(row["executed_targets_rad"], dtype=float) for row in [left, right]
            )
            if (
                executed_a.shape != executed_b.shape
                or executed_a.ndim != 2
                or executed_a.shape[1] != 6
                or not len(executed_a)
            ):
                raise ValueError("executed targets must match (T, 6)")
            if not np.isfinite(executed_a).all() or not np.isfinite(executed_b).all():
                raise ValueError("non-finite executed target")
            executed_distances = np.linalg.norm(executed_a - executed_b, axis=1)
            executed_indices = np.flatnonzero(executed_distances > threshold_rad)
            executed_divergence = int(executed_indices[0]) if len(executed_indices) else None
            executed_mean = float(executed_distances.mean())
        comparisons.append(
            {
                "case_id": case_id,
                "action_seed": left["action_seed"],
                "chunk_horizon": len(a),
                "first_chunk_l2_mean_rad": float(per_step.mean()),
                "first_chunk_l2_max_rad": float(per_step.max()),
                "first_action_divergence_step": int(indices[0]) if len(indices) else None,
                "first_executed_divergence_step": executed_divergence,
                "executed_l2_mean_rad": executed_mean,
                "branch_onset_step": onset,
                "before_branch_l2_mean_rad": float(per_step[:onset].mean()) if onset else None,
                "both_success": left["task_success"] and right["task_success"],
            }
        )
    successes = sum(r["task_success"] for r in episodes)
    verdict = "not_identified_no_independent_branch_onset"
    if successes != len(episodes):
        verdict = "not_identified_capability_not_established"
    return {
        "kind": "learned_policy_capability_screen_not_tpsc_effect",
        "episodes": len(episodes),
        "task_successes": successes,
        "success_rate": successes / len(episodes),
        "pairs": comparisons,
        "distance_threshold_rad": threshold_rad,
        "shared_prefix_verdict": verdict,
        "uniform_separation_verdict": "not_tested",
        "limitations": [
            "Natural rollout images can differ across branches; this does not isolate language.",
            "Distances describe the first predicted chunk, not an identified correct shared prefix.",
            "A separately validated branch onset and task competence are required for causal conclusions.",
        ],
    }
