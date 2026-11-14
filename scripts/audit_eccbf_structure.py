"""Audit current ECCBF algebra and public prompts; no policy or physics runs.

Run from the repository root in the analysis environment. The random vectors
below are numerical witnesses of an identity, not robot observations or results.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from cogcal.calibration import FactorialCalibrator  # noqa: E402
from probes.generators.eccbf_factorial import generate_records  # noqa: E402


def audit() -> dict:
    rng = np.random.default_rng(20261114)
    cells = {cell: rng.normal(size=(11, 6)) for cell in [(0, 0), (1, 0), (0, 1), (1, 1)]}
    means = {cell: values.mean(axis=0) for cell, values in cells.items()}
    calibrator = FactorialCalibrator.from_factorial(cells, threshold=0.5)
    corner_errors = []
    bilinear_errors = []
    for s, e in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        corrected, _ = calibrator.correct(np.zeros(6), semantic_score=s, execution_score=e)
        expected = means[(s, e)] - means[(0, 0)]
        corner_errors.append(float(np.max(np.abs(-corrected - expected))))
    for s, e in rng.uniform(0, 1, size=(1000, 2)):
        corrected, _ = calibrator.correct(np.zeros(6), semantic_score=float(s), execution_score=float(e))
        u, v = (s if s >= 0.5 else 0.0), (e if e >= 0.5 else 0.0)
        expected = (
            u * (1 - v) * (means[(1, 0)] - means[(0, 0)])
            + (1 - u) * v * (means[(0, 1)] - means[(0, 0)])
            + u * v * (means[(1, 1)] - means[(0, 0)])
        )
        bilinear_errors.append(float(np.max(np.abs(-corrected - expected))))

    records = generate_records(num_scenes=100, seed=42)
    neutral = {
        (row["scene_id"], row["execution_condition"]): row["instruction"]
        for row in records if row["semantic_condition"] == "neutral"
    }
    # The transformation sees only the prompt, never a target label or metadata.
    def canonicalize(prompt: str) -> str:
        return "Current task:" + prompt.split("Current task:", 1)[1]

    prompt_matches = sum(
        canonicalize(row["instruction"]) == neutral[(row["scene_id"], row["execution_condition"])]
        for row in records
    )
    paths = ["src/cogcal/calibration.py", "src/cogcal/metrics.py", "probes/generators/eccbf_factorial.py"]
    result = {
        "date": "2026-11-14",
        "scope": "structural audit only; synthetic algebra witness and public text; no VLA, physics, success rates or hardware",
        "source_sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths},
        "algebra": {
            "synthetic_seed": 20261114,
            "action_dimensions": 6,
            "samples_per_cell": 11,
            "corner_checks": 4,
            "corner_identity_max_abs_error": max(corner_errors),
            "continuous_score_checks": 1000,
            "bilinear_identity_max_abs_error": max(bilinear_errors),
            "meaning": "current correction is a gated bilinear conditional residual; at binary corners it is the cell mean minus baseline mean",
        },
        "prompts": {
            "generator_seed": 42,
            "scene_ids": 100,
            "records": len(records),
            "canonicalized_equal_to_matched_neutral": prompt_matches,
            "transform": "keep the substring beginning at the explicit Current task: marker",
            "transform_inputs": ["instruction string only"],
            "limitation": "exact for this generator; not evidence for arbitrary language, physical recovery or VLA task competence",
        },
    }
    assert max(corner_errors + bilinear_errors) < 1e-12
    assert prompt_matches == len(records)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "experiments/so101/novelty-structural-audit.json")
    args = parser.parse_args()
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
