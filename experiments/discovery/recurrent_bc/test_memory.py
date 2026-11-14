"""Causality and reset contracts for the ordinary recurrent BC baseline."""

import importlib.util
from pathlib import Path

import torch


def model(mode="carry"):
    path = Path(__file__).with_name("memory_policy.py")
    spec = importlib.util.spec_from_file_location("tested_memory_policy", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    torch.manual_seed(7)
    torch.set_num_threads(2)
    return module.MemoryBC(mode).eval()


def inputs():
    torch.manual_seed(8)
    return torch.rand(2, 4, 6, 64, 64), torch.randn(2, 4, 8, 6)


@torch.inference_mode()
def test_future_observations_cannot_change_predicted_prefix():
    net = model()
    image, q = inputs()
    original = net(image, q)
    image[:, 2:] = torch.randn_like(image[:, 2:])
    q[:, 2:] = torch.randn_like(q[:, 2:])
    changed = net(image, q)
    torch.testing.assert_close(original[:, :2], changed[:, :2])


@torch.inference_mode()
def test_step_inference_matches_training_sequence_with_carried_hidden():
    net = model()
    image, q = inputs()
    sequence = net(image, q)
    hidden = None
    steps = []
    for t in range(4):
        action, hidden = net.step(image[:, t], q[:, t], hidden)
        steps.append(action)
    torch.testing.assert_close(torch.stack(steps, dim=1), sequence, atol=1e-6, rtol=1e-5)
    fresh, _ = net.step(image[:, 0], q[:, 0], None)
    torch.testing.assert_close(fresh, sequence[:, 0])


@torch.inference_mode()
def test_reset_control_ignores_previous_hidden_and_has_same_parameter_count():
    net = model("reset")
    image, q = inputs()
    sequence = net(image, q)
    hidden = torch.randn(1, 2, 128)
    steps = []
    for t in range(4):
        action, hidden = net.step(image[:, t], q[:, t], hidden)
        steps.append(action)
    torch.testing.assert_close(torch.stack(steps, dim=1), sequence, atol=1e-6, rtol=1e-5)
    assert sum(p.numel() for p in net.parameters()) == sum(p.numel() for p in model().parameters())
