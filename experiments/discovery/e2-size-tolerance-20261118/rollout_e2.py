"""E2 tolerance probe: fixed lateral offset, five object yaw angles.

Inference only, same frozen ACT checkpoint and carrier bytecode as E1'. E2 asks a
single question: at the same lateral offset delta, does success depend on the
object's effective width along the closing axis? Yaw is the knob because a yawed
cube changes W_eff = W(|cos t| + |sin t|) while its silhouette barely changes, so
unlike a size sweep it does not throw the policy out of its visual distribution.

The first design (cube edge 20/28/36 mm) was killed by smoke runs: both off-nominal
sizes failed at delta ~1 mm (0/8 episodes) because size also changes appearance and
the frozen policy simply missed the grasp. PREREG.md section 0 records that evidence;
the yaw sweep below holds size and appearance nearly fixed.
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

YAW_DEGS = (0.0, 2.0, 5.0, 10.0, 15.0, 30.0, 45.0)
DELTA_CENTERS_MM = (1.0, 14.0, 18.0)  # 1.0 mm only for tag=smoke sanity checks
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
    parser.add_argument("--tag", choices=["scan", "smoke", "e2"], default="scan")
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
    if args.tag == "scan" and (args.seed_count != SEED_COUNT or args.seed_start != SEED_START):
        parser.error(f"the pilot fixes seeds {SEED_START}-{SEED_START + SEED_COUNT - 1} with {SEED_COUNT} episodes")
    if not 1 <= args.seed_count <= SEED_COUNT:
        parser.error(f"seed count must be 1..{SEED_COUNT}")
    seeds = list(range(args.seed_start, args.seed_start + args.seed_count))
    if not set(seeds) <= set(range(SEED_START, SEED_START + SEED_COUNT)):
        parser.error(f"seeds must stay inside the pre-registered {SEED_START}-{SEED_START + SEED_COUNT - 1}")

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
                "kind": "e2_yaw_tolerance_probe_not_method",
                "yaw_deg": args.yaw_deg,
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
                "prereg_sha256": sha(HERE / "PREREG.md"),
                "seeds": seeds,
                "control_fps": 30,
                "control_budget": 285,
                "horizon": 100,
                "execute": 30,
                "policy_inputs": ["current_two_RGB", "current_measured_q_rad"],
                "source_sha256": {str(p): sha(p) for p in [
                    CARRIER_PYC, HERE / "rollout_e2.py", OFFICIAL / "rollout.py",
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
                            target = chunk[step % 30]
                            recorder.control_step = step
                            command = c.step(target)
                            record.update({"raw_target_rad": target.tolist(), "command_rad": command.tolist(),
                                           "q_after_rad": c.observe()["q_rad"].tolist(),
                                           "sim_time_s": float(c.data.time)})
                            trace.write(json.dumps(record) + "\n")
                    physics_path = args.physics / f"{seed}.npz"
                    recorder.save(physics_path)
                    row = {"seed": seed, "yaw_deg": args.yaw_deg, "w_eff_mm": w_eff,
                           "delta_center_mm": args.delta_center_mm, "delta_mm": delta_mm, "tag": args.tag,
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
              "tag": args.tag, "episodes": len(rows),
              "task_successes": sum(r["task_success"] for r in rows),
              "new_method_effect": "not_tested", "novelty": "not_established", "rows": rows}
    (args.out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["yaw_deg", "w_eff_mm", "delta_center_mm", "episodes", "task_successes"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
