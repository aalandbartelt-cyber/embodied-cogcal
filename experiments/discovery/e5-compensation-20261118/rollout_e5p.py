"""E5-prime: command-side q5 (wrist_roll) compensation for object yaw.

Frozen ACT checkpoint, carrier bytecode and harness identical to E2. The only
change is on the command side: every control target sent to the simulator gets a
constant offset on joint index 4 (wrist_roll), i.e. target[4] += bias_rad.

Why this is admissible: FK on the qualified model gives d(phi_close)/d(q5) =
1.0000, the roll axis is vertical and passes through the fingertip grasp point,
and q5 += 15 deg moves the gripper origin by 0.00 mm (ANCHOR_PROBE.md section 5).
So the offset rotates the closing axis without moving the grasp point: the
minimal intervention for "the policy never turns the wrist".

Arms (registered in PREREG_E5P.md):
  * theta=15 deg, bias=+15 deg  -- matched compensation (primary);
  * theta=0 deg,  bias=+15 deg  -- naive fixed offset (specificity control).
The bias is held for all 285 control steps; the placement criterion is
orientation-free (position xy <= 35 mm, |z - 0.014| <= 12 mm), so keeping the
wrist rotated through release cannot fail the task by cube yaw alone. Removing
the bias during lift would rotate a held object, a second intervention that
would confound the compensation test (PREREG_E5P section 8 records the
deviation from the DIRECTION sketch).

The bias has no visual feedback loop of its own: the policy sees the measured q
(including the offset) at the next query, so any policy reaction is measured,
not assumed away.
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

YAW_DEGS = (0.0, 15.0)
DELTA_CENTERS_MM = (1.0,)
Q5_INDEX = 4  # wrist_roll in the carrier's six-joint order
SEED_START = 12850
SEED_COUNT = 20
CUBE_EDGE_MM = 28.0
REPO = HERE.parents[2]
CARRIER_PYC = REPO / ".carrier-rt/a/b/carrier.pyc"


def w_eff_mm(yaw_deg: float) -> float:
    """Effective width of a square of side CUBE_EDGE_MM seen along the closing axis."""
    t = math.radians(yaw_deg)
    return float(CUBE_EDGE_MM * (abs(math.cos(t)) + abs(math.sin(t))))


def delta_mm_for(yaw_deg: float, center_mm: float, seed: int) -> float:
    """Deterministic uniform draw inside [center-0.5, center+0.5) mm.

    Keyed by (yaw, delta centre, seed) so one seed sees the same offset in every
    yaw condition: the width comparison is paired across yaw.
    """
    rng = np.random.default_rng([20261118, int(yaw_deg * 10), int(center_mm * 10), seed])
    return float(center_mm + rng.uniform(-0.5, 0.5))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yaw-deg", type=float, required=True, choices=list(YAW_DEGS),
                        help="cube yaw about the vertical axis, degrees")
    parser.add_argument("--delta-center-mm", type=float, required=True, choices=list(DELTA_CENTERS_MM),
                        help="delta centre of the 1 mm uniform bin")
    parser.add_argument("--q5-bias-deg", type=float, required=True,
                        help="constant wrist_roll offset added to every command, degrees")
    parser.add_argument("--tag", choices=["smoke", "e5p"], default="e5p")
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
    w_eff = w_eff_mm(args.yaw_deg)
    registered = set(range(SEED_START, SEED_START + SEED_COUNT))
    if args.tag == "e5p":
        if (args.seed_count, args.seed_start) != (SEED_COUNT, SEED_START):
            parser.error(f"registered E5-prime runs fix seeds {SEED_START}-{SEED_START + SEED_COUNT - 1}")
        if abs(args.q5_bias_deg) not in (0.0, 15.0):
            parser.error("registered arms use bias 0 or +15 deg only")
    else:
        if args.seed_count > 4:
            parser.error("smoke runs use at most 4 episodes")
        if set(range(args.seed_start, args.seed_start + args.seed_count)) & registered:
            parser.error("smoke seeds must not touch the registered 12850-12869 block")
    bias_rad = math.radians(args.q5_bias_deg)
    if not -math.radians(30) <= bias_rad <= math.radians(30):
        parser.error("bias outside the FK-audited range (-30, +30) deg")
    seeds = list(range(args.seed_start, args.seed_start + args.seed_count))

    # Carrier bytecode is the only surviving artifact of the audited collector; its
    # baked ROOT expects four parent levels, hence the relocated copy. Identity is
    # anchored on that bytecode's hash plus the frozen XML hash below.
    if not CARRIER_PYC.exists():
        raise FileNotFoundError(f"surviving carrier bytecode missing: {CARRIER_PYC}")
    carrier_loader = importlib.machinery.SourcelessFileLoader("e1p_carrier", str(CARRIER_PYC))
    spec = importlib.util.spec_from_loader("e1p_carrier", carrier_loader)
    carrier_module = importlib.util.module_from_spec(spec)
    carrier_loader.exec_module(carrier_module)
    if carrier_module.ROOT.resolve() != REPO.resolve():
        raise ValueError(f"carrier root mismatch: {carrier_module.ROOT}")
    c = carrier_module.Carrier()
    if sha(c.upstream.MODEL_XML) != XML_SHA256 or mujoco.__version__ != "4.0.1":
        raise ValueError("model/physics changed from qualified teacher")

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
            deltas = {seed: delta_mm_for(args.yaw_deg, args.delta_center_mm, seed) for seed in seeds}
            contract = {
                "kind": "e5p_command_side_q5_compensation_not_method",
                "yaw_deg": args.yaw_deg,
                "q5_bias_deg": args.q5_bias_deg,
                "q5_bias_rad": bias_rad,
                "q5_index": Q5_INDEX,
                "q5_joint": "wrist_roll",
                "injection": "target[4] += bias for all 285 control steps; policy inputs untouched",
                "cube_edge_mm": CUBE_EDGE_MM,
                "w_eff_mm": w_eff,
                "delta_center_mm": args.delta_center_mm,
                "delta_halfwidth_mm": 0.5,
                "delta_mm_per_seed": deltas,
                "tag": args.tag,
                "worker": ready,
                "checkpoint": str(args.checkpoint),
                "checkpoint_sha256": sha(args.checkpoint),
                "carrier_pyc": str(CARRIER_PYC),
                "carrier_pyc_sha256": sha(CARRIER_PYC),
                "carrier_source": "deleted after the audit; loaded from surviving bytecode",
                "training_contract_sha256": sha(args.training_contract),
                "prereg_sha256": sha(HERE / "PREREG_E5P.md"),
                "seeds": seeds,
                "control_fps": 30,
                "control_budget": 285,
                "horizon": 100,
                "execute": 30,
                "policy_inputs": ["current_two_RGB", "current_measured_q_rad"],
                "source_sha256": {str(p): sha(p) for p in [
                    CARRIER_PYC, HERE / "rollout_e5p.py", OFFICIAL / "rollout.py",
                    OFFICIAL / "infer_worker.py", OFFICIAL / "act_interface.py",
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
                    # Yaw about the vertical axis: the cube stays flat on the table
                    # (free-joint z unchanged), but its width along the closing axis
                    # becomes W(|cos t| + |sin t|). Appearance is nearly unchanged.
                    half = math.radians(args.yaw_deg) / 2.0
                    c.data.qpos[c.cube_address + 3:c.cube_address + 7] = [
                        math.cos(half), 0.0, 0.0, math.sin(half)]
                    if delta_mm:
                        c.source_xyz = c.source_xyz + shift
                        c.data.qpos[c.cube_address:c.cube_address + 3] = c.source_xyz
                        mujoco.mj_forward(c.model, c.data)
                        if c.initial_penetrations():
                            raise ValueError("shifted object interpenetrates robot")
                    worker.stdin.write(json.dumps({"reset": True}) + "\n")
                    worker.stdin.flush()
                    if receive(worker) != {"reset": True}:
                        raise ValueError("worker did not reset")
                    recorder = PhysicsRecorder(c)
                    trace_path = args.out / f"{seed}.trace.jsonl"
                    with trace_path.open("x") as trace:
                        chunk = None
                        for step in range(285):
                            before = c.observe()["q_rad"]
                            query = step % 30 == 0
                            record = {"seed": seed, "control_step": step, "q_before_rad": before.tolist(),
                                      "delta_mm": delta_mm}
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
                                           "q5_bias_rad": bias_rad,
                                           "command_rad": command.tolist(),
                                           "q_after_rad": c.observe()["q_rad"].tolist(),
                                           "sim_time_s": float(c.data.time)})
                            trace.write(json.dumps(record) + "\n")
                    physics_path = args.physics / f"{seed}.npz"
                    recorder.save(physics_path)
                    row = {"seed": seed, "yaw_deg": args.yaw_deg, "w_eff_mm": w_eff,
                           "delta_center_mm": args.delta_center_mm, "delta_mm": delta_mm, "tag": args.tag,
                           "q5_bias_deg": args.q5_bias_deg,
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
            c.close()
            worker.stdin.close()
            try:
                worker.wait(timeout=15)
            except subprocess.TimeoutExpired:
                worker.terminate()
                worker.wait(timeout=15)
    result = {"yaw_deg": args.yaw_deg, "w_eff_mm": w_eff, "delta_center_mm": args.delta_center_mm,
              "q5_bias_deg": args.q5_bias_deg, "tag": args.tag, "episodes": len(rows),
              "task_successes": sum(r["task_success"] for r in rows),
              "new_method_effect": "not_tested", "novelty": "not_established", "rows": rows}
    (args.out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["yaw_deg", "w_eff_mm", "delta_center_mm", "episodes", "task_successes"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
