"""Verify E8 records against hashes captured in their original contracts.

Run from any directory with --repo pointing to the repository.  The source
hash discrepancies detected on 2026-11-17 are intentional audit failures;
this tool does not modify evidence or overwrite historical contracts.
"""
import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('--repo', type=Path, default=Path.cwd())
root = parser.parse_args().repo.resolve()
base = root / 'experiments/discovery/e8-theta-estimator-20261118'
@lru_cache(maxsize=None)
def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()
arms = ['est0','est15','est-15','nocomp15','nocomp-15','diag-15-neg7p5','diag-15-neg10','diag-15-pos15','smoke-est15','smoke-est-15']
errors=[]
restored=[]
for arm in arms:
    p=base/'runs'/arm
    c=json.loads((p/'contract.json').read_text())
    rows=[json.loads(l) for l in (p/'episodes.jsonl').read_text().splitlines() if l.strip()]
    if len(rows)!=len(c['seeds']) or {r['seed'] for r in rows}!=set(c['seeds']): errors.append((arm,'seed mismatch'))
    for r in rows:
        for label, path, expected in [('trace',p / f"{r['seed']}.trace.jsonl",r['trace_sha256']),('physics',root / r['physics_path'],r['physics_sha256'])]:
            if not path.exists(): errors.append((arm,r['seed'],label,'missing'))
            elif digest(path)!=expected: errors.append((arm,r['seed'],label,'hash mismatch'))
    for label,key,path in [('protocol','prereg_sha256',base/'PREREG_E8.md'),('estimator','theta_estimator_sha256',base/'theta_estimator.py'),('validation','validation_sha256',base/'validation_open/validation.json')]:
        expected=c.get(key) if label=='protocol' else c.get('estimator',{}).get(key)
        if expected and digest(path)!=expected: errors.append((arm,label,'hash mismatch'))
    for pathstr, expected in c.get('source_sha256',{}).items():
        try:
            relative=Path(pathstr).relative_to('/home/mary/research/embodied-cogcal')
        except ValueError:
            errors.append((arm,'source',pathstr,'outside recorded project root'))
            continue
        path=root/relative
        if path.is_file() and digest(path)==expected:
            continue
        candidate=base/'source_versions'/('rollout_e8_'+expected+'.py')
        if path.name=='rollout_e8.py' and candidate.is_file() and digest(candidate)==expected:
            restored.append((arm,str(candidate.relative_to(root))))
        elif not path.is_file():
            errors.append((arm,'source',str(relative),'missing'))
        else:
            errors.append((arm,'source',str(relative),'hash mismatch'))
    for key in ('checkpoint','carrier_pyc'):
        try:
            relative=Path(c[key]).relative_to('/home/mary/research/embodied-cogcal')
            p=root/relative
            if not p.is_file(): errors.append((arm,key,str(relative),'missing'))
            elif digest(p)!=c[key+'_sha256']: errors.append((arm,key,str(relative),'hash mismatch'))
        except (KeyError,ValueError):
            errors.append((arm,key,'invalid recorded path or hash'))
    print(arm,'rows',len(rows),'recorded success',sum(r['task_success'] for r in rows))
print('source_versions_verified',len(restored))
for x in restored: print('restored',*x)
print('error_count',len(errors))
for x in errors[:30]: print(x)
raise SystemExit(bool(errors))
