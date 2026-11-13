from __future__ import annotations

import numpy as np

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
