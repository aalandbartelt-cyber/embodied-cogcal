from __future__ import annotations

import numpy as np
import pytest

from scripts.run_so101_scripted_rollout import interpolate_controls


def test_interpolate_controls_includes_start_and_end():
    start = np.zeros(6)
    end = np.ones(6)
    controls = interpolate_controls(start, end, steps=4)

    assert controls.shape == (4, 6)
    np.testing.assert_allclose(controls[0], start)
    np.testing.assert_allclose(controls[-1], end)


def test_interpolate_controls_rejects_invalid_steps():
    try:
        interpolate_controls(np.zeros(2), np.ones(2), steps=1)
    except ValueError as exc:
        assert "steps" in str(exc)
    else:
        raise AssertionError("steps=1 should be rejected")


def test_interpolate_controls_rejects_nonfinite_actions():
    with pytest.raises(ValueError, match="finite"):
        interpolate_controls(np.zeros(6), np.full(6, np.nan), steps=4)


def test_scripted_smoke_writes_timed_step_trace_without_task_scores(tmp_path):
    import json

    mujoco = pytest.importorskip("mujoco")
    from scripts.run_so101_scripted_rollout import run_rollout
    from simulation.so101.scene import DEFAULT_SCENE

    video = tmp_path / "smoke.mp4"
    trace = tmp_path / "steps.jsonl"
    run_rollout(DEFAULT_SCENE, video, trace, steps=4)
    rows = [json.loads(line) for line in trace.read_text().splitlines()]
    assert len(rows) == 4
    assert all(row["record_type"] == "step" for row in rows)
    assert all(row["experiment_kind"] == "plumbing_smoke" for row in rows)
    assert all("task_success" not in row for row in rows)
    assert rows[-1]["sim_time_s"] == pytest.approx(4 / 30, abs=0.002)
    assert video.stat().st_size > 0
    model = mujoco.MjModel.from_xml_path(str(DEFAULT_SCENE))
    assert all(len(row["action"]) == model.nu for row in rows)


def test_scripted_smoke_rejects_hardlinked_input_output(tmp_path):
    pytest.importorskip("mujoco")
    from scripts.run_so101_scripted_rollout import run_rollout

    scene = tmp_path / "scene.xml"
    scene.write_text("original scene")
    trace = tmp_path / "trace.jsonl"
    trace.hardlink_to(scene)
    with pytest.raises(ValueError, match="paths must differ"):
        run_rollout(scene, tmp_path / "movie.mp4", trace, steps=4)
    assert scene.read_text() == "original scene"
