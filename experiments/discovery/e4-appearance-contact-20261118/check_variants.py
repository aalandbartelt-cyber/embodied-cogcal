"""E4 instrumentation checks, run before any rollout.

See make_variants.py for the design. The cube carries `cube_look` (group 0,
rendered, massless, contype 0) and `cube_visual` (group 3, hidden, mass 0.020,
contype 2). Real object rotation is E2's mechanism -- the free-joint quaternion
written at reset (+15 deg) -- while the rendering of the look geom is cancelled
back to axis-aligned where the condition needs it. No physics representation is
rebuilt for the collision condition: only a massless geom's frame differs.

Checks, all at fixed seeds and before any result is collected:
  1. compiled geom quats and world frames carry exactly the yaw each condition
     claims (look -15 deg inside collision, +15 deg inside visual, 0 in deg0;
     cube_visual +15 deg whenever the body yaw is 15);
  2. deg0 renders byte-identically to the upstream single-geom training model;
  3. collision renders byte-identically to deg0 although its object is rotated
     15 deg (appearance is axis-aligned, contact is rotated);
  4. visual renders byte-identically to `both` (which is deg0 plus a body yaw of
     15 deg, i.e. E2's theta=15);
  5. every compiled model array equals deg0 except geom_quat[cube_look], and the
     cube body keeps body_simple=1 / body_iquat=identity in every tree;
  6. open-loop replay of E2's theta=15 command traces: (a) the harness itself
     reproduces E2's recorded joint trajectory, (b) deg0(+body yaw) and
     collision agree step by step, (c) deg0 and visual agree step by step.

Writes variants_check.json. Exit 0 only if every check passes; failure aborts E4
as an instrumentation failure.
"""

from __future__ import annotations

import hashlib
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
CARRIER_PYC = REPO / ".carrier-rt/a/b/carrier.pyc"
E2_RUN = REPO / "experiments/discovery/e2-size-tolerance-20261118/runs"
SEED = 12880
REPLAY_SEEDS = (12850, 12851)
TREES = ("deg0", "visual", "collision")
PHYSICS_FIELDS = (
    "body_mass", "body_inertia", "body_ipos", "body_pos", "body_quat",
    "body_parentid", "body_jntnum", "body_jntadr", "body_dofnum", "body_dofadr",
    "geom_size", "geom_pos", "geom_contype", "geom_conaffinity", "geom_condim", "geom_friction",
    "geom_solref", "geom_solimp", "geom_margin", "geom_gap", "geom_priority", "geom_rbound",
    "geom_bodyid", "jnt_type", "jnt_qposadr", "jnt_dofadr", "jnt_axis", "jnt_pos", "jnt_stiffness",
    "jnt_range", "jnt_limited", "dof_armature", "dof_damping", "dof_frictionloss",
    "actuator_gear", "actuator_ctrlrange", "actuator_ctrllimited", "actuator_gainprm",
    "actuator_biasprm", "pair_dim", "pair_geom1", "pair_geom2", "pair_solref", "pair_solimp",
    "pair_friction", "pair_margin",
)
BOOKKEEPING_FIELDS = ("geom_quat", "geom_sameframe", "mesh_pathadr")
CUBE_GEOMS = ("cube_visual", "cube_look")
POS_TOL = 1e-9   # metres, per control step, over a 285-step contact-rich replay
ORI_TOL = 1e-9   # matrix entries


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rot_z(deg: float) -> np.ndarray:
    t = math.radians(deg)
    return np.array([[math.cos(t), -math.sin(t), 0.0],
                     [math.sin(t), math.cos(t), 0.0],
                     [0.0, 0.0, 1.0]])


def yaw_of(xmat: np.ndarray) -> float:
    return float(math.degrees(math.atan2(xmat[1, 0], xmat[0, 0])))


