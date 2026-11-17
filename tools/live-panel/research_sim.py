"""Client for the MuJoCo frame server.

The console never draws a stand-in robot: it asks the renderer for a real
MuJoCo frame of the recorded state and shows exactly what came back, or an
explicit error when the renderer is unavailable.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYTHON = os.environ.get('WB_SIM_PYTHON', '/home/mary/miniconda3/envs/cogcal-sim/bin/python')
SCRIPT = HERE / 'sim_render.py'
PORT = int(os.environ.get('WB_SIM_PORT', '8791'))
BASE = f'http://127.0.0.1:{PORT}'

_START_LOCK = threading.Lock()
_LAST = {'at': 0.0, 'error': None, 'process': None}


def _reachable(timeout=0.5):
    try:
        with urllib.request.urlopen(BASE + '/health', timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, OSError):
        return False


def _port_open():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.3)
        return probe.connect_ex(('127.0.0.1', PORT)) == 0


def ensure(timeout=30.0):
    """Start the renderer if needed and wait until it answers /health."""
    if _reachable():
        return True
    with _START_LOCK:
        if _reachable():
            return True
        if _port_open():
            _LAST.update(at=time.monotonic(), error=f'端口 {PORT} 已被其他进程占用')
            raise RuntimeError(_LAST['error'])
        if not Path(PYTHON).exists():
            _LAST.update(at=time.monotonic(), error=f'找不到仿真环境 python：{PYTHON}')
            raise RuntimeError(_LAST['error'])
        if not SCRIPT.exists():
            raise RuntimeError(f'渲染脚本缺失：{SCRIPT}')
        environment = dict(os.environ, MUJOCO_GL=os.environ.get('MUJOCO_GL', 'egl'))
        log = open('/tmp/wb-sim-render.log', 'ab')
        process = subprocess.Popen([PYTHON, str(SCRIPT), '--port', str(PORT)],
                                   cwd=str(HERE.parents[1]), env=environment,
                                   stdout=log, stderr=log, start_new_session=True)
        _LAST['process'] = process
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if _reachable(0.4):
                _LAST.update(at=time.monotonic(), error=None)
                return True
            if process.poll() is not None:
                detail = ''
                try:
                    detail = Path('/tmp/wb-sim-render.log').read_text(encoding='utf-8')[-400:]
                except OSError:
                    pass
                _LAST.update(at=time.monotonic(), error=f'渲染进程退出：{detail.strip() or "无日志"}')
                raise RuntimeError(_LAST['error'])
            time.sleep(0.25)
        _LAST.update(at=time.monotonic(), error='渲染服务启动超时')
        raise RuntimeError(_LAST['error'])


def frame(relative, step, azimuth=-115.0, elevation=24.0, distance=1.05, timeout=10.0):
    """Return ``(jpeg_bytes, control_step)`` for one recorded state."""
    ensure()
    query = (f'/frame?trace={urllib.parse.quote(relative, safe="")}'
             f'&step={int(step)}&az={float(azimuth):.1f}&el={float(elevation):.1f}&dist={float(distance):.2f}')
    try:
        with urllib.request.urlopen(BASE + query, timeout=timeout) as response:
            payload = response.read()
            actual = response.headers.get('X-Sim-Step')
    except urllib.error.HTTPError as error:
        detail = ''
        try:
            detail = json.loads(error.read()).get('error', '')
        except (ValueError, OSError):
            pass
        raise RuntimeError(detail or f'渲染失败 HTTP {error.code}') from error
    return payload, int(actual) if actual is not None else int(step)


def health():
    if _reachable():
        return {'state': 'ready', 'port': PORT}
    return {'state': 'stopped', 'port': PORT, 'error': _LAST['error']}
