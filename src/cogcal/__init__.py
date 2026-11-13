"""Local tooling for the embodied cognitive-calibration workspace."""

__version__ = "0.1.0"

from .calibration import CalibrationDecision, FactorialCalibrator
from .metrics import FactorialEffects, factorial_effects, success_rate, wilson_interval

__all__ = [
    "CalibrationDecision",
    "FactorialCalibrator",
    "FactorialEffects",
    "factorial_effects",
    "success_rate",
    "wilson_interval",
]
