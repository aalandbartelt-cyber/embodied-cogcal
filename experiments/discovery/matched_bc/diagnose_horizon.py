"""Adaptive validation-only horizon diagnostic, preserving the failed baseline.

This changes execution/query cadence, not weights. No method-effect, new
held-out performance, or compensation-mechanism inference is permitted.
"""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import time
from collections import deque
from pathlib import Path

import numpy as np
from carrier import STEPS, Carrier, split_seeds

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/discovery/matched-bc-horizon-diagnostic-20261114"
CHECKPOINT = ROOT / "checkpoints/matched-bc-20261114/final-2000.pt"
POLICY = "/home/mary/.cache/cogcal/venvs/tpsc-policy/bin/python"
EXPECTED_CHECKPOINT = "f49da6e9c82c55a2478bf580e049365fbde3e3bd8bff2a8fc1bfcbe33a23e237"


def main():
    if hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest() != EXPECTED_CHECKPOINT:
        raise ValueError("frozen checkpoint changed")
    # Write the diagnostic choices before any validation outcome is observed.
    RUN.mkdir(exist_ok=False)
    plan = {
        "kind": "adaptive_validation_diagnostic_after_failed_0_of_20_baseline",
        "hypothesis": "short consumed prefix may fail to advance across near-static teacher observations",
        "not_established": ["root cause", "new mechanism", "new method", "held-out capability"],
        "seeds": split_seeds("val"), "execute_grid": [6, 30], "checkpoint": str(CHECKPOINT),
        "checkpoint_sha256": EXPECTED_CHECKPOINT, "new_training": False,
        "control_hz": 30, "prediction_horizon": 30,
        "effective_policy_image_query_hz": {"6": 5, "30": 1},
        "selection_rule": "report both; no best seed/checkpoint; no test or compensation claims",
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in Path(__file__).parent.glob("*.py")},
    }
    (RUN / "plan-before-validation.json").write_text(json.dumps(plan, indent=2) + "\n")
    carrier = Carrier()
    rows = []
    with (RUN / "worker.stderr.txt").open("x") as errors:
        worker = subprocess.Popen(
            [POLICY, "-u", str(Path(__file__).with_name("policy.py")),
             "--checkpoint", str(CHECKPOINT)], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=errors, text=True, bufsize=1,
        )
        try:
            ready = worker.stdout.readline()
            if not ready or not json.loads(ready)["ready"]:
                raise RuntimeError("policy worker did not initialize")
            with (RUN / "episodes.jsonl").open("x") as output:
                for execute in plan["execute_grid"]:
                    for seed in plan["seeds"]:
                        start = time.monotonic()
                        q = carrier.reset(seed)["q_rad"]
                        history = deque([q.copy() for _ in range(8)], maxlen=8)
                        with (RUN / f"e{execute}-s{seed}.trace.jsonl").open("x") as trace:
                            for step in range(STEPS):
                                query = step % execute == 0
                                if query:
                                    obs = carrier.observe(images=True)
                                    request = {"rgb": base64.b64encode(obs["rgb"].tobytes()).decode(),
                                               "q_history_rad": np.asarray(history).tolist()}
                                    worker.stdin.write(json.dumps(request) + "\n")
                                    worker.stdin.flush()
                                    response = worker.stdout.readline()
                                    if not response:
                                        raise RuntimeError("policy worker exited")
                                    chunk = np.asarray(json.loads(response)["chunk_rad"])
                                    if chunk.shape != (30, 6) or not np.isfinite(chunk).all():
                                        raise ValueError("invalid prediction")
                                before = carrier.observe()["q_rad"]
                                command = carrier.step(chunk[step % execute])
                                after = carrier.observe()["q_rad"]
                                history.append(after.copy())
                                row = {"step": step, "q_before_rad": before.tolist(),
                                       "q_after_rad": after.tolist(), "command_rad": command.tolist()}
                                if query:
                                    row["chunk_rad"] = chunk.tolist()
                                    row["q_history_input_rad"] = request["q_history_rad"]
                                    row["rgb_sha256"] = hashlib.sha256(obs["rgb"].tobytes()).hexdigest()
                                trace.write(json.dumps(row) + "\n")
                        row = {"seed": seed, "execute": execute,
                               "wall_s": time.monotonic() - start, **carrier.outcome()}
                        rows.append(row)
                        output.write(json.dumps(row) + "\n")
                        output.flush()
                        print(json.dumps(row), flush=True)
        finally:
            carrier.close()
            worker.stdin.close()
            try:
                worker.wait(timeout=15)
            except subprocess.TimeoutExpired:
                worker.terminate()
                worker.wait(timeout=15)
    result = {"kind": plan["kind"], "rows": rows, "all_reported": True,
              "by_execute": {str(e): {"episodes": sum(r["execute"] == e for r in rows),
                                     "successes": sum(r["task_success"] for r in rows if r["execute"] == e)}
                             for e in plan["execute_grid"]},
              "held_out_capability": "not_established", "compensation_effect": "not_tested"}
    (RUN / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["by_execute"]), flush=True)


if __name__ == "__main__":
    main()
