"""Small ordinary CNN/chunk-BC model; no proposed research mechanism.

The sole language is constant. Inputs contain RGB and measured q history.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

HISTORY = 8
HORIZON = 30
EXECUTE = 6


class ChunkBC(nn.Module):
    def __init__(self):
        super().__init__()
        self.vision = nn.Sequential(
            nn.Conv2d(6, 16, 5, stride=2, padding=2), nn.ReLU(),
            nn.Conv2d(16, 32, 3, stride=2, padding=1), nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)), nn.Flatten(),
        )
        self.head = nn.Sequential(
            nn.Linear(1024 + HISTORY * 6, 256), nn.ReLU(),
            nn.Linear(256, 256), nn.ReLU(), nn.Linear(256, HORIZON * 6),
        )

    def forward(self, images, q_history):
        features = self.vision(images)
        return self.head(torch.cat([features, q_history.flatten(1)], dim=1)).reshape(-1, HORIZON, 6)


def image_tensor(rgb, device):
    rgb = np.asarray(rgb, dtype=np.uint8)
    if rgb.ndim == 4:
        rgb = rgb[None]
    if rgb.shape[1:] != (2, 128, 128, 3):
        raise ValueError("expected matched two-camera uint8 frames")
    tensor = torch.from_numpy(rgb.transpose(0, 1, 4, 2, 3).copy()).to(device)
    tensor = tensor.reshape(len(rgb), 6, 128, 128).float() / 255
    return F.interpolate(tensor, size=(64, 64), mode="bilinear", align_corners=False)


class Predictor:
    def __init__(self, checkpoint):
        self.device = torch.device("cuda")
        state = torch.load(checkpoint, map_location=self.device, weights_only=True)
        self.model = ChunkBC().to(self.device)
        self.model.load_state_dict(state["model"], strict=True)
        self.model.eval()
        self.q_mean, self.q_std = state["q_mean"], state["q_std"]
        self.a_mean, self.a_std = state["a_mean"], state["a_std"]

    @torch.inference_mode()
    def predict(self, rgb, q_history):
        q = np.asarray(q_history, dtype=np.float32)
        if q.shape != (HISTORY, 6) or not np.isfinite(q).all():
            raise ValueError("expected eight finite measured q vectors")
        images = image_tensor(rgb, self.device)
        q = (torch.from_numpy(q).to(self.device) - self.q_mean) / self.q_std
        prediction = self.model(images, q[None])[0] * self.a_std + self.a_mean
        if not torch.isfinite(prediction).all():
            raise ValueError("nonfinite learned chunk")
        return prediction.cpu().numpy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    predictor = Predictor(args.checkpoint)
    print(json.dumps({"ready": True, "gpu": torch.cuda.get_device_name(),
                      "checkpoint": str(args.checkpoint), "history": HISTORY,
                      "horizon": HORIZON, "execute": EXECUTE}), flush=True)
    for line in sys.stdin:
        request = json.loads(line)
        rgb = np.frombuffer(base64.b64decode(request["rgb"]), dtype=np.uint8).reshape(2, 128, 128, 3)
        chunk = predictor.predict(rgb, request["q_history_rad"])
        print(json.dumps({"chunk_rad": chunk.tolist()}), flush=True)


if __name__ == "__main__":
    main()
