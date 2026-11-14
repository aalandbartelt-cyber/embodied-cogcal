"""Smoke-test the TPSC scene/manifest without a VLA.

For every manifest record, reset the scene and verify object/goal/barrier
placement.  Then place the target object at the goal center and verify the
evaluator flips from false to true.  This is a scene/geometry check, not a
policy result and not evidence that TPSC works.

Run in the simulation environment:

    MUJOCO_GL=egl /home/mary/miniconda3/envs/cogcal-sim/bin/python \
      experiments/so101/tpsc-pilot/smoke_scene.py \
      --manifest experiments/so101/tpsc-pilot/manifest-full.jsonl --mode full
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from simulation.so101.tpsc_scene import (
    evaluate_tpsc_success,
    load_tpsc_scene,
    observation,
    placement_from_record,
    reset_tpsc_scene,
)


def _load(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _place_target_in_goal(model: Any, data: Any, mujoco: Any, target: str, goal: tuple[float, float, float]) -> None:
    body = model.body(f"{target}_object")
    joint_id = int(model.body_jntadr[body.id])
    address = int(model.jnt_qposadr[joint_id])
    data.qpos[address : address + 3] = [goal[0], goal[1], 0.041]
    data.qpos[address + 3 : address + 7] = [1.0, 0.0, 0.0, 0.0]
    mujoco.mj_forward(model, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--mode", choices=("pilot", "full"), default="pilot")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("scene-smoke.json"))
    args = parser.parse_args()

    import mujoco

    records = _load(args.manifest)
    model, data = load_tpsc_scene(mujoco_module=mujoco)
    errors: list[str] = []
    checked = 0
    families: set[str] = set()
    rendered: set[tuple[str, str]] = set()
    renderer = None
    if args.render:
        renderer = mujoco.Renderer(model, height=240, width=320)

    for record in records:
        placement = placement_from_record(record)
        reset_tpsc_scene(model, data, placement, mujoco)
        checked += 1
        families.add(record["family"])
        np.testing.assert_allclose(data.body("red_object").xpos, placement.red, atol=1e-9)
        np.testing.assert_allclose(data.body("blue_object").xpos, placement.blue, atol=1e-9)
        np.testing.assert_allclose(data.body("goal_region").xpos, placement.goal, atol=1e-9)
        if placement.barrier is None:
            if abs(float(data.body("barrier").xpos[2]) + 0.5) > 1e-6:
                errors.append(f"{record['episode_id']}: disabled barrier not moved away")
        else:
            np.testing.assert_allclose(data.body("barrier").xpos, placement.barrier, atol=1e-9)
        if evaluate_tpsc_success(model, data, placement):
            errors.append(f"{record['episode_id']}: target starts inside goal")
        _place_target_in_goal(model, data, mujoco, placement.target_object, placement.goal)
        if not evaluate_tpsc_success(model, data, placement):
            errors.append(f"{record['episode_id']}: target not detected in goal")
        render_key = (record["family"], record["branch"])
        if renderer is not None and render_key not in rendered:
            renderer.update_scene(data, camera="front_camera")
            image = renderer.render().copy()
            out = args.out.parent / f"tpsc_{record['family']}_{record['branch']}.png"
            import imageio.v3 as iio
            iio.imwrite(out, image)
            rendered.add(render_key)

    if renderer is not None:
        renderer.close()
    result = {
        "kind": "tpsc_scene_smoke_not_policy_result",
        "manifest": str(args.manifest),
        "mode": args.mode,
        "records_checked": checked,
        "families": sorted(families),
        "mujoco_version": mujoco.__version__,
        "errors": errors,
        "ok": not errors,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
