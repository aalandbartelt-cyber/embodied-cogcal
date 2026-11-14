"""Deterministic TPSC paired-task scene interface for the SO-101 MuJoCo model.

This module owns scene setup and evaluator-side state only.  It does not call a
VLA, does not read success labels for the policy, and does not implement the
TPSC method.  The three task families are:

- shared-prefix: same object, same early action, different goal;
- no-common-prefix: different target objects/approach from the first frame;
- multi-valid: same object/goal, two physically valid routes around a barrier.

See ``experiments/so101/tpsc-data-protocol.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from simulation.so101.scene import (
    evaluate_placement,
    freejoint_qpos,
    load_scene,
    policy_observation,
    step_joint_targets,
)

DEFAULT_TPSC_SCENE = Path(__file__).resolve().parents[2] / "simulation/so101/tpsc_scene.xml"
TASK_FAMILIES = ("shared_prefix", "no_common_prefix", "multi_valid")


@dataclass(frozen=True)
class TpscPlacement:
    """Evaluator-side placement for one TPSC episode."""

    red: tuple[float, float, float]
    blue: tuple[float, float, float]
    goal: tuple[float, float, float]
    target_object: str = "red"
    barrier: tuple[float, float, float] | None = None
    barrier_size: tuple[float, float, float] = (0.02, 0.06, 0.04)

    def __post_init__(self) -> None:
        if self.target_object not in {"red", "blue"}:
            raise ValueError("target_object must be red or blue")
        for name in ("red", "blue", "goal"):
            value = getattr(self, name)
            if len(value) != 3:
                raise ValueError(f"{name} position must contain three coordinates")
            if not np.isfinite(value).all():
                raise ValueError(f"{name} position must be finite")
        if self.barrier is not None:
            if len(self.barrier) != 3:
                raise ValueError("barrier position must contain three coordinates")
            if not np.isfinite(self.barrier).all():
                raise ValueError("barrier position must be finite")
        if len(self.barrier_size) != 3 or not np.isfinite(self.barrier_size).all():
            raise ValueError("barrier_size must contain three finite values")
        if np.any(np.asarray(self.barrier_size) <= 0):
            raise ValueError("barrier_size must be positive")


def _set_free_body_pose(
    model: Any,
    data: Any,
    mujoco_module: Any,
    body_name: str,
    position: tuple[float, float, float],
) -> None:
    body_id = mujoco_module.mj_name2id(model, mujoco_module.mjtObj.mjOBJ_BODY, body_name)
    if body_id < 0:
        raise ValueError(f"body not found: {body_name}")
    joint_id = int(model.body_jntadr[body_id])
    if joint_id < 0 or int(model.jnt_type[joint_id]) != int(mujoco_module.mjtJoint.mjJNT_FREE):
        raise ValueError(f"body is not free-jointed: {body_name}")
    qpos_address = int(model.jnt_qposadr[joint_id])
    data.qpos[qpos_address : qpos_address + 7] = freejoint_qpos(position)


def reset_tpsc_scene(
    model: Any,
    data: Any,
    placement: TpscPlacement,
    mujoco_module: Any | None = None,
) -> None:
    """Reset objects/goal/barrier and forward the scene to a consistent state."""

    if mujoco_module is None:
        import mujoco as mujoco_module
    mujoco_module.mj_resetData(model, data)
    _set_free_body_pose(model, data, mujoco_module, "red_object", placement.red)
    _set_free_body_pose(model, data, mujoco_module, "blue_object", placement.blue)
    model.body("goal_region").pos[:] = placement.goal
    barrier_body = model.body("barrier")
    barrier_geom = model.geom("barrier_geom")
    if placement.barrier is None:
        barrier_body.pos[:] = (0.0, 0.0, -0.5)
    else:
        barrier_body.pos[:] = placement.barrier
        barrier_geom.size[:] = placement.barrier_size
    mujoco_module.mj_forward(model, data)


def evaluate_tpsc_success(model: Any, data: Any, placement: TpscPlacement) -> bool:
    """Evaluator-only stable goal predicate for the target object."""
    return evaluate_placement(model, data, placement.target_object)


def observation(model: Any, data: Any, renderer: Any, *, camera: str = "front_camera"):
    """RGB + six SO-101 joint positions; no object/goal truth."""
    return policy_observation(model, data, renderer, camera=camera)


def placement_from_record(record: dict[str, Any]) -> TpscPlacement:
    """Build a scene placement from one manifest record."""
    barrier = record.get("barrier_pose")
    barrier_size = record.get("barrier_size")
    return TpscPlacement(
        red=tuple(record["red_pose"]),
        blue=tuple(record["blue_pose"]),
        goal=tuple(record["goal_pose"]),
        target_object=record["target_object"],
        barrier=None if barrier is None else tuple(barrier),
        barrier_size=(0.02, 0.06, 0.04) if barrier_size is None else tuple(barrier_size),
    )


def load_tpsc_scene(scene_path: str | Path = DEFAULT_TPSC_SCENE, mujoco_module: Any | None = None):
    """Load the TPSC scene without starting a rollout."""
    return load_scene(scene_path, mujoco_module)


__all__ = [
    "DEFAULT_TPSC_SCENE",
    "TASK_FAMILIES",
    "TpscPlacement",
    "evaluate_tpsc_success",
    "load_tpsc_scene",
    "observation",
    "placement_from_record",
    "reset_tpsc_scene",
    "step_joint_targets",
]
