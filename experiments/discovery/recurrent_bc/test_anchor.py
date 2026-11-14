"""Causal initial RGB feature baseline contracts."""

import importlib.util
from pathlib import Path

import torch


def load():
    path = Path(__file__).with_name("anchor_policy.py")
    spec = importlib.util.spec_from_file_location("tested_anchor_policy", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@torch.inference_mode()
def test_fixed_initial_feature_sequence_matches_step_and_has_no_future_leak():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    net = load().AnchorBC().eval()
    images = torch.rand(2, 4, 6, 64, 64)
    q = torch.randn(2, 4, 8, 6)
    anchor = torch.randn(2, 6)
    sequence = net(images, q, anchor)
    hidden = None
    outputs = []
    for t in range(4):
        action, hidden = net.step(images[:, t], q[:, t], anchor, hidden)
        outputs.append(action)
    torch.testing.assert_close(sequence, torch.stack(outputs, 1), atol=1e-6, rtol=1e-5)
    images[:, 2:] = torch.randn_like(images[:, 2:])
    q[:, 2:] = torch.randn_like(q[:, 2:])
    changed = net(images, q, anchor)
    torch.testing.assert_close(changed[:, :2], sequence[:, :2])
