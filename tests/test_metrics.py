from __future__ import annotations

import numpy as np
import pytest

from cogcal.metrics import factorial_effects, success_rate, wilson_interval


def test_factorial_effects_identifies_semantic_execution_and_interaction_terms():
    cells = {
        (0, 0): np.array([[0.0, 0.0], [0.0, 0.0]]),
        (1, 0): np.array([[2.0, 2.0], [2.0, 2.0]]),
        (0, 1): np.array([[3.0, 3.0], [3.0, 3.0]]),
        (1, 1): np.array([[10.0, 10.0], [10.0, 10.0]]),
    }

    effects = factorial_effects(cells)

    np.testing.assert_allclose(effects.semantic, [2.0, 2.0])
    np.testing.assert_allclose(effects.execution, [3.0, 3.0])
    np.testing.assert_allclose(effects.interaction, [5.0, 5.0])


def test_factorial_effects_rejects_missing_cells():
    with pytest.raises(ValueError, match="four factorial cells"):
        factorial_effects({(0, 0): np.zeros(2)})


def test_success_rate_and_wilson_interval_are_bounded():
    assert success_rate([True, False, True, True]) == pytest.approx(0.75)
    low, high = wilson_interval(3, 4)
    assert 0.0 <= low <= 0.75 <= high <= 1.0


def test_success_rate_rejects_empty_trials():
    with pytest.raises(ValueError, match="at least one"):
        success_rate([])


@pytest.mark.parametrize("values", [[], [[np.nan, 0.0]], [[np.inf, 0.0]], [[], []]])
def test_factorial_effects_rejects_empty_or_nonfinite_cells(values):
    cells = {key: [[0.0, 0.0]] for key in [(0, 0), (1, 0), (0, 1), (1, 1)]}
    cells[(1, 1)] = values
    with pytest.raises(ValueError, match="nonempty|finite"):
        factorial_effects(cells)
