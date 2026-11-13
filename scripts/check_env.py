#!/usr/bin/env python
"""Check the local cogcal environment and the integrity of archived docs."""

from __future__ import annotations

import hashlib
import importlib.metadata as md
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogcal.paths import DOCS, REFERENCE, ROOT  # noqa: E402

REQUIRED_PACKAGES = [
    "numpy",
    "pandas",
    "scipy",
    "scikit-learn",
    "matplotlib",
    "seaborn",
    "imageio",
    "jupyterlab",
    "pytest",
    "ruff",
    "pyyaml",
    "tqdm",
]


def version(package: str) -> str:
    try:
        return md.version(package)
    except md.PackageNotFoundError:
        return "MISSING"


def check_manifest() -> tuple[int, list[str]]:
    manifest = REFERENCE / "MANIFEST.sha256"
    if not manifest.exists():
        return 0, ["MANIFEST.sha256 missing"]
    problems: list[str] = []
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split("  ", 1)
        path = REFERENCE / name
        checked += 1
        if not path.exists():
            problems.append(f"missing: {name}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            problems.append(f"hash mismatch: {name}")
    return checked, problems


def main() -> int:
    print(f"python      {sys.version.split()[0]}")
    print(f"platform    {platform.platform()}")
    print(f"root        {ROOT}")
    print(f"docs        {DOCS}")
    for package in REQUIRED_PACKAGES:
        print(f"{package:12s}{version(package)}")

    try:
        import torch  # noqa: F401

        print("torch       INSTALLED (unexpected for the local dev env)")
    except ModuleNotFoundError:
        print("torch       not installed (expected: model runtime is on A100)")

    main_record = DOCS / "具身认知标定_研究方向形成全记录_20261112.md"
    print(f"main record {'present' if main_record.exists() else 'MISSING'}")

    checked, problems = check_manifest()
    print(f"reference   {checked} files checked, {len(problems)} problem(s)")
    for problem in problems:
        print(f"  - {problem}")

    failed = bool(problems) or not main_record.exists() or any(
        version(p) == "MISSING" for p in REQUIRED_PACKAGES
    )
    print("\nRESULT:", "FAIL" if failed else "OK")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
