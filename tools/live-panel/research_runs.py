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
