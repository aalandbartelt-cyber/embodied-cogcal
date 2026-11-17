"""Bounded, read-only readers for episode and control trace artifacts."""
from __future__ import annotations
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

MAX_EPISODE_BYTES = 2_000_000
MAX_TRACE_BYTES = 8_000_000
MAX_DIRS = 2500
MAX_RUNS = 300
MAX_TOTAL_EPISODE_BYTES = 16_000_000


def inside(root, path):
    try:
        return path.resolve().is_relative_to((root / 'experiments/discovery').resolve())
    except OSError:
        return False


def read_lines(path, limit):
    try:
        with path.open('rb') as f:
            data = f.read(limit + 1)
    except OSError:
        return [], True, 0
    truncated = len(data) > limit
    data = data[:limit]
    partial = truncated or bool(data and not data.endswith(b'\n'))
    lines = data.split(b'\n')[:-1]
    records = []
    invalid = 0
    for line in lines:
        try:
            row = json.loads(line)
            if isinstance(row, dict): records.append(row)
            else: invalid += 1
        except (ValueError, UnicodeDecodeError):
            invalid += 1
    return records, partial, invalid


def discover_runs(root, experiment):
    root = Path(root).resolve()
    if not experiment or experiment in ('.', '..') or '/' in experiment or '\\' in experiment:
        return None
    base = root / 'experiments/discovery' / experiment
    if not base.is_dir() or not inside(root, base):
        return None
    out=[]; visited=0; limited=False; bytes_seen=0
    for here, dirs, files in os.walk(base, followlinks=False):
        visited += 1
        if visited > MAX_DIRS or len(out) >= MAX_RUNS:
            limited=True; break
        depth = len(Path(here).relative_to(base).parts)
        dirs[:] = sorted(d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'physics', 'physics_fallback') and not Path(here,d).is_symlink()) if depth < 5 else []
        if 'episodes.jsonl' not in files:
            continue
        folder=Path(here); ep=folder/'episodes.jsonl'
        if ep.is_symlink(): continue
        try: size=ep.stat().st_size
        except OSError: continue
        if bytes_seen + min(size, MAX_EPISODE_BYTES) > MAX_TOTAL_EPISODE_BYTES:
            limited=True; break
        bytes_seen += min(size, MAX_EPISODE_BYTES)
        rows, partial, invalid=read_lines(ep,MAX_EPISODE_BYTES)
        try:
            contract_path=folder/'contract.json'
            contract=json.loads(contract_path.read_text(encoding='utf-8')) if contract_path.is_file() and not contract_path.is_symlink() and contract_path.stat().st_size <= 1_000_000 else {}
            if not isinstance(contract,dict): contract={}
        except (OSError,ValueError): contract={}
        unique={}; duplicates=0; unkeyed=0
        for row in rows:
            seed=row.get('seed')
            if not isinstance(seed,(int,str)) or isinstance(seed,bool): unkeyed+=1; continue
            key=str(seed)
            if key in unique: duplicates+=1; continue
            unique[key]=row
        success=sum(row.get('task_success') is True for row in unique.values())
        failure=sum(row.get('task_success') is False for row in unique.values())
        planned=len(contract['seeds']) if isinstance(contract.get('seeds'),list) else None
        conditions={k:contract[k] for k in ('kind','tag','arm','yaw_deg','bias_mode','bias_deg','cube_edge_mm','delta_center_mm','control_budget') if k in contract and isinstance(contract[k],(int,float,str,bool))}
        traces=[p for p in sorted(folder.glob('*.trace.jsonl')) if p.is_file() and not p.is_symlink() and inside(root,p)][:200]
        rel=folder.relative_to(root).as_posix()
        try: updated=datetime.fromtimestamp(ep.stat().st_mtime,timezone.utc).isoformat()
        except OSError: updated=None
        out.append({'id':rel,'name':folder.name,'completed':len(unique),'success':success,'failure':failure,
                    'unscored':len(unique)-success-failure,'planned':planned,'duplicates':duplicates,'unkeyed':unkeyed,
                    'invalid':invalid,'partial':partial,'conditions':conditions,'updated':updated,
                    'episodes':rel+'/episodes.jsonl', 'contract':rel+'/contract.json' if contract else None,
                    'traces':[p.relative_to(root).as_posix() for p in traces]})
    return {'runs':out,'limited':limited,'visited':visited}


def load_trace(root, relative):
    root=Path(root).resolve()
    if not relative.startswith('experiments/discovery/') or not relative.endswith('.trace.jsonl'):
        return None
    path=root/relative
    if path.is_symlink() or not inside(root,path) or not path.is_file(): return None
    rows,partial,invalid=read_lines(path,MAX_TRACE_BYTES)
    points=[]; axis=None
    for row in rows:
        q=row.get('q_after_rad'); command=row.get('command_rad')
        if not isinstance(q,list) or len(q)<5: continue
        x=row.get('sim_time_s') if isinstance(row.get('sim_time_s'),(int,float)) else row.get('control_step')
        unit='sim_time_s' if isinstance(row.get('sim_time_s'),(int,float)) else 'control_step'
        val=q[4]; cmd=command[4] if isinstance(command,list) and len(command)>=5 else None
        if not isinstance(x,(int,float)) or not isinstance(val,(int,float)) or not math.isfinite(x) or not math.isfinite(val): continue
        if axis and axis!=unit: continue
        axis=unit
        if not isinstance(cmd,(int,float)) or not math.isfinite(cmd): cmd=None
        points.append([x,val,cmd])
    # Preserve the entire interval when downsampling. Never interpolate.
    total=len(points)
    if total>1500:
        indices=sorted({round(i*(total-1)/1499) for i in range(1500)})
        points=[points[i] for i in indices]
    try: updated=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat()
    except OSError: updated=None
    return {'path':relative,'axis':axis,'points':points,'total':total,'partial':partial,'invalid':invalid,'updated':updated}


