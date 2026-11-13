from __future__ import annotations

import numpy as np
import pytest

from cogcal.calibration import FactorialCalibrator


def _cells() -> dict[tuple[int, int], np.ndarray]:
    return {
        (0, 0): np.array([0.0, 0.0]),
        (1, 0): np.array([2.0, 2.0]),
        (0, 1): np.array([3.0, 3.0]),
        (1, 1): np.array([10.0, 10.0]),
    }


def test_calibrator_corrects_all_active_components():
    calibrator = FactorialCalibrator.from_factorial(_cells(), threshold=0.5)

    corrected, decision = calibrator.correct(
        np.array([10.0, 10.0]), semantic_score=1.0, execution_score=1.0
    )

    np.testing.assert_allclose(corrected, [0.0, 0.0])
    assert decision.triggered is True
    assert decision.components == (1.0, 1.0, 1.0)


def test_calibrator_is_identity_below_gate_threshold():
    calibrator = FactorialCalibrator.from_factorial(_cells(), threshold=0.5)

    corrected, decision = calibrator.correct(
        np.array([10.0, 10.0]), semantic_score=0.2, execution_score=0.2
    )

    np.testing.assert_allclose(corrected, [10.0, 10.0])
    assert decision.triggered is False


def test_calibrator_rejects_action_shape_mismatch():
    calibrator = FactorialCalibrator.from_factorial(_cells())
    with pytest.raises(ValueError, match="action shape"):
        calibrator.correct(np.array([1.0, 2.0, 3.0]), semantic_score=1.0, execution_score=0.0)


def test_calibrator_rejects_missing_factorial_cells():
    with pytest.raises(ValueError, match="four factorial cells"):
        FactorialCalibrator.from_factorial({(0, 0): np.zeros(2)})
