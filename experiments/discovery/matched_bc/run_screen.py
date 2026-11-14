"""Sequential, fail-closed execution of the already specified ordinary BC screen."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).resolve().parent
RUN = ROOT / "experiments/discovery/matched-bc-lowrate-20261114"
SIM = "/home/mary/miniconda3/envs/cogcal-sim/bin/python"
POLICY = "/home/mary/.cache/cogcal/venvs/tpsc-policy/bin/python"


def event(kind, **details):
    row = {"event": kind, "time_utc": datetime.now(timezone.utc).isoformat(), **details}
    with (RUN / "pipeline-events.jsonl").open("a") as stream:
        stream.write(json.dumps(row) + "\n")
    print(json.dumps(row), flush=True)


def main():
    if (RUN / "pipeline-events.jsonl").exists():
        raise FileExistsError("fresh pipeline required; inspect existing process before any resume")
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in SCRIPTS.glob("*.py")}
    (RUN / "pipeline-source-hashes.json").write_text(json.dumps(hashes, indent=2) + "\n")
    event("start", scope="ordinary_matched_bc_not_method", source_hashes=hashes)
    checkpoint = ROOT / "checkpoints/matched-bc-20261114/final-2000.pt"
    stages = [
        ("collection", [SIM, "-u", str(SCRIPTS / "collect.py"),
                        "--qualification", str(RUN / "qualification-result.json"),
                        "--data", str(ROOT / "data/discovery/matched-bc-lowrate-20261114"),
                        "--records", str(RUN / "collection")]),
        ("training", [POLICY, "-u", str(SCRIPTS / "train.py"),
                      "--records", str(RUN / "collection"),
                      "--checkpoint", str(checkpoint), "--out", str(RUN / "training")]),
        ("test", [SIM, "-u", str(SCRIPTS / "evaluate.py"),
                  "--checkpoint", str(checkpoint), "--policy-python", POLICY,
                  "--out", str(RUN / "test"), "--split", "test"]),
    ]
    for name, command in stages:
        started = time.monotonic()
        event("stage_start", stage=name, command=command)
        with (RUN / (name + ".stdout.txt")).open("x") as stdout:
            result = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=subprocess.STDOUT)
        event("stage_exit", stage=name, exit_code=result.returncode, wall_s=time.monotonic() - started)
        if result.returncode:
            raise SystemExit(result.returncode)
    summary = json.loads((RUN / "test/summary.json").read_text())
    event("complete", episodes=summary["episodes"], task_successes=summary["task_successes"],
          capability_gate=summary["task_successes"] >= 16, novelty="not_established")


if __name__ == "__main__":
    main()
