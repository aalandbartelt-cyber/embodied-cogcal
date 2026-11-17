"""E8: closed-loop q5 compensation driven by an RGB-only yaw estimate.

Frozen ACT checkpoint, carrier bytecode and harness identical to E2/E5/E7.  The
only policy intervention is still command-side: target[4] += bias_rad.  The new
part is that bias_rad comes from a 512 px top-view RGB estimator, not from the
object qpos.  The estimator is validated separately; this script records both the
estimate and the (QA-only) estimation error.

Registered arms (PREREG_E8.md):
  est15   yaw=+15, delta=1.0 mm, estimated bias, 330 steps, seeds 12850-12869
  est0    yaw=  0, delta=1.0 mm, estimated bias, 330 steps, seeds 12850-12869
  est-15  yaw=-15, delta=1.0 mm, estimated bias, 330 steps, seeds 12850-12869  (exploratory)
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.machinery
import importlib.util
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import mujoco
import numpy as np

HERE = Path(__file__).resolve().parent
SCAN = HERE.parent / "gain-scan-20261117"
OFFICIAL = HERE.parent / "official-act-20261116"
sys.path.insert(0, str(OFFICIAL))
from rollout import CARRIER_PATH, XML_SHA256, PhysicsRecorder, receive, sha  # noqa: E402

sys.path.insert(0, str(HERE))
from theta_estimator import estimate_yaw_deg  # noqa: E402

YAW_DEGS = (-15.0, 0.0, 15.0)
DELTA_CENTER_MM = 1.0
Q5_INDEX = 4
SEED_START = 12850
SEED_COUNT = 20
CUBE_EDGE_MM = 28.0
REPO = HERE.parents[2]
CARRIER_PYC = REPO / ".carrier-rt/a/b/carrier.pyc"
CLOSE_Q6 = 0.26
CLOSE_MIN_STEP = 40
CONTROL_BUDGET = 330
ESTIMATOR_CAMERA = "top"
ESTIMATOR_RESOLUTION = 512
VALIDATION_JSON = HERE / "validation_open" / "validation.json"


def w_eff_mm(yaw_deg: float) -> float:
    t = math.radians(yaw_deg)
    return float(CUBE_EDGE_MM * (abs(math.cos(t)) + abs(math.sin(t))))


def delta_mm_for(yaw_deg: float, center_mm: float, seed: int) -> float:
    yaw_key = int(round(yaw_deg * 10))
    if yaw_key < 0:
        yaw_key += 1000
    rng = np.random.default_rng([20261118, yaw_key, int(center_mm * 10), seed])
    return float(center_mm + rng.uniform(-0.5, 0.5))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yaw-deg", type=float, required=True)
    parser.add_argument("--tag", choices=["smoke", "e8"], default="e8")
    parser.add_argument("--checkpoint", type=Path,
                        default=Path("/home/mary/research/embodied-cogcal/checkpoints/official-act-20261116/final-20000.pt"))
    parser.add_argument("--training-contract", type=Path, default=OFFICIAL / "training/contract.json")
    parser.add_argument("--policy-python", type=Path,
                        default=Path("/home/mary/.cache/cogcal/venvs/tpsc-policy/bin/python"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--physics", type=Path, required=True)
    parser.add_argument("--seed-start", type=int, default=SEED_START)
    parser.add_argument("--seed-count", type=int, default=SEED_COUNT)
    args = parser.parse_args()
    if args.out.exists() or args.physics.exists():
        parser.error("fresh output required")
    if args.yaw_deg not in YAW_DEGS:
        parser.error(f"registered E8 yaws are {YAW_DEGS}")
    if args.tag == "e8":
        if (args.seed_count, args.seed_start) != (SEED_COUNT, SEED_START):
            parser.error(f"registered E8 runs fix seeds {SEED_START}-{SEED_START + SEED_COUNT - 1}")
    else:
        if args.seed_count > 2:
            parser.error("smoke runs use at most 2 episodes")
        if set(range(args.seed_start, args.seed_start + args.seed_count)) & set(
                range(SEED_START, SEED_START + SEED_COUNT)):
            parser.error("smoke seeds must not touch the registered 12850-12869 block")
    if not VALIDATION_JSON.exists():
        raise FileNotFoundError("run validate_estimator.py first")
    validation = json.loads(VALIDATION_JSON.read_text())
    if float(validation["max_abs_error_deg"]) > 1.5:
        raise ValueError("estimator failed the preregistered static precision gate")
    seeds = list(range(args.seed_start, args.seed_start + args.seed_count))
    w_eff = w_eff_mm(args.yaw_deg)

    if not CARRIER_PYC.exists():
        raise FileNotFoundError(f"surviving carrier bytecode missing: {CARRIER_PYC}")
    carrier_loader = importlib.machinery.SourcelessFileLoader("e8_carrier", str(CARRIER_PYC))
    spec = importlib.util.spec_from_loader("e8_carrier", carrier_loader)
    carrier_module = importlib.util.module_from_spec(spec)
    carrier_loader.exec_module(carrier_module)
    if carrier_module.ROOT.resolve() != REPO.resolve():
        raise ValueError(f"carrier root mismatch: {carrier_module.ROOT}")
    c = carrier_module.Carrier()
    if sha(c.upstream.MODEL_XML) != XML_SHA256 or mujoco.__version__ != "4.0.1":
        raise ValueError("model/physics changed from qualified teacher")

    estimator_renderer = mujoco.Renderer(c.model, ESTIMATOR_RESOLUTION, ESTIMATOR_RESOLUTION)
    estimator_camera = mujoco.MjvCamera()
    camera_settings = c.camera_settings[ESTIMATOR_CAMERA]
    estimator_camera.lookat[:] = camera_settings["lookat"]
    estimator_camera.distance = camera_settings["distance"]
    estimator_camera.azimuth = camera_settings["azimuth"]
    estimator_camera.elevation = camera_settings["elevation"]

    args.out.mkdir(parents=True)
    args.physics.mkdir(parents=True)
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    environment["PYTHONNOUSERSITE"] = "1"
    recorder = None
    original_step = mujoco.mj_step

    def step_and_record(model, data, *a, **kwargs):
        result = original_step(model, data, *a, **kwargs)
        if recorder is not None and model is c.model and data is c.data:
            recorder.sample()
        return result

    rows = []
    with (args.out / "worker.stderr.txt").open("x") as errors:
        worker = subprocess.Popen(
            [str(args.policy_python), "-u", str(OFFICIAL / "infer_worker.py"),
             "--checkpoint", str(args.checkpoint), "--contract", str(args.training_contract)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors,
            text=True, bufsize=1, env=environment)
        try:
            ready = receive(worker)
            if not ready.get("ready"):
                raise ValueError("no valid worker readiness")
            deltas = {seed: delta_mm_for(args.yaw_deg, DELTA_CENTER_MM, seed) for seed in seeds}
            contract = {
                "kind": "e8_rgb_theta_estimator_not_method",
                "yaw_deg": args.yaw_deg,
                "q5_index": Q5_INDEX,
                "q5_joint": "wrist_roll",
                "injection": "target[4] += bias_estimator; policy inputs untouched",
                "estimator": {
                    "input": "top RGB only, 512x512",
                    "method": "orange threshold + largest component + minimum-area rectangle",
                    "range_deg": [-45.0, 45.0],
                    "color_threshold": "r>200 & g>150 & b<150 & r-b>60",
                    "area_px": [200, 5000],
                    "validation_json": str(VALIDATION_JSON),
                    "validation_max_abs_error_deg": validation["max_abs_error_deg"],
                    "validation_mean_abs_error_deg": validation["mean_abs_error_deg"],
                    "validation_sha256": sha(VALIDATION_JSON),
                    "theta_estimator_sha256": sha(HERE / "theta_estimator.py"),
                },
                "control_budget": CONTROL_BUDGET,
                "budget_rationale": "E7A: 330 removes the release-tail confound and is fixed for all arms",
                "cube_edge_mm": CUBE_EDGE_MM,
                "w_eff_mm": w_eff,
                "delta_center_mm": DELTA_CENTER_MM,
                "delta_halfwidth_mm": 0.5,
                "delta_mm_per_seed": deltas,
                "tag": args.tag,
                "worker": ready,
                "checkpoint": str(args.checkpoint),
                "checkpoint_sha256": sha(args.checkpoint),
                "carrier_pyc": str(CARRIER_PYC),
                "carrier_pyc_sha256": sha(CARRIER_PYC),
                "training_contract_sha256": sha(args.training_contract),
                "prereg_sha256": sha(HERE / "PREREG_E8.md"),
                "seeds": seeds,
                "control_fps": 30,
                "horizon": 100,
                "execute": 30,
                "policy_inputs": ["current_two_RGB", "current_measured_q_rad"],
                "estimator_uses_object_qpos": False,
                "source_sha256": {str(p): sha(p) for p in [
                    CARRIER_PYC, HERE / "rollout_e8.py", HERE / "theta_estimator.py",
                    OFFICIAL / "rollout.py", OFFICIAL / "infer_worker.py", OFFICIAL / "act_interface.py",
                ]},
            }
            (args.out / "contract.json").write_text(json.dumps(contract, indent=2) + "\n")
            mujoco.mj_step = step_and_record
            with (args.out / "episodes.jsonl").open("x") as output:
                for seed in seeds:
                    started = time.monotonic()
                    delta_mm = deltas[seed]
                    shift = np.array([delta_mm / 1000.0, delta_mm / 1000.0, 0.0])
                    recorder = None
                    c.reset(seed)
                    half = math.radians(args.yaw_deg) / 2.0
                    c.data.qpos[c.cube_address + 3:c.cube_address + 7] = [
                        math.cos(half), 0.0, 0.0, math.sin(half)]
                    if delta_mm:
                        c.source_xyz = c.source_xyz + shift
                        c.data.qpos[c.cube_address:c.cube_address + 3] = c.source_xyz
                        mujoco.mj_forward(c.model, c.data)
                        if c.initial_penetrations():
                            raise ValueError("shifted object interpenetrates robot")
                    estimator_renderer.update_scene(c.data, camera=estimator_camera)
                    estimate_deg = estimate_yaw_deg(estimator_renderer.render())
                    estimate_error_deg = estimate_deg - args.yaw_deg
                    if abs(estimate_error_deg) > 5.0:
                        raise ValueError(
                            f"estimator gross failure at seed {seed}: true={args.yaw_deg} est={estimate_deg}")
                    bias_rad = math.radians(estimate_deg)
                    if not -math.radians(30) <= bias_rad <= math.radians(30):
                        raise ValueError("estimated bias outside the FK-audited range")
                    worker.stdin.write(json.dumps({"reset": True}) + "\n")
                    worker.stdin.flush()
                    if receive(worker) != {"reset": True}:
                        raise ValueError("worker did not reset")
                    recorder = PhysicsRecorder(c)
                    trace_path = args.out / f"{seed}.trace.jsonl"
                    close_step = None
                    with trace_path.open("x") as trace:
                        chunk = None
                        for step in range(CONTROL_BUDGET):
                            before = c.observe()["q_rad"]
                            if close_step is None and step >= CLOSE_MIN_STEP and before[5] < CLOSE_Q6:
                                close_step = step
                            query = step % 30 == 0
                            record = {"seed": seed, "control_step": step, "q_before_rad": before.tolist(),
                                      "delta_mm": delta_mm, "yaw_est_deg": estimate_deg,
                                      "yaw_est_error_deg": estimate_error_deg,
                                      "q5_bias_est_rad": bias_rad,
                                      "close_onset_step": close_step}
                            if query:
                                observation = c.observe(images=True)
                                q = np.asarray(observation["q_rad"], dtype=np.float32)
                                request = {"rgb": base64.b64encode(observation["rgb"].tobytes()).decode(),
                                           "q_rad": q.tolist()}
                                worker.stdin.write(json.dumps(request) + "\n")
                                worker.stdin.flush()
                                chunk = np.asarray(receive(worker)["chunk_rad"])
                                if chunk.shape != (100, 6) or not np.isfinite(chunk).all():
                                    raise ValueError("bad ACT chunk")
                                record.update({"chunk_rad": chunk.tolist(), "policy_q_rad": q.tolist(),
                                               "rgb_sha256": hashlib.sha256(observation["rgb"].tobytes()).hexdigest(),
                                               "rgb_age_steps": 0})
                            policy_target = chunk[step % 30].copy()
                            target = policy_target.copy()
                            target[Q5_INDEX] += bias_rad
                            recorder.control_step = step
                            command = c.step(target)
                            record.update({"policy_target_rad": policy_target.tolist(),
                                           "raw_target_rad": target.tolist(),
                                           "command_rad": command.tolist(),
                                           "q_after_rad": c.observe()["q_rad"].tolist(),
                                           "sim_time_s": float(c.data.time)})
                            trace.write(json.dumps(record) + "\n")
                    physics_path = args.physics / f"{seed}.npz"
                    recorder.save(physics_path)
                    row = {"seed": seed, "yaw_deg": args.yaw_deg, "w_eff_mm": w_eff,
                           "delta_center_mm": DELTA_CENTER_MM, "delta_mm": delta_mm, "tag": args.tag,
                           "yaw_est_deg": estimate_deg, "yaw_est_error_deg": estimate_error_deg,
                           "q5_bias_est_deg": estimate_deg, "q5_bias_est_rad": bias_rad,
                           "control_budget": CONTROL_BUDGET,
                           "close_onset_step": close_step,
                           "wall_s": time.monotonic() - started,
                           "source_xyz_m": c.source_xyz.tolist(), "goal_xyz_m": c.goal_xyz.tolist(),
                           "physics_path": str(physics_path), "physics_sha256": sha(physics_path),
                           "trace_sha256": sha(trace_path), **c.outcome()}
                    row["failure_reason"] = (
                        None if row["task_success"] else "two_finger_lift_not_established"
                        if row["longest_two_finger_lift_s"] < .5 else "placement_not_achieved"
                        if not row["placed"] else "release_not_verified"
                        if not row["released"] else "penetration_limit_exceeded")
                    output.write(json.dumps(row) + "\n")
                    output.flush()
                    rows.append(row)
                    print(json.dumps(row), flush=True)
        finally:
            mujoco.mj_step = original_step
            estimator_renderer.close()
            c.close()
            worker.stdin.close()
            try:
                worker.wait(timeout=15)
            except subprocess.TimeoutExpired:
                worker.terminate()
                worker.wait(timeout=15)
    result = {"yaw_deg": args.yaw_deg, "w_eff_mm": w_eff, "delta_center_mm": DELTA_CENTER_MM,
              "tag": args.tag, "episodes": len(rows),
              "task_successes": sum(r["task_success"] for r in rows),
              "mean_abs_yaw_est_error_deg": float(np.mean([abs(r["yaw_est_error_deg"]) for r in rows])),
              "max_abs_yaw_est_error_deg": float(np.max([abs(r["yaw_est_error_deg"]) for r in rows])),
              "new_method_effect": "not_tested", "novelty": "not_established", "rows": rows}
    (args.out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["yaw_deg", "w_eff_mm", "tag", "episodes",
                                            "task_successes", "mean_abs_yaw_est_error_deg",
                                            "max_abs_yaw_est_error_deg"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
