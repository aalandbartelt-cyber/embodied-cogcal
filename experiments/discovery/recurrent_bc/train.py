"""Train fixed ordinary carry/reset BC with matched full-episode sampling."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from memory_policy import MemoryBC, image_tensor

ROOT = Path(__file__).resolve().parents[3]
RECORDS = ROOT / "experiments/discovery/matched-bc-lowrate-20261114/collection"
NORMALIZER = ROOT / "checkpoints/matched-bc-20261114/final-2000.pt"
NORMALIZER_SHA = "f49da6e9c82c55a2478bf580e049365fbde3e3bd8bff2a8fc1bfcbe33a23e237"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_episodes(rows, device):
    images, histories, targets, masks = [], [], [], []
    query = np.arange(0, 285, 6)
    future = query[:, None] + np.arange(30)
    history = np.maximum(query[:, None] - np.arange(7, -1, -1), 0)
    for row in rows:
        path = Path(row["path"])
        if sha(path) != row["sha256"]:
            raise ValueError("demonstration content changed")
        with np.load(path) as episode:
            rgb, q, action = episode["rgb"], episode["q"], episode["action"]
            if q.shape != (285, 6) or not np.isfinite(q).all() or not np.isfinite(action).all():
                raise ValueError("invalid episode")
            if not np.array_equal(episode["rgb_age_control_steps"][query], np.zeros(48)):
                raise ValueError("query frames are not fresh")
            images.append(image_tensor(rgb[query], device).half())
            histories.append(q[history])
            targets.append(action[np.minimum(future, 284)])
            masks.append(future < 285)
    return (torch.stack(images), torch.from_numpy(np.stack(histories)).to(device),
            torch.from_numpy(np.stack(targets)).to(device),
            torch.from_numpy(np.stack(masks)).to(device))


def masked_mse(prediction, target, mask):
    return (((prediction - target) ** 2) * mask[..., None]).sum() / (6 * mask.sum())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["carry", "reset"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists() or args.checkpoint.exists():
        parser.error("new output and fixed final checkpoint required")
    if sha(NORMALIZER) != NORMALIZER_SHA:
        raise ValueError("inherited train-only statistics source changed")
    rows = [json.loads(line) for line in (RECORDS / "episodes.jsonl").read_text().splitlines()]
    if (len(rows) != 32 or
        {r["seed"] for r in rows if r["split"] == "train"} != set(range(4100, 4124)) or
        {r["seed"] for r in rows if r["split"] == "val"} != set(range(5100, 5108)) or
        not all(r["task_success"] for r in rows)):
        raise ValueError("unexpected demonstration identities or failures")
    args.out.mkdir(parents=True, exist_ok=False)
    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda")
    torch.manual_seed(42)
    np.random.seed(42)
    torch.backends.cudnn.benchmark = False
    inherited = torch.load(NORMALIZER, map_location=device, weights_only=True)
    stats = {name: inherited[name] for name in ["q_mean", "q_std", "a_mean", "a_std"]}
    train = load_episodes([r for r in rows if r["split"] == "train"], device)
    val = load_episodes([r for r in rows if r["split"] == "val"], device)
    net = MemoryBC(args.mode)
    initial = hashlib.sha256()
    for tensor in net.state_dict().values():
        initial.update(tensor.cpu().numpy().tobytes())
    net = net.to(device)
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    sampler = torch.Generator(device=device).manual_seed(42)
    contract = {
        "kind": "ordinary_memory_bc_capability_not_new_method", "mode": args.mode,
        "seed": 42, "steps": 2000, "batch_episodes": 8, "queries_per_episode": 48,
        "prediction_horizon": 30, "execute": 6, "lr": 0.001,
        "sampling": "full episode at query steps 0,6,...,282; replacement episode sampling",
        "sampling_generator": "dedicated CUDA Generator seed42, separate from model RNG",
        "checkpoint_selection": "fixed_final_2000_not_best",
        "initial_parameter_sha256": initial.hexdigest(),
        "normalizer_source_sha256": NORMALIZER_SHA, "normalizer_train_only": True,
        "source_hashes": {p.name: sha(p) for p in Path(__file__).parent.glob("*.py")},
        "data_contract_sha256": sha(RECORDS / "collection-contract.json"),
        "gpu": torch.cuda.get_device_name(), "torch": torch.__version__,
        "teacher_forced_training": True, "test_used": False,
        "limitations": ["Implicit query counting is possible.",
                        "Different architecture/query sampling from previous failed CNN baseline.",
                        "No language, compensation, TPSC or novelty claim."],
    }
    (args.out / "contract.json").write_text(json.dumps(contract, indent=2) + "\n")
    batches = hashlib.sha256()
    started = time.monotonic()
    with (args.out / "updates.jsonl").open("x") as stream:
        for step in range(1, 2001):
            net.train()
            index = torch.randint(len(train[0]), (8,), device=device, generator=sampler)
            batches.update(index.cpu().numpy().tobytes())
            prediction = net(train[0][index].float(), (train[1][index] - stats["q_mean"]) / stats["q_std"])
            target = (train[2][index] - stats["a_mean"]) / stats["a_std"]
            loss = masked_mse(prediction, target, train[3][index])
            if not torch.isfinite(loss):
                raise ValueError("nonfinite loss")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(net.parameters(), 10, error_if_nonfinite=True)
            optimizer.step()
            if step % 200 == 0:
                net.eval()
                with torch.no_grad():
                    vp = net(val[0].float(), (val[1] - stats["q_mean"]) / stats["q_std"])
                    vl = masked_mse(vp, (val[2] - stats["a_mean"]) / stats["a_std"], val[3])
                row = {"step": step, "train_normalized_mse": float(loss.detach()),
                       "all_8_val_teacher_forced_mse": float(vl),
                       "wall_s": time.monotonic() - started}
                stream.write(json.dumps(row) + "\n")
                stream.flush()
                print(json.dumps(row), flush=True)
    torch.save({"model": net.state_dict(), "mode": args.mode,
                "training_step": 2000, **stats}, args.checkpoint)
    result = {"mode": args.mode, "step": 2000, "checkpoint": str(args.checkpoint),
              "checkpoint_sha256": sha(args.checkpoint), "wall_s": time.monotonic() - started,
              "initial_parameter_sha256": initial.hexdigest(), "sample_indices_sha256": batches.hexdigest(),
              "parameters": sum(p.numel() for p in net.parameters()),
              "cuda_max_allocated_bytes": torch.cuda.max_memory_allocated(), "test_used": False}
    (args.out / "completed.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
