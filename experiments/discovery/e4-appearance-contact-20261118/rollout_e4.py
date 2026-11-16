"""E4 rollout: one of four appearance/contact conditions, 20 paired seeds.

Same frozen ACT checkpoint, same surviving carrier bytecode, same control budget
as E2. The only knob is where the 15 deg of yaw sits -- see make_variants.py and
PREREG.md:

  deg0        model deg0,        body 0 deg   (control: E2's theta=0)
  visual      model visual,      body 0 deg   (image rotated, object axis-aligned)
  collision   model collision,   body 15 deg  (object rotated, image axis-aligned)
  both        model deg0,        body 15 deg  (E2's theta=15)

Inference only. The contract records the tree, the compiled XML hash, both yaws
as measured from d.geom_xmat at reset, and the instrumentation-check hash.
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
OFFICIAL = HERE.parent / "official-act-20261116"
sys.path.insert(0, str(OFFICIAL))
from rollout import PhysicsRecorder, receive, sha  # noqa: E402

SEED_START = 12880
SEED_COUNT = 20
DELTA_CENTER_MM = 1.0
DELTA_HALFWIDTH_MM = 0.5
REPO = HERE.parents[2]
CARRIER_PYC = REPO / ".carrier-rt/a/b/carrier.pyc"
CONDITIONS = ("deg0", "visual", "collision", "both")


def delta_mm_for(seed: int) -> float:
    """Deterministic uniform draw, keyed by seed only so all four conditions see
    the same offset for the same seed (paired comparison)."""
    rng = np.random.default_rng([20261118, 20261118, seed])
    return float(DELTA_CENTER_MM + rng.uniform(-DELTA_HALFWIDTH_MM, DELTA_HALFWIDTH_MM))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", required=True, choices=list(CONDITIONS))
    parser.add_argument("--tag", choices=["smoke", "e4"], default="e4")
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
    if not 1 <= args.seed_count <= SEED_COUNT:
        parser.error(f"seed count must be 1..{SEED_COUNT}")
    seeds = list(range(args.seed_start, args.seed_start + args.seed_count))
    if not set(seeds) <= set(range(SEED_START, SEED_START + SEED_COUNT)):
        parser.error(f"seeds must stay inside the pre-registered {SEED_START}-{SEED_START + SEED_COUNT - 1}")

    variants = json.loads((HERE / "variants.json").read_text())
    entry = variants["conditions"][args.condition]
    check = json.loads((HERE / "variants_check.json").read_text())
    if not check.get("checks_passed") or check.get("variants_sha256") != sha(HERE / "variants.json"):
        raise ValueError("instrumentation checks are missing, failed, or stale; run check_variants.py")

    if not CARRIER_PYC.exists():
        raise FileNotFoundError(f"surviving carrier bytecode missing: {CARRIER_PYC}")
    loader = importlib.machinery.SourcelessFileLoader("e4_carrier", str(CARRIER_PYC))
    spec = importlib.util.spec_from_loader("e4_carrier", loader)
    carrier_module = importlib.util.module_from_spec(spec)
    loader.exec_module(carrier_module)
    if carrier_module.ROOT.resolve() != REPO.resolve():
        raise ValueError(f"carrier root mismatch: {carrier_module.ROOT}")
    c = carrier_module.Carrier(source=Path(entry["source"]).resolve())
    if Path(c.upstream.MODEL_XML).resolve() != Path(entry["xml"]).resolve():
        raise ValueError(f"carrier model {c.upstream.MODEL_XML} is not the condition model {entry['xml']}")
    if sha(c.upstream.MODEL_XML) != entry["xml_sha256"]:
        raise ValueError("condition model hash changed")
    if mujoco.__version__ != "4.0.1":
        raise ValueError("mujoco version changed from qualified teacher")

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

    body_yaw = float(entry["body_yaw_deg"])
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
            deltas = {seed: delta_mm_for(seed) for seed in seeds}
            contract = {
                "kind": "e4_appearance_contact_decoupling_not_method",
                "condition": args.condition,
                "tree": entry["tree"],
                "model_xml": entry["xml"],
                "model_xml_sha256": entry["xml_sha256"],
                "body_yaw_deg": body_yaw,
                "look_geom_yaw_deg": entry["geom_yaw_deg"].get("cube_look", 0.0),
                "image_yaw_deg": entry["image_yaw_deg"],
                "cube_edge_mm": 28.0,
                "delta_center_mm": DELTA_CENTER_MM,
                "delta_halfwidth_mm": DELTA_HALFWIDTH_MM,
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
                "variants_sha256": sha(HERE / "variants.json"),
                "variants_check_sha256": sha(HERE / "variants_check.json"),
                "seeds": seeds,
                "control_fps": 30,
                "control_budget": 285,
                "horizon": 100,
                "execute": 30,
                "policy_inputs": ["current_two_RGB", "current_measured_q_rad"],
                "source_sha256": {str(p): sha(p) for p in [
                    CARRIER_PYC, HERE / "rollout_e4.py", HERE / "make_variants.py",
                    HERE / "check_variants.py", OFFICIAL / "rollout.py",
                    OFFICIAL / "infer_worker.py", OFFICIAL / "act_interface.py",
                ]},
            }
            (args.out / "contract.json").write_text(json.dumps(contract, indent=2) + "\n")
            mujoco.mj_step = step_and_record
            look = mujoco.mj_name2id(c.model, mujoco.mjtObj.mjOBJ_GEOM, "cube_look")
            visual = mujoco.mj_name2id(c.model, mujoco.mjtObj.mjOBJ_GEOM, "cube_visual")
            with (args.out / "episodes.jsonl").open("x") as output:
                for seed in seeds:
                    started = time.monotonic()
                    delta_mm = deltas[seed]
                    shift = np.array([delta_mm / 1000.0, delta_mm / 1000.0, 0.0])
                    recorder = None
                    c.reset(seed)
                    if body_yaw:
                        half = math.radians(body_yaw) / 2.0
                        c.data.qpos[c.cube_address + 3:c.cube_address + 7] = [
                            math.cos(half), 0.0, 0.0, math.sin(half)]
                    if delta_mm:
                        c.source_xyz = c.source_xyz + shift
                        c.data.qpos[c.cube_address:c.cube_address + 3] = c.source_xyz
                    mujoco.mj_forward(c.model, c.data)
                    if c.initial_penetrations():
                        raise ValueError("shifted object interpenetrates robot")
                    look_yaw = math.degrees(math.atan2(
                        float(c.data.geom_xmat[look][3]), float(c.data.geom_xmat[look][0])))
                    visual_yaw = math.degrees(math.atan2(
                        float(c.data.geom_xmat[visual][3]), float(c.data.geom_xmat[visual][0])))
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
                                      "delta_mm": delta_mm, "body_yaw_deg": body_yaw,
                                      "look_yaw_deg": look_yaw, "collision_yaw_deg": visual_yaw}
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
                    row = {"seed": seed, "condition": args.condition, "body_yaw_deg": body_yaw,
                           "look_yaw_deg": look_yaw, "collision_yaw_deg": visual_yaw,
                           "delta_mm": delta_mm, "tag": args.tag,
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
    result = {"condition": args.condition, "tree": entry["tree"], "body_yaw_deg": body_yaw,
              "image_yaw_deg": entry["image_yaw_deg"], "tag": args.tag, "episodes": len(rows),
              "task_successes": sum(r["task_success"] for r in rows),
              "new_method_effect": "not_tested", "novelty": "not_established", "rows": rows}
    (args.out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["condition", "episodes", "task_successes"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
