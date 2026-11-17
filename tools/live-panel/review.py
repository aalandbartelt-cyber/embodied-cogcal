#!/usr/bin/env python3
"""Append-only sign-off ledger for the research standard.

The console stays read-only; human confirmations are recorded here by CLI.  A
sign-off pins the SHA-256 of every evidence file it cites, so editing any of
them turns the record ``stale`` and the gate falls back to ``manual`` — the same
"timestamp + hash + invalidate on change" rule the brief panel already uses.

    python3 tools/live-panel/review.py sign   --experiment E --stage external \
        --action confirm --evidence PATH [--evidence PATH ...] [--reviewer r1] [--note "…"]
    python3 tools/live-panel/review.py revoke --experiment E --stage external
    python3 tools/live-panel/review.py list   [--experiment E] [--json]
    python3 tools/live-panel/review.py verify
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = 'docs/reviews/STANDARD_REVIEWS.jsonl'
SCHEMA = 'standard-review/1'
SIGNABLE = {'report', 'external', 'evidence'}
ACTIONS = {'confirm', 'partial', 'refute', 'revoke'}
REVIEWER = re.compile(r'^[A-Za-z0-9._-]{1,40}$')


def _now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def relative(root: Path, path: Path) -> str:
    """Repository-relative posix path; rejects escapes and symlinks."""
    root = Path(root).resolve()
    candidate = Path(path)
    original = candidate if candidate.is_absolute() else root / candidate
    if original.is_symlink():
        raise ValueError('evidence must not be a symlink')
    if candidate.is_absolute():
        candidate = candidate.resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            raise ValueError('evidence must live inside the repository') from None
    else:
        candidate = (root / candidate).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            raise ValueError('evidence must live inside the repository') from None
    if not candidate.is_file():
        raise ValueError(f'evidence not found: {candidate}')
    return candidate.relative_to(root).as_posix()


def append(root: Path, record: dict) -> None:
    root = Path(root)
    target = root / LEDGER
    target.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, sort_keys=True)
    with target.open('a', encoding='utf-8', newline='\n') as handle:
        handle.write(line + '\n')
        handle.flush()


def read(root: Path):
    path = Path(root) / LEDGER
    if not path.is_file():
        return [], []
    records, problems = [], []
    for number, line in enumerate(path.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError('not an object')
            records.append(payload)
        except ValueError:
            problems.append({'line': number, 'problem': 'unparsable'})
    return records, problems


def fold(root: Path, records=None) -> dict:
    """Collapse the ledger into the current state per (experiment, stage)."""
    root = Path(root).resolve()
    if records is None:
        records, _ = read(root)
    state = {}
    for record in records:
        experiment = record.get('experiment')
        stage = record.get('stage')
        if not experiment or not stage:
            continue
        key = (experiment, stage)
        if record.get('action') == 'revoke':
            state.pop(key, None)
            continue
        evidence = record.get('evidence') or []
        stale = False
        for item in evidence:
            try:
                path = root / item['path']
                if not path.is_file() or sha256(path) != item.get('sha256'):
                    stale = True
                    break
            except (KeyError, OSError):
                stale = True
                break
        state[key] = {'action': record.get('action'), 'note': record.get('note', ''),
                      'at': record.get('at', ''), 'reviewer': record.get('reviewer', ''),
                      'stale': stale, 'evidence': evidence}
    return state


def verify(root: Path) -> dict:
    root = Path(root).resolve()
    records, problems = read(root)
    for index, record in enumerate(records, 1):
        if record.get('schema') != SCHEMA:
            problems.append({'line': index, 'problem': 'schema mismatch'})
        if record.get('stage') not in SIGNABLE:
            problems.append({'line': index, 'problem': f"stage not signable: {record.get('stage')}"})
        if record.get('action') not in ACTIONS:
            problems.append({'line': index, 'problem': f"unknown action: {record.get('action')}"})
        experiment = root / 'experiments/discovery' / str(record.get('experiment', ''))
        if not experiment.is_dir():
            problems.append({'line': index, 'problem': 'experiment not found'})
        for item in record.get('evidence') or []:
            path = item.get('path', '')
            if path.startswith('/') or '..' in Path(path).parts:
                problems.append({'line': index, 'problem': f'unsafe path: {path}'})
                continue
            try:
                if sha256(root / path) != item.get('sha256'):
                    problems.append({'line': index, 'problem': f'stale evidence: {path}'})
            except OSError:
                problems.append({'line': index, 'problem': f'missing evidence: {path}'})
    return {'records': len(records), 'problems': problems, 'ok': not problems}


def _gate_is_manual(root: Path, experiment: str, stage: str) -> bool:
    """A sign-off may only fill a gate the judge left ``manual``."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import research_standard

    folder = Path(root) / 'experiments/discovery' / experiment
    result = research_standard.evaluate(Path(root), folder)
    state = result['stages'].get(stage, {}).get('state')
    return state == 'manual'


