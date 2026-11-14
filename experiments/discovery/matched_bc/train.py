"""Train one fixed ordinary BC baseline; held-out test never used here."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from policy import EXECUTE, HISTORY, HORIZON, ChunkBC, image_tensor


def load_data(rows, device):
    images, histories, targets, masks = [], [], [], []
    for row in rows:
        path = Path(row["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("data changed after collection")
        with np.load(path) as episode:
            q, action = episode["q"], episode["action"]
            if q.shape != (285, 6) or action.shape != (285, 6):
                raise ValueError("bad fixed episode length")
            if not np.isfinite(q).all() or not np.isfinite(action).all():
                raise ValueError("nonfinite observations/actions")
            image_batches = []
            for start in range(0, len(q), 32):
                image_batches.append(image_tensor(episode["rgb"][start:start + 32], device).half())
            images.append(torch.cat(image_batches))
            indices = np.arange(len(q))[:, None] - np.arange(HISTORY - 1, -1, -1)
            histories.append(q[np.maximum(indices, 0)])
            future = np.arange(len(q))[:, None] + np.arange(HORIZON)
            targets.append(action[np.minimum(future, len(q) - 1)])
            masks.append(future < len(q))
    return (
        torch.cat(images),
        torch.from_numpy(np.concatenate(histories)).to(device),
        torch.from_numpy(np.concatenate(targets)).to(device),
        torch.from_numpy(np.concatenate(masks)).to(device),
    )


def masked_mse(prediction, target, mask):
    return (((prediction - target) ** 2) * mask[:, :, None]).sum() / (mask.sum() * 6)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.checkpoint.exists() or args.out.exists():
        parser.error("fresh checkpoint and records required")
    complete = json.loads((args.records / "collection-complete.json").read_text())
    if complete["episodes"] != 32 or not complete["all_teacher_success"]:
        parser.error("all 32 predetermined teacher episodes must qualify")
    rows = [json.loads(line) for line in (args.records / "episodes.jsonl").read_text().splitlines()]
    if len({r["seed"] for r in rows}) != 32 or any(r["split"] == "test" for r in rows):
        raise ValueError("duplicate or leaked episodes")
    torch.manual_seed(42)
    np.random.seed(42)
    torch.backends.cudnn.benchmark = False
    device = torch.device("cuda")
    args.out.mkdir(parents=True, exist_ok=False)
    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    contract = {
        "kind": "ordinary_matched_chunk_bc_capability_not_new_method",
        "seed": 42, "steps": 2000, "batch": 64, "lr": 0.001,
        "history": HISTORY, "horizon": HORIZON, "execute": EXECUTE,
        "checkpoint_selection": "fixed_final_2000_not_best",
        "input": "two_rgb_and_measured_q_history; constant_instruction_single_task",
        "gpu": torch.cuda.get_device_name(), "torch": torch.__version__,
        "data_contract_sha256": hashlib.sha256((args.records / "collection-contract.json").read_bytes()).hexdigest(),
        "source_sha256": {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                          for name in ["train.py", "policy.py"]},
    }
    (args.out / "training-contract.json").write_text(json.dumps(contract, indent=2) + "\n")
    train = load_data([r for r in rows if r["split"] == "train"], device)
    validation = load_data([r for r in rows if r["split"] == "val"], device)
    q_mean = train[1][:, -1].mean(0)
    q_std = train[1][:, -1].std(0).clamp_min(0.01)
    # Normalization uses only current state/actions from the train episodes.
    a_mean = train[2][:, 0].mean(0)
    a_std = train[2][:, 0].std(0).clamp_min(0.01)
    net = ChunkBC().to(device)
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    started = time.monotonic()
    with (args.out / "updates.jsonl").open("x") as log:
        for step in range(1, 2001):
            net.train()
            index = torch.randint(len(train[0]), (64,), device=device)
            prediction = net(train[0][index].float(), (train[1][index] - q_mean) / q_std)
            loss = masked_mse(prediction, (train[2][index] - a_mean) / a_std, train[3][index])
            if not torch.isfinite(loss):
                raise ValueError("nonfinite loss")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(net.parameters(), 10)
            optimizer.step()
            if step % 100 == 0:
                net.eval()
                with torch.no_grad():
                    vi = torch.arange(min(256, len(validation[0])), device=device)
                    vp = net(validation[0][vi].float(), (validation[1][vi] - q_mean) / q_std)
                    vl = masked_mse(vp, (validation[2][vi] - a_mean) / a_std, validation[3][vi])
                row = {"step": step, "train_normalized_mse": float(loss.detach()),
                       "first_val_episode_partial_mse": float(vl),
                       "wall_s": time.monotonic() - started}
                log.write(json.dumps(row) + "\n")
                log.flush()
                print(json.dumps(row), flush=True)
    torch.save({
        "model": net.state_dict(), "q_mean": q_mean, "q_std": q_std,
        "a_mean": a_mean, "a_std": a_std, "training_step": 2000,
    }, args.checkpoint)
    result = {"kind": contract["kind"], "step": 2000, "wall_s": time.monotonic() - started,
              "checkpoint": str(args.checkpoint),
              "checkpoint_sha256": hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),
              "parameters": sum(p.numel() for p in net.parameters()),
              "train_episodes": 24, "validation_episodes": 8, "test_used": False,
              "cuda_max_allocated_bytes": torch.cuda.max_memory_allocated()}
    (args.out / "completed.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
