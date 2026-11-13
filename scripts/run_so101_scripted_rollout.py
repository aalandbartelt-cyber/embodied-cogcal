"""Run a model-free SO-101 actuator/video smoke rollout.

This is a plumbing check, not a VLA result. It verifies that the same scene can
produce actions, frames, and a trace before an A100 policy is connected.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def interpolate_controls(start: np.ndarray, end: np.ndarray, *, steps: int) -> np.ndarray:
    """Return linearly interpolated actuator controls including both endpoints."""

    if steps < 2:
        raise ValueError("steps must be at least two")
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    if start.shape != end.shape:
        raise ValueError("start and end controls must have the same shape")
    if not np.isfinite(start).all() or not np.isfinite(end).all():
        raise ValueError("controls must be finite")
    return np.linspace(start, end, num=steps)


def run_rollout(scene: Path, output_video: Path, output_trace: Path, *, steps: int = 240) -> None:
    try:
        import imageio.v2 as imageio
        import mujoco
    except ImportError as exc:
        raise SystemExit("cogcal-sim requires mujoco and imageio for scripted rollout") from exc

    from simulation.so101.scene import (
        load_scene,
        policy_observation,
        reset_scene,
        step_joint_targets,
    )

    paths = [scene, output_video, output_trace]
    if any(
        left.resolve() == right.resolve()
        or (left.exists() and right.exists() and left.samefile(right))
        for left, right in combinations(paths, 2)
    ):
        raise ValueError("scene, video and trace paths must differ")
    model, data = load_scene(scene, mujoco)
    reset_scene(model, data, mujoco)

    # A conservative six-joint waypoint sequence for actuator and renderer checks.
    start = np.zeros(model.nu, dtype=float)
    end = np.array([0.0, -0.45, 0.75, -0.55, 0.0, 0.35], dtype=float)
    controls = interpolate_controls(start, end, steps=steps)

    output_video.parent.mkdir(parents=True, exist_ok=True)
    output_trace.parent.mkdir(parents=True, exist_ok=True)
    # Render at 30 Hz of simulated time rather than playing 2 ms physics steps
    # at 30 fps. Stream frames/records so long traces do not accumulate in RAM.
    with (
        mujoco.Renderer(model, height=480, width=640) as renderer,
        imageio.get_writer(output_video, fps=30, codec="libx264") as writer,
        output_trace.open("w", encoding="utf-8") as trace,
    ):
        for step, control in enumerate(controls):
            target_time = (step + 1) / 30
            substeps = max(1, int(np.ceil((target_time - data.time) / model.opt.timestep)))
            step_joint_targets(model, data, control, substeps=substeps, mujoco_module=mujoco)
            observation = policy_observation(model, data, renderer)
            writer.append_data(observation["rgb"])
            record = {
                "episode_id": "so101_scripted_smoke",
                "record_type": "step",
                "experiment_kind": "plumbing_smoke",
                "step": step,
                "sim_time_s": float(data.time),
                "action_space": "so101_joint_position_rad",
                "action": control.tolist(),
                "qpos": data.qpos.tolist(),
                "qvel": data.qvel.tolist(),
                "failure_reason": "scripted_plumbing_smoke_only",
            }
            trace.write(json.dumps(record, allow_nan=False) + "\n")
    print(f"video={output_video}")
    print(f"trace={output_trace}")
    print(f"frames={len(controls)} sim_time_s={data.time:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", type=Path, default=Path("simulation/so101/eccbf_factorial_scene.xml"))
    parser.add_argument("--video", type=Path, default=Path("results/videos/so101_scripted_smoke.mp4"))
    parser.add_argument("--trace", type=Path, default=Path("results/source_data/so101_scripted_smoke.jsonl"))
    parser.add_argument("--steps", type=int, default=240)
    args = parser.parse_args()
    run_rollout(args.scene, args.video, args.trace, steps=args.steps)


if __name__ == "__main__":
    main()
