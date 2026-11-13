from __future__ import annotations

import hashlib

from cogcal.paths import ANALYSIS, DOCS, EXPERIMENTS, PROBES, REFERENCE, RESULTS


def test_reference_has_nine_documents():
    files = sorted(p for p in REFERENCE.glob("*.md") if p.name != "SOURCE.md")
    assert len(files) == 9, [p.name for p in files]


def test_reference_manifest_matches():
    manifest = REFERENCE / "MANIFEST.sha256"
    lines = [line for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 9
    for line in lines:
        digest, name = line.split("  ", 1)
        actual = hashlib.sha256((REFERENCE / name).read_bytes()).hexdigest()
        assert actual == digest, name


def test_main_record_present():
    path = DOCS / "具身认知标定_研究方向形成全记录_20261112.md"
    assert path.exists()
    assert path.stat().st_size > 100_000


def test_project_directories_present():
    for path in (DOCS, REFERENCE, PROBES, ANALYSIS, EXPERIMENTS, RESULTS):
        assert path.is_dir(), path
