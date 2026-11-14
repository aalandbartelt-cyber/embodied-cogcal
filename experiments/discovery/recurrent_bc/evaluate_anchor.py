"""Fixed-budget evaluation of ordinary initial-RGB-feature BC."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/discovery/matched_bc"))
from carrier import STEPS, Carrier  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--policy-python", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    carrier = Carrier()
    outcomes = []
    with (args.out / "worker.stderr.txt").open("x") as errors:
        worker = subprocess.Popen(
            [str(args.policy_python), "-u", str(Path(__file__).with_name("anchor_policy.py")),
             "--checkpoint", str(args.checkpoint)], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=errors, text=True, bufsize=1,
        )
        try:
            ready = worker.stdout.readline()
            if not ready:
                raise RuntimeError("worker failed to initialize")
            contract = {
                "kind": "ordinary_bc_new_fixed_capability_test_not_method_effect",
                "worker": json.loads(ready), "seeds": list(range(8100, 8120)),
                "checkpoint_sha256": sha(args.checkpoint), "control_hz": 30,
                "query_and_camera_hz": 5, "execute": 6, "horizon": 30,
                "control_budget": STEPS, "q_history": 8,
                "policy_inputs": ["two_RGB", "measured_q_history", "cached_initial_RGB_color_features"],
                "episode_reset_signal": "clears hidden; never a neural input feature",
                "clock_or_phase_or_object_input": False, "sim_pauses_during_inference": True,
                "source_sha256": {str(p.relative_to(ROOT)): sha(p)
                                  for p in list(Path(__file__).parent.glob("*.py")) +
                                  [ROOT / "experiments/discovery/matched_bc/carrier.py",
                                   ROOT / "experiments/discovery/matched_bc/policy.py"]},
            }
            (args.out / "contract.json").write_text(json.dumps(contract, indent=2) + "\n")
            with (args.out / "episodes.jsonl").open("x") as output:
                for seed in contract["seeds"]:
                    started = time.monotonic()
                    q = carrier.reset(seed)["q_rad"]
                    history = deque([q.copy() for _ in range(8)], maxlen=8)
                    with (args.out / f"{seed}.trace.jsonl").open("x") as trace:
                        for step in range(STEPS):
                            query = step % 6 == 0
                            if query:
                                observation = carrier.observe(images=True)
                                request = {"rgb": base64.b64encode(observation["rgb"].tobytes()).decode(),
                                           "q_history_rad": np.asarray(history).tolist(), "reset": step == 0}
                                worker.stdin.write(json.dumps(request) + "\n")
                                worker.stdin.flush()
                                response = worker.stdout.readline()
                                if not response:
                                    raise RuntimeError("worker exited during episode")
                                prediction = json.loads(response)
                                chunk = np.asarray(prediction["chunk_rad"])
                                if chunk.shape != (30, 6) or not np.isfinite(chunk).all():
                                    raise ValueError("invalid neural chunk")
                                if step == 0 and prediction["memory"]["hidden_input_l2"] != 0:
                                    raise ValueError("hidden state leaked across episodes")
                            before = carrier.observe()["q_rad"]
                            command = carrier.step(chunk[step % 6])
                            after = carrier.observe()["q_rad"]
                            history.append(after.copy())
                            row = {"seed": seed, "control_step": step,
                                   "q_before_rad": before.tolist(), "q_after_rad": after.tolist(),
                                   "command_rad": command.tolist(), "sim_time_s": float(carrier.data.time),
                                   "unique_finger_contacts": carrier.last_finger_count,
                                   "object_xyz_m_evaluator_only": carrier.data.qpos[
                                       carrier.cube_address:carrier.cube_address + 3].tolist()}
                            if query:
                                row.update(chunk_rad=chunk.tolist(), memory=prediction["memory"],
                                           q_history_input_rad=request["q_history_rad"],
                                           rgb_sha256=hashlib.sha256(observation["rgb"].tobytes()).hexdigest())
                            trace.write(json.dumps(row) + "\n")
                    row = {"seed": seed, "wall_s": time.monotonic() - started,
                           "source_xyz_m": carrier.source_xyz.tolist(),
                           "goal_xyz_m": carrier.goal_xyz.tolist(), **carrier.outcome()}
                    row["failure_reason"] = (
                        None if row["task_success"] else
                        "two_finger_lift_not_established" if row["longest_two_finger_lift_s"] < .5 else
                        "placement_not_achieved" if not row["placed"] else
                        "release_not_verified" if not row["released"] else "penetration_limit_exceeded")
                    output.write(json.dumps(row) + "\n")
                    output.flush()
                    outcomes.append(row)
                    print(json.dumps(row), flush=True)
        finally:
            carrier.close()
            worker.stdin.close()
            try:
                worker.wait(timeout=15)
            except subprocess.TimeoutExpired:
                worker.terminate()
                worker.wait(timeout=15)
    result = {"kind": contract["kind"], "mode": contract["worker"]["mode"],
              "episodes": len(outcomes), "successes": sum(r["task_success"] for r in outcomes),
              "rows": outcomes, "failure_mechanism": "not_identified", "novelty": "not_established",
              "limits": ["Fixed-color conservative task; cached initial RGB; possible implicit query clock.",
                         "No matched hardware calibration or language comprehension.",
                         "No compensation or TPSC intervention; simulation pauses for inference."]}
    (args.out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["mode", "episodes", "successes"]}), flush=True)


if __name__ == "__main__":
    main()
