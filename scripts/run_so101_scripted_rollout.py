"""Run a model-free SO-101 actuator/video smoke rollout.

This is a plumbing check, not a VLA result. It verifies that the same scene can
produce actions, frames, and a trace before an A100 policy is connected.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def interpolate_controls(start: np.ndarray, end: np.ndarray, *, steps: int) -> np.ndarray:
    """Return linearly interpolated actuator controls including both endpoints."""

    if steps < 2:
        raise ValueError("steps must be at least two")
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    if start.shape != end.shape:
        raise ValueError("start and end controls must have the same shape")
    return np.linspace(start, end, num=steps)


def run_rollout(scene: Path, output_video: Path, output_trace: Path, *, steps: int = 240) -> None:
    try:
        import imageio.v2 as imageio
        import mujoco
    except ImportError as exc:
        raise SystemExit("cogcal-sim requires mujoco and imageio for scripted rollout") from exc

    model = mujoco.MjModel.from_xml_path(str(scene))
    data = mujoco.MjData(model)
    mujoco.mj_resetData(model, data)

    # A conservative six-joint waypoint sequence for actuator and renderer checks.
    start = np.zeros(model.nu, dtype=float)
    end = np.array([0.0, -0.45, 0.75, -0.55, 0.0, 0.35], dtype=float)
    controls = interpolate_controls(start, end, steps=steps)

    renderer = mujoco.Renderer(model, height=480, width=640)
    output_video.parent.mkdir(parents=True, exist_ok=True)
    output_trace.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    frames: list[np.ndarray] = []

    for step, control in enumerate(controls):
        data.ctrl[:] = control
        mujoco.mj_step(model, data)
        renderer.update_scene(data, camera="front_camera")
        frames.append(renderer.render().copy())
        records.append(
            {
                "episode_id": "so101_scripted_smoke",
                "step": step,
                "semantic_condition": "neutral",
                "execution_condition": "nominal",
                "calibration_variant": "raw",
                "action": control.tolist(),
                "qpos": data.qpos.tolist(),
                "qvel": data.qvel.tolist(),
                "task_success": False,
                "failure_reason": "scripted_plumbing_smoke_only",
            }
        )

    with imageio.get_writer(output_video, fps=30, codec="libx264") as writer:
        for frame in frames:
            writer.append_data(frame)
    output_trace.write_text("\n".join(json.dumps(row) for row in records) + "\n", encoding="utf-8")
    print(f"video={output_video}")
    print(f"trace={output_trace}")
    print(f"frames={len(frames)}")


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
