#!/usr/bin/env python3
"""Flatten the SO-101 scene into one self-contained MJCF for the browser viewer.

MuJoCo compiled to WebAssembly cannot read the repository, so ``<include>`` is
resolved here and the mesh directory is left as ``assets/`` for the viewer to
mount into its virtual file system.  Asset bytes are served by the console from
``third_party/SO-ARM100/Simulation/SO101/assets`` unchanged.

Usage:
    python3 tools/live-panel/build_scene.py
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCENE = REPO / 'simulation/so101/eccbf_factorial_scene.xml'
OUT = Path(__file__).resolve().parent / 'vendor/scene/scene.xml'

INCLUDE = re.compile(r'<include\s+file="([^"]+)"\s*/>')


def resolve(path: Path, seen: set[Path]) -> str:
    path = path.resolve()
    if path in seen:
        raise RuntimeError(f'circular include: {path}')
    seen.add(path)
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'<\?xml[^>]*\?>', '', text)

    def replace(match: re.Match) -> str:
        child = (path.parent / match.group(1)).resolve()
        return resolve(child, seen)

    text = INCLUDE.sub(replace, text)
    if path != SCENE:
        # Inner files carry their own <mujoco> wrapper and <compiler>; the outer
        # scene already provides both, so strip them before splicing.
        text = re.sub(r'<mujoco\b[^>]*>', '', text)
        text = re.sub(r'</mujoco>', '', text)
        text = re.sub(r'<compiler[^/]*/>', '', text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=str(OUT))
    args = parser.parse_args()
    text = resolve(SCENE, set())
    # The browser viewer mounts meshes under assets/ regardless of the source path.
    text = re.sub(r'<compiler\b([^>]*?)/>',
                  lambda m: '<compiler' + re.sub(r'\s*meshdir="[^"]*"', '', m.group(1)) + ' meshdir="assets"/>',
                  text, count=1)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding='utf-8')

    files = sorted({name for name in re.findall(r'file="([^"]+)"', text) if re.search(r'\.(stl|obj|png)$', name, re.I)})
    assets = REPO / 'third_party/SO-ARM100/Simulation/SO101/assets'
    missing = [name for name in files if not (assets / name).is_file()]
    print(f'wrote {out} ({len(text)} chars), mesh files: {len(files)}, missing: {missing}')
    return 0 if not missing else 1


if __name__ == '__main__':
    raise SystemExit(main())
