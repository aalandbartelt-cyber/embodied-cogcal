"""Run one fixed initial-RGB-feature BC baseline; preserve earlier trials."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/discovery/anchor-bc-20261114"
POLICY = "/home/mary/.cache/cogcal/venvs/tpsc-policy/bin/python"
SIM = "/home/mary/miniconda3/envs/cogcal-sim/bin/python"


def event(kind, **detail):
    record = {"event": kind, "time_utc": datetime.now(timezone.utc).isoformat(), **detail}
    with (RUN / "pipeline-events.jsonl").open("a") as stream:
        stream.write(json.dumps(record) + "\n")
    print(json.dumps(record), flush=True)


def main():
    RUN.mkdir(parents=True, exist_ok=False)
    sources = list(Path(__file__).parent.glob("*.py")) + [
        ROOT / "experiments/discovery/matched_bc/carrier.py",
        ROOT / "experiments/discovery/matched_bc/policy.py",
        ROOT / "docs/plans/2026-11-14-initial-visual-feature-bc.md",
    ]
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (RUN / "source-hashes.json").write_text(json.dumps(hashes, indent=2) + "\n")
    event("start", kind_of_work="ordinary_bc_capability_not_method", source_hashes=hashes)
    stages = [
        ("training", [POLICY, "-u", str(Path(__file__).with_name("train_anchor.py"))]),
        ("test", [SIM, "-u", str(Path(__file__).with_name("evaluate_anchor.py")),
                  "--checkpoint", str(ROOT / "checkpoints/anchor-bc-20261114/final-2000.pt"),
                  "--out", str(RUN / "test"), "--policy-python", POLICY]),
    ]
    for stage, command in stages:
        started = time.monotonic()
        event("stage_start", stage=stage, command=command)
        with (RUN / f"{stage}.stdout.txt").open("x") as stdout:
            result = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=subprocess.STDOUT)
        event("stage_exit", stage=stage, exit_code=result.returncode, wall_s=time.monotonic() - started)
        if result.returncode:
            raise SystemExit(result.returncode)
    summary = json.loads((RUN / "test/summary.json").read_text())
    event("complete", successes=summary["successes"], episodes=summary["episodes"],
          capability_gate=summary["successes"] >= 16, novelty="not_established")


if __name__ == "__main__":
    main()
