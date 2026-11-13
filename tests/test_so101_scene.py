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


def test_reset_applies_goal_and_restores_velocities():
    mujoco = pytest.importorskip("mujoco")
    from simulation.so101.scene import load_scene, reset_scene

    model, data = load_scene(mujoco_module=mujoco)
    placement = ObjectPlacement(red=(0.16, -0.12, 0.036), blue=(0.16, 0.12, 0.036), goal=(0.28, 0.03, 0.003))
    data.qvel[:] = 0.5
    reset_scene(model, data, mujoco, placement)

    np.testing.assert_allclose(data.body("red_object").xpos, placement.red)
    np.testing.assert_allclose(data.body("goal_region").xpos, placement.goal)
    np.testing.assert_allclose(data.qvel, 0)


@pytest.mark.parametrize("position", [(np.nan, 0, 0), (0, np.inf, 0)])
def test_object_placement_rejects_nonfinite_values(position):
    with pytest.raises(ValueError, match="finite"):
        ObjectPlacement(red=position, blue=(0, 0, 0), goal=(0, 0, 0))


def test_runtime_joint_action_rejects_openvla_seven_dimensional_action():
    mujoco = pytest.importorskip("mujoco")
    from simulation.so101.scene import load_scene, step_joint_targets

    model, data = load_scene(mujoco_module=mujoco)
    with pytest.raises(ValueError, match="six joint targets"):
        step_joint_targets(model, data, np.zeros(7), mujoco_module=mujoco)


def test_runtime_joint_action_steps_time_and_rejects_invalid_targets():
    mujoco = pytest.importorskip("mujoco")
    from simulation.so101.scene import load_scene, step_joint_targets

    model, data = load_scene(mujoco_module=mujoco)
    step_joint_targets(model, data, np.zeros(6), substeps=2, mujoco_module=mujoco)
    assert data.time == pytest.approx(2 * model.opt.timestep)
    with pytest.raises(ValueError, match="finite"):
        step_joint_targets(model, data, np.full(6, np.nan), mujoco_module=mujoco)
    with pytest.raises(ValueError, match="limits"):
        step_joint_targets(model, data, np.full(6, 100), mujoco_module=mujoco)


def test_evaluator_distinguishes_correct_and_wrong_object():
    mujoco = pytest.importorskip("mujoco")
    from simulation.so101.scene import evaluate_placement, load_scene, reset_scene

    model, data = load_scene(mujoco_module=mujoco)
    placement = ObjectPlacement(red=(0.28, 0, 0.041), blue=(0.12, 0.12, 0.036), goal=(0.28, 0, 0.003))
    reset_scene(model, data, mujoco, placement)
    assert evaluate_placement(model, data, "red") is True
    assert evaluate_placement(model, data, "blue") is False
    joint_id = model.body("red_object").jntadr[0]
    data.qvel[model.jnt_dofadr[joint_id]] = 1.0
    assert evaluate_placement(model, data, "red") is False


def test_policy_observation_has_rgb_and_only_six_robot_joint_values():
    mujoco = pytest.importorskip("mujoco")
    from simulation.so101.scene import load_scene, policy_observation, reset_scene

    model, data = load_scene(mujoco_module=mujoco)
    reset_scene(model, data, mujoco)
    with mujoco.Renderer(model, height=96, width=128) as renderer:
        observation = policy_observation(model, data, renderer)
    assert set(observation) == {"rgb", "joint_positions_rad"}
    assert observation["rgb"].shape == (96, 128, 3)
    assert observation["joint_positions_rad"].shape == (6,)
    assert observation["rgb"].dtype == np.uint8


def test_probe_placements_materialize_same_physics_in_all_four_conditions():
    mujoco = pytest.importorskip("mujoco")
    from probes.generators.eccbf_factorial import generate_records
    from simulation.so101.scene import load_scene, reset_scene

    model, data = load_scene(mujoco_module=mujoco)
    states = []
    for record in generate_records(num_scenes=1, seed=42):
        placement = ObjectPlacement(**record["scene_metadata"]["placements"])
        reset_scene(model, data, mujoco, placement)
        states.append(data.qpos.copy())
        np.testing.assert_allclose(data.body("red_object").xpos, placement.red)
    for state in states[1:]:
        np.testing.assert_array_equal(state, states[0])
