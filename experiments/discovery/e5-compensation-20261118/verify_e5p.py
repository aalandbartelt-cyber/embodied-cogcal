#!/usr/bin/env python3
"""Verify the E5' artifacts: hashes, completeness, and the two manipulation checks.

Reads the frozen PREREG_E5P.md, both registered arms, and the E2 reference runs.
Checks (fail loudly, exit 1):

  * contract kind / bias / seeds / prereg hash / source hash / carrier + checkpoint
    hashes agree with E2's registered contract;
  * 20 episodes per arm, every seed 12850-12869, delta drawn from the same key as
    E2, 285 control steps, trace and physics files present and hash-consistent;
  * P5: median measured q5 over steps 55-85 in arm A is inside 0.695 +/- 0.035 rad;
  * P6: FK closing-axis angle of arm A's step-55 target is +15.0 +/- 0.5 deg relative
    to E2 y15 at the same seed (both the bias-isolated and the cross-condition
    readings are reported).

Writes verify_e5p.json next to this file.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import mujoco
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
E2 = HERE.parent / "e2-size-tolerance-20261118"
XML = REPO / "third_party/SO-ARM100/Simulation/SO101/so101_new_calib.xml"
SEEDS = list(range(12850, 12870))
ARMS = {"A": ("e5p-y15-b15", 15.0, 15.0), "B": ("e5p-y0-b15", 0.0, 15.0)}
Q5 = 4
CLOSE = (55, 86)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def closing_angle(model, data, body_id: int, q) -> float:
    data.qpos[:6] = q
    mujoco.mj_forward(model, data)
    y = data.xmat[body_id].reshape(3, 3)[:, 1]
    return math.degrees(math.atan2(y[1], y[0]))


def main() -> None:
    failures: list[str] = []
    prereg_sha = sha(HERE / "PREREG_E5P.md")
    source_sha = sha(HERE / "rollout_e5p.py")
    e2_contract = json.loads((E2 / "runs/e2-y15-d1/contract.json").read_text())
    e2_y0_contract = json.loads((E2 / "runs/e2-y0-d1/contract.json").read_text())

    model = mujoco.MjModel.from_xml_path(str(XML))
    data = mujoco.MjData(model)
    gid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "gripper")

    out: dict = {
        "prereg_sha256": prereg_sha,
        "xml_sha256": sha(XML),
        "source_sha256": source_sha,
        "arms": {},
        "P5": {},
        "P6": {},
    }

    for arm, (name, theta, bias) in ARMS.items():
        run = HERE / "runs" / name
        contract = json.loads((run / "contract.json").read_text())
        episodes = load_jsonl(run / "episodes.jsonl")
        summary = json.loads((run / "summary.json").read_text())

        def check(ok: bool, msg: str) -> None:
            if not ok:
                failures.append(f"{arm}: {msg}")

        check(contract["kind"] == "e5p_command_side_q5_compensation_not_method", "kind")
        check(contract["yaw_deg"] == theta, "yaw")
        check(contract["q5_bias_deg"] == bias, "bias")
        check(contract["q5_index"] == Q5 and contract["q5_joint"] == "wrist_roll", "q5 index/joint")
        check(contract["seeds"] == SEEDS, "registered seeds")
        check(contract["prereg_sha256"] == prereg_sha, "prereg hash")
        check(contract["source_sha256"].get(str(HERE / "rollout_e5p.py")) == source_sha, "runner source hash")
        check(contract["checkpoint_sha256"] == e2_contract["checkpoint_sha256"], "checkpoint hash")
        check(contract["carrier_pyc_sha256"] == e2_contract["carrier_pyc_sha256"], "carrier hash")
        check(contract["training_contract_sha256"] == e2_contract["training_contract_sha256"], "training contract")
        check(contract["worker"].get("ready") is True, "worker ready")
        for path, expected in contract["source_sha256"].items():
            src = Path(path)
            check(src.exists() and sha(src) == expected, f"source hash {path}")
        check(XML.stat().st_mtime <= (run / "contract.json").stat().st_mtime, "XML modified after run")
        check(contract["w_eff_mm"] == (34.29285639896449 if theta == 15.0 else 28.0), "w_eff")
        dmm = contract["delta_mm_per_seed"]
        check(sorted(int(k) for k in dmm) == SEEDS, "delta seed keys")
        check(all(0.5 <= float(v) < 1.5 for v in dmm.values()), "delta range")

        check(len(episodes) == 20, f"episodes={len(episodes)}")
        check([r["seed"] for r in episodes] == SEEDS, "episode order/seeds")
        check(summary["episodes"] == 20, "summary episodes")
        check(summary["task_successes"] == sum(r["task_success"] for r in episodes), "summary successes")

        q5_close: list[float] = []
        for row in episodes:
            seed = row["seed"]
            check(abs(row["delta_mm"] - float(dmm[str(seed)])) < 1e-12, f"{seed} delta mismatch")
            check(row["q5_bias_deg"] == bias, f"{seed} row bias")
            check(row["controls"] == 285, f"{seed} controls")
            check(row["object_pose_writes_during_rollout"] == 0, f"{seed} pose writes")
            check(np.isfinite(row["max_object_robot_penetration_m"]), f"{seed} penetration")
            check(row["physics_path"] == f"runs/{name}-physics/{seed}.npz", f"{seed} physics path")
            phys_path = HERE / row["physics_path"]
            check(phys_path.exists(), f"{seed} physics missing")
            if phys_path.exists():
                check(sha(phys_path) == row["physics_sha256"], f"{seed} physics hash")
                phys = np.load(phys_path)
                n_ticks = len(phys["time"])
                check(n_ticks > 0 and all(len(phys[k]) == n_ticks for k in phys.files), f"{seed} physics lengths")
                check(bool(np.isfinite(phys["xyz"]).all()), f"{seed} physics xyz finite")
                check(bool(np.isfinite(phys["q"]).all()), f"{seed} physics q finite")
                steps = phys["control_step"]
                check(int(steps.min()) == 0 and int(steps.max()) == 284, f"{seed} physics control steps")

            trace_path = run / f"{seed}.trace.jsonl"
            trace = load_jsonl(trace_path)
            check(len(trace) == 285, f"{seed} trace len {len(trace)}")
            check(sha(trace_path) == row["trace_sha256"], f"{seed} trace hash")
            for i, t in enumerate(trace[:2]):
                check("policy_target_rad" in t and "q5_bias_rad" in t, f"{seed}[{i}] trace fields")
            check(all(t["q5_bias_rad"] == contract["q5_bias_rad"] for t in trace), f"{seed} trace bias")
            q_after = np.array([t["q_after_rad"] for t in trace])
            raw = np.array([t["raw_target_rad"] for t in trace])
            pol = np.array([t["policy_target_rad"] for t in trace])
            check(np.allclose(raw[:, Q5] - pol[:, Q5], contract["q5_bias_rad"], atol=1e-12), f"{seed} injection identity")
            q5_close.append(float(np.median(q_after[CLOSE[0]:CLOSE[1], Q5])))
            # measured wrist_roll follows the biased target through the close
            check(abs(float(np.median(q_after[CLOSE[0]:CLOSE[1], Q5] - raw[CLOSE[0]:CLOSE[1], Q5]))) < 0.02,
                  f"{seed} q5 tracking")

        out["arms"][arm] = {
            "name": name,
            "theta_deg": theta,
            "q5_bias_deg": bias,
            "episodes": len(episodes),
            "successes": sum(r["task_success"] for r in episodes),
            "failures": [(r["seed"], r["failure_reason"]) for r in episodes if not r["task_success"]],
            "delta_mm": sorted(float(v) for v in dmm.values()),
            "q5_close_median_rad": {
                "min": min(q5_close),
                "median": float(np.median(q5_close)),
                "max": max(q5_close),
            },
        }
        out["P5"][arm] = {
            "ok": all(0.66 <= v <= 0.73 for v in q5_close),
            "n_in_band": sum(0.66 <= v <= 0.73 for v in q5_close),
            "band_rad": [0.66, 0.73],
        }
        if not out["P5"][arm]["ok"]:
            failures.append(f"{arm}: P5 q5 close median outside 0.695 +/- 0.035")

    # P6: closing-axis FK on step 55, A vs E2 y15 (same seed).
    a_run = HERE / "runs/e5p-y15-b15"
    a_episodes = load_jsonl(a_run / "episodes.jsonl")
    e2_run = E2 / "runs/e2-y15-d1"
    e2_episodes = [json.loads(line) for line in (e2_run / "episodes.jsonl").read_text().splitlines() if line.strip()]
    e2_by_seed = {r["seed"]: r for r in e2_episodes}
    d_iso, d_cross = [], []
    for row in a_episodes:
        seed = row["seed"]
        a_trace = load_jsonl(a_run / f"{seed}.trace.jsonl")
        e_trace = load_jsonl(e2_run / f"{seed}.trace.jsonl")
        step = 55
        phi_a_raw = closing_angle(model, data, gid, a_trace[step]["raw_target_rad"])
        phi_a_pol = closing_angle(model, data, gid, a_trace[step]["policy_target_rad"])
        phi_e = closing_angle(model, data, gid, e_trace[step]["raw_target_rad"])
        d_iso.append((phi_a_raw - phi_a_pol + 180.0) % 360.0 - 180.0)
        d_cross.append((phi_a_raw - phi_e + 180.0) % 360.0 - 180.0)
    out["P6"] = {
        "step": 55,
        "bias_isolated_deg": {"median": float(np.median(d_iso)), "min": float(min(d_iso)), "max": float(max(d_iso))},
        "cross_condition_deg": {"median": float(np.median(d_cross)), "min": float(min(d_cross)), "max": float(max(d_cross))},
        "ok": abs(float(np.median(d_cross)) - 15.0) <= 0.5,
    }
    if not out["P6"]["ok"]:
        failures.append("P6 cross-condition median outside 15.0 +/- 0.5 deg")

    out["failures"] = failures
    out["ok"] = not failures
    (HERE / "verify_e5p.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("ok", "failures", "arms", "P5", "P6")}, indent=2))
    sys.exit(0 if not failures else 1)


if __name__ == "__main__":
    main()
