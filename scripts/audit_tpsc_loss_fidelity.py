"""CPU algebra audit of pinned BAS-VLA source, not a robot/policy experiment.

Run with a PyTorch environment and --source-root pointing to the verified
upstream snapshot. Only the two hash-pinned, inspected modules are imported.
The original per-timestep toy record is deliberately left unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import platform
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import torch

REVISION = "51f0dab5b2edab6539f3bccda7a04b3cb1d52a6c"
REPOSITORY = "https://github.com/NEBULIS-Lab/Beyond-Appearance-Shifts"
SOURCE_HASHES = {
    "bas_vla/breaking/training.py":
        "515f4ff3dd7eb6c7952c2cd887617e6065cbd06f252a19b3e00484a0c78b36b2",
    "bas_vla/breaking/residual_adapter.py":
        "d980768f256bd40fa08e13a6e829a48a0930d74bda66fe376c0887f5954bbc79",
    "docs/training.md":
        "87073acbbd03f9afb1ade57a396cbf064bfb495ed0bb98d90495a727dff49f43",
}


class IdentityAdapter(torch.nn.Module):
    def forward(self, action, features):
        return action


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    source_records = []
    for name, expected in SOURCE_HASHES.items():
        digest = hashlib.sha256((source_root / name).read_bytes()).hexdigest()
        if digest != expected:
            raise ValueError(f"unreviewed upstream source: {name}")
        source_records.append({
            "path": name,
            "sha256": digest,
            "url": f"{REPOSITORY}/blob/{REVISION}/{name}",
        })
    sys.path.insert(0, str(source_root))
    upstream = importlib.import_module("bas_vla.breaking.training")
    if Path(upstream.__file__).resolve() != source_root / "bas_vla/breaking/training.py":
        raise ValueError("upstream import resolved outside verified snapshot")
    cfg = upstream.training_config("paper_three_component", margin=0.5)

    def evaluate(name, clean, brk, prefix_coordinates, expected_loss):
        c = torch.tensor(clean, dtype=torch.float64, requires_grad=True)
        b = torch.tensor(brk, dtype=torch.float64, requires_grad=True)
        u = c.detach().clone().requires_grad_(True)
        features = torch.zeros((c.shape[0], 1), dtype=torch.float64)
        batch = {
            "clean_base": c, "control_base": u, "break_base": b,
            "expert": c.detach().clone(),
            "clean_feat": features, "control_feat": features, "break_feat": features,
        }
        total, metrics, _ = upstream.compute_losses(IdentityAdapter(), batch, cfg)
        total.backward()
        value = metrics["loss_margin_clean"]
        if not math.isclose(value, expected_loss, abs_tol=1e-12):
            raise AssertionError((name, value, expected_loss))
        if not math.isclose(float(total), value, abs_tol=1e-12):
            raise AssertionError("identity/expert fixture should isolate separation")
        flat_grad = b.grad.flatten()
        return {
            "name": name, "record_shape": list(c.shape),
            "clean": c.detach().tolist(), "control": u.detach().tolist(),
            "break": b.detach().tolist(), "metrics": metrics,
            "break_gradient": b.grad.tolist(),
            "direct_prefix_gradient_max_abs": float(flat_grad[:prefix_coordinates].abs().max()),
            "distance_per_record": torch.linalg.vector_norm(b - c, dim=-1).detach().tolist(),
        }

    a = [1., 1., 1., -1., -1., 0.]
    b = [1., 1., 1., 1., 1., 0.]
    cases = [
        evaluate("branch_inside_flattened_chunk", [a], [b], 3, 0.),
        evaluate("same_six_steps_as_six_records", [[x] for x in a], [[x] for x in b], 3, 1 / 3),
        evaluate("chunk_entirely_before_branch", [a[:3]], [b[:3]], 3, 0.5),
        evaluate("active_margin_but_exact_shared_prefix", [a],
                 [[1., 1., 1., -0.95, -0.95, 0.]], 3, 0.5 - math.sqrt(0.005)),
        evaluate("active_margin_with_tiny_prefix_difference", [a],
                 [[1.01, 1.01, 1.01, -0.95, -0.95, 0.]], 3, 0.5 - math.sqrt(0.0053)),
    ]
    # At an exact collision PyTorch chooses zero for the norm's subgradient.
    # Positive objective value is therefore not evidence of a nonzero update.
    for index in [0, 1, 2, 3]:
        if cases[index]["direct_prefix_gradient_max_abs"] != 0.:
            raise AssertionError("exact shared coordinates should have zero direct gradient")
    if cases[4]["direct_prefix_gradient_max_abs"] <= 0:
        raise AssertionError("nonzero prefix difference should expose active norm gradient")

    horizon_checks = []
    for horizon in [1, 4, 25, 50]:
        distance = math.sqrt(horizon) * 0.1
        check = evaluate(f"repeated_difference_h{horizon}", [[0.] * horizon],
                         [[0.1] * horizon], horizon, max(0., 0.5 - distance))
        horizon_checks.append({"horizon": horizon, "per_step_difference": 0.1,
                               "flattened_l2": distance,
                               "separation_loss": check["metrics"]["loss_margin_clean"]})

    loss_a = {"left": 0., "right": 1., "drop": 1.}
    loss_b = {"left": 1., "right": 0., "drop": 1.}
    viable_a = {k for k, value in loss_a.items() if value == 0.}
    viable_b = {k for k, value in loss_b.items() if value == 0.}
    if loss_a["drop"] != loss_b["drop"] or viable_a & viable_b:
        raise AssertionError("equal failure losses must not imply common viable action")

    root = Path(__file__).resolve().parents[1]
    report = {
        "kind": "source_faithful_algebra_and_cpu_autograd_not_policy_training",
        "repository": REPOSITORY, "revision": REVISION, "sources": source_records,
        "python": platform.python_version(), "torch": torch.__version__, "device": "cpu",
        "project_commit_at_run": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "original_toy_sha256": hashlib.sha256(
            (root / "experiments/so101/shared-prefix-separation-audit.json").read_bytes()).hexdigest(),
        "objective_config": asdict(cfg), "cases": cases, "horizon_checks": horizon_checks,
        "equal_loss_counterexample": {
            "loss_A": loss_a, "loss_B": loss_b, "same_candidate": "drop",
            "viable_A": sorted(viable_a), "viable_B": sorted(viable_b),
            "intersection": [], "same_candidate_success": False,
        },
        "checks": {
            "original_toy_per_step_sum": cases[1]["metrics"]["loss_margin_clean"] * 6,
            "faithful_flattened_chunk_loss": cases[0]["metrics"]["loss_margin_clean"],
            "hand_values_and_gradients_verified": True,
        },
        "conclusion": "Original toy is layout-conditional; it does not establish BAS-VLA prefix damage.",
        "limits": [
            "Uses upstream paper_three_component preset, not an evaluated upstream checkpoint.",
            "Identity adapter isolates output-space derivatives; shared neural parameters can couple coordinates.",
            "Exact-zero norm subgradient is the inspected PyTorch convention, not an impossibility theorem.",
            "Margin 0.5 reproduces the old toy, not upstream numeric default 0.15.",
            "No VLA rollout, optimizer training, success effect or novelty clearance is measured.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps(report["checks"]))


if __name__ == "__main__":
    main()
