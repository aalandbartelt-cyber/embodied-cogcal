"""E1' integrity check: hashes, seed memberships, sampled deltas, per-episode files.

Fails loudly rather than repairing. Reads only what the run wrote plus the frozen
objects it claims to have used.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNS = HERE / "runs"
BINS = 10
SEEDS = list(range(12800, 12820))


def sha(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    sys.path.insert(0, str(HERE.parent / "official-act-20261116"))
    from rollout import XML_SHA256  # noqa: PLC0415

    import mujoco
    from importlib.machinery import SourcelessFileLoader
    import importlib.util

    pyc = REPO / ".carrier-rt/a/b/carrier.pyc"
    loader = SourcelessFileLoader("verify_e1p_carrier", str(pyc))
    spec = importlib.util.spec_from_loader("verify_e1p_carrier", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    carrier = module.Carrier()
    assert sha(carrier.upstream.MODEL_XML) == XML_SHA256, "XML hash drifted"
    assert mujoco.__version__ == "4.0.1", f"mujoco {mujoco.__version__}"
    carrier.close()

    prereg = HERE / "PREREG.md"
    problems = []
    for b in range(BINS):
        run, physics = RUNS / f"e1p-b{b}", RUNS / f"e1p-b{b}-physics"
        contract = json.loads((run / "contract.json").read_text())
        rows = [json.loads(l) for l in (run / "episodes.jsonl").read_text().splitlines() if l.strip()]
        if contract["prereg_sha256"] != sha(prereg):
            problems.append(f"b{b}: prereg hash mismatch")
        if contract["seeds"] != SEEDS:
            problems.append(f"b{b}: seed list mismatch")
        if len(rows) != len(SEEDS):
            problems.append(f"b{b}: {len(rows)} episodes, expected {len(SEEDS)}")
        deltas = contract["delta_mm_per_seed"]
        for seed in SEEDS:
            row = next((r for r in rows if int(r["seed"]) == seed), None)
            if row is None:
                problems.append(f"b{b}: missing seed {seed}")
                continue
            if abs(float(row["delta_mm"]) - float(deltas[str(seed)])) > 1e-9:
                problems.append(f"b{b}/{seed}: delta drifted")
            if not 3.0 * b <= float(row["delta_mm"]) < 3.0 * (b + 1):
                problems.append(f"b{b}/{seed}: delta outside bin")
            if sha(physics / f"{seed}.npz") != row["physics_sha256"]:
                problems.append(f"b{b}/{seed}: physics hash mismatch")
            if sha(run / f"{seed}.trace.jsonl") != row["trace_sha256"]:
                problems.append(f"b{b}/{seed}: trace hash mismatch")
    summary = HERE / "e1p_result.json"
    if summary.exists():
        result = json.loads(summary.read_text())
        if len(result.get("rows", [])) != BINS * len(SEEDS):
            problems.append("analysis rows incomplete")
    print(json.dumps({"bins": BINS, "seeds": len(SEEDS), "problems": problems}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
