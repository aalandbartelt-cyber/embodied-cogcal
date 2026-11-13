"""Load and optionally render the pinned SO-101 MuJoCo asset."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def default_scene() -> Path:
    return Path(__file__).resolve().parents[1] / "third_party/SO-ARM100/Simulation/SO101/scene.xml"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", type=Path, default=default_scene())
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("results/figures/so101_smoke.png"))
    args = parser.parse_args()

    try:
        import mujoco
    except ImportError as exc:
        raise SystemExit(
            "mujoco is not installed; create cogcal-sim and install the simulation dependencies"
        ) from exc

    if not args.scene.exists():
        raise SystemExit(f"scene file does not exist: {args.scene}")

    model = mujoco.MjModel.from_xml_path(str(args.scene))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    joint_names = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(model.njnt)]
    print(f"scene={args.scene}")
    print(f"nq={model.nq} nv={model.nv} nu={model.nu} joints={joint_names}")
    print(f"MUJOCO_GL={os.environ.get('MUJOCO_GL', '<unset>')}")

    if not args.render:
        return

    renderer = mujoco.Renderer(model, height=480, width=640)
    renderer.update_scene(data)
    pixels = renderer.render()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        from imageio.v3 import imwrite
    except ImportError as exc:
        raise SystemExit("imageio is required for --render") from exc
    imwrite(args.output, pixels)
    print(f"render={args.output}")


if __name__ == "__main__":
    main()
