"""Static validation of the RGB-only yaw estimator.

Renders the estimator's top view across the task yaw range and several reset
seeds, then compares the estimate against the programmed yaw.  This uses object
qpos only as the ground-truth label, never as estimator input.
"""

from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import json
import math
import sys
from pathlib import Path

import mujoco
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
from theta_estimator import estimate_yaw  # noqa: E402

CARRIER_PYC = REPO / ".carrier-rt/a/b/carrier.pyc"
CAMERA = "top"
RESOLUTION = 512


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=[12850, 12851, 12852, 12853, 12854])
    parser.add_argument("--yaw-min", type=float, default=-45.0)
    parser.add_argument("--yaw-max", type=float, default=45.0)
    parser.add_argument("--yaw-step", type=float, default=2.5)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    args.out.mkdir(parents=True)

    loader = importlib.machinery.SourcelessFileLoader("e8_carrier", str(CARRIER_PYC))
    spec = importlib.util.spec_from_loader("e8_carrier", loader)
    carrier_module = importlib.util.module_from_spec(spec)
    loader.exec_module(carrier_module)
    c = carrier_module.Carrier()
    renderer = mujoco.Renderer(c.model, RESOLUTION, RESOLUTION)
    camera = mujoco.MjvCamera()
    settings = c.camera_settings[CAMERA]
    camera.lookat[:] = settings["lookat"]
    camera.distance = settings["distance"]
    camera.azimuth = settings["azimuth"]
    camera.elevation = settings["elevation"]

    yaws = np.arange(args.yaw_min, args.yaw_max + args.yaw_step / 2, args.yaw_step)
    rows = []
    try:
        for yaw in yaws:
            for seed in args.seeds:
                c.reset(seed)
                half = math.radians(float(yaw)) / 2.0
                c.data.qpos[c.cube_address + 3:c.cube_address + 7] = [
                    math.cos(half), 0.0, 0.0, math.sin(half)]
                mujoco.mj_forward(c.model, c.data)
                renderer.update_scene(c.data, camera=camera)
                rgb = renderer.render()
                result = estimate_yaw(rgb)
                rows.append({"yaw_true_deg": float(yaw), "yaw_est_deg": result.yaw_deg,
                             "error_deg": result.yaw_deg - float(yaw), "seed": seed,
                             "rectangle_angle_deg": result.rectangle_angle_deg,
                             "area_px": result.area_px, "bbox": list(result.bbox)})
    finally:
        renderer.close()
        c.close()

    errors = np.array([row["error_deg"] for row in rows], dtype=float)
    summary = {
        "n": len(rows),
        "yaw_min_deg": float(yaws.min()),
        "yaw_max_deg": float(yaws.max()),
        "yaw_step_deg": args.yaw_step,
        "seeds": args.seeds,
        "max_abs_error_deg": float(np.max(np.abs(errors))),
        "mean_abs_error_deg": float(np.mean(np.abs(errors))),
        "p95_abs_error_deg": float(np.percentile(np.abs(errors), 95)),
        "rows": rows,
    }
    (args.out / "validation.json").write_text(json.dumps(summary, indent=2) + "\n")
    (args.out / "validation.csv").write_text(
        "yaw_true_deg,yaw_est_deg,error_deg,seed,rectangle_angle_deg,area_px\n"
        + "\n".join(f"{r['yaw_true_deg']},{r['yaw_est_deg']},{r['error_deg']},{r['seed']},"
                    f"{r['rectangle_angle_deg']},{r['area_px']}" for r in rows) + "\n")
    print(json.dumps({k: summary[k] for k in [
        "n", "max_abs_error_deg", "mean_abs_error_deg", "p95_abs_error_deg"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