def load_physics(root, trace_relative):
    """Read a recorded physics archive only when episode and both hashes match.

    This is a completed-episode artifact reader, not an online physics stream.
    Returns explicit unavailable/error states instead of guessing missing data.
    """
    import hashlib
    import io
    import re
    import zipfile

    root = Path(root).resolve()
    if (not isinstance(trace_relative, str)
            or not trace_relative.startswith('experiments/discovery/')
            or not re.fullmatch(r'\d+\.trace\.jsonl', Path(trace_relative).name)):
        return {'status': 'invalid_source'}
    trace = root / trace_relative
    if trace.is_symlink() or not inside(root, trace) or not trace.is_file():
        return {'status': 'invalid_source'}
    episode_file = trace.parent / 'episodes.jsonl'
    if episode_file.is_symlink() or not inside(root, episode_file) or not episode_file.is_file():
        return {'status': 'missing_episode'}
    rows, partial, invalid = read_lines(episode_file, MAX_EPISODE_BYTES)
    if partial or invalid:
        return {'status': 'incomplete_episode_index'}
    seed = trace.name.split('.')[0]
    matches = [row for row in rows if str(row.get('seed')) == seed]
    if not matches:
        return {'status': 'missing_episode'}
    if len(matches) != 1:
        return {'status': 'ambiguous_episode'}
    record = matches[0]
    relative = record.get('physics_path')
    physics_hash = record.get('physics_sha256')
    trace_hash = record.get('trace_sha256')
    if (not isinstance(relative, str) or not relative.startswith('experiments/discovery/')
            or not relative.endswith('.npz')):
        return {'status': 'invalid_source'}
    if not all(isinstance(h, str) and re.fullmatch(r'[0-9a-f]{64}', h)
               for h in (physics_hash, trace_hash)):
        return {'status': 'missing_provenance'}
    physics = root / relative
    if physics.is_symlink() or not inside(root, physics) or not physics.is_file():
        return {'status': 'invalid_source'}
    try:
        if physics.stat().st_size > 32_000_000 or trace.stat().st_size > MAX_TRACE_BYTES:
            return {'status': 'too_large'}
        physics_bytes = physics.read_bytes()
        trace_bytes = trace.read_bytes()
        if (len(physics_bytes) > 32_000_000 or len(trace_bytes) > MAX_TRACE_BYTES):
            return {'status': 'too_large'}
        if (hashlib.sha256(physics_bytes).hexdigest() != physics_hash
                or hashlib.sha256(trace_bytes).hexdigest() != trace_hash):
            return {'status': 'hash_mismatch'}
        with zipfile.ZipFile(io.BytesIO(physics_bytes)) as archive:
            if (len(archive.infolist()) > 32
                    or sum(item.file_size for item in archive.infolist()) > 64_000_000):
                return {'status': 'too_large'}
        try:
            import numpy as np
        except ImportError:
            return {'status': 'numpy_unavailable'}
        with np.load(io.BytesIO(physics_bytes), allow_pickle=False) as data:
            t = data['time']; xyz = data['xyz']; mask = data['finger_mask']
            contact = data['robot_contact']; penetration = data['penetration']
            n = len(t)
            if (n < 1 or n > 2_000_000 or t.shape != (n,) or xyz.shape != (n, 3)
                    or mask.shape != (n,) or contact.shape != (n,)
                    or penetration.shape != (n,)):
                return {'status': 'invalid_physics'}
            if (not all(np.issubdtype(a.dtype, np.number) for a in (t, xyz, mask, penetration))
                    or mask.dtype.kind not in 'ui' or contact.dtype.kind != 'b'
                    or not all(np.all(np.isfinite(a)) for a in (t, xyz, mask, penetration))
                    or np.any(np.diff(t) < 0) or np.any(penetration < 0)
                    or np.any(mask < 0) or np.any(mask > 3)):
                return {'status': 'invalid_physics'}
            indices = np.linspace(0, n - 1, min(n, 1500), dtype=int)
            points = [[float(t[i]), float(xyz[i, 0]), float(xyz[i, 1]), float(xyz[i, 2]),
                       int(mask[i]), bool(contact[i]), float(penetration[i])] for i in indices]
            return {'status': 'verified', 'source': relative, 'sha256': physics_hash,
                    'trace_sha256': trace_hash, 'total': n, 'points': points,
                    'max_z_m': float(np.max(xyz[:, 2])),
                    'max_penetration_m': float(np.max(penetration)),
                    'updated': datetime.fromtimestamp(physics.stat().st_mtime, timezone.utc).isoformat()}
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile):
        return {'status': 'invalid_physics'}
