"""Sequential fixed-baseline experiment; stops on any stage failure."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/discovery/recurrent-bc-20261114"
POLICY = "/home/mary/.cache/cogcal/venvs/tpsc-policy/bin/python"
SIM = "/home/mary/miniconda3/envs/cogcal-sim/bin/python"


def event(kind, **details):
    row = {"event": kind, "time_utc": datetime.now(timezone.utc).isoformat(), **details}
    with (RUN / "pipeline-events.jsonl").open("a") as stream:
        stream.write(json.dumps(row) + "\n")
    print(json.dumps(row), flush=True)


def main():
    RUN.mkdir(parents=True, exist_ok=False)
    sources = list(Path(__file__).parent.glob("*.py")) + [
        ROOT / "experiments/discovery/matched_bc/carrier.py",
        ROOT / "experiments/discovery/matched_bc/policy.py",
        ROOT / "docs/plans/2026-11-14-recurrent-bc-capability.md",
    ]
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (RUN / "source-hashes.json").write_text(json.dumps(source_hashes, indent=2) + "\n")
    event("start", kind_of_work="ordinary_bc_capability_not_method", source_hashes=source_hashes)
    for mode in ["carry", "reset"]:
        checkpoint = ROOT / f"checkpoints/recurrent-bc-20261114/{mode}-2000.pt"
        stages = [
            ("train", [POLICY, "-u", str(Path(__file__).with_name("train.py")), "--mode", mode,
                       "--out", str(RUN / f"train-{mode}"), "--checkpoint", str(checkpoint)]),
            ("test", [SIM, "-u", str(Path(__file__).with_name("evaluate.py")),
                      "--checkpoint", str(checkpoint), "--out", str(RUN / f"test-{mode}"),
                      "--policy-python", POLICY]),
        ]
        for stage, command in stages:
            started = time.monotonic()
            event("stage_start", mode=mode, stage=stage, command=command)
            with (RUN / f"{mode}-{stage}.stdout.txt").open("x") as stdout:
                result = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=subprocess.STDOUT)
            event("stage_exit", mode=mode, stage=stage, exit_code=result.returncode,
                  wall_s=time.monotonic() - started)
            if result.returncode:
                raise SystemExit(result.returncode)
    trained = [json.loads((RUN / f"train-{m}/completed.json").read_text()) for m in ["carry", "reset"]]
    matched = all(trained[0][key] == trained[1][key]
                  for key in ["initial_parameter_sha256", "sample_indices_sha256", "parameters"])
    summaries = {m: json.loads((RUN / f"test-{m}/summary.json").read_text())["successes"]
                 for m in ["carry", "reset"]}
    event("complete", successes=summaries, matched_initialization_and_sampling=matched,
          novelty="not_established", capability_gate={k: v >= 16 for k, v in summaries.items()})


if __name__ == "__main__":
    main()
