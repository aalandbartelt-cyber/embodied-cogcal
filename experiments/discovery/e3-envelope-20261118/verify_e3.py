"""Verify E3 artifacts: contract integrity, per-cell completeness, hashes.

Exit code 0 only if every cell passes every check. No episode is silently
skipped: a cell with a single failed check fails the whole verification.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
YAWS = (0, 5, 10, 15)
DELTAS = (2, 8, 14)
SEED_START = 12920
SEED_COUNT = 20
CUBE_EDGE_MM = 28.0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(cond: bool, message: str, problems: list[str]) -> None:
    if not cond:
        problems.append(message)


def quat_yaw_deg(q: list[float]) -> float:
    # q = [w, x, y, z], yaw about z: 2 atan2(z, w)
    return math.degrees(2.0 * math.atan2(q[3], q[0]))


def main() -> int:
    problems: list[str] = []
    prereg_sha = sha(HERE / "PREREG.md")
    checked = 0
    for yaw in YAWS:
        for delta in DELTAS:
            run = HERE / "runs" / f"e3-y{yaw}-d{delta}"
            contract_path = run / "contract.json"
            rows_path = run / "episodes.jsonl"
            summary_path = run / "summary.json"
            local: list[str] = []
            for path in (contract_path, rows_path, summary_path):
                check(path.exists(), f"{run.name}: missing {path.name}", local)
            if local:
                problems.extend(local)
                continue
            contract = json.loads(contract_path.read_text())
            rows = [json.loads(line) for line in rows_path.read_text().splitlines() if line.strip()]
            summary = json.loads(summary_path.read_text())

            check(contract["kind"] == "e3_yaw_delta_envelope_not_method", f"{run.name}: kind", problems)
            check(contract["yaw_deg"] == yaw, f"{run.name}: contract yaw {contract['yaw_deg']}", problems)
            check(contract["delta_mm"] == delta, f"{run.name}: contract delta {contract['delta_mm']}", problems)
            check(contract["tag"] == "e3", f"{run.name}: tag", problems)
            check(abs(contract["w_eff_mm"] - CUBE_EDGE_MM * (abs(math.cos(math.radians(yaw)))
                                                           + abs(math.sin(math.radians(yaw))))) < 1e-9,
                  f"{run.name}: w_eff", problems)
            check(contract["control_budget"] == 285, f"{run.name}: control budget", problems)
            check(contract["prereg_sha256"] == prereg_sha, f"{run.name}: prereg drift", problems)
            seeds = contract["seeds"]
            check(len(seeds) == SEED_COUNT, f"{run.name}: {len(seeds)} seeds in contract", problems)
            check(seeds == list(range(SEED_START, SEED_START + SEED_COUNT)), f"{run.name}: seed range", problems)
            check(len(rows) == SEED_COUNT, f"{run.name}: {len(rows)} rows", problems)
            check(sorted(r["seed"] for r in rows) == sorted(seeds), f"{run.name}: row seeds", problems)
            check(summary["episodes"] == SEED_COUNT, f"{run.name}: summary episodes", problems)
            check(summary["task_successes"] == sum(1 for r in rows if r["task_success"]),
                  f"{run.name}: summary successes", problems)

            for row in rows:
                seed = int(row["seed"])
                check(row["tag"] == "e3", f"{run.name} seed {seed}: row tag", problems)
                check(row["yaw_deg"] == yaw, f"{run.name} seed {seed}: row yaw", problems)
                check(row["delta_mm"] == delta, f"{run.name} seed {seed}: row delta", problems)
                check(row["controls"] == 285, f"{run.name} seed {seed}: controls", problems)
                check(abs(quat_yaw_deg(row["reset_quat_wxyz"]) - yaw) < 1e-6,
                      f"{run.name} seed {seed}: reset quat yaw", problems)
                success = row["task_success"]
                check(success == (bool(row["placed"]) and bool(row["released"])),
                      f"{run.name} seed {seed}: success != placed & released", problems)
                check((row["failure_reason"] is None) == bool(success),
                      f"{run.name} seed {seed}: failure_reason/success mismatch", problems)
                npz = HERE / row["physics_path"]
                check(npz.exists(), f"{run.name} seed {seed}: physics npz missing", problems)
                if npz.exists():
                    check(sha(npz) == row["physics_sha256"], f"{run.name} seed {seed}: physics sha", problems)
                check(len(row["trace_sha256"]) == 64, f"{run.name} seed {seed}: trace sha missing", problems)
                checked += 1

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
    print(f"OK {len(YAWS) * len(DELTAS)} cells x {SEED_COUNT} seeds verified ({checked} episodes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
