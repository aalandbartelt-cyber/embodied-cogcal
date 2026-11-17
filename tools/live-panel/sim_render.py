#!/usr/bin/env python3
"""MuJoCo frame server for the research console.

Runs under the simulation environment (needs ``mujoco`` + ``PIL``) and serves
real MuJoCo renders of recorded states over loopback HTTP.  The console proxies
this endpoint; if the server cannot start (no EGL, no MuJoCo) the console shows
the error instead of drawing a stand-in.

    GET /frame?trace=<repo-relative>&step=<int>&az=&el=&dist=
        -> image/jpeg  (X-Sim-Step: actual control step)
    GET /health -> {"ok": true}

Rendering happens on the single server thread because the EGL context is bound
to the thread that created the Renderer.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

os.environ.setdefault('MUJOCO_GL', 'egl')

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

import mujoco  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

from simulation.so101.scene import DEFAULT_SCENE, JOINT_NAMES, load_scene  # noqa: E402

STATE = {}


def trace_rows(path: Path):
    try:
        st = path.stat()
    except OSError:
        return []
    key = (str(path), st.st_size, st.st_mtime_ns)
    cached = STATE.get('trace')
    if cached and cached[0] == key:
        return cached[1]
    rows = []
    try:
        with path.open(encoding='utf-8', errors='replace') as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and isinstance(row.get('q_after_rad'), list):
                    rows.append(row)
    except OSError:
        return []
    rows.sort(key=lambda row: row.get('control_step', 0))
    STATE['trace'] = (key, rows)
    return rows


def physics_index(trace_path: Path):
    folder = trace_path.parent
    seed = trace_path.name.split('.')[0]
    key = (str(folder), seed)
    cached = STATE.get('physics_key')
    if cached and cached[0] == key:
        return cached[1]
    result = None
    try:
        lines = (folder / 'episodes.jsonl').read_text(encoding='utf-8').splitlines()
        rows = [json.loads(line) for line in lines if line.strip()]
    except (OSError, ValueError):
        rows = []
    match = next((row for row in rows if str(row.get('seed')) == seed), None)
    rel = (match or {}).get('physics_path')
    if isinstance(rel, str):
        try:
            with np.load(REPO / rel, allow_pickle=False) as data:
                result = (np.asarray(data['time'], dtype=float), np.asarray(data['xyz'], dtype=float))
        except (OSError, ValueError, KeyError):
            result = None
    STATE['physics_key'] = (key, result)
    return result


def set_free_body(model, data, name, position):
    body = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, name)
    if body < 0:
        return
    joint = int(model.body_jntadr[body])
    if joint < 0 or int(model.jnt_type[joint]) != int(mujoco.mjtJoint.mjJNT_FREE):
        return
    address = int(model.jnt_qposadr[joint])
    data.qpos[address:address + 3] = position
    data.qpos[address + 3:address + 7] = [1.0, 0.0, 0.0, 0.0]


def frame_jpeg(trace_path: Path, step: int, azimuth: float, elevation: float, distance: float):
    model, data = STATE['model'], STATE['data']
    rows = trace_rows(trace_path)
    if not rows:
        raise RuntimeError('该轨迹尚无完整行')
    row = rows[-1] if step < 0 else min(rows, key=lambda item: abs(int(item.get('control_step', 0)) - step))
    joints = row.get('q_after_rad') or []
    for index, name in enumerate(JOINT_NAMES):
        joint = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
        if joint < 0 or index >= len(joints):
            continue
        value = joints[index]
        if isinstance(value, (int, float)):
            data.qpos[int(model.jnt_qposadr[joint])] = float(value)
    physics = physics_index(trace_path)
    if physics is not None:
        times, xyz = physics
        stamp = row.get('sim_time_s')
        if times.size and isinstance(stamp, (int, float)):
            set_free_body(model, data, 'red_object', xyz[int(np.argmin(np.abs(times - float(stamp))))])
    mujoco.mj_forward(model, data)

    camera = mujoco.MjvCamera()
    camera.type = mujoco.mjtCamera.mjCAMERA_FREE
    camera.azimuth = azimuth
    camera.elevation = elevation
    camera.distance = distance
    camera.lookat[:] = [0.17, 0.0, 0.10]
    renderer = STATE['renderer']
    renderer.update_scene(data, camera=camera)
    renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW] = True
    pixels = renderer.render()
    buffer = io.BytesIO()
    Image.fromarray(pixels).save(buffer, 'JPEG', quality=78)
    return buffer.getvalue(), row.get('control_step')


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/health':
            return self.reply(200, b'{"ok": true}', 'application/json')
        if parsed.path != '/frame':
            return self.reply(404, b'not found', 'text/plain')
        query = parse_qs(parsed.query)
        relative = query.get('trace', [''])[0]
        if not relative.startswith('experiments/discovery/') or not relative.endswith('.trace.jsonl'):
            return self.reply(400, b'bad trace', 'text/plain')
        trace_path = (REPO / relative).resolve()
        if not str(trace_path).startswith(str(REPO / 'experiments/discovery')):
            return self.reply(403, b'forbidden', 'text/plain')
        try:
            step = int(query.get('step', ['-1'])[0])
            azimuth = float(query.get('az', ['-115'])[0])
            elevation = float(query.get('el', ['24'])[0])
            distance = float(query.get('dist', ['1.05'])[0])
            payload, actual = frame_jpeg(trace_path, step, azimuth, elevation, distance)
        except Exception as error:  # noqa: BLE001 - report to the console
            traceback.print_exc()
            body = json.dumps({'error': f'{type(error).__name__}: {error}'}, ensure_ascii=False).encode()
            return self.reply(503, body, 'application/json')
        self.reply(200, payload, 'image/jpeg', {'X-Sim-Step': str(actual)})

    def reply(self, code, body, kind, extra=None):
        self.send_response(code)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8791)
    parser.add_argument('--width', type=int, default=900)
    parser.add_argument('--height', type=int, default=520)
    args = parser.parse_args()
    model, data = load_scene(DEFAULT_SCENE, mujoco)
    # MuJoCo caps offscreen rendering at the framebuffer declared in the model.
    model.vis.global_.offwidth = max(int(model.vis.global_.offwidth), args.width)
    model.vis.global_.offheight = max(int(model.vis.global_.offheight), args.height)
    STATE['model'] = model
    STATE['data'] = data
    STATE['renderer'] = mujoco.Renderer(model, args.height, args.width)
    server = HTTPServer(('127.0.0.1', args.port), Handler)
    print(f'renderer ready on 127.0.0.1:{args.port} {args.width}x{args.height}', flush=True)
    server.serve_forever()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
