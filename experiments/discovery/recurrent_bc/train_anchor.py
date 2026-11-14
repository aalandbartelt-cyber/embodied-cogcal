"""Fixed ordinary BC training with initial RGB color features."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from anchor_policy import AnchorBC
from color_localization_audit import color_features
from train import NORMALIZER, NORMALIZER_SHA, RECORDS, load_episodes, masked_mse, sha

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/discovery/anchor-bc-20261114/training"
CHECKPOINT = ROOT / "checkpoints/anchor-bc-20261114/final-2000.pt"


def initial_features(rows, device):
    values = []
    for row in rows:
        path = Path(row["path"])
        if sha(path) != row["sha256"]:
            raise ValueError("data changed")
        with np.load(path) as episode:
            values.append(color_features(episode["rgb"][0]))
    return torch.from_numpy(np.stack(values)).to(device)


def main():
    if RUN.exists() or CHECKPOINT.exists():
        raise FileExistsError("fresh fixed-final experiment required")
    if sha(NORMALIZER) != NORMALIZER_SHA:
        raise ValueError("normalizer source changed")
    rows = [json.loads(line) for line in (RECORDS / "episodes.jsonl").read_text().splitlines()]
    groups = {s: [r for r in rows if r["split"] == s] for s in ["train", "val"]}
    assert {r["seed"] for r in groups["train"]} == set(range(4100, 4124))
    assert {r["seed"] for r in groups["val"]} == set(range(5100, 5108))
    assert len(rows) == 32 and all(r["task_success"] for r in rows)
    RUN.mkdir(parents=True, exist_ok=False)
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(42)
    np.random.seed(42)
    torch.backends.cudnn.benchmark = False
    device = torch.device("cuda")
    inherited = torch.load(NORMALIZER, map_location=device, weights_only=True)
    stats = {key: inherited[key] for key in ["q_mean", "q_std", "a_mean", "a_std"]}
    train, val = load_episodes(groups["train"], device), load_episodes(groups["val"], device)
    anchor_train = initial_features(groups["train"], device)
    anchor_val = initial_features(groups["val"], device)
    stats["anchor_mean"] = anchor_train.mean(0)
    stats["anchor_std"] = anchor_train.std(0).clamp_min(1e-4)
    anchor_train = (anchor_train - stats["anchor_mean"]) / stats["anchor_std"]
    anchor_val = (anchor_val - stats["anchor_mean"]) / stats["anchor_std"]
    net = AnchorBC().to(device)
    optimizer = torch.optim.Adam(net.parameters(), lr=.001)
    sampler = torch.Generator(device=device).manual_seed(42)
    contract = {
        "kind": "ordinary_initial_rgb_feature_bc_capability_not_method", "seed": 42,
        "steps": 2000, "batch_episodes": 8, "lr": .001, "execute": 6, "horizon": 30,
        "camera_query_hz": 5, "control_hz": 30, "queries_per_episode": 48,
        "test_used": False, "selection": "fixed_final_2000_not_best",
        "initial_color_features": "fixed mask from prior train/val diagnostic; cached initial RGB only",
        "initial_feature_stats": "24train only", "normalizer_source_sha256": NORMALIZER_SHA,
        "source_hashes": {p.name: sha(p) for p in Path(__file__).parent.glob("*.py")},
        "gpu": torch.cuda.get_device_name(), "torch": torch.__version__,
        "limitations": ["Fixed colors/cameras/narrow task, possible implicit query clock.",
                        "Changes representation and parameter count; no pure causal memory contrast.",
                        "No novel method, hardware precision or language claim."],
    }
    (RUN / "contract.json").write_text(json.dumps(contract, indent=2) + "\n")
    batches = hashlib.sha256()
    started = time.monotonic()
    with (RUN / "updates.jsonl").open("x") as stream:
        for step in range(1, 2001):
            net.train()
            index = torch.randint(24, (8,), device=device, generator=sampler)
            batches.update(index.cpu().numpy().tobytes())
            prediction = net(train[0][index].float(),
                             (train[1][index] - stats["q_mean"]) / stats["q_std"], anchor_train[index])
            loss = masked_mse(prediction, (train[2][index] - stats["a_mean"]) / stats["a_std"], train[3][index])
            if not torch.isfinite(loss):
                raise ValueError("nonfinite loss")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(net.parameters(), 10, error_if_nonfinite=True)
            optimizer.step()
            if step % 200 == 0:
                net.eval()
                with torch.no_grad():
                    prediction = net(val[0].float(), (val[1] - stats["q_mean"]) / stats["q_std"], anchor_val)
                    vl = masked_mse(prediction, (val[2] - stats["a_mean"]) / stats["a_std"], val[3])
                row = {"step": step, "train_normalized_mse": float(loss.detach()),
                       "all_8_val_teacher_forced_mse": float(vl), "wall_s": time.monotonic() - started}
                stream.write(json.dumps(row) + "\n")
                stream.flush()
                print(json.dumps(row), flush=True)
    torch.save({"model": net.state_dict(), "training_step": 2000, **stats}, CHECKPOINT)
    result = {"checkpoint": str(CHECKPOINT), "checkpoint_sha256": sha(CHECKPOINT),
              "step": 2000, "parameters": sum(p.numel() for p in net.parameters()),
              "wall_s": time.monotonic() - started, "cuda_max_allocated_bytes": torch.cuda.max_memory_allocated(),
              "sample_indices_sha256": batches.hexdigest(), "test_used": False}
    (RUN / "completed.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
