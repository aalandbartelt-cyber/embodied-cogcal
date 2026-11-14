"""SmolVLA inference process: receives only RGB, six measured joints, language, seed.

Use a LOCAL frozen checkpoint including its original pre/post processors.
MuJoCo stays in a separate environment; no simulator/evaluator state is imported.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import json
import sys
import time
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    with contextlib.redirect_stdout(sys.stderr):
        import torch
        from lerobot.configs.policies import PreTrainedConfig
        from lerobot.policies.factory import make_pre_post_processors
        from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy

        config = PreTrainedConfig.from_pretrained(args.checkpoint)
        config.device = "cuda"
        config.load_vlm_weights = False  # full policy weights below supply the VLM
        policy = SmolVLAPolicy.from_pretrained(args.checkpoint, config=config, strict=True)
        pre, post = make_pre_post_processors(config, pretrained_path=str(args.checkpoint))
        policy.eval()
    keys = list(config.image_features)
    if len(keys) < 2:
        raise ValueError("two-camera checkpoint required")
    print(
        json.dumps(
            {
                "ready": True,
                "gpu": torch.cuda.get_device_name(0),
                "checkpoint": str(args.checkpoint),
                "image_keys": keys,
            }
        ),
        flush=True,
    )
    for line in sys.stdin:
        request = json.loads(line)
        if set(request) != {"images", "joint_positions_deg", "task", "seed"}:
            raise ValueError("only images, joint_positions_deg, task, seed allowed")
        state = np.asarray(request["joint_positions_deg"], dtype=np.float32)
        if state.shape != (6,) or not np.isfinite(state).all():
            raise ValueError("invalid robot state")
        batch = {"observation.state": torch.from_numpy(state), "task": request["task"]}
        for name, payload in zip(keys[:2], request["images"], strict=True):
            rgb = (
                np.frombuffer(base64.b64decode(payload), dtype=np.uint8).reshape(256, 256, 3).copy()
            )
            batch[name] = torch.from_numpy(rgb).permute(2, 0, 1).float() / 255.0
        torch.manual_seed(request["seed"])
        torch.cuda.manual_seed_all(request["seed"])
        policy.reset()
        torch.cuda.synchronize()
        started = time.perf_counter()
        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
            chunk = policy.predict_action_chunk(pre(batch))
            # Saved processors accept a tensor with arbitrary leading axes.
            chunk = post(chunk).detach().float().cpu().numpy()[0]
        torch.cuda.synchronize()
        if chunk.ndim != 2 or chunk.shape[1] != 6 or not np.isfinite(chunk).all():
            raise ValueError("non-finite or invalid action chunk")
        print(
            json.dumps(
                {
                    "chunk": chunk.tolist(),
                    "inference_s": time.perf_counter() - started,
                    "max_allocated_bytes": torch.cuda.max_memory_allocated(),
                }
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
