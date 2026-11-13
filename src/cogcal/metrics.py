"""Metrics for the ECCBF factorial calibration experiments."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import sqrt

import numpy as np
from scipy.stats import norm

FactorialCell = tuple[int, int]


@dataclass(frozen=True)
class FactorialEffects:
    """Mean action-space effects from a 2x2 semantic/execution design."""

    baseline: np.ndarray
    semantic: np.ndarray
    execution: np.ndarray
    interaction: np.ndarray


def _as_mean_vector(values: Sequence[Sequence[float]] | Sequence[float]) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim == 1:
        return array
    if array.ndim == 2:
        return array.mean(axis=0)
    raise ValueError("factorial cell values must be one- or two-dimensional")


def factorial_effects(cells: Mapping[FactorialCell, Sequence[Sequence[float]] | Sequence[float]]) -> FactorialEffects:
    """Compute main and interaction effects from matched 2x2 cell observations.

    The first key component is the semantic condition and the second is the
    execution condition. Both components must be coded as 0/1.
    """

    required = {(0, 0), (1, 0), (0, 1), (1, 1)}
    if set(cells) != required:
        raise ValueError("factorial effects require exactly four factorial cells")

    means = {cell: _as_mean_vector(values) for cell, values in cells.items()}
    shape = means[(0, 0)].shape
    if any(value.shape != shape for value in means.values()):
        raise ValueError("all factorial cells must have the same action shape")

    baseline = means[(0, 0)]
    semantic = means[(1, 0)] - baseline
    execution = means[(0, 1)] - baseline
    interaction = means[(1, 1)] - means[(1, 0)] - means[(0, 1)] + baseline
    return FactorialEffects(baseline, semantic, execution, interaction)


def success_rate(successes: Sequence[bool | int]) -> float:
    """Return the fraction of successful episodes."""

    if len(successes) == 0:
        raise ValueError("successes must contain at least one episode")
    return float(np.asarray(successes, dtype=float).mean())


def wilson_interval(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    """Return a Wilson score interval for a binomial success rate."""

    if trials <= 0:
        raise ValueError("trials must be positive")
    if successes < 0 or successes > trials:
        raise ValueError("successes must be between zero and trials")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between zero and one")

    z = float(norm.ppf(0.5 + confidence / 2.0))
    p = successes / trials
    denominator = 1.0 + z**2 / trials
    center = (p + z**2 / (2.0 * trials)) / denominator
    radius = z * sqrt((p * (1.0 - p) + z**2 / (4.0 * trials)) / trials) / denominator
    return max(0.0, center - radius), min(1.0, center + radius)
