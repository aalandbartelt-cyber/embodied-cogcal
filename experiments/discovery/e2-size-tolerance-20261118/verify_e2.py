"""Verify E2 artifacts: contract integrity, per-condition completeness, hashes.

Exit code 0 only if every condition passes every check. No episode is silently
skipped: a condition with a single failed check fails the whole verification.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
YAWS = (0, 2, 5, 10, 15)
SEED_COUNT = 20
DELTA_LO, DELTA_HI = 0.5, 1.5


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(cond: bool, message: str, problems: list[str]) -> None:
    if not cond:
        problems.append(message)


def main() -> int:
    problems: list[str] = []
    for yaw in YAWS:
        local: list[str] = []
        run = HERE / "runs" / f"e2-y{yaw}-d1"
        contract_path = run / "contract.json"
        rows_path = run / "episodes.jsonl"
        summary_path = run / "summary.json"
        for path in (contract_path, rows_path, summary_path):
            check(path.exists(), f"{run.name}: missing {path.name}", local)
        if local:
            problems.extend(local)
            continue
        contract = json.loads(contract_path.read_text())
        rows = [json.loads(line) for line in rows_path.read_text().splitlines() if line.strip()]
        summary = json.loads(summary_path.read_text())

        check(contract["yaw_deg"] == yaw, f"{run.name}: contract yaw {contract['yaw_deg']}", problems)
        check(contract["kind"] == "e2_yaw_tolerance_probe_not_method", f"{run.name}: kind", problems)
        check(contract["delta_center_mm"] == 1.0, f"{run.name}: delta centre", problems)
        seeds = contract["seeds"]
        check(len(seeds) == SEED_COUNT, f"{run.name}: {len(seeds)} seeds in contract", problems)
        check(seeds == list(range(12850, 12850 + SEED_COUNT)), f"{run.name}: seed range", problems)
        check(len(rows) == SEED_COUNT, f"{run.name}: {len(rows)} rows", problems)
        check(sorted(r["seed"] for r in rows) == sorted(seeds), f"{run.name}: row seeds", problems)
        check(summary["episodes"] == SEED_COUNT, f"{run.name}: summary episodes", problems)
        check(summary["task_successes"] == sum(1 for r in rows if r["task_success"]),
              f"{run.name}: summary successes", problems)

        for row in rows:
            seed = int(row["seed"])
            expected_delta = contract["delta_mm_per_seed"].get(str(seed), contract["delta_mm_per_seed"].get(seed))
            check(row["yaw_deg"] == yaw, f"{run.name} seed {seed}: row yaw", problems)
            check(abs(row["delta_mm"] - expected_delta) < 1e-9, f"{run.name} seed {seed}: delta", problems)
            check(DELTA_LO <= row["delta_mm"] <= DELTA_HI, f"{run.name} seed {seed}: delta range", problems)
            npz = HERE / row["physics_path"]
            check(npz.exists(), f"{run.name} seed {seed}: physics npz missing", problems)
            if npz.exists():
                check(sha(npz) == row["physics_sha256"], f"{run.name} seed {seed}: physics sha", problems)
            check(len(row["trace_sha256"]) == 64, f"{run.name} seed {seed}: trace sha missing", problems)
            check(row["controls"] == 285, f"{run.name} seed {seed}: controls", problems)

        for name, digest in contract["source_sha256"].items():
            path = Path(name)
            check(path.exists(), f"{run.name}: source missing {name}", problems)
            if path.exists():
                check(sha(path) == digest, f"{run.name}: source sha drift {name}", problems)

    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"{len(problems)} problem(s)")
        return 1
    print(f"OK {len(YAWS)} conditions x {SEED_COUNT} seeds verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
