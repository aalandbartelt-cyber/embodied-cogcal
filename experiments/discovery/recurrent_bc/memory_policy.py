"""Ordinary causal GRU BC and a matched reset control; no research method."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.discovery.matched_bc.policy import image_tensor  # noqa: E402


class MemoryBC(nn.Module):
    def __init__(self, mode="carry"):
        super().__init__()
        if mode not in {"carry", "reset"}:
            raise ValueError("unknown memory mode")
        self.mode = mode
        self.vision = nn.Sequential(
            nn.Conv2d(6, 16, 5, stride=2, padding=2), nn.ReLU(),
            nn.Conv2d(16, 32, 3, stride=2, padding=1), nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)), nn.Flatten(),
        )
        self.project = nn.Sequential(nn.Linear(1024 + 48, 128), nn.ReLU())
        self.memory = nn.GRU(128, 128, batch_first=True)
        self.head = nn.Linear(128, 30 * 6)

    def encode(self, images, q_history):
        batch, length = images.shape[:2]
        visual = self.vision(images.reshape(batch * length, 6, 64, 64))
        q = q_history.reshape(batch * length, 48)
        return self.project(torch.cat([visual, q], dim=-1)).reshape(batch, length, 128)

    def forward(self, images, q_history):
        tokens = self.encode(images, q_history)
        batch, length = tokens.shape[:2]
        if self.mode == "carry":
            states, _ = self.memory(tokens)
        else:
            states, _ = self.memory(tokens.reshape(batch * length, 1, 128))
            states = states.reshape(batch, length, 128)
        return self.head(states).reshape(batch, length, 30, 6)

    def step(self, image, q_history, hidden=None):
        token = self.encode(image[:, None], q_history[:, None])
        states, hidden = self.memory(token, hidden if self.mode == "carry" else None)
        return self.head(states[:, 0]).reshape(len(image), 30, 6), hidden


class Predictor:
    def __init__(self, checkpoint):
        self.device = torch.device("cuda")
        state = torch.load(checkpoint, map_location=self.device, weights_only=True)
        self.mode = state["mode"]
        self.net = MemoryBC(self.mode).to(self.device).eval()
        self.net.load_state_dict(state["model"], strict=True)
        self.q_mean, self.q_std = state["q_mean"], state["q_std"]
        self.a_mean, self.a_std = state["a_mean"], state["a_std"]
        self.hidden = None

    @torch.inference_mode()
    def predict(self, rgb, q_history, reset=False):
        if reset:
            self.hidden = None
        q = np.asarray(q_history, dtype=np.float32)
        if q.shape != (8, 6) or not np.isfinite(q).all():
            raise ValueError("eight finite measured q observations required")
        before = 0.0 if self.hidden is None or self.mode == "reset" else float(self.hidden.norm())
        images = image_tensor(rgb, self.device)
        q = (torch.from_numpy(q).to(self.device) - self.q_mean) / self.q_std
        actions, self.hidden = self.net.step(images, q[None], self.hidden)
        actions = actions[0] * self.a_std + self.a_mean
        if not torch.isfinite(actions).all() or not torch.isfinite(self.hidden).all():
            raise ValueError("nonfinite neural state or command")
        hidden_bytes = self.hidden.cpu().numpy().tobytes()
        info = {"reset_requested": bool(reset), "hidden_input_l2": before,
                "hidden_output_l2": float(self.hidden.norm()),
                "hidden_output_sha256": hashlib.sha256(hidden_bytes).hexdigest()}
        return actions.cpu().numpy(), info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    predictor = Predictor(args.checkpoint)
    print(json.dumps({"ready": True, "mode": predictor.mode,
                      "gpu": torch.cuda.get_device_name(), "horizon": 30, "execute": 6,
                      "inputs": ["RGB", "measured_q_history"], "clock_or_phase_input": False}), flush=True)
    for line in sys.stdin:
        request = json.loads(line)
        rgb = np.frombuffer(base64.b64decode(request["rgb"], validate=True), dtype=np.uint8)
        chunk, info = predictor.predict(rgb.reshape(2, 128, 128, 3),
                                        request["q_history_rad"], request.get("reset", False))
        print(json.dumps({"chunk_rad": chunk.tolist(), "memory": info}), flush=True)


if __name__ == "__main__":
    main()
