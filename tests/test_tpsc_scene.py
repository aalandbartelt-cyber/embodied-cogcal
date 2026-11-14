from __future__ import annotations

from collections import Counter

import numpy as np
import pytest

from probes.generators.tpsc_pairs import generate_records, waypoint_targets
from simulation.so101.tpsc_scene import TpscPlacement


def _by_episode(records):
    return {record["episode_id"]: record for record in records}


def test_pilot_manifest_has_20_records_and_matched_shared_prefix():
    records = generate_records(mode="pilot", seed=42, episodes_per_branch=10)
    assert len(records) == 20
    assert Counter(record["branch"] for record in records) == {"left": 10, "right": 10}
    by_id = _by_episode(records)
    for index in range(10):
        left = by_id[f"shared_left_right_{index:04d}_left"]
        right = by_id[f"shared_left_right_{index:04d}_right"]
        assert left["red_pose"] == right["red_pose"]
        assert left["blue_pose"] == right["blue_pose"]
        assert left["goal_pose"] != right["goal_pose"]
        assert left["target_object"] == right["target_object"] == "red"
        assert left["barrier_pose"] is None and right["barrier_pose"] is None


def test_full_manifest_has_three_families_and_40_each():
    records = generate_records(mode="full", seed=42, episodes_per_branch=10)
    assert len(records) == 120
    assert Counter(record["family"] for record in records) == {
        "shared_prefix": 40,
        "no_common_prefix": 40,
        "multi_valid": 40,
    }
    multi = [record for record in records if record["family"] == "multi_valid"]
    assert all(record["barrier_pose"] is not None for record in multi)
    no_common = [record for record in records if record["family"] == "no_common_prefix"]
    assert {record["target_object"] for record in no_common} == {"red", "blue"}


def test_waypoint_targets_encode_family_structure():
    records = generate_records(mode="full", seed=42, episodes_per_branch=1)
    by_id = _by_episode(records)

    shared_left = dict(waypoint_targets(by_id["shared_left_right_0000_left"]))
    shared_right = dict(waypoint_targets(by_id["shared_left_right_0000_right"]))
    for name in ("above_object", "grasp", "lift"):
        assert shared_left[name] == shared_right[name]
    assert shared_left["above_goal"] != shared_right["above_goal"]

    no_common_red = dict(waypoint_targets(by_id["no_common_red_blue_0000_red"]))
    no_common_blue = dict(waypoint_targets(by_id["no_common_red_blue_0000_blue"]))
    assert no_common_red["above_object"] != no_common_blue["above_object"]

    multi_left = dict(waypoint_targets(by_id["multi_valid_center_0000_left"]))
    multi_right = dict(waypoint_targets(by_id["multi_valid_center_0000_right"]))
    for name in ("above_object", "grasp", "lift"):
        assert multi_left[name] == multi_right[name]
    assert multi_left["route"] != multi_right["route"]


def test_manifest_positions_stay_on_table():
    records = generate_records(mode="full", seed=42, episodes_per_branch=10)
    for record in records:
        for key in ("red_pose", "blue_pose"):
            x, y, z = record[key]
            assert 0.05 <= x <= 0.40
            assert -0.40 <= y <= 0.40
            assert z == pytest.approx(0.036)
        x, y, z = record["goal_pose"]
        assert 0.10 <= x <= 0.40
        assert -0.30 <= y <= 0.30
        assert z == pytest.approx(0.003)


def test_tpsc_placement_rejects_bad_target_and_barrier_size():
    with pytest.raises(ValueError, match="target_object"):
        TpscPlacement(red=(0.1, 0, 0.036), blue=(0.1, 0.2, 0.036), goal=(0.3, 0, 0.003), target_object="green")
    with pytest.raises(ValueError, match="barrier_size"):
        TpscPlacement(
            red=(0.1, 0, 0.036),
            blue=(0.1, 0.2, 0.036),
            goal=(0.3, 0, 0.003),
            barrier=(0.2, 0, 0.04),
            barrier_size=(0.02, 0.0, 0.04),
        )


def test_tpsc_scene_resets_objects_goal_and_barrier():
    mujoco = pytest.importorskip("mujoco")
    from simulation.so101.tpsc_scene import load_tpsc_scene, placement_from_record, reset_tpsc_scene

    records = generate_records(mode="full", seed=42, episodes_per_branch=1)
    shared = next(record for record in records if record["family"] == "shared_prefix")
    multi = next(record for record in records if record["family"] == "multi_valid")
    model, data = load_tpsc_scene(mujoco_module=mujoco)

    shared_placement = placement_from_record(shared)
    reset_tpsc_scene(model, data, shared_placement, mujoco)
    np.testing.assert_allclose(data.body("red_object").xpos, shared_placement.red, atol=1e-9)
    np.testing.assert_allclose(data.body("goal_region").xpos, shared_placement.goal, atol=1e-9)
    assert data.body("barrier").xpos[2] == pytest.approx(-0.5)

    multi_placement = placement_from_record(multi)
    reset_tpsc_scene(model, data, multi_placement, mujoco)
    np.testing.assert_allclose(data.body("barrier").xpos, multi_placement.barrier, atol=1e-9)
    np.testing.assert_allclose(model.geom("barrier_geom").size, multi_placement.barrier_size, atol=1e-9)


def test_tpsc_evaluator_flips_when_target_reaches_goal():
    mujoco = pytest.importorskip("mujoco")
    from simulation.so101.tpsc_scene import (
        evaluate_tpsc_success,
        load_tpsc_scene,
        placement_from_record,
        reset_tpsc_scene,
    )

    record = next(record for record in generate_records(mode="pilot") if record["branch"] == "left")
    placement = placement_from_record(record)
    model, data = load_tpsc_scene(mujoco_module=mujoco)
    reset_tpsc_scene(model, data, placement, mujoco)
    assert evaluate_tpsc_success(model, data, placement) is False

    body = model.body(f"{placement.target_object}_object")
    joint_id = int(model.body_jntadr[body.id])
    address = int(model.jnt_qposadr[joint_id])
    data.qpos[address : address + 3] = [placement.goal[0], placement.goal[1], 0.041]
    data.qpos[address + 3 : address + 7] = [1.0, 0.0, 0.0, 0.0]
    mujoco.mj_forward(model, data)
    assert evaluate_tpsc_success(model, data, placement) is True
