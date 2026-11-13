"""Factorized action calibration for the ECCBF hypothesis."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from .metrics import FactorialCell, factorial_effects


@dataclass(frozen=True)
class CalibrationDecision:
    """Audit record for one runtime correction decision."""

    triggered: bool
    semantic_score: float
    execution_score: float
    components: tuple[float, float, float]


@dataclass(frozen=True)
class FactorialCalibrator:
    """Experimental correction algebra with an explicit interaction component.

    Scores are observable conflict estimates supplied by a runtime detector.
    Ground-truth task labels are intentionally not accepted by this interface.
    Cells must be prevalidated target-relative residuals for correction use.
    Raw action contrasts alone do not identify cognitive bias or justify removal
    of the semantic component when a new instruction legitimately changes goals.
    """

    semantic_bias: np.ndarray
    execution_bias: np.ndarray
    interaction_bias: np.ndarray
    threshold: float = 0.5

    @classmethod
    def from_factorial(
        cls,
        cells: Mapping[FactorialCell, Sequence[Sequence[float]] | Sequence[float]],
        *,
        threshold: float = 0.5,
    ) -> FactorialCalibrator:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between zero and one")
        effects = factorial_effects(cells)
        return cls(effects.semantic, effects.execution, effects.interaction, threshold)

    @property
    def action_shape(self) -> tuple[int, ...]:
        return self.semantic_bias.shape

    def correct(
        self,
        action: Sequence[float],
        *,
        semantic_score: float,
        execution_score: float,
    ) -> tuple[np.ndarray, CalibrationDecision]:
        vector = np.asarray(action, dtype=float)
        if vector.shape != self.action_shape:
            raise ValueError(f"action shape {vector.shape} does not match {self.action_shape}")
        if not np.isfinite(vector).all():
            raise ValueError("action must be finite")
        if not 0.0 <= semantic_score <= 1.0 or not 0.0 <= execution_score <= 1.0:
            raise ValueError("conflict scores must be between zero and one")

        triggered = max(semantic_score, execution_score) >= self.threshold
        if not triggered:
            decision = CalibrationDecision(False, semantic_score, execution_score, (0.0, 0.0, 0.0))
            return vector.copy(), decision

        semantic_scale = semantic_score if semantic_score >= self.threshold else 0.0
        execution_scale = execution_score if execution_score >= self.threshold else 0.0
        interaction_scale = semantic_scale * execution_scale
        correction = (
            semantic_scale * self.semantic_bias
            + execution_scale * self.execution_bias
            + interaction_scale * self.interaction_bias
        )
        decision = CalibrationDecision(
            True,
            semantic_score,
            execution_score,
            (float(semantic_scale), float(execution_scale), float(interaction_scale)),
        )
        return vector - correction, decision
