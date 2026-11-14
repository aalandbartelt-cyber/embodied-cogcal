"""Real carrier decode + SmolVLA CUDA forward/backward, not task evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path


def main():
    import torch
    from lerobot.configs.policies import PreTrainedConfig
    from lerobot.datasets.lerobot_dataset import LeRobotDataset
    from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
    from lerobot.policies.smolvla.processor_smolvla import make_smolvla_pre_post_processors

    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error("output already exists")
    torch.manual_seed(42)
    torch.set_num_threads(4)
    dataset = LeRobotDataset(
        "ngocthuong2212/so101_mujoco_follower_7_31",
        root="data/tpsc-carrier",
        revision="de301f7afe016cef14ac46a238714f52e15bf932",
        video_backend="pyav",
        delta_timestamps={"action": [i / 30 for i in range(50)]},
    )
    sample = dataset[0]
    print("DECODE_OK", len(dataset), dataset.num_episodes, flush=True)
    config = PreTrainedConfig.from_pretrained("checkpoints/smolvla_base")
    config.device = "cuda"
    config.load_vlm_weights = False
    policy = SmolVLAPolicy.from_pretrained("checkpoints/smolvla_base", config=config, strict=True)
    pre, post = make_smolvla_pre_post_processors(config, dataset.meta.stats)
    sample["observation.images.camera1"] = sample.pop("observation.images.top")
    sample["observation.images.camera2"] = sample.pop("observation.images.front")
    # The official training pipeline collates chunks to (B, H, D) first.
    batch = pre(torch.utils.data.default_collate([sample]))
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    policy.train()
    with torch.autocast("cuda", dtype=torch.bfloat16):
        loss, _ = policy(batch)
    loss.backward()
    torch.cuda.synchronize()
    training_s = time.perf_counter() - started
    finite_gradients = all(
        torch.isfinite(p.grad).all().item() for p in policy.parameters() if p.grad is not None
    )
    gradient_parameters = sum(p.numel() for p in policy.parameters() if p.grad is not None)
    policy.zero_grad(set_to_none=True)
    policy.reset()
    policy.eval()
    started = time.perf_counter()
    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
        normalized = policy.predict_action_chunk(batch)
        actions = post(normalized).detach().float().cpu()
    torch.cuda.synchronize()
    inference_s = time.perf_counter() - started
    if not torch.isfinite(actions).all() or not finite_gradients or not torch.isfinite(loss):
        raise ValueError("non-finite forward/backward")
    result = {
        "kind": "carrier_cuda_forward_backward_not_policy_result",
        "dataset_robot_type": "so_follower",
        "dataset_episodes": dataset.num_episodes,
        "dataset_frames": len(dataset),
        "sample_index": 0,
        "torch": torch.__version__,
        "gpu": torch.cuda.get_device_name(0),
        "cuda_capability": list(torch.cuda.get_device_capability(0)),
        "normalizer": "explicit carrier dataset mean/std for initialization smoke only",
        "adapter": "no physics executed; carrier all-six-degree interpretation remains unverified",
        "loss": float(loss.detach()),
        "finite_gradients": finite_gradients,
        "gradient_parameters": gradient_parameters,
        "forward_backward_s": training_s,
        "chunk_shape": list(actions.shape),
        "chunk_finite": True,
        "inference_s": inference_s,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "model_sha256": hashlib.file_digest(
            Path("checkpoints/smolvla_base/model.safetensors").open("rb"), "sha256"
        ).hexdigest()
        if hasattr(hashlib, "file_digest")
        else None,
        "claim": "carrier_loader_model_gradient_smoke_not_task_success_or_tpsc_effect",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
