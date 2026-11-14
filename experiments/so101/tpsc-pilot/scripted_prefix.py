"""Scripted IK waypoint prefix check for the TPSC pilot.

This is not a VLA result and not a success benchmark.  It generates a
deterministic pick-place waypoint sequence with damped-least-squares IK and
checks whether the shared-prefix branches have identical joint targets/executed
prefixes before the goal branch.  A low grasp success rate is acceptable here;
the scientific question (does a VLA policy share the prefix?) still requires a
policy rollout.

Run in the simulation environment:

    env -u PYTHONPATH PYTHONNOUSERSITE=1 PYTHONPATH=. \
      /home/mary/miniconda3/envs/cogcal-sim/bin/python \
      experiments/so101/tpsc-pilot/scripted_prefix.py \
      --manifest experiments/so101/tpsc-pilot/manifest-pilot.jsonl --mode pilot
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from probes.generators.tpsc_pairs import waypoint_targets
from simulation.so101.scene import JOINT_NAMES
from simulation.so101.tpsc_scene import (
    evaluate_tpsc_success,
    load_tpsc_scene,
    placement_from_record,
    reset_tpsc_scene,
    step_joint_targets,
)

ARM_JOINTS = JOINT_NAMES[:5]
GRIPPER_JOINT = JOINT_NAMES[5]
OPEN = 0.0
CLOSED = 1.4
IK_ITERS = 240
IK_TOL = 0.004
DAMPING = 1e-3
STEPS_PER_SEGMENT = 10
SUBSTEPS = 10


def _load(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _solve_ik(
    model: Any,
    data: Any,
    mujoco: Any,
    target: np.ndarray,
    q_start: np.ndarray,
    *,
    qpos_addresses: list[int],
    dof_addresses: list[int],
    low: np.ndarray,
    high: np.ndarray,
    jaw_body_id: int,
    gripper_address: int,
    jaw_name: str,
) -> tuple[np.ndarray, float, int, bool]:
    q = np.asarray(q_start, dtype=float).copy()
    best_q = q.copy()
    best_error = float("inf")
    for iteration in range(IK_ITERS):
        data.qpos[qpos_addresses] = q
        data.qpos[gripper_address] = OPEN
        mujoco.mj_forward(model, data)
        jaw = data.body(jaw_name).xpos.copy()
        error = target - jaw
        error_norm = float(np.linalg.norm(error))
        if error_norm < best_error:
            best_error = error_norm
            best_q = q.copy()
        if error_norm < IK_TOL:
            return q, error_norm, iteration, True
        jacp = np.zeros((3, model.nv))
        jacr = np.zeros((3, model.nv))
        mujoco.mj_jac(model, data, jacp, jacr, jaw, jaw_body_id)
        jacobian = jacp[:, dof_addresses]
        # Damped least squares with a small nullspace bias toward the start pose.
        jj = jacobian @ jacobian.T + DAMPING * np.eye(3)
        pinv = jacobian.T @ np.linalg.solve(jj, np.eye(3))
        dq = pinv @ error
        nullspace = np.eye(len(q)) - pinv @ jacobian
        dq += nullspace @ (0.05 * (q_start - q))
        norm = float(np.linalg.norm(dq))
        if norm > 0.2:
            dq *= 0.2 / norm
        q = np.clip(q + dq, low, high)
    return best_q, best_error, IK_ITERS, False


def _interpolate(start: np.ndarray, end: np.ndarray, steps: int) -> np.ndarray:
    return np.linspace(start, end, num=steps + 1)[1:]


def _prefix_names(family: str) -> list[str]:
    # close is a gripper-only waypoint at the grasp pose; route is after lift.
    if family == "multi_valid":
        return ["home", "above_object", "grasp", "close", "lift"]
    return ["home", "above_object", "grasp", "close", "lift"]


def _rollout(
    model: Any,
    data: Any,
    mujoco: Any,
    record: dict[str, Any],
    *,
    qpos_addresses: list[int],
    dof_addresses: list[int],
    low: np.ndarray,
    high: np.ndarray,
    jaw_body_id: int,
    jaw_name: str,
    gripper_address: int,
    q_home: np.ndarray,
    write_trace: bool,
    trace_path: Path | None,
    kinematic_carry: bool = False,
) -> dict[str, Any]:
    placement = placement_from_record(record)
    reset_tpsc_scene(model, data, placement, mujoco)
    target_body = model.body(f"{record['target_object']}_object")
    target_joint = int(model.body_jntadr[target_body.id])
    target_qpos_address = int(model.jnt_qposadr[target_joint])
    target_dof_address = int(model.jnt_dofadr[target_joint])
    ik_failures: list[dict[str, Any]] = []
    ik_errors: list[float] = []

    # Solve arm waypoints with the gripper open; the close/open waypoints reuse
    # the adjacent arm pose and only change the gripper command.
    arm_targets: dict[str, np.ndarray] = {"home": q_home.copy()}
    current_q = q_home.copy()
    for name, target in waypoint_targets(record):
        target = np.asarray(target, dtype=float)
        q, error, iterations, ok = _solve_ik(
            model,
            data,
            mujoco,
            target,
            current_q,
            qpos_addresses=qpos_addresses,
            dof_addresses=dof_addresses,
            low=low,
            high=high,
            jaw_body_id=jaw_body_id,
            gripper_address=gripper_address,
            jaw_name=jaw_name,
        )
        arm_targets[name] = q
        current_q = q
        ik_errors.append(error)
        if not ok:
            ik_failures.append({"waypoint": name, "error_m": error, "iterations": iterations})

    # IK solving leaves data.qpos at the last solution; reset again so every
    # episode starts from the same home state before executing the prefix.
    reset_tpsc_scene(model, data, placement, mujoco)

    controls: list[np.ndarray] = []
    waypoint_sequence: list[tuple[str, np.ndarray, float]] = [
        ("home", arm_targets["home"], OPEN),
        ("above_object", arm_targets["above_object"], OPEN),
        ("grasp", arm_targets["grasp"], OPEN),
        ("close", arm_targets["grasp"], CLOSED),
        ("lift", arm_targets["lift"], CLOSED),
    ]
    if record["family"] == "multi_valid":
        waypoint_sequence.append(("route", arm_targets["route"], CLOSED))
    waypoint_sequence.extend(
        [
            ("above_goal", arm_targets["above_goal"], CLOSED),
            ("place", arm_targets["place"], CLOSED),
            ("open", arm_targets["place"], OPEN),
            ("retreat", arm_targets["retreat"], OPEN),
        ]
    )

    target_prefix: list[np.ndarray] = []
    executed_prefix: list[np.ndarray] = []
    prefix_steps = 0
    attached = False
    attach_offset: np.ndarray | None = None
    place_success: bool | None = None
    for index, (name, arm_target, gripper) in enumerate(waypoint_sequence):
        if index == 0:
            continue
        if name == "open":
            attached = False
        start = np.append(waypoint_sequence[index - 1][1], waypoint_sequence[index - 1][2])
        end = np.append(arm_target, gripper)
        for control in _interpolate(start, end, STEPS_PER_SEGMENT):
            controls.append(control)
            step_joint_targets(model, data, control, substeps=SUBSTEPS, mujoco_module=mujoco)
            if kinematic_carry and name == "close":
                attached = True
                attach_offset = data.body(f"{record['target_object']}_object").xpos - data.body(jaw_name).xpos
            if attached and attach_offset is not None:
                # Kinematic carry: keep the object at a fixed offset from the
                # moving jaw.  Clearly not a physics grasp; used only to test
                # the goal predicate and the post-divergence path.
                jaw = data.body(jaw_name).xpos
                data.qpos[target_qpos_address : target_qpos_address + 3] = jaw + attach_offset
                data.qpos[target_qpos_address + 3 : target_qpos_address + 7] = [1.0, 0.0, 0.0, 0.0]
                data.qvel[target_dof_address : target_dof_address + 6] = 0.0
                mujoco.mj_forward(model, data)
            if name in _prefix_names(record["family"]):
                target_prefix.append(control.copy())
                executed_prefix.append(data.qpos.copy())
                prefix_steps += 1
        if kinematic_carry and name == "place":
            # Kinematic placement for the goal-predicate/path smoke: put the
            # object exactly on the goal surface.  This is not a physics grasp.
            data.qpos[target_qpos_address : target_qpos_address + 3] = [
                placement.goal[0],
                placement.goal[1],
                0.041,
            ]
            data.qpos[target_qpos_address + 3 : target_qpos_address + 7] = [1.0, 0.0, 0.0, 0.0]
            data.qvel[target_dof_address : target_dof_address + 6] = 0.0
            mujoco.mj_forward(model, data)
            place_success = evaluate_tpsc_success(model, data, placement)

    success = evaluate_tpsc_success(model, data, placement)
    trace = None
    if write_trace and trace_path is not None:
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        rows = []
        for step, control in enumerate(controls):
            rows.append({
                "episode_id": record["episode_id"],
                "step": step,
                "action": control.tolist(),
                "sim_time_s": float(step * SUBSTEPS * model.opt.timestep),
                "success": bool(success),
            })
        trace_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
        trace = str(trace_path)
    return {
        "success": bool(success),
        "place_success": place_success,
        "ik_failures": ik_failures,
        "ik_max_error_m": max(ik_errors) if ik_errors else 0.0,
        "target_prefix": target_prefix,
        "executed_prefix": executed_prefix,
        "prefix_steps": prefix_steps,
        "route_target": np.append(arm_targets["route"], CLOSED) if "route" in arm_targets else None,
        "trace": trace,
    }


def _compare_pair(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_target = np.asarray(left["target_prefix"])
    right_target = np.asarray(right["target_prefix"])
    left_exec = np.asarray(left["executed_prefix"])
    right_exec = np.asarray(right["executed_prefix"])
    n = min(len(left_target), len(right_target), len(left_exec), len(right_exec))
    target_diff = float(np.max(np.abs(left_target[:n] - right_target[:n]))) if n else float("inf")
    executed_diff = float(np.max(np.abs(left_exec[:n] - right_exec[:n]))) if n else float("inf")
    route_diff = None
    if left.get("route_target") is not None and right.get("route_target") is not None:
        route_diff = float(np.max(np.abs(np.asarray(left["route_target"]) - np.asarray(right["route_target"]))))
    return {
        "prefix_steps": n,
        "prefix_target_max_diff": target_diff,
        "prefix_executed_max_diff": executed_diff,
        "route_target_max_diff": route_diff,
        "left_success": left["success"],
        "right_success": right["success"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--mode", choices=("pilot", "full"), default="pilot")
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("scripted-prefix-report.json"))
    parser.add_argument("--trace-dir", type=Path, default=None)
    parser.add_argument("--max-traces", type=int, default=4)
    parser.add_argument("--kinematic-carry", action="store_true")
    args = parser.parse_args()

    import mujoco

    records = _load(args.manifest)
    model, data = load_tpsc_scene(mujoco_module=mujoco)
    qpos_addresses = [int(model.jnt_qposadr[model.joint(name).id]) for name in ARM_JOINTS]
    dof_addresses = [int(model.jnt_dofadr[model.joint(name).id]) for name in ARM_JOINTS]
    # Use actuator ctrlrange, not the possibly wider joint range: the scene
    # rejects targets outside ctrlrange, and IK must not generate them.
    low = np.array([float(model.actuator(name).ctrlrange[0]) for name in ARM_JOINTS])
    high = np.array([float(model.actuator(name).ctrlrange[1]) for name in ARM_JOINTS])
    gripper_address = int(model.jnt_qposadr[model.joint(GRIPPER_JOINT).id])
    jaw_name = "moving_jaw_so101_v1"
    jaw_body_id = int(model.body(jaw_name).id)
    q_home = np.zeros(len(ARM_JOINTS), dtype=float)

    results: dict[str, dict[str, Any]] = {}
    traces = 0
    for record in records:
        trace_path = None
        if args.trace_dir is not None and traces < args.max_traces:
            trace_path = args.trace_dir / f"{record['episode_id']}.jsonl"
            traces += 1
        results[record["episode_id"]] = _rollout(
            model,
            data,
            mujoco,
            record,
            qpos_addresses=qpos_addresses,
            dof_addresses=dof_addresses,
            low=low,
            high=high,
            jaw_body_id=jaw_body_id,
            jaw_name=jaw_name,
            gripper_address=gripper_address,
            q_home=q_home,
            write_trace=trace_path is not None,
            trace_path=trace_path,
            kinematic_carry=args.kinematic_carry,
        )

    by_pair: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        by_pair[record["pair_id"]][record["branch"]] = results[record["episode_id"]]
    pair_reports = []
    for pair_id, branches in sorted(by_pair.items()):
        if "left" in branches and "right" in branches:
            left, right = branches["left"], branches["right"]
        elif "red" in branches and "blue" in branches:
            left, right = branches["red"], branches["blue"]
        else:
            continue
        comparison = _compare_pair(left, right)
        family = next(record["family"] for record in records if record["pair_id"] == pair_id)
        divergence = "above_goal" if family == "shared_prefix" else ("above_object" if family == "no_common_prefix" else "route")
        pair_reports.append({
            "pair_id": pair_id,
            "family": family,
            "divergence_waypoint": divergence,
            **comparison,
        })

    successes = sum(1 for result in results.values() if result["success"])
    place_successes = sum(1 for result in results.values() if result["place_success"])
    ik_failures = [
        {"episode_id": episode_id, **failure}
        for episode_id, result in results.items()
        for failure in result["ik_failures"]
    ]
    report = {
        "kind": "tpsc_scripted_prefix_smoke_not_vla_result",
        "manifest": str(args.manifest),
        "mode": args.mode,
        "kinematic_carry": bool(args.kinematic_carry),
        "episodes": len(records),
        "successes": successes,
        "success_rate": successes / len(records) if records else 0.0,
        "place_successes": place_successes,
        "place_success_rate": place_successes / len(records) if records else 0.0,
        "ik_max_error_m": max(result["ik_max_error_m"] for result in results.values()) if results else 0.0,
        "ik_failures": ik_failures,
        "pairs": pair_reports,
        "limitations": [
            "Scripted IK controller, not a VLA/policy result.",
            "Success is a physics smoke result, not a benchmark; low grasp success is allowed.",
            "The prefix comparison proves task geometry/waypoint sharing, not that a learned policy shares the prefix.",
            "No collision avoidance, camera visibility, or domain randomization is modeled.",
            "Kinematic carry keeps the object at a fixed jaw offset; it is not a physics grasp."
            if args.kinematic_carry
            else "No kinematic carry; grasp success is physics-only.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=lambda x: x.tolist()) + "\n")
    print(json.dumps({
        "output": str(args.out),
        "episodes": report["episodes"],
        "successes": report["successes"],
        "success_rate": round(report["success_rate"], 3),
        "place_successes": report["place_successes"],
        "place_success_rate": round(report["place_success_rate"], 3),
        "ik_max_error_m": round(report["ik_max_error_m"], 4),
        "ik_failures": len(report["ik_failures"]),
        "pairs": report["pairs"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
