"""Fixed physical feasibility witnesses and ordinary retargeting controls."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import mujoco
import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/discovery/matched_bc"))
from carrier import Carrier  # noqa: E402
from retarget import MODES, generate  # noqa: E402

SOURCE = np.array([.2, -.075, .014])
GOAL = np.array([.2, .075, .014])
CASES = [
    ([.195, -.08, .014], [.175, .075, .014]),
    ([.195, -.07, .014], [.225, .075, .014]),
    ([.205, -.08, .014], [.175, .075, .014]),
    ([.205, -.07, .014], [.225, .075, .014]),
]


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def reset(carrier, source, goal):
    carrier.reset(9000)
    carrier.source_xyz = np.asarray(source, dtype=float)
    carrier.goal_xyz = np.asarray(goal, dtype=float)
    carrier.data.qpos[carrier.cube_address:carrier.cube_address + 3] = source
    mujoco.mj_forward(carrier.model, carrier.data)
    if carrier.initial_penetrations():
        raise ValueError("initial object/robot penetration in specified layout")


def execute(carrier, folder, name, source, goal, commands):
    reset(carrier, source, goal)
    if commands.shape != (285, 6) or not np.isfinite(commands).all():
        raise ValueError("expected 285 finite joint commands")
    with (folder / f"{name}.trace.jsonl").open("x") as trace:
        for step, command in enumerate(commands):
            before = carrier.data.qpos[:6].copy()
            sent = carrier.step(command)
            row = {
                "control_step": step, "q_before_rad": before.tolist(),
                "requested_rad": command.tolist(), "sent_rad": sent.tolist(),
                "q_after_rad": carrier.data.qpos[:6].tolist(),
                "object_xyz_m_evaluator_only": carrier.data.qpos[
                    carrier.cube_address:carrier.cube_address + 3].tolist(),
                "time_s": float(carrier.data.time), "physics_ticks": carrier.physics_ticks,
                "two_fingers_at_last_physics_tick": carrier.last_finger_count == 2,
                "held_run_physics_ticks": carrier.held_run,
                "longest_held_run_physics_ticks": carrier.longest_held_run,
                "release_run_physics_ticks": carrier.release_run,
                "max_penetration_m_to_date": carrier.max_penetration,
                "object_pose_writes_during_rollout": carrier.object_pose_writes_during_rollout,
            }
            trace.write(json.dumps(row) + "\n")
    result = {"name": name, "source_xyz_m": list(source), "goal_xyz_m": list(goal),
              **carrier.outcome()}
    save(folder / f"{name}.outcome.json", result)
    print(json.dumps(result), flush=True)
    return result


def run(carrier, folder):
    rows = []
    source_actions = None
    for index, (source, goal) in enumerate([(SOURCE, GOAL), *CASES]):
        name = "witness-source" if index == 0 else f"witness-target-{index - 1}"
        try:
            reset(carrier, source, goal)
            actions = carrier.teacher_actions()
        except ValueError as error:
            row = {"name": name, "source_xyz_m": list(source), "goal_xyz_m": list(goal),
                   "task_success": False, "controls": 0,
                   "qualification_error_before_rollout": str(error)}
            save(folder / f"{name}.outcome.json", row)
            rows.append(row)
            print(json.dumps(row), flush=True)
            continue
        if index == 0:
            source_actions = actions.copy()
        rows.append(execute(carrier, folder, name, source, goal, actions))
    if not all(row["task_success"] for row in rows):
        return {"status": "stopped_witness_gate", "rows": rows}
    for mode in MODES:
        commands, diagnostic = generate(carrier, source_actions, np.zeros(3), np.zeros(3), mode)
        difference = float(np.abs(commands - source_actions).max())
        diagnostic["identity_command_max_difference_rad"] = difference
        save(folder / f"identity-{mode}.ik.json", diagnostic)
        if difference > 1e-5:
            return {"status": "stopped_identity_command_gate", "rows": rows}
        rows.append(execute(carrier, folder, f"identity-{mode}", SOURCE, GOAL, commands))
        if not rows[-1]["task_success"]:
            return {"status": "stopped_identity_physics_gate", "rows": rows}
    for index, (source, goal) in enumerate(CASES):
        for mode in MODES:
            commands, diagnostic = generate(carrier, source_actions,
                                            np.asarray(source) - SOURCE, np.asarray(goal) - GOAL, mode)
            name = f"retarget-{index}-{mode}"
            save(folder / f"{name}.ik.json", diagnostic)
            row = execute(carrier, folder, name, source, goal, commands)
            rows.append(row)
    totals = {mode: sum(row["task_success"] for row in rows
                       if row["name"].startswith("retarget-") and row["name"].endswith(mode))
              for mode in MODES}
    return {"status": "completed", "rows": rows, "retarget_successes_of_four": totals,
            "decision": ("simple_direction_control_sufficient_in_tested_box_no_new_method_needed"
                         if totals["task_direction"] == 4 else
                         "unresolved_generation_or_contact_failure_not_new_mechanism_proof")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    plan = ROOT / "docs/plans/2026-11-14-retarget-physical-screen.md"
    shutil.copy2(plan, args.out / "plan-before-execution.md")
    bindings = {}
    for source in [Path(__file__), Path(__file__).with_name("retarget.py"),
                   ROOT / "experiments/discovery/matched_bc/carrier.py"]:
        destination = args.out / f"bound-{source.name}"
        shutil.copy2(source, destination)
        bindings[str(source.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()
    carrier = Carrier()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"],
                                    cwd=carrier.upstream.ROOT, text=True)
    if dirty.strip():
        raise ValueError("external tracked source modified; do not silently restore")
    contract = {
        "kind": "privileged_scripted_generation_screen_not_learned_policy_or_method_evaluation",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "bindings_sha256": bindings, "plan_sha256": hashlib.sha256(plan.read_bytes()).hexdigest(),
        "source_xyz_m": SOURCE.tolist(), "goal_xyz_m": GOAL.tolist(), "cases": CASES,
        "mujoco": mujoco.__version__, "numpy": np.__version__, "scipy": scipy.__version__,
        "dependency_added": "scipy==1.16.3 --no-deps; numpy and mujoco unchanged",
        "external_revision": subprocess.check_output(["git", "rev-parse", "HEAD"],
                                                      cwd=carrier.upstream.ROOT, text=True).strip(),
        "model_xml_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [carrier.upstream.MODEL_XML,
                                       carrier.upstream.MODEL_XML.with_name("so101_new_calib.xml")]},
        "physics_timestep_s": float(carrier.model.opt.timestep),
        "limits": ["Four hand-selected geometric layouts, not independent stochastic replications.",
                   "Source command FK and fixed privileged subtask boundaries, not observed-state reconstruction.",
                   "Ordinary IK controls, not faithful CP-Gen/MoMaGen implementations.",
                   "Goal graphics unchanged, no RGB used; no semantic instruction comparison.",
                   "External pads/friction not hardware-calibrated; 35mm is qualification not precision."]}
    save(args.out / "contract.json", contract)
    try:
        result = run(carrier, args.out)
        result.update({"episodes_completed": sum(row["controls"] == 285 for row in result["rows"]),
                       "attempts": len(result["rows"]),
                       "finished_utc": datetime.now(timezone.utc).isoformat(),
                       "claim": "bounded_generator_qualification_only_not_vla_or_novelty"})
        save(args.out / "summary.json", result)
        print(json.dumps({k: v for k, v in result.items() if k != "rows"}), flush=True)
    finally:
        carrier.close()


if __name__ == "__main__":
    main()
