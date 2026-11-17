#!/usr/bin/env python3
"""Extract a compact kinematic description of the SO-101 arm from the MJCF.

The console renders arm posture from recorded joint angles; it must not embed a
hand-written guess of the robot's geometry.  This script reads the model that
the simulation actually loads, walks the body tree, and writes ``arm-model.json``
next to this file.  Re-run it only when the upstream model changes.

Usage:
    python3 arm_model.py [--repo PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

MODEL = 'third_party/SO-ARM100/Simulation/SO101/so101_new_calib.xml'
SCENE = 'simulation/so101/eccbf_factorial_scene.xml'
JOINT_ORDER = ('shoulder_pan', 'shoulder_lift', 'elbow_flex', 'wrist_flex', 'wrist_roll', 'gripper')


def _floats(text, count, default):
    if not text:
        return list(default)
    values = [float(item) for item in text.split()]
    return values if len(values) == count else list(default)


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(repo: Path) -> dict:
    model_path = repo / MODEL
    tree = ET.parse(model_path)
    root = tree.getroot()

    bodies = []

    def walk(element, parent):
        for body in element.findall('body'):
            name = body.get('name', '')
            joint = body.find('joint')
            entry = {
                'name': name,
                'parent': parent,
                'pos': _floats(body.get('pos'), 3, (0.0, 0.0, 0.0)),
                'quat': _floats(body.get('quat'), 4, (1.0, 0.0, 0.0, 0.0)),
                'joint': None,
            }
            if joint is not None:
                entry['joint'] = {
                    'name': joint.get('name', ''),
                    'axis': _floats(joint.get('axis'), 3, (0.0, 0.0, 1.0)),
                    'range': _floats(joint.get('range'), 2, (-3.14, 3.14)),
                }
            bodies.append(entry)
            walk(body, name)

    worldbody = root.find('worldbody')
    walk(worldbody, None)

    scene = {'table': None, 'goal': None, 'objects': []}
    scene_path = repo / SCENE
    if scene_path.is_file():
        scene_root = ET.parse(scene_path).getroot()
        for body in scene_root.iter('body'):
            name = body.get('name', '')
            geom = body.find('geom')
            if geom is None:
                continue
            pos = _floats(body.get('pos'), 3, (0.0, 0.0, 0.0))
            size = _floats(geom.get('size'), 3, (0.0, 0.0, 0.0))
            if name == 'goal_region':
                scene['goal'] = {'pos': pos, 'size': size}
            else:
                scene['objects'].append({'name': name, 'pos': pos, 'size': size})
        for geom in scene_root.iter('geom'):
            if geom.get('name') == 'table':
                scene['table'] = {'pos': _floats(geom.get('pos'), 3, (0.0, 0.0, 0.0)),
                                  'size': _floats(geom.get('size'), 3, (0.0, 0.0, 0.0))}

    return {
        'model': MODEL,
        'model_sha256': _digest(model_path),
        'scene': SCENE if scene_path.is_file() else None,
        'scene_sha256': _digest(scene_path) if scene_path.is_file() else None,
        'joint_order': list(JOINT_ORDER),
        'bodies': bodies,
        'table': scene['table'],
        'goal': scene['goal'],
        'objects': scene['objects'],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument('--out', default=str(Path(__file__).with_name('arm-model.json')))
    args = parser.parse_args()
    payload = extract(Path(args.repo).resolve())
    Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    missing = [name for name in JOINT_ORDER
               if not any((body.get('joint') or {}).get('name') == name for body in payload['bodies'])]
    print(f"bodies={len(payload['bodies'])} joints_missing={missing}")
    return 0 if not missing else 1


if __name__ == '__main__':
    raise SystemExit(main())
