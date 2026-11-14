"""Episode-level matched RGB/q BC evaluation; no privileged policy inputs."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import time
from collections import deque
from pathlib import Path

import numpy as np
from carrier import STEPS, Carrier, split_seeds

HISTORY = 8
HORIZON = 30
EXECUTE = 6


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--policy-python", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--split", choices=["val", "test"], default="test")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    c = Carrier()
    rows = []
    with (args.out / "worker.stderr.txt").open("x") as errors:
        worker = subprocess.Popen(
            [str(args.policy_python), "-u", str(Path(__file__).with_name("policy.py")),
             "--checkpoint", str(args.checkpoint)], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=errors, text=True, bufsize=1,
        )
        try:
            ready = worker.stdout.readline()
            if not ready:
                raise RuntimeError("BC worker failed before episode; inspect stderr")
            contract = {
                "kind": "fixed_final_matched_bc_capability_not_tpsc_or_new_method",
                "worker": json.loads(ready), "split": args.split,
                "seeds": split_seeds(args.split), "fps": 30, "camera_fps": 5,
                "control_budget": STEPS, "history": HISTORY, "horizon": HORIZON,
                "execute": EXECUTE, "scene": "external_contact_pad_model_not_original_tpsc",
                "checkpoint_sha256": hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),
                "source_sha256": {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                  for name in ["carrier.py", "policy.py", "evaluate.py"]},
                "policy_inputs": ["two_RGB", "measured_q_history"],
                "constant_instruction": True, "language_understanding_claim": False,
                "sim_pauses_during_inference": True,
            }
            (args.out / "evaluation-contract.json").write_text(json.dumps(contract, indent=2) + "\n")
            with (args.out / "episodes.jsonl").open("x") as output:
                for seed in contract["seeds"]:
                    start = time.monotonic()
                    observation = c.reset(seed)
                    history = deque([observation["q_rad"].copy() for _ in range(HISTORY)], maxlen=HISTORY)
                    chunk = None
                    with (args.out / f"{seed}.trace.jsonl").open("x") as trace:
                        for step in range(STEPS):
                            query = step % EXECUTE == 0
                            if query:
                                obs = c.observe(images=True)
                                request = {
                                    "rgb": base64.b64encode(obs["rgb"].tobytes()).decode(),
                                    "q_history_rad": np.asarray(history).tolist(),
                                }
                                worker.stdin.write(json.dumps(request) + "\n")
                                worker.stdin.flush()
                                response = worker.stdout.readline()
                                if not response:
                                    raise RuntimeError("BC worker exited during episode")
                                chunk = np.asarray(json.loads(response)["chunk_rad"])
                                if chunk.shape != (HORIZON, 6) or not np.isfinite(chunk).all():
                                    raise ValueError("bad BC prediction")
                            before = c.observe()["q_rad"]
                            action = c.step(chunk[step % EXECUTE])
                            after = c.observe()["q_rad"]
                            history.append(after.copy())
                            row = {"seed": seed, "control_step": step,
                                   "q_before_rad": before.tolist(), "command_rad": action.tolist(),
                                   "q_after_rad": after.tolist(), "sim_time_s": float(c.data.time),
                                   "unique_finger_contacts": c.last_finger_count}
                            if query:
                                row.update({"chunk_rad": chunk.tolist(),
                                            "q_history_input_rad": np.asarray(request["q_history_rad"]).tolist(),
                                            "rgb_sha256": hashlib.sha256(obs["rgb"].tobytes()).hexdigest()})
                            trace.write(json.dumps(row) + "\n")
                    outcome = c.outcome()
                    row = {"seed": seed, "wall_s": time.monotonic() - start, **outcome}
                    row["failure_reason"] = (
                        None if row["task_success"] else
                        "two_finger_lift_not_established" if row["longest_two_finger_lift_s"] < 0.5 else
                        "placement_not_achieved" if not row["placed"] else
                        "release_not_verified" if not row["released"] else "penetration_limit_exceeded"
                    )
                    output.write(json.dumps(row) + "\n")
                    output.flush()
                    rows.append(row)
                    print(json.dumps(row), flush=True)
        finally:
            c.close()
            worker.stdin.close()
            try:
                worker.wait(timeout=15)
            except subprocess.TimeoutExpired:
                worker.terminate()
                worker.wait(timeout=15)
    result = {
        "kind": "matched_ordinary_bc_capability_screen",
        "episodes": len(rows), "task_successes": sum(r["task_success"] for r in rows),
        "split": args.split, "rows": rows,
        "method_effect": "not_tested", "novelty": "not_established",
        "limitations": ["Single fixed task and conservative workspace.",
                        "External pads/friction not physical-hardware calibrated.",
                        "No TPSC semantic pairs or compensation intervention.",
                        "Physics paused during inference; no real-time claim."],
    }
    (args.out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["episodes", "task_successes", "split"]}), flush=True)


if __name__ == "__main__":
    main()
