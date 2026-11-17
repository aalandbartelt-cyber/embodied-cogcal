#!/usr/bin/env python3
"""Read-only research console backed by repository artifacts; stdlib only."""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import shlex
import research_runs
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
ALLOWED = ('experiments/discovery/', 'results/videos/', 'results/validation/')
EXTENSIONS = {'.md', '.json', '.jsonl', '.log', '.txt', '.py', '.sh', '.mp4'}


def safe_artifact(root: Path, relative: str):
    if not relative.startswith(ALLOWED):
        return None
    try:
        base = root.resolve()
        path = (base / relative).resolve()
        if not path.is_relative_to(base) or path.suffix.lower() not in EXTENSIONS or not path.is_file():
            return None
        return path
    except (OSError, ValueError):
        return None


def info(root: Path, path: Path):
    rel = path.relative_to(root).as_posix()
    return {'name': path.name, 'path': rel, 'url': '/artifact?path=' + quote(rel, safe=''),
            'updated': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}


def live_processes(root: Path):
    # A process is shown only when its working directory or command references this repository.
    records = []
    proc = Path('/proc')
    if not proc.exists():
        return records
    for entry in proc.iterdir():
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            cmd = (entry / 'cmdline').read_bytes().replace(b'\0', b' ').decode('utf-8', 'replace').strip()
            cwd = os.readlink(entry / 'cwd')
            if ('experiments/discovery/' in cmd or '/experiments/discovery/' in cwd) and (str(root) in cmd or cwd.startswith(str(root) + '/')):
                records.append({'pid': int(entry.name), 'command': cmd[:350], 'cwd': cwd})
        except (OSError, ValueError):
            continue
    return records


def check_brief(root: Path, entry: dict):
    result = dict(entry)
    source = safe_artifact(root, entry.get('source', ''))
    if source is None:
        result['source_status'] = 'missing'
    else:
        result['source_status'] = 'matched' if hashlib.sha256(source.read_bytes()).hexdigest() == entry.get('sha256') else 'changed'
        result['url'] = '/artifact?path=' + quote(entry['source'], safe='')
    return result


