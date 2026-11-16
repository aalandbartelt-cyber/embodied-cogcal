"""Independent verifier for the E4 outputs.

Checks the registered contract against the committed instrumentation files, the
per-episode invariants, and the rendering-equality predictions that define each
condition. It recomputes nothing about the policy; it only confirms that the
artifacts are the registered experiment and that the instrument behaved as
calibrated in check_variants.py.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "official-act-20261116"))
from rollout import sha  # noqa: E402

CONDITIONS = ("deg0", "visual", "collision", "both")
SEEDS = list(range(12880, 12900))
checks = []


def check(ok: bool, label: str) -> None:
    checks.append((bool(ok), label))
    print(("PASS " if ok else "FAIL ") + label, flush=True)


def main() -> int:
    variants = json.loads((HERE / "variants.json").read_text())
    instrument = json.loads((HERE / "variants_check.json").read_text())
    check(instrument["checks_passed"], "instrumentation checks passed")
    check(instrument["variants_sha256"] == sha(HERE / "variants.json"), "instrumentation matches variants.json")
    if not instrument["checks_passed"]:
        return 1

    contracts = {}
    summaries = {}
    first_rgb = {}
    for condition in CONDITIONS:
        out = HERE / f"runs/e4-{condition}"
        contracts[condition] = json.loads((out / "contract.json").read_text())
        summaries[condition] = json.loads((out / "summary.json").read_text())
    for condition in CONDITIONS:
        c = contracts[condition]
        entry = variants["conditions"][condition]
        check(c["condition"] == condition and c["tree"] == entry["tree"], f"{condition}: registered tree")
        check(c["body_yaw_deg"] == entry["body_yaw_deg"], f"{condition}: registered body yaw")
        check(c["image_yaw_deg"] == entry["image_yaw_deg"], f"{condition}: registered rendered yaw")
        check(c["model_xml_sha256"] == entry["xml_sha256"], f"{condition}: contract carries the condition model hash")
        check(c["seeds"] == SEEDS, f"{condition}: registered seeds")
        check(c["control_budget"] == 285 and c["horizon"] == 100 and c["execute"] == 30,
              f"{condition}: same control budget as E2")
        check(c["prereg_sha256"] == sha(HERE / "PREREG.md"), f"{condition}: preregistration unchanged")
        check(c["variants_check_sha256"] == sha(HERE / "variants_check.json"),
              f"{condition}: instrumentation hash unchanged")
        check(c["policy_inputs"] == ["current_two_RGB", "current_measured_q_rad"],
              f"{condition}: policy inputs as audited")
        check(len(c["delta_mm_per_seed"]) == 20, f"{condition}: twenty registered offsets")
        check(all(0.5 <= v <= 1.5 for v in c["delta_mm_per_seed"].values()),
              f"{condition}: offsets inside U(0.5,1.5) mm")
    for key in ("checkpoint_sha256", "training_contract_sha256"):
        values = {contracts[c][key] for c in CONDITIONS}
        check(len(values) == 1, f"all conditions use the same {key}")
    deltas = {s: contracts["deg0"]["delta_mm_per_seed"][str(s)] for s in SEEDS}
    check(all(contracts[c]["delta_mm_per_seed"] == {str(s): deltas[s] for s in SEEDS} for c in CONDITIONS),
          "paired offsets identical across the four conditions")
    check(all(contracts[c]["model_xml_sha256"] == variants["conditions"][c]["xml_sha256"] for c in CONDITIONS),
          "each condition compiled its registered model")

    expected_yaw = {"deg0": (0.0, 0.0), "visual": (0.0, 15.0),
                    "collision": (15.0, 0.0), "both": (15.0, 15.0)}
    for condition in CONDITIONS:
        out = HERE / f"runs/e4-{condition}"
        summary = summaries[condition]
        rows = {r["seed"]: r for r in summary["rows"]}
        check(sorted(rows) == SEEDS and summary["episodes"] == 20, f"{condition}: twenty paired episodes")
        check(summary["task_successes"] == sum(r["task_success"] for r in summary["rows"]),
              f"{condition}: summary counts its rows")
        body, image = expected_yaw[condition]
        check(all(abs(r["body_yaw_deg"] - body) < 1e-9 and abs(r["look_yaw_deg"] - image) < 1e-6
                  for r in rows.values()),
              f"{condition}: measured frames carry the registered yaw")
        for seed in SEEDS:
            row = rows[seed]
            trace = out / f"{seed}.trace.jsonl"
            lines = [json.loads(line) for line in trace.read_text().splitlines()]
            step0 = lines[0]
            check(len(lines) == 285, f"{condition}/{seed}: 285 trace steps")
            check(abs(row["delta_mm"] - deltas[seed]) < 1e-12, f"{condition}/{seed}: paired offset")
            check(row["controls"] == 285 and abs(row["sim_time_s"] - 9.5) < 1e-9,
                  f"{condition}/{seed}: control budget")
            check(row["object_pose_writes_during_rollout"] == 0,
                  f"{condition}/{seed}: no pose writes during rollout")
            check(row["failure_reason"] is None or not row["task_success"],
                  f"{condition}/{seed}: failure reason only on failure")
            check(row["trace_sha256"] == sha(trace) and row["physics_sha256"] == sha(Path(row["physics_path"])),
                  f"{condition}/{seed}: artifacts intact")
            physics = np.load(row["physics_path"])
            check(all(np.isfinite(physics[name]).all() for name in physics.files),
                  f"{condition}/{seed}: physics finite")
            check(physics["q"].shape[1:] == (6,) and physics["xyz"].shape[1:] == (3,)
                  and physics["time"].shape == physics["control_step"].shape,
                  f"{condition}/{seed}: physics arrays shaped as recorded")
            first_rgb[(condition, seed)] = step0["rgb_sha256"]
            check(step0["control_step"] == 0 and step0["rgb_age_steps"] == 0,
                  f"{condition}/{seed}: first observation queried at step 0")

    for seed in SEEDS:
        check(first_rgb[("deg0", seed)] == first_rgb[("collision", seed)],
              f"{seed}: collision renders exactly the deg0 image (appearance control)")
        check(first_rgb[("visual", seed)] == first_rgb[("both", seed)],
              f"{seed}: visual renders exactly E2's theta=15 appearance")
        check(first_rgb[("visual", seed)] != first_rgb[("deg0", seed)],
              f"{seed}: visual can be told apart from deg0")

    passed = sum(ok for ok, _ in checks)
    failures = [label for ok, label in checks if not ok]
    (HERE / "verify_e4.json").write_text(json.dumps(
        {"checks": len(checks), "passed": passed, "failed": failures}, indent=2) + "\n")
    print(f"\n{passed}/{len(checks)} checks passed")
    if failures:
        print(f"FAILURES: {failures}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
