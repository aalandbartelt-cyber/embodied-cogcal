from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from simulation.so101.scene import ObjectPlacement, freejoint_qpos


def test_freejoint_qpos_uses_unit_quaternion():
    np.testing.assert_allclose(
        freejoint_qpos((0.1, -0.2, 0.3)),
        [0.1, -0.2, 0.3, 1.0, 0.0, 0.0, 0.0],
    )


def test_object_placement_rejects_wrong_position_shape():
    with pytest.raises(ValueError, match="three coordinates"):
        ObjectPlacement(red=(0.0, 0.0), blue=(0.0, 0.0, 0.0), goal=(0.0, 0.0, 0.0))


def test_so101_scene_loads_and_resets_when_mujoco_is_available():
    mujoco = pytest.importorskip("mujoco")
    from simulation.so101.scene import load_scene, reset_scene

    root = Path(__file__).resolve().parents[1]
    model, data = load_scene(root / "simulation/so101/eccbf_factorial_scene.xml", mujoco)
    reset_scene(model, data, mujoco)

    assert model.nu == 6
    assert data.qpos.shape[0] == model.nq
