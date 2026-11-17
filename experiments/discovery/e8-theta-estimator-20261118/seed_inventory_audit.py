"""Bounded read-only seed-reference inventory; absence never proves freshness.

Includes tracked, untracked, ignored and hidden files in the current tree. It
skips Git object storage, symbolic links, binary/non-UTF8 and oversized files;
external histories, dynamic code and unrecognized formats remain unknown.
It writes only to stdout. Structured hits are references, not proof of use.
"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re

NAME = re.compile(r'^(\d+)(?:\..+)?$')
SEED_KEY = re.compile(r'(^|_)(seed|seeds|seed_start|seed_end)$', re.I)
SEED_CONTEXT = re.compile(r'\bseeds?\b[^\n\d]{0,32}(\d+)(?:\s*[-–—~]\s*(\d+))?', re.I)


def scan(root, low, high, max_bytes=32 * 1024 * 1024):
    root = Path(root).resolve()
    if not root.is_dir() or low > high or max_bytes <= 0:
        raise ValueError('invalid root, range or size limit')
    coverage = Counter({key: 0 for key in ('text_files_scanned', 'bytes_scanned',
        'binary_skipped', 'oversize_skipped', 'symlink_skipped',
        'git_directory_skipped', 'read_errors', 'json_parse_errors')})
    hits = set()
    omissions = []

    def add(rel, value, kind):
        if isinstance(value, int) and not isinstance(value, bool) and low <= value <= high:
            hits.add((rel, value, kind))

    def inspect(obj, rel, in_seed=False):
        if isinstance(obj, dict):
            for k, v in obj.items():
                key = str(k).lower()
                seed = bool(SEED_KEY.search(key))
                if seed and isinstance(v, list):
                    inspect(v, rel, True)
                elif seed and isinstance(v, int):
                    add(rel, v, 'structured_seed')
                elif seed and isinstance(v, str) and v.isdecimal():
                    add(rel, int(v), 'structured_seed')
                elif isinstance(v, (dict, list)):
                    inspect(v, rel, in_seed)
            if isinstance(obj.get('seed_start'), int) and isinstance(obj.get('seed_count'), int):
                start, count = obj['seed_start'], obj['seed_count']
                if 0 <= count <= 1_000_000:
                    for v in range(max(start, low), min(start + count, high + 1)):
                        add(rel, v, 'structured_seed_range')
        elif isinstance(obj, list):
            for value in obj:
                if in_seed and isinstance(value, int):
                    add(rel, value, 'structured_seed')
                elif isinstance(value, (dict, list)):
                    inspect(value, rel, in_seed)

    def onerror(err):
        coverage['read_errors'] += 1
        omissions.append({'path': str(getattr(err, 'filename', 'unknown')), 'reason': 'directory_read_error'})

    for directory, dirs, files in os.walk(root, topdown=True, followlinks=False, onerror=onerror):
        dirs.sort(); files.sort()
        retained = []
        for name in dirs:
            p = Path(directory) / name
            if name == '.git':
                coverage['git_directory_skipped'] += 1
            elif p.is_symlink():
                coverage['symlink_skipped'] += 1
                omissions.append({'path': str(p.relative_to(root)), 'reason': 'symlink'})
            else:
                retained.append(name)
        dirs[:] = retained
        for name in files:
            path = Path(directory) / name
            rel = path.relative_to(root).as_posix()
            match = NAME.match(name)
            if match:
                add(rel, int(match.group(1)), 'numeric_filename')
            try:
                if path.is_symlink():
                    coverage['symlink_skipped'] += 1
                    omissions.append({'path': rel, 'reason': 'symlink'})
                    continue
                if path.stat().st_size > max_bytes:
                    coverage['oversize_skipped'] += 1
                    omissions.append({'path': rel, 'reason': 'oversize'})
                    continue
                raw = path.read_bytes()
                if b'\0' in raw[:8192]:
                    coverage['binary_skipped'] += 1
                    omissions.append({'path': rel, 'reason': 'binary'})
                    continue
                try:
                    content = raw.decode('utf-8-sig')
                except UnicodeDecodeError:
                    coverage['binary_skipped'] += 1
                    omissions.append({'path': rel, 'reason': 'non_utf8'})
                    continue
                coverage['text_files_scanned'] += 1
                coverage['bytes_scanned'] += len(raw)
                suffix = path.suffix.lower()
                if suffix == '.json':
                    try:
                        inspect(json.loads(content), rel)
                    except (ValueError, RecursionError):
                        coverage['json_parse_errors'] += 1
                elif suffix == '.jsonl':
                    for line in content.splitlines():
                        if not line.strip():
                            continue
                        try:
                            inspect(json.loads(line), rel)
                        except (ValueError, RecursionError):
                            coverage['json_parse_errors'] += 1
                for match in SEED_CONTEXT.finditer(content):
                    first = int(match.group(1))
                    last = int(match.group(2)) if match.group(2) else first
                    if first <= last and last - first <= 1000000:
                        for value in range(max(first, low), min(last, high) + 1):
                            add(rel, value, 'text_seed_reference')
            except (OSError, ValueError) as exc:
                coverage['read_errors'] += 1
                omissions.append({'path': rel, 'reason': type(exc).__name__})
    return {'status': 'incomplete_no_freshness_claim', 'root': str(root),
        'candidate_range': [low, high], 'max_file_bytes': max_bytes,
        'coverage': dict(coverage),
        'hits': [{'path': p, 'value': v, 'kind': k} for p, v, k in sorted(hits)],
        'omissions': sorted(omissions, key=lambda x: (x['path'], x['reason'])),
        'limitations': ['Git objects/history, external records, binary, symlinks and oversize files are not inspected',
            'Text and structured references are not proof of actual use; unrecognized seed formats may be missed']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--start', type=int, required=True)
    parser.add_argument('--end', type=int, required=True)
    parser.add_argument('--max-bytes', type=int, default=32 * 1024 * 1024)
    args = parser.parse_args()
    print(json.dumps(scan(args.root, args.start, args.end, args.max_bytes), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
