import numpy as np
import pytest

from analysis.tpsc_prefix import paired_report, simulation_degrees_to_rad


def test_sim_carrier_has_all_six_degree_joints_including_negative_gripper():
    action = np.array([10.0, -20.0, 30.0, 40.0, -50.0, -10.0])
    np.testing.assert_allclose(simulation_degrees_to_rad(action), np.deg2rad(action))
    with pytest.raises(ValueError):
        simulation_degrees_to_rad([0.0] * 5)
    with pytest.raises(ValueError):
        simulation_degrees_to_rad([0.0, 0.0, 0.0, 0.0, 0.0, float("nan")])


def _episodes():
    return [
        {
            "episode_id": f"pair_{i:04d}_{branch}",
            "case_id": f"pair_{i:04d}",
            "branch": branch,
            "action_seed": 42,
            "task_success": True,
            "first_chunk_rad": [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [delta, 0.0, 0.0, 0.0, 0.0, 0.0]],
            "branch_onset_step": None,
        }
        for i in range(10)
        for branch, delta in [("left", 0.0), ("right", float(i) / 10.0)]
    ]


def test_report_keeps_all_ten_repeats_and_does_not_invent_semantic_onset():
    report = paired_report(_episodes(), threshold_rad=0.01)
    assert report["episodes"] == 20
    assert len(report["pairs"]) == 10
    assert report["pairs"][-1]["first_action_divergence_step"] == 1
    assert report["pairs"][0]["first_action_divergence_step"] is None
    assert report["shared_prefix_verdict"] == "not_identified_no_independent_branch_onset"


def test_duplicate_missing_or_different_random_seed_is_rejected():
    rows = _episodes()
    for bad in [rows + [rows[0]], rows[:-1]]:
        with pytest.raises(ValueError):
            paired_report(bad)
    rows[1]["action_seed"] = 99
    with pytest.raises(ValueError):
        paired_report(rows)


def test_failed_task_cannot_support_shared_prefix_damage():
    rows = _episodes()
    rows[0]["task_success"] = False
    report = paired_report(rows)
    assert report["task_successes"] == 19
    assert report["shared_prefix_verdict"] == "not_identified_capability_not_established"
    assert report["uniform_separation_verdict"] == "not_tested"


def test_future_chunk_divergence_is_not_executed_action_divergence():
    rows = _episodes()[:2]
    rows[0]["first_chunk_rad"] = np.zeros((50, 6)).tolist()
    b = np.zeros((50, 6))
    b[20, 0] = 1.0
    rows[1]["first_chunk_rad"] = b.tolist()
    for row in rows:
        row["executed_targets_rad"] = np.zeros((10, 6)).tolist()
    pair = paired_report(rows)["pairs"][0]
    assert pair["first_action_divergence_step"] == 20
    assert pair["first_executed_divergence_step"] is None