def carrier_module():
    loader = importlib.machinery.SourcelessFileLoader("e4p_carrier", str(CARRIER_PYC))
    spec = importlib.util.spec_from_loader("e4p_carrier", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def model_arrays(model) -> dict[str, np.ndarray]:
    arrays: dict[str, np.ndarray] = {}
    for name in dir(model):
        if name.startswith("_"):
            continue
        try:
            value = getattr(model, name)
        except Exception:
            continue
        if isinstance(value, np.ndarray) and value.dtype.kind in "iufb":
            arrays[name] = value
    return arrays


def set_state(carrier, seed: int, body_yaw_deg: float, delta_mm: float) -> None:
    carrier.reset(seed)
    if body_yaw_deg:
        half = math.radians(body_yaw_deg) / 2.0
        carrier.data.qpos[carrier.cube_address + 3:carrier.cube_address + 7] = [
            math.cos(half), 0.0, 0.0, math.sin(half)]
    if delta_mm:
        shift = np.array([delta_mm / 1000.0, delta_mm / 1000.0, 0.0])
        carrier.source_xyz = carrier.source_xyz + shift
        carrier.data.qpos[carrier.cube_address:carrier.cube_address + 3] = carrier.source_xyz
    mujoco.mj_forward(carrier.model, carrier.data)
    if carrier.initial_penetrations():
        raise ValueError("shifted object interpenetrates robot")


def e2_delta(seed: int) -> float:
    contract = json.loads((E2_RUN / "e2-y15-d1" / "contract.json").read_text())
    return float(contract["delta_mm_per_seed"][str(seed)])


def e2_trace(seed: int) -> list[dict]:
    path = E2_RUN / "e2-y15-d1" / f"{seed}.trace.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return sorted(rows, key=lambda r: r["control_step"])


def replay(module, source: Path, seed: int, body_yaw_deg: float, delta_mm: float,
           commands: list[list[float]]) -> list[dict]:
    carrier = module.Carrier(source=Path(source).resolve())
    try:
        set_state(carrier, seed, body_yaw_deg, delta_mm)
        look = mujoco.mj_name2id(carrier.model, mujoco.mjtObj.mjOBJ_GEOM, "cube_look")
        visual = mujoco.mj_name2id(carrier.model, mujoco.mjtObj.mjOBJ_GEOM, "cube_visual")
        steps = []
        for target in commands:
            carrier.step(np.asarray(target, dtype=float))
            steps.append({
                "q_rad": np.asarray(carrier.data.qpos[:6], dtype=float).copy(),
                "visual_pos": np.asarray(carrier.data.geom_xpos[visual], dtype=float).copy(),
                "visual_xmat": np.asarray(carrier.data.geom_xmat[visual], dtype=float).copy(),
                "look_pos": np.asarray(carrier.data.geom_xpos[look], dtype=float).copy(),
                "look_xmat": np.asarray(carrier.data.geom_xmat[look], dtype=float).copy(),
                "ncon": int(carrier.data.ncon),
            })
        return steps
    finally:
        carrier.close()


def main() -> int:
    record = json.loads((HERE / "variants.json").read_text())
    problems: list[str] = []

    def check(ok: bool, message: str) -> None:
        if not ok:
            problems.append(message)
        print(("PASS " if ok else "FAIL ") + message)

    module = carrier_module()
    check(module.ROOT.resolve() == REPO.resolve(), "carrier ROOT")
    check(mujoco.__version__ == "4.0.1", "mujoco version 4.0.1")

    conditions = record["conditions"]
    carriers = {}
    for name in TREES:
        carriers[name] = module.Carrier(source=Path(conditions[name]["source"]).resolve())

    evidence: dict[str, dict] = {}
    image: dict[str, str] = {}
    for condition, entry in conditions.items():
        carrier = carriers[entry["tree"]]
        set_state(carrier, SEED, entry["body_yaw_deg"], 0.0)
        look = mujoco.mj_name2id(carrier.model, mujoco.mjtObj.mjOBJ_GEOM, "cube_look")
        visual = mujoco.mj_name2id(carrier.model, mujoco.mjtObj.mjOBJ_GEOM, "cube_visual")
        model_yaw = {name: float(np.degrees(2.0 * math.atan2(carrier.model.geom_quat[gid][3], carrier.model.geom_quat[gid][0])))
                     for name, gid in (("cube_look", look), ("cube_visual", visual))}
        world_yaw = {name: yaw_of(np.asarray(carrier.data.geom_xmat[gid], dtype=float).reshape(3, 3))
                     for name, gid in (("cube_look", look), ("cube_visual", visual))}
        rgb = carrier.observe(images=True)["rgb"]
        image[condition] = hashlib.sha256(rgb.tobytes()).hexdigest()
        evidence[condition] = {
            "tree": entry["tree"], "source": entry["source"], "model_xml": entry["xml"],
            "xml_sha256": entry["xml_sha256"], "body_yaw_deg": entry["body_yaw_deg"],
            "geom_model_yaw_deg": model_yaw, "geom_world_yaw_deg": world_yaw,
            "rgb_sha256": image[condition],
            "body_simple_cube": int(carrier.model.body_simple[carrier.model.body("cube").id]),
            "body_iquat_cube": [float(v) for v in carrier.model.body_iquat[carrier.model.body("cube").id]],
        }
        check(abs(world_yaw["cube_look"] - entry["image_yaw_deg"]) < 1e-6,
              f"{condition}: look world yaw {world_yaw['cube_look']:.6f} == image yaw {entry['image_yaw_deg']}")
        check(abs(world_yaw["cube_visual"] - entry["body_yaw_deg"]) < 1e-6,
              f"{condition}: collision world yaw {world_yaw['cube_visual']:.6f} == body yaw {entry['body_yaw_deg']}")
        check(abs(model_yaw["cube_look"] - entry["geom_yaw_deg"].get("cube_look", 0.0)) < 1e-6,
              f"{condition}: compiled look quat is {model_yaw['cube_look']:.6f} deg")
        check(abs(model_yaw["cube_visual"]) < 1e-6, f"{condition}: compiled collision quat is identity")
        check(np.abs(np.asarray(carrier.data.geom_xmat[look]).reshape(3, 3) - rot_z(entry["image_yaw_deg"])).max() < 1e-6
              if abs(entry["image_yaw_deg"]) > 1e-9 else
              np.abs(np.asarray(carrier.data.geom_xmat[look]).reshape(3, 3) - np.eye(3)).max() < 1e-6,
              f"{condition}: look xmat equals its rotation")
        check(np.abs(np.asarray(carrier.data.geom_xmat[visual]).reshape(3, 3) - rot_z(entry["body_yaw_deg"])).max() < 1e-6
              if abs(entry["body_yaw_deg"]) > 1e-9 else
              np.abs(np.asarray(carrier.data.geom_xmat[visual]).reshape(3, 3) - np.eye(3)).max() < 1e-6,
              f"{condition}: collision xmat equals its rotation")

    # Check 2/3/4: image identities.
    upstream = module.Carrier()
    set_state(upstream, SEED, 0.0, 0.0)
    upstream_sha = hashlib.sha256(upstream.observe(images=True)["rgb"].tobytes()).hexdigest()
    upstream.close()
    check(image["deg0"] == upstream_sha, "deg0 rgb == upstream single-geom model rgb")
    check(image["collision"] == image["deg0"],
          "collision rgb == deg0 rgb while its object is rotated 15 deg")
    check(image["visual"] == image["both"], "visual rgb == both rgb (E2's theta=15 appearance)")
    check(image["visual"] != image["deg0"], "visual rotation changes the image")
    check(evidence["both"]["body_simple_cube"] == 1 and evidence["collision"]["body_simple_cube"] == 1,
          "cube body stays simple (body_simple=1) in both and collision")

    # Check 5: the dynamics-defining model arrays are untouched; the only
    # differences are compile bookkeeping for the moved visual frame
    # (geom_quat/geom_sameframe of cube_look, and mesh_pathadr, whose values are
    # names-buffer offsets and shift by a few bytes with the extra attribute).
    base = model_arrays(carriers["deg0"].model)
    cube_body = carriers["deg0"].model.body("cube").id
    look_id = mujoco.mj_name2id(carriers["deg0"].model, mujoco.mjtObj.mjOBJ_GEOM, "cube_look")
    for tree in ("visual", "collision"):
        arrays = model_arrays(carriers[tree].model)
        check(set(arrays) == set(base), f"{tree}: same model array names")
        physics = []
        for name in PHYSICS_FIELDS:
            if name not in base or name not in arrays:
                continue
            if not np.array_equal(base[name], arrays[name]):
                physics.append(name)
        check(not physics, f"{tree}: physics arrays equal to deg0, differing: {physics}")
        bookkeeping = {}
        for name in sorted(set(arrays) & set(base)):
            if np.array_equal(base[name], arrays[name]):
                continue
            if name in ("geom_quat", "geom_sameframe"):
                diff = np.abs(arrays[name].astype(float) - base[name].astype(float))
                rows = np.nonzero((diff.max(axis=1) if diff.ndim == 2 else diff) > 0)[0]
                bookkeeping[name] = sorted(int(i) for i in rows)
            else:
                bookkeeping[name] = "names-buffer layout"
        check(bookkeeping.get("geom_quat") == [look_id] and bookkeeping.get("geom_sameframe") == [look_id],
              f"{tree}: bookkeeping diffs confined to cube_look row ({bookkeeping})")
        check(set(bookkeeping) <= set(BOOKKEEPING_FIELDS),
              f"{tree}: no unexpected differing arrays ({sorted(bookkeeping)})")
        check(int(carriers[tree].model.body_simple[cube_body]) == 1, f"{tree}: cube body_simple == 1")
        check(np.abs(carriers[tree].model.body_iquat[cube_body] - np.array([1.0, 0, 0, 0])).max() < 1e-12,
              f"{tree}: cube body_iquat == identity")

    # Check 6: replay E2's theta=15 commands. (a) harness self-check, then
    # (b) deg0+bodyyaw vs collision+bodyyaw and (c) deg0 vs visual.
    replay_evidence = {}
    for seed in REPLAY_SEEDS:
        rows = e2_trace(seed)
        commands = [row["command_rad"] for row in rows]
        delta = e2_delta(seed)

        upstream_run = replay(module, Path(conditions["both"]["source"]), seed, 15.0, delta, commands)
        recorded_q = np.array([row["q_after_rad"] for row in rows], dtype=float)
        replayed_q = np.array([s["q_rad"] for s in upstream_run], dtype=float)
        self_diff = float(np.abs(recorded_q - replayed_q).max())
        check(self_diff < 1e-9, f"replay harness reproduces E2 recorded q trajectory (seed {seed}, max diff {self_diff:.2e})")

        both = replay(module, Path(conditions["both"]["source"]), seed, 15.0, delta, commands)
        collision = replay(module, Path(conditions["collision"]["source"]), seed, 15.0, delta, commands)
        pos_diff = max(float(np.abs(a["visual_pos"] - b["visual_pos"]).max()) for a, b in zip(both, collision))
        ori_diff = max(float(np.abs(a["visual_xmat"] - b["visual_xmat"]).max()) for a, b in zip(both, collision))
        ncon_diff = sum(1 for a, b in zip(both, collision) if a["ncon"] != b["ncon"])
        check(pos_diff < POS_TOL, f"replay both vs collision: cube position max diff {pos_diff:.2e} m (seed {seed})")
        check(ori_diff < ORI_TOL, f"replay both vs collision: cube orientation max diff {ori_diff:.2e} (seed {seed})")

        deg0 = replay(module, Path(conditions["deg0"]["source"]), seed, 0.0, delta, commands)
        visual = replay(module, Path(conditions["visual"]["source"]), seed, 0.0, delta, commands)
        vis_pos = max(float(np.abs(a["visual_pos"] - b["visual_pos"]).max()) for a, b in zip(deg0, visual))
        vis_ori = max(float(np.abs(a["visual_xmat"] - b["visual_xmat"]).max()) for a, b in zip(deg0, visual))
        check(vis_pos < POS_TOL, f"replay deg0 vs visual: cube position max diff {vis_pos:.2e} m (seed {seed})")
        check(vis_ori < ORI_TOL, f"replay deg0 vs visual: cube orientation max diff {vis_ori:.2e} (seed {seed})")
        replay_evidence[str(seed)] = {
            "self_check_q_max_diff": self_diff,
            "both_vs_collision_pos_max_diff_m": pos_diff,
            "both_vs_collision_ori_max_diff": ori_diff,
            "both_vs_collision_ncon_mismatch_steps": ncon_diff,
            "deg0_vs_visual_pos_max_diff_m": vis_pos,
            "deg0_vs_visual_ori_max_diff": vis_ori,
        }

    for carrier in carriers.values():
        carrier.close()

    result = {
        "seed": SEED, "replay_seeds": list(REPLAY_SEEDS), "mujoco": mujoco.__version__,
        "carrier_pyc_sha256": sha(CARRIER_PYC), "variants_sha256": sha(HERE / "variants.json"),
        "checks_passed": not problems, "problems": problems,
        "conditions": evidence, "images": image, "image_upstream": upstream_sha,
        "replay": replay_evidence,
    }
    (HERE / "variants_check.json").write_text(json.dumps(result, indent=2) + "\n")
    if problems:
        print(f"\n{len(problems)} check(s) failed; E4 aborts as instrumentation failure", file=sys.stderr)
        return 1
    print("\nall instrumentation checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
