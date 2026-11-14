"""Scientific contract checks for the independent, matched BC carrier."""

import importlib.util
from pathlib import Path

import numpy as np

MODULE = Path(__file__).with_name("carrier.py")


def load():
    spec = importlib.util.spec_from_file_location("matched_carrier", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_split_seeds_never_overlap_and_have_fixed_counts():
    module = load()
    groups = [module.split_seeds(s) for s in ["train", "val", "test"]]
    assert [len(g) for g in groups] == [24, 8, 20]
    assert len(set(sum(groups, []))) == 52


def test_reset_is_valid_and_teacher_commands_use_finite_radians():
    module = load()
    carrier = module.Carrier(module.DEFAULT_SOURCE)
    observation = carrier.reset(4100)
    assert set(observation) == {"q_rad", "task"}
    assert observation["q_rad"].shape == (6,)
    assert np.isfinite(observation["q_rad"]).all()
    assert not carrier.initial_penetrations()
    actions = carrier.teacher_actions()
    assert actions.shape == (285, 6)
    assert np.isfinite(actions).all()
    assert np.all(actions >= carrier.low)
    assert np.all(actions <= carrier.high)
    before = carrier.observe()["q_rad"].copy()
    assert np.array_equal(before, observation["q_rad"])
    assert np.array_equal(carrier.teacher_actions(), actions)


def test_future_chunk_does_not_cross_episode_or_invent_final_labels():
    module = load()
    actions = np.arange(30, dtype=float).reshape(5, 6)
    chunk, mask = module.future_chunk(actions, 3, 4)
    assert chunk.shape == (4, 6)
    assert np.array_equal(chunk[:2], actions[3:])
    assert np.array_equal(mask, [True, True, False, False])


def test_clock_advances_exactly_thirty_hz_without_pose_writes():
    module = load()
    carrier = module.Carrier(module.DEFAULT_SOURCE)
    carrier.reset(4100)
    targets = carrier.teacher_actions()
    for action in targets[:3]:
        carrier.step(action)
    assert abs(carrier.data.time - 0.1) < carrier.model.opt.timestep
    assert carrier.controls == 3
    assert carrier.object_pose_writes_during_rollout == 0
