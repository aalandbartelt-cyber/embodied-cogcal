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


def freejoint_qpos(position: tuple[float, float, float]) -> np.ndarray:
    """Return MuJoCo free-joint qpos with an identity quaternion."""

    if len(position) != 3:
        raise ValueError("free-joint position must contain three coordinates")
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


DEFAULT_PLACEMENT = ObjectPlacement(
    red=(0.12, -0.12, 0.105),
    blue=(0.12, 0.12, 0.105),
    goal=(0.42, 0.0, 0.071),
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
    mujoco_module.mj_forward(model, data)
