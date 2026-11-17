"""Evaluate each experiment against the research standard's stage gates.

The console shows where a study stands, but it must never declare a stage passed
on weak evidence: checks that need a human read are reported as ``manual`` and
count as blockers for the overall stage.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

STAGES = (
    ('hypothesis', '问题与假设'),
    ('prereg', '预注册'),
    ('execution', '执行'),
    ('integrity', '完整性'),
    ('report', '结果与负结果'),
    ('external', '外部效度'),
    ('evidence', '论文级证据'),
)

MANUAL = ('external', 'evidence')
HYPOTHESIS = re.compile(r'H1|假设|hypothes', re.I)
CRITERION = re.compile(r'判据|criterion|阈值|threshold', re.I)
SEEDS = re.compile(r'种子|seed', re.I)
STOPPING = re.compile(r'停止|中止|stopping|stop rule', re.I)
NEGATIVE = re.compile(r'负结果|negative|偏差|deviation', re.I)
EXTERNAL = re.compile(r'外部效度|external validity|第二.?seed|second seed|真机|real robot', re.I)


def _read(path: Path, limit=400_000) -> str:
    try:
        if path.stat().st_size > limit:
            return ''
        return path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return ''


def _run_dirs(folder: Path):
    runs = []
    for episodes in folder.rglob('episodes.jsonl'):
        if episodes.is_file() and not episodes.is_symlink():
            runs.append(episodes.parent)
    return sorted(runs)


def evaluate(root: Path, folder: Path) -> dict:
    root = Path(root).resolve()
    folder = Path(folder).resolve()
    files = [p for p in folder.iterdir() if p.is_file() and not p.is_symlink()] if folder.is_dir() else []
    prereg = [p for p in files if p.name.upper().startswith('PREREG') and p.suffix.lower() == '.md']
    results = [p for p in files if p.name.upper().startswith('RESULT') and p.suffix.lower() == '.md']
    deviations = [p for p in files if 'DEVIATION' in p.name.upper()]
    prereg_text = '\n'.join(_read(p) for p in prereg)
    result_text = '\n'.join(_read(p) for p in results)
    deviation_text = '\n'.join(_read(p) for p in deviations)

    runs = _run_dirs(folder)
    contracts = [run / 'contract.json' for run in runs if (run / 'contract.json').is_file()]
    episodes = []
    for contract in contracts:
        try:
            payload = json.loads(_read(contract, 500_000) or '{}')
        except ValueError:
            payload = {}
        planned = len(payload.get('seeds')) if isinstance(payload.get('seeds'), list) else None
        index = contract.parent / 'episodes.jsonl'
        rows = 0
        try:
            rows = sum(1 for line in index.read_text(encoding='utf-8', errors='replace').splitlines() if line.strip())
        except OSError:
            rows = 0
        episodes.append({'run': contract.parent.relative_to(root).as_posix(), 'planned': planned, 'observed': rows})

    verifiers = [p for p in files if re.match(r'(verify|validation|audit)', p.name, re.I)] + \
                [p for p in folder.rglob('verify_*.json') if p.is_file()][:5]

    stages = {}

    if prereg and HYPOTHESIS.search(prereg_text):
        stages['hypothesis'] = ('pass', '预注册中写明可检验假设')
    elif prereg:
        stages['hypothesis'] = ('fail', '预注册存在，但未写明可检验假设（H1/预测方向）')
    else:
        stages['hypothesis'] = ('fail', '缺少 PREREG*.md')

    missing = []
    if not prereg:
        missing.append('预注册文件')
    else:
        if not CRITERION.search(prereg_text):
            missing.append('成功判据')
        if not SEEDS.search(prereg_text):
            missing.append('种子集合')
        if not STOPPING.search(prereg_text):
            missing.append('停止规则')
    stages['prereg'] = ('fail', '缺少：' + '、'.join(missing)) if missing else ('pass', '判据/种子/停止规则齐备')

    started = [item for item in episodes if item['observed'] > 0]
    if contracts and started:
        stages['execution'] = ('pass', f"{len(started)} 个运行已有逐集记录")
    elif contracts:
        stages['execution'] = ('fail', '已有合同但尚无逐集记录')
    else:
        stages['execution'] = ('fail', '未发现 contract.json 或 episodes.jsonl')

    incomplete = [item for item in episodes if item['planned'] and item['observed'] < item['planned']]
    if verifiers and not incomplete:
        stages['integrity'] = ('pass', f'{len(verifiers)} 份校验工件，集数完整')
    elif incomplete:
        stages['integrity'] = ('fail', '；'.join(f"{i['run'].split('/')[-1]} {i['observed']}/{i['planned']}" for i in incomplete[:3]))
    else:
        stages['integrity'] = ('fail', '缺少独立校验工件（verify/analysis）')

    if results and NEGATIVE.search(result_text + '\n' + deviation_text):
        stages['report'] = ('pass', '结果与偏差/负结果已归档')
    elif results:
        stages['report'] = ('warn', '有结果文档，但未见负结果或偏差记录')
    else:
        stages['report'] = ('fail', '缺少 RESULTS*.md')

    if results and EXTERNAL.search(result_text + '\n' + deviation_text):
        stages['external'] = ('manual', '文档提到外部效度，需人工确认是否成立')
    else:
        stages['external'] = ('manual', '未见第二 seed / 第二物体 / 真机结论')

    stages['evidence'] = ('manual', '图表的文件来源与哈希需人工核对')

    order = [name for name, _ in STAGES]
    reached = 0
    for name in order:
        if stages[name][0] == 'pass':
            reached += 1
        else:
            break
    blockers = [f'{label}：{stages[name][1]}' for name, label in STAGES if stages[name][0] in ('fail', 'warn')]
    manual = [f'{label}：{stages[name][1]}' for name, label in STAGES if stages[name][0] == 'manual']

    return {'id': folder.name, 'stage': reached, 'stage_name': STAGES[min(reached, len(STAGES) - 1)][1],
            'stages': {name: {'state': stages[name][0], 'detail': stages[name][1]} for name in order},
            'blockers': blockers, 'manual': manual, 'runs': len(episodes)}


def evaluate_all(root: Path) -> dict:
    root = Path(root).resolve()
    discovery = root / 'experiments/discovery'
    items = []
    if discovery.is_dir():
        for folder in sorted(discovery.iterdir()):
            if folder.is_dir() and not folder.is_symlink():
                try:
                    items.append(evaluate(root, folder))
                except OSError:
                    continue
    items.sort(key=lambda item: (item['stage'], item['id']), reverse=True)
    counts = {name: sum(1 for item in items if item['stages'][name]['state'] == 'pass') for name, _ in STAGES}
    return {'stages': [{'key': key, 'label': label} for key, label in STAGES],
            'counts': counts, 'experiments': items}