def build_catalog(root: Path):
    root = root.resolve()
    experiments = []
    discovery = root / 'experiments/discovery'
    if discovery.is_dir():
        for folder in sorted(discovery.iterdir()):
            if not folder.is_dir() or folder.is_symlink():
                continue
            try:
                files = [p for p in folder.iterdir() if p.is_file() and not p.is_symlink()]
                prereg = [p for p in files if p.name.upper().startswith('PREREG') and p.suffix.lower() == '.md']
                results = [p for p in files if p.name.upper().startswith('RESULT') and p.suffix.lower() == '.md']
                verification = [p for p in files if p.name.lower().startswith(('verify', 'verification', 'validate')) and p.suffix.lower() in {'.json', '.py', '.log', '.txt'}]
                analysis = [p for p in files if p.name.lower().startswith('analysis') and p.suffix.lower() == '.json']
                logs = [p for p in files if p.suffix.lower() in {'.log', '.txt'}]
                if not (prereg or results or verification or analysis or logs):
                    continue
                def mapped(paths):
                    return [info(root, p) for p in sorted(paths)]
                updated = max((p.stat().st_mtime for p in files), default=folder.stat().st_mtime)
                experiments.append({'id': folder.name, 'prereg': mapped(prereg), 'results': mapped(results),
                                    'verification': mapped(verification), 'analysis': mapped(analysis), 'logs': mapped(logs),
                                    'updated': datetime.fromtimestamp(updated, timezone.utc).isoformat()})
            except OSError:
                continue
    experiments.sort(key=lambda x: x['updated'], reverse=True)
    video = safe_artifact(root, 'results/videos/so101_readiness.mp4')
    trace = safe_artifact(root, 'results/validation/so101_readiness.steps.jsonl')
    simulation = {'video': info(root, video), 'trace': info(root, trace) if trace else None,
                  'description': 'SO-101 脚本化环境连通性回放；仅为历史 smoke test，不代表策略验证或实时仿真。'} if video else None
    try:
        raw_brief = json.loads((HERE / 'research-brief.json').read_text(encoding='utf-8-sig'))
        brief = [check_brief(root, entry) for entry in raw_brief]
    except (OSError, ValueError, TypeError, KeyError):
        brief = []
    return {'brief': brief, 'generated_at': datetime.now(timezone.utc).isoformat(), 'experiments': experiments,
            'simulation': simulation, 'processes': live_processes(root)}


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, code, data, kind, extra=None):
        self.send_response(code)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ('/', '/index.html'):
            return self.send_bytes(200, (HERE / 'research.html').read_bytes(), 'text/html; charset=utf-8')
        if parsed.path == '/api/catalog':
            return self.send_bytes(200, json.dumps(build_catalog(PROJECT), ensure_ascii=False).encode(), 'application/json; charset=utf-8')
        if parsed.path == '/api/runs':
            experiment = parse_qs(parsed.query).get('experiment', [''])[0]
            data = research_runs.discover_runs(PROJECT, experiment)
            if data is None:
                return self.send_bytes(404, b'not found', 'text/plain')
            # Match only explicit --out paths, not directory names or stale log files.
            processes = live_processes(PROJECT)
            for run in data['runs']:
                run['pids'] = []
                for process in processes:
                    try:
                        parts = shlex.split(process['command'])
                        outputs = [parts[i+1] for i, part in enumerate(parts[:-1]) if part == '--out']
                        outputs += [part[6:] for part in parts if part.startswith('--out=')]
                        for output in outputs:
                            path = Path(output)
                            if not path.is_absolute(): path = Path(process['cwd']) / path
                            if path.resolve() == (PROJECT / run['id']).resolve():
                                run['pids'].append(process['pid'])
                                break
                    except (ValueError, OSError):
                        continue
            return self.send_bytes(200, json.dumps(data, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
        if parsed.path == '/api/trace':
            relative = parse_qs(parsed.query).get('path', [''])[0]
            data = research_runs.load_trace(PROJECT, relative)
            if data is None:
                return self.send_bytes(404, b'not found', 'text/plain')
            return self.send_bytes(200, json.dumps(data, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
        if parsed.path == '/api/history':
            try:
                lines = (HERE / 'events.jsonl').read_text(encoding='utf-8').splitlines()[-60:]
                events = []
                for line in lines:
                    try:
                        value = json.loads(line)
                        events.append({k: value.get(k) for k in ('at', 'type', 'text')})
                    except (ValueError, AttributeError):
                        continue
                return self.send_bytes(200, json.dumps(events, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
            except OSError:
                return self.send_bytes(200, b'[]', 'application/json; charset=utf-8')
        if parsed.path == '/healthz':
            return self.send_bytes(200, b'ok', 'text/plain; charset=utf-8')
        if parsed.path == '/artifact':
            relative = parse_qs(parsed.query).get('path', [''])[0]
            path = safe_artifact(PROJECT, relative)
            if path is None:
                return self.send_bytes(404, b'not found', 'text/plain')
            try:
                data = path.read_bytes()
            except OSError:
                return self.send_bytes(404, b'not found', 'text/plain')
            kind = 'video/mp4' if path.suffix.lower() == '.mp4' else 'text/plain; charset=utf-8'
            headers = {'Accept-Ranges': 'bytes'}
            if path.suffix.lower() == '.mp4' and self.headers.get('Range'):
                match = re.fullmatch(r'bytes=(\d+)-(\d*)', self.headers['Range'].strip())
                if match:
                    start = int(match.group(1)); end = min(int(match.group(2)) if match.group(2) else len(data) - 1, len(data) - 1)
                    if start <= end:
                        headers['Content-Range'] = f'bytes {start}-{end}/{len(data)}'
                        return self.send_bytes(206, data[start:end + 1], kind, headers)
            return self.send_bytes(200, data, kind, headers)
        return self.send_bytes(404, b'not found', 'text/plain')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f'Research console: http://{args.host}:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
