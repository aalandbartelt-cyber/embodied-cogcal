"""Training/validation-only diagnostic of information in visible orange pixels.

Labels are used only for this offline diagnostic. This is not a rollout policy,
new method, hardware calibration, or causal explanation of neural failures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RECORDS = ROOT / "experiments/discovery/matched-bc-lowrate-20261114/collection/episodes.jsonl"


def color_features(rgb):
    value = np.asarray(rgb, dtype=np.float32)
    if value.shape != (2, 128, 128, 3):
        raise ValueError("matched two-camera RGB required")
    result = []
    yy, xx = np.mgrid[:128, :128]
    for image in value:
        red, green, blue = image[..., 0], image[..., 1], image[..., 2]
        mask = ((red > 150) & (green > 30) & (green < 200) & (blue < 120) &
                (red > 1.3 * green) & (green > 1.2 * blue))
        count = int(mask.sum())
        if count:
            result.extend([float(xx[mask].mean() / 127), float(yy[mask].mean() / 127), count / 16384])
        else:
            result.extend([0.0, 0.0, 0.0])
    return np.asarray(result, dtype=np.float32)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("new output required")
    rows = [json.loads(line) for line in RECORDS.read_text().splitlines()]
    x, y, identities = [], [], []
    for row in rows:
        path = Path(row["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("data changed")
        with np.load(path) as data:
            features = color_features(data["rgb"][0])
        x.append(features[[0, 1, 3, 4]])
        y.append(row["object_initial_xyz_m"][:2])
        identities.append({"seed": row["seed"], "split": row["split"],
                           "features": features.tolist()})
    x, y = np.asarray(x), np.asarray(y)
    train = np.asarray([r["split"] == "train" for r in rows])
    mean, std = x[train].mean(0), np.maximum(x[train].std(0), 1e-6)
    design = np.c_[(x - mean) / std, np.ones(len(x))]
    weights = np.linalg.solve(design[train].T @ design[train] + 1e-6 * np.eye(5), design[train].T @ y[train])
    prediction = design @ weights
    error = np.linalg.norm(prediction - y, axis=1)
    for i, row in enumerate(identities):
        row.update(predicted_xy_m=prediction[i].tolist(), target_xy_m=y[i].tolist(), error_m=float(error[i]))
    report = {
        "kind": "posthoc_train_val_visible_color_information_diagnostic_not_neural_causal_proof",
        "threshold_choice": "single fixed orange mask after inspecting initial camera preview; no val threshold search",
        "fit": "train-only ridge linear mapping of two RGB centroids to initial XY; ridge1e-6",
        "training_episodes": int(train.sum()), "validation_episodes": int((~train).sum()),
        "test_used": False, "rows": identities, "weights": weights.tolist(),
        "feature_mean": mean.tolist(), "feature_std": std.tolist(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "summary": {split: {"mean_error_m": float(error[mask].mean()),
                            "max_error_m": float(error[mask].max())}
                    for split, mask in [("train", train), ("val", ~train)]},
        "limits": ["Initial visible object only, fixed colors/lighting/camera and narrow workspace.",
                   "No closed-loop competence, no hardware precision result, no novel method.",
                   "Does not establish whether the CNN ignored location or why grasp failed."],
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"]))


if __name__ == "__main__":
    main()
