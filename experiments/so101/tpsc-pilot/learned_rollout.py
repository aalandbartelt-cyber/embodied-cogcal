"""20-row capability screen. No kinematic carry, object reset or TPSC correction.

All-six-degree simulation adapter is an EXPLICIT unverified carrier assumption.
This driver never interprets failure as a scientific TPSC effect.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from analysis.tpsc_prefix import paired_report, simulation_degrees_to_rad  # noqa: E402
from simulation.so101.scene import JOINT_NAMES, step_joint_targets  # noqa: E402
from simulation.so101.tpsc_scene import (  # noqa: E402
    evaluate_tpsc_success,
    load_tpsc_scene,
    placement_from_record,
    reset_tpsc_scene,
)


def main():
    import mujoco

    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--policy-python", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--control-steps", type=int, default=300)
    p.add_argument("--execute-steps", type=int, default=10)
    args = p.parse_args()
    if args.control_steps < 1 or args.execute_steps < 1:
        p.error("positive execution budgets required")
    records = [json.loads(x) for x in args.manifest.read_text().splitlines() if x.strip()]
    if len(records) != 20 or any(r["family"] != "shared_prefix" for r in records):
        p.error("this registered pilot accepts exactly 20 shared-prefix records")
    args.out.mkdir(parents=True, exist_ok=False)
    model, data = load_tpsc_scene()
    addresses = [int(model.jnt_qposadr[model.joint(n).id]) for n in JOINT_NAMES]
    low, high = model.actuator_ctrlrange[:, 0], model.actuator_ctrlrange[:, 1]
    renderer = mujoco.Renderer(model, height=256, width=256)
    # 30 Hz against 2 ms MuJoCo: accumulated rounding, never fixed 16 steps.
    elapsed_ticks = 0
    results = []
    with (args.out / "worker.stderr.log").open("w") as errors:
        worker = subprocess.Popen(
            [
                str(args.policy_python),
                str(Path(__file__).with_name("policy_worker.py")),
                "--checkpoint",
                str(args.checkpoint),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=errors,
            text=True,
            bufsize=1,
        )
        try:
            ready = worker.stdout.readline()
            if not ready:
                raise RuntimeError("worker failed to load; see worker.stderr.log")
            (args.out / "runtime.json").write_text(
                json.dumps(
                    {
                        "worker": json.loads(ready),
                        "mujoco_version": mujoco.__version__,
                        "manifest_sha256": hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
                        "dataset_robot_type": "so_follower",
                        "adapter": "simulation_all_6_degrees_to_radians_UNVERIFIED_SOURCE",
                        "claim": "capability_screen_not_tpsc_result",
                        "fps": 30,
                    },
                    indent=2,
                )
            )
            with (args.out / "episodes.jsonl").open("x") as output:
                for record in records:
                    placement = placement_from_record(record)
                    reset_tpsc_scene(model, data, placement)
                    elapsed_ticks = 0
                    clips = 0
                    first_chunk = None
                    failure = None
                    lifted = False
                    executed_targets = []
                    release_ticks = 0
                    target_body_id = model.body(f"{placement.target_object}_object").id
                    robot_ids = {
                        model.body(n).id
                        for n in [
                            "base",
                            "shoulder",
                            "upper_arm",
                            "lower_arm",
                            "wrist",
                            "gripper",
                            "moving_jaw_so101_v1",
                        ]
                    }
                    with (args.out / (record["episode_id"] + ".trace.jsonl")).open("x") as trace:
                        for step in range(0, args.control_steps, args.execute_steps):
                            images = []
                            for camera in ["overhead_camera", "front_camera"]:
                                renderer.update_scene(data, camera=camera)
                                images.append(
                                    base64.b64encode(renderer.render().tobytes()).decode()
                                )
                            request = {
                                "images": images,
                                "joint_positions_deg": np.rad2deg(data.qpos[addresses]).tolist(),
                                "task": record["task_text"],
                                "seed": 42 + step,
                            }
                            worker.stdin.write(json.dumps(request) + "\n")
                            worker.stdin.flush()
                            response = worker.stdout.readline()
                            if not response:
                                raise RuntimeError("inference worker exited; see worker.stderr.log")
                            prediction = json.loads(response)
                            q_before = data.qpos[addresses].copy()
                            executed_segment = []
                            chunk = simulation_degrees_to_rad(prediction["chunk"])
                            if len(chunk) < min(args.execute_steps, args.control_steps - step):
                                raise ValueError(
                                    "predicted chunk shorter than registered execution window"
                                )
                            if first_chunk is None:
                                first_chunk = chunk.tolist()
                            for offset, action in enumerate(
                                chunk[: min(args.execute_steps, args.control_steps - step)]
                            ):
                                clipped = np.clip(action, low, high)
                                clips += int(np.any(clipped != action))
                                executed_segment.append(clipped.tolist())
                                executed_targets.append(clipped.tolist())
                                tick_goal = round((step + offset + 1) / (30 * model.opt.timestep))
                                step_joint_targets(
                                    model, data, clipped, substeps=tick_goal - elapsed_ticks
                                )
                                elapsed_ticks = tick_goal
                                lifted |= (
                                    float(data.body(f"{placement.target_object}_object").xpos[2])
                                    >= 0.08
                                )
                                touching = any(
                                    (
                                        int(model.geom_bodyid[c.geom1]) == target_body_id
                                        and int(model.geom_bodyid[c.geom2]) in robot_ids
                                    )
                                    or (
                                        int(model.geom_bodyid[c.geom2]) == target_body_id
                                        and int(model.geom_bodyid[c.geom1]) in robot_ids
                                    )
                                    for c in data.contact
                                )
                                release_ticks = 0 if touching else release_ticks + 1
                            trace.write(
                                json.dumps(
                                    {
                                        "episode_id": record["episode_id"],
                                        "step": step,
                                        "qpos_robot_before_rad": q_before.tolist(),
                                        "executed_targets_rad": executed_segment,
                                        "action_seed": 42 + step,
                                        "input_rgb_sha256": [
                                            hashlib.sha256(base64.b64decode(x)).hexdigest()
                                            for x in images
                                        ],
                                        "action_chunk_rad": chunk.tolist(),
                                        "qpos_robot_rad": data.qpos[addresses].tolist(),
                                        "sim_time_s": float(data.time),
                                        "inference_s": prediction["inference_s"],
                                        "clip_events_cumulative": clips,
                                    }
                                )
                                + "\n"
                            )
                            trace.flush()
                            if not np.isfinite(data.qpos).all():
                                failure = "non_finite_simulation"
                                break
                    placement_ok = evaluate_tpsc_success(model, data, placement)
                    success = placement_ok and lifted and release_ticks >= 3 and failure is None
                    row = {
                        "episode_id": record["episode_id"],
                        "case_id": record["episode_id"].rsplit("_", 1)[0],
                        "branch": record["branch"],
                        "action_seed": 42,
                        "task_success": bool(success),
                        "placement_success": bool(placement_ok),
                        "lift_observed": bool(lifted),
                        "final_no_robot_contact_ticks": release_ticks,
                        "failure_reason": failure
                        or (
                            None
                            if success
                            else (
                                "stable_placement_not_achieved"
                                if not placement_ok
                                else (
                                    "required_lift_not_observed"
                                    if not lifted
                                    else "release_not_verified"
                                )
                            )
                        ),
                        "first_chunk_rad": first_chunk,
                        "executed_targets_rad": executed_targets,
                        "final_target_xyz": data.body(
                            f"{placement.target_object}_object"
                        ).xpos.tolist(),
                        "branch_onset_step": None,
                        "clip_events": clips,
                        "claim": "capability_screen_unverified_camera_and_adapter_not_tpsc_effect",
                    }
                    output.write(json.dumps(row) + "\n")
                    output.flush()
                    results.append(row)
                    print(
                        json.dumps(
                            {
                                "episode_id": row["episode_id"],
                                "success": row["task_success"],
                                "clips": clips,
                            }
                        ),
                        flush=True,
                    )
        finally:
            if worker.stdin:
                worker.stdin.close()
            worker.terminate()
            worker.wait(timeout=30)
            renderer.close()
    report = paired_report(results)
    report["capability_gate"] = "not_established_until_camera_and_adapter_validated"
    (args.out / "prefix-report.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
