"""Minimal model-agnostic SO-101 MuJoCo scene interface.

This module deliberately does not call a VLA. It owns deterministic scene setup,
observation extraction and evaluator-side state access so model runners can be
added later without duplicating task semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

DEFAULT_SCENE = (
    Path(__file__).resolve().parents[2] / "simulation/so101/eccbf_factorial_scene.xml"
)
JOINT_NAMES = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper")


def freejoint_qpos(position: tuple[float, float, float]) -> np.ndarray:
    """Return MuJoCo free-joint qpos with an identity quaternion."""

    if len(position) != 3:
        raise ValueError("free-joint position must contain three coordinates")
    if not np.isfinite(position).all():
        raise ValueError("free-joint position must be finite")
    return np.asarray([*position, 1.0, 0.0, 0.0, 0.0], dtype=float)


@dataclass(frozen=True)
class ObjectPlacement:
    """Evaluator-side object placement for the deterministic tabletop scene."""

    red: tuple[float, float, float]
    blue: tuple[float, float, float]
    goal: tuple[float, float, float]

    def __post_init__(self) -> None:
        for name in ("red", "blue", "goal"):
            value = getattr(self, name)
            if len(value) != 3:
                raise ValueError(f"{name} position must contain three coordinates")
            if not np.isfinite(value).all():
                raise ValueError(f"{name} position must be finite")


DEFAULT_PLACEMENT = ObjectPlacement(
    red=(0.12, -0.12, 0.036),
    blue=(0.12, 0.12, 0.036),
    goal=(0.28, 0.0, 0.003),
)


def load_scene(scene_path: str | Path = DEFAULT_SCENE, mujoco_module: Any | None = None):
    """Load a scene and return `(model, data)` without starting a rollout."""

    if mujoco_module is None:
        try:
            import mujoco as mujoco_module
        except ImportError as exc:
            raise RuntimeError("mujoco is required for SO-101 simulation") from exc
    path = Path(scene_path)
    if not path.exists():
        raise FileNotFoundError(path)
    model = mujoco_module.MjModel.from_xml_path(str(path))
    data = mujoco_module.MjData(model)
    return model, data


def _set_free_body_pose(model: Any, data: Any, mujoco_module: Any, body_name: str, position: tuple[float, float, float]) -> None:
    body_id = mujoco_module.mj_name2id(model, mujoco_module.mjtObj.mjOBJ_BODY, body_name)
    if body_id < 0:
        raise ValueError(f"body not found: {body_name}")
    joint_id = int(model.body_jntadr[body_id])
    if joint_id < 0 or int(model.jnt_type[joint_id]) != int(mujoco_module.mjtJoint.mjJNT_FREE):
        raise ValueError(f"body is not free-jointed: {body_name}")
    qpos_address = int(model.jnt_qposadr[joint_id])
    data.qpos[qpos_address : qpos_address + 7] = freejoint_qpos(position)


def reset_scene(
    model: Any,
    data: Any,
    mujoco_module: Any | None = None,
    placement: ObjectPlacement = DEFAULT_PLACEMENT,
) -> None:
    """Reset robot/object state and forward the scene to a consistent observation."""

    if mujoco_module is None:
        import mujoco as mujoco_module
    mujoco_module.mj_resetData(model, data)
    _set_free_body_pose(model, data, mujoco_module, "red_object", placement.red)
    _set_free_body_pose(model, data, mujoco_module, "blue_object", placement.blue)
    model.body("goal_region").pos[:] = placement.goal
    mujoco_module.mj_forward(model, data)


def step_joint_targets(
    model: Any,
    data: Any,
    targets: Any,
    *,
    substeps: int = 1,
    mujoco_module: Any | None = None,
) -> None:
    """Execute six SO-101 joint position targets in radians, including hinge gripper.

    These are not LIBERO 7D Cartesian actions or normalized LeRobot motor values.
    Reject bad inputs rather than silently converting, clamping, or truncating.
    """
    vector = np.asarray(targets, dtype=float)
    if model.nu != 6 or vector.shape != (6,):
        raise ValueError("SO-101 action requires six joint targets in radians")
    if not np.isfinite(vector).all():
        raise ValueError("joint targets must be finite")
    if isinstance(substeps, bool) or not isinstance(substeps, int) or substeps < 1:
        raise ValueError("substeps must be a positive integer")
    ids = [model.actuator(name).id for name in JOINT_NAMES]
    limits = model.actuator_ctrlrange[ids]
    if np.any(vector < limits[:, 0]) or np.any(vector > limits[:, 1]):
        raise ValueError("joint targets exceed model actuator limits")
    if mujoco_module is None:
        import mujoco as mujoco_module
    data.ctrl[ids] = vector
    mujoco_module.mj_step(model, data, nstep=substeps)
    mujoco_module.mj_forward(model, data)


def policy_observation(
    model: Any, data: Any, renderer: Any, *, camera: str = "front_camera"
) -> dict[str, np.ndarray]:
    """Return only RGB and robot joints, excluding object poses and evaluator truth."""
    addresses = [model.jnt_qposadr[model.joint(name).id] for name in JOINT_NAMES]
    renderer.update_scene(data, camera=camera)
    return {
        "rgb": renderer.render().copy(),
        "joint_positions_rad": data.qpos[addresses].copy(),
    }


def evaluate_placement(model: Any, data: Any, target_color: str) -> bool:
    """Evaluator-only stable placement check, not proof of grasp/lift history.

    The complete object's axis-aligned footprint must lie in the goal, its bottom
    must be on the goal surface (12 mm tolerance), and velocities must be small.
    A future pick/place runner must additionally record lift and release events.
    """
    if target_color not in {"red", "blue"}:
        raise ValueError("target_color must be red or blue")
    geom = model.geom(f"{target_color}_object_geom")
    position = data.geom_xpos[geom.id]
    rotation = data.geom_xmat[geom.id].reshape(3, 3)
    half_size = np.abs(rotation) @ geom.size
    goal = model.geom("goal_geom")
    center = data.geom_xpos[goal.id]
    inside = np.all(np.abs(position[:2] - center[:2]) + half_size[:2] <= goal.size[:2])
    bottom = position[2] - half_size[2]
    on_surface = abs(bottom - (center[2] + goal.size[2])) <= 0.012
    body = model.body(f"{target_color}_object")
    joint = int(model.body_jntadr[body.id])
    address = int(model.jnt_dofadr[joint])
    velocity = data.qvel[address : address + 6]
    stable = np.linalg.norm(velocity[:3]) <= 0.02 and np.linalg.norm(velocity[3:]) <= 0.2
    return bool(inside and on_surface and stable and np.isfinite(velocity).all())
