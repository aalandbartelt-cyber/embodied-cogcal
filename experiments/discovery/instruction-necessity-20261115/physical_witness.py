"""Fixed SO101 contact witness for language-blind sequential target completion."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "experiments/discovery/matched_bc"))
from carrier import Carrier  # noqa: E402

INITIAL = {"A": np.array([.2, -.075, .014]), "B": np.array([.2, .075, .014])}
FPS = 30


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    with path.open("x") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")


def scene(upstream):
    spec = mujoco.MjSpec.from_file(str(upstream.MODEL_XML))
    original = spec.geom("cube_visual")
    spec.body("cube").pos = INITIAL["A"]
    extra = spec.worldbody.add_body(name="cube_B_body", pos=INITIAL["B"])
    extra.add_freejoint(name="cube_B")
    extra.add_geom(name="cube_B_visual", type=original.type, size=original.size,
                   mass=original.mass, friction=original.friction, condim=original.condim,
                   contype=original.contype, conaffinity=original.conaffinity,
                   solref=original.solref, solimp=original.solimp, rgba=[.15, .7, .35, 1.])
    for pair in list(spec.pairs):
        spec.add_pair(geomname1="cube_B_visual", geomname2=pair.geomname2,
                      condim=pair.condim, friction=pair.friction,
                      solref=pair.solref, solimp=pair.solimp)
    return spec, spec.compile()


def commands(model, up, order):
    actions, phases, errors = [], [], []
    for name in order:
        scratch = mujoco.MjData(model)
        q = up.HOME.copy()
        targets = []
        for position in [INITIAL[name] + [0, 0, up.APPROACH_H], INITIAL[name],
                         INITIAL[name] + [0, 0, up.TRANSIT_H]]:
            q, error, angle = up.solve_pose_ik(model, scratch, model.site(up.PINCH_SITE).id,
                                            q, position, up.APPROACH_Q, up.DOWN)
            errors.append({"object": name, "position_error_m": error, "direction_error_deg": angle})
            if error > .004 or angle > 5:
                raise ValueError("fixed IK gate failed")
            targets.append(q.copy())
        above, grasp, lift = targets
        schedule = [("settle", up.HOME, up.APPROACH_Q, .4),
                    ("approach", above, up.APPROACH_Q, 1.),
                    ("descend", grasp, up.APPROACH_Q, 1.3),
                    ("close", grasp, up.CLOSE_Q, 1.),
                    ("lift", lift, up.CLOSE_Q, 1.3),
                    ("hold", lift, up.CLOSE_Q, .3),
                    ("lower", grasp, up.CLOSE_Q, .8),
                    ("release", grasp, up.APPROACH_Q, .8),
                    ("home", up.HOME, up.APPROACH_Q, .8)]
        previous = np.r_[up.HOME, up.APPROACH_Q]
        for phase, arm, grip, seconds in schedule:
            target = np.r_[arm, grip]
            for tick in range(round(seconds * FPS)):
                fraction = np.clip((tick / FPS) / (seconds * .6), 0, 1)
                blend = fraction * fraction * (3 - 2 * fraction)
                actions.append(previous + (target - previous) * blend)
                phases.append({"candidate": name, "phase": phase})
            previous = target
    if len(actions) != 231 * len(order):
        raise ValueError("unexpected duration")
    return np.asarray(actions), phases, errors


def execute(model, up, actions, phases, destination):
    data = mujoco.MjData(model)
    mujoco.mj_resetData(model, data)
    data.qpos[:6] = np.r_[up.HOME, up.APPROACH_Q]
    addresses = {name: int(model.jnt_qposadr[model.joint(joint).id])
                 for name, joint in [("A", "cube"), ("B", "cube_B")]}
    geometries = {name: model.geom(geom).id for name, geom in [("A", "cube_visual"), ("B", "cube_B_visual")]}
    for name, address in addresses.items():
        data.qpos[address:address + 7] = np.r_[INITIAL[name], 1, 0, 0, 0]
    data.ctrl[:] = data.qpos[:6]
    mujoco.mj_forward(model, data)
    pads = {model.geom(name).id for name in ["jaw_pad_fixed", "jaw_pad_moving"]}
    robot = {model.body(n).id for n in ["base", "shoulder", "upper_arm", "lower_arm", "wrist", "gripper", "moving_jaw_so101_v1"]}
    for contact in data.contact:
        if any(contact.geom1 == g or contact.geom2 == g for g in geometries.values()) and contact.dist < -.001:
            raise ValueError("invalid initial penetration")
    held = {n: 0 for n in INITIAL}
    longest = held.copy()
    first = {n: None for n in INITIAL}
    max_penetration = held.copy()
    physical_tick, clips = 0, 0
    with destination.open("x") as stream:
        for index, command in enumerate(actions):
            sent = np.clip(command, model.actuator_ctrlrange[:, 0], model.actuator_ctrlrange[:, 1])
            clips += int(np.any(sent != command))
            data.ctrl[:] = sent
            tick_goal = round((index + 1) / (FPS * model.opt.timestep))
            contacts = {n: set() for n in INITIAL}
            for _ in range(tick_goal - physical_tick):
                mujoco.mj_step(model, data)
                contacts = {n: set() for n in INITIAL}
                for contact in data.contact:
                    for name, geom in geometries.items():
                        if contact.geom1 != geom and contact.geom2 != geom:
                            continue
                        other = int(contact.geom2 if contact.geom1 == geom else contact.geom1)
                        if other in pads:
                            contacts[name].add(other)
                        if model.geom_bodyid[other] in robot:
                            max_penetration[name] = max(max_penetration[name], -float(contact.dist))
                for name, address in addresses.items():
                    valid = len(contacts[name]) == 2 and data.qpos[address + 2] > INITIAL[name][2] + .05
                    held[name] = held[name] + 1 if valid else 0
                    longest[name] = max(longest[name], held[name])
                    if first[name] is None and held[name] * model.opt.timestep >= .5:
                        first[name] = float(data.time)
            physical_tick = tick_goal
            if not np.isfinite(data.qpos).all():
                raise ValueError("nonfinite simulation")
            row = {"control_index": index, "time_s": float(data.time), "requested_rad": command.tolist(),
                   "sent_rad": sent.tolist(), "q_rad": data.qpos[:6].tolist(), "phase": phases[index],
                   "tcp_xyz_m": data.site(up.PINCH_SITE).xpos.tolist(),
                   "objects": {n: {"xyz_m": data.qpos[a:a + 3].tolist(), "fingers": len(contacts[n]),
                                   "held_ticks": held[n], "longest_held_ticks": longest[n],
                                   "max_penetration_m": max_penetration[n]} for n, a in addresses.items()}}
            stream.write(json.dumps(row) + "\n")
    valid_contact = all(value <= .0015 for value in max_penetration.values())
    completed = {n: first[n] is not None and valid_contact for n in INITIAL}
    reached = [(t, n) for n, t in first.items() if t is not None]
    earliest = min(reached)[1] if reached else None
    return {"controls": len(actions), "sim_time_s": float(data.time), "clip_vectors": clips,
            "first_physical_completion_s": first, "first_completed_object": earliest,
            "longest_two_finger_lift_s": {n: k * model.opt.timestep for n, k in longest.items()},
            "max_penetration_m": max_penetration, "contact_gate_passed": valid_contact,
            "ever_physical_completion": completed,
            "terminal_held_now": {n: bool(len(contacts[n]) == 2 and data.qpos[a + 2] > INITIAL[n][2] + .05) for n, a in addresses.items()},
            "first_completion_matches": {n: n == earliest and valid_contact for n in INITIAL},
            "object_pose_writes_after_reset": 0, "final_qpos": data.qpos.tolist()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    shutil.copy2(HERE / "PLAN-physical.md", args.out / "plan-before-execution.md")
    shutil.copy2(Path(__file__), args.out / "executed-runner.py")
    carrier = Carrier()
    up = carrier.upstream
    if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=up.ROOT, text=True).strip():
        raise ValueError("external source modified")
    spec, model = scene(up)
    (args.out / "scene-override.xml").write_text(spec.to_xml())
    bindings = {str(p.relative_to(ROOT)): digest(p) for p in [Path(__file__), HERE / "PLAN-physical.md",
                ROOT / "experiments/discovery/matched_bc/carrier.py", up.MODEL_XML]}
    save(args.out / "contract.json", {"kind": "privileged_scripted_physical_witness_not_vla", "bindings": bindings,
          "external_revision": "b02b8b2e300733dbe76cead4f3a57425c37955fe", "mujoco": mujoco.__version__,
          "numpy": np.__version__, "fps": FPS, "physics_timestep_s": model.opt.timestep,
          "scene_override_sha256": digest(args.out / "scene-override.xml"),
          "initial_xyz_m": {n: v.tolist() for n, v in INITIAL.items()}})
    rows = []
    for name, order in [("scan_AB", ["A", "B"]), ("scan_BA", ["B", "A"]), ("single_A", ["A"]), ("single_B", ["B"]), ("no_op", [])]:
        try:
            actions, phases, errors = commands(model, up, order)
            if not order:
                actions = np.tile(np.r_[up.HOME, up.APPROACH_Q], (462, 1))
                phases = [{"candidate": None, "phase": "no_op"}] * len(actions)
            np.save(args.out / f"{name}.commands.npy", actions)
            save(args.out / f"{name}.ik.json", errors)
            result = {"case": name, "order": order, **execute(model, up, actions, phases, args.out / f"{name}.trace.jsonl")}
        except ValueError as error:
            result = {"case": name, "order": order, "error": str(error)}
        save(args.out / f"{name}.result.json", result)
        rows.append(result)
        print(json.dumps(result), flush=True)
    save(args.out / "summary.json", {"rows": rows, "limits": ["Five fixed deterministic controller cases, not statistical replicates.",
          "No language input to the schedule, privileged IK sees fixed object positions.",
          "This MuJoCo scene is not an InstructMove Isaac reproduction or a learned-policy experiment.",
          "No physical hardware and no novelty or new-method effectiveness established."]})
    carrier.close()


if __name__ == "__main__":
    main()
