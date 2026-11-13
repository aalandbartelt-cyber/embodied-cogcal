"""Project paths, kept in one place so scripts do not hard-code them."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(os.environ.get("COGCAL_ROOT", Path(__file__).resolve().parents[2])).resolve()

DOCS = ROOT / "docs"
REFERENCE = DOCS / "reference"
PROBES = ROOT / "probes"
ANALYSIS = ROOT / "analysis"
EXPERIMENTS = ROOT / "experiments"
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
VIDEOS = RESULTS / "videos"
CONFIGS = ROOT / "configs"


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def rel(path: Path | str) -> str:
    path = Path(path).resolve()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()
