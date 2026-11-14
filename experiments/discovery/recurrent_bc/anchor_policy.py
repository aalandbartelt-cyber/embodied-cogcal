"""Ordinary GRU BC with cached initial RGB color features; no novel method."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from color_localization_audit import color_features
from memory_policy import MemoryBC, image_tensor
from torch import nn


class AnchorBC(MemoryBC):
    def __init__(self):
        super().__init__("carry")
        self.project = nn.Sequential(nn.Linear(1024 + 48 + 6, 128), nn.ReLU())

    def encode_anchor(self, images, q_history, anchor):
        batch, length = images.shape[:2]
        visual = self.vision(images.reshape(batch * length, 6, 64, 64))
        q = q_history.reshape(batch * length, 48)
        initial = anchor[:, None].expand(batch, length, 6).reshape(batch * length, 6)
        return self.project(torch.cat([visual, q, initial], -1)).reshape(batch, length, 128)

    def forward(self, images, q_history, anchor):
        tokens = self.encode_anchor(images, q_history, anchor)
        state, _ = self.memory(tokens)
        return self.head(state).reshape(*tokens.shape[:2], 30, 6)

    def step(self, images, q_history, anchor, hidden=None):
        token = self.encode_anchor(images[:, None], q_history[:, None], anchor)
        state, hidden = self.memory(token, hidden)
        return self.head(state[:, 0]).reshape(len(images), 30, 6), hidden


class Predictor:
    def __init__(self, checkpoint):
        self.device = torch.device("cuda")
        state = torch.load(checkpoint, map_location=self.device, weights_only=True)
        self.net = AnchorBC().to(self.device).eval()
        self.net.load_state_dict(state["model"], strict=True)
        for key in ["q_mean", "q_std", "a_mean", "a_std", "anchor_mean", "anchor_std"]:
            setattr(self, key, state[key])
        self.hidden = self.anchor = None

    @torch.inference_mode()
    def predict(self, rgb, q_history, reset):
        if reset:
            self.hidden = None
            initial = torch.from_numpy(color_features(rgb)).to(self.device)
            self.anchor = (initial - self.anchor_mean) / self.anchor_std
        if self.anchor is None:
            raise ValueError("episode initial RGB required before prediction")
        q = np.asarray(q_history, dtype=np.float32)
        if q.shape != (8, 6) or not np.isfinite(q).all():
            raise ValueError("eight finite measured q observations required")
        before = 0.0 if self.hidden is None else float(self.hidden.norm())
        q = (torch.from_numpy(q).to(self.device) - self.q_mean) / self.q_std
        action, self.hidden = self.net.step(image_tensor(rgb, self.device), q[None],
                                            self.anchor[None], self.hidden)
        chunk = action[0] * self.a_std + self.a_mean
        if not torch.isfinite(chunk).all() or not torch.isfinite(self.hidden).all():
            raise ValueError("nonfinite neural output")
        info = {"reset_requested": bool(reset), "hidden_input_l2": before,
                "hidden_output_l2": float(self.hidden.norm()),
                "hidden_output_sha256": hashlib.sha256(self.hidden.cpu().numpy().tobytes()).hexdigest(),
                "initial_color_feature_sha256": hashlib.sha256(self.anchor.cpu().numpy().tobytes()).hexdigest()}
        return chunk.cpu().numpy(), info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    predictor = Predictor(args.checkpoint)
    print(json.dumps({"ready": True, "mode": "carry_initial_RGB_features",
                      "gpu": torch.cuda.get_device_name(), "clock_or_phase_input": False}), flush=True)
    for line in __import__("sys").stdin:
        request = json.loads(line)
        rgb = np.frombuffer(base64.b64decode(request["rgb"], validate=True), dtype=np.uint8)
        chunk, info = predictor.predict(rgb.reshape(2, 128, 128, 3),
                                        request["q_history_rad"], request.get("reset", False))
        print(json.dumps({"chunk_rad": chunk.tolist(), "memory": info}), flush=True)


if __name__ == "__main__":
    main()
