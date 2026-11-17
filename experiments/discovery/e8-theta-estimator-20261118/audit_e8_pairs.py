import hashlib
import json
import math
from pathlib import Path

root = Path('/home/mary/research/embodied-cogcal/experiments/discovery/e8-theta-estimator-20261118')
arms = ['nocomp15', 'est15', 'nocomp-15', 'est-15', 'diag-15-neg7p5', 'diag-15-neg10', 'diag-15-pos15']
data = {}
for arm in arms:
    p = root / 'runs' / arm / 'episodes.jsonl'
    rows = [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
    assert len(rows) == 20 and len({r['seed'] for r in rows}) == 20, arm
    data[arm] = {r['seed']: r for r in rows}
    print(arm, 'n=',len(rows), 'success=',sum(r['task_success'] for r in rows), 'episodes_sha256=',hashlib.sha256(p.read_bytes()).hexdigest())

for a,b in [('nocomp15','est15'),('nocomp-15','est-15'),('nocomp-15','diag-15-neg7p5'),('nocomp-15','diag-15-neg10'),('nocomp-15','diag-15-pos15')]:
    assert data[a].keys() == data[b].keys()
    for seed in data[a]:
        x,y=data[a][seed],data[b][seed]
        for key in ['source_xyz_m','goal_xyz_m','yaw_deg','control_budget']:
            assert x[key] == y[key], (a,b,seed,key,x[key],y[key])
    loss=sum(data[a][s]['task_success'] and not data[b][s]['task_success'] for s in data[a])
    gain=sum(not data[a][s]['task_success'] and data[b][s]['task_success'] for s in data[a])
    n=loss+gain
    p=min(1.0,2*sum(math.comb(n,k) for k in range(min(loss,gain)+1))/2**n) if n else 1.0
    print(a,'->',b,'loss=',loss,'gain=',gain,'paired_difference=',(gain-loss)/20,'exact_two_sided_p=',p)