def sign(root: Path, experiment: str, stage: str, action: str, evidence, reviewer='local', note=''):
    root = Path(root).resolve()
    if not (root / 'experiments/discovery' / experiment).is_dir():
        raise ValueError(f'unknown experiment: {experiment}')
    if stage not in SIGNABLE:
        raise ValueError(f'stage is judged automatically: {stage}')
    if action not in {'confirm', 'partial', 'refute'}:
        raise ValueError(f'unsupported action: {action}')
    if not REVIEWER.match(reviewer or ''):
        raise ValueError('reviewer must be 1-40 characters of [A-Za-z0-9._-]')
    if '\n' in (note or '') or len(note or '') > 400:
        raise ValueError('note must be a single line under 400 characters')
    if not _gate_is_manual(root, experiment, stage):
        raise ValueError(f'gate {stage} is decided automatically; human sign-off is refused')
    items = [{'path': relative(root, item), 'sha256': sha256(root / relative(root, item))} for item in evidence]
    if not items:
        raise ValueError('at least one evidence file is required')
    record = {'schema': SCHEMA, 'at': _now(), 'experiment': experiment, 'stage': stage,
              'action': action, 'evidence': items, 'reviewer': reviewer or 'local', 'note': note or ''}
    append(root, record)
    return record


def revoke(root: Path, experiment: str, stage: str, note='', reviewer='local'):
    root = Path(root).resolve()
    if stage not in SIGNABLE:
        raise ValueError(f'stage is judged automatically: {stage}')
    record = {'schema': SCHEMA, 'at': _now(), 'experiment': experiment, 'stage': stage,
              'action': 'revoke', 'evidence': [], 'reviewer': reviewer or 'local', 'note': note or ''}
    append(root, record)
    return record


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(ROOT))
    sub = parser.add_subparsers(dest='command', required=True)

    signer = sub.add_parser('sign')
    signer.add_argument('--experiment', required=True)
    signer.add_argument('--stage', required=True, choices=sorted(SIGNABLE))
    signer.add_argument('--action', default='confirm', choices=['confirm', 'partial', 'refute'])
    signer.add_argument('--evidence', action='append', required=True)
    signer.add_argument('--reviewer', default='local')
    signer.add_argument('--note', default='')

    revoker = sub.add_parser('revoke')
    revoker.add_argument('--experiment', required=True)
    revoker.add_argument('--stage', required=True, choices=sorted(SIGNABLE))
    revoker.add_argument('--note', default='')
    revoker.add_argument('--reviewer', default='local')

    lister = sub.add_parser('list')
    lister.add_argument('--experiment')
    lister.add_argument('--json', action='store_true')

    sub.add_parser('verify')

    args = parser.parse_args(argv)
    root = Path(args.root)
    try:
        if args.command == 'sign':
            record = sign(root, args.experiment, args.stage, args.action, args.evidence, args.reviewer, args.note)
            print(json.dumps(record, ensure_ascii=False))
            return 0
        if args.command == 'revoke':
            print(json.dumps(revoke(root, args.experiment, args.stage, args.note, args.reviewer), ensure_ascii=False))
            return 0
        if args.command == 'list':
            state = fold(root)
            if args.experiment:
                state = {key: value for key, value in state.items() if key[0] == args.experiment}
            payload = [{'experiment': key[0], 'stage': key[1], **value} for key, value in sorted(state.items())]
            if args.json:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                for item in payload:
                    print(f"{item['experiment']}\t{item['stage']}\t{item['action']}\t"
                          f"{'stale' if item['stale'] else 'ok'}\t{item['note'][:60]}")
            return 0
        result = verify(root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['ok'] else 3
    except ValueError as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
