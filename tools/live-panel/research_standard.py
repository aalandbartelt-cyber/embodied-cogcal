"""Evaluate each experiment against the research standard's stage gates.

Structure first, keywords only as a labelled fallback.  Missing artefacts are
reported as ``manual``/``warn`` — never ``fail`` — because "not recorded" and
"recorded and wrong" are different facts (the E8 prereg was once failed merely
for not containing the word "停止").
"""
from __future__ import annotations

import json
import re
from pathlib import Path

GATES = (
    ('hypothesis', '问题与假设', 0),
    ('prereg', '预注册', 0),
    ('execution', '执行', 0),
    ('integrity', '完整性', 0),
    ('report', '结果与裁决', 1),
    ('external', '外部效度', 2),
    ('evidence', '论文级证据', 4),
)
STAGES = tuple((key, label) for key, label, _ in GATES)
D_STAGE_GATES = {0: ('hypothesis', 'prereg', 'execution', 'integrity'),
                 1: ('report',), 2: ('external',), 3: ('external',), 4: ('evidence',)}
D_STAGE_LABELS = {0: 'D0 台账', 1: 'D1 确认性+测量有效性', 2: 'D2 方向/剂量边界',
                  3: 'D3 外部效度', 4: 'D4 论文级'}

H_BLOCK = re.compile(r'^(?:#{1,4}\s*|\*\*)?H(\d+[a-z]?)\b', re.M)
QUANTITY = re.compile(r'[≥≤<>]|>=|<=|[+-]?\d+(?:\.\d+)?\s*(?:mm|cm|m|s|ms|deg|°|%|步|集|\d+\s*/\s*\d+)')
ARMS_TABLE = re.compile(r'^\|\s*(?:臂|arm|条件|condition)\s*\|', re.M | re.I)
SEED_RANGE = re.compile(r'\d{2,5}\s*[–\-~至]\s*\d{2,5}')
CRITERION = re.compile(r'判据|criterion|阈值|threshold|成功率|task_success', re.I)
STOPPING_LEGACY = re.compile(r'停止|中止|stopping|stop rule', re.I)
STOPPING_STRUCT = re.compile(r'若[^\n。]{0,40}(?:则|就|即)[^\n。]{0,40}|不跑\s*\d+[^\n。]{0,30}|超限[^\n。]{0,30}', re.I)
ANALYSIS_PLAN = re.compile(r'分析计划|统计方法|检验|McNemar|Fisher|bootstrap|多重比较', re.I)
VERDICT = re.compile(r'\b(SUPPORTED|FAILED|INCONCLUSIVE|NOT_TESTED)\b|支持|不支持|不确定|无法判定')
NEGATIVE = re.compile(r'负结果|negative|偏差|deviation', re.I)
MANUAL_GATES = ('external', 'evidence')
EXCLUDED_PARTS = {'smoke', 'audit', 'demo-render', '__pycache__'}
EXCLUDED_TAGS = {'smoke', 'audit', 'demo', 'fixture'}


def _read(path: Path, limit=400_000):
    try:
        if path.stat().st_size > limit:
            return '', 'too_large'
        return path.read_text(encoding='utf-8', errors='replace'), None
    except OSError:
        return '', 'missing'


def _files(folder: Path):
    try:
        return [p for p in folder.iterdir() if p.is_file() and not p.is_symlink()]
    except OSError:
        return []


def _run_dirs(folder: Path):
    runs, excluded = [], 0
    for episodes in folder.rglob('episodes.jsonl'):
        if not episodes.is_file() or episodes.is_symlink():
            continue
        relative_parts = {part.lower() for part in episodes.relative_to(folder).parts[:-1]}
        contract = episodes.parent / 'contract.json'
        tag = ''
        if contract.is_file():
            try:
                tag = str(json.loads(_read(contract, 500_000)[0] or '{}').get('tag', '')).lower()
            except ValueError:
                tag = ''
        if relative_parts & EXCLUDED_PARTS or tag in EXCLUDED_TAGS:
            excluded += 1
            continue
        runs.append(episodes.parent)
    return sorted(runs), excluded


def _hypotheses(text):
    """Return [(id, block_text)] for `H1`-style headings."""
    lines = text.splitlines()
    blocks, current, buffer = [], None, []
    for line in lines:
        match = H_BLOCK.match(line)
        if match:
            if current:
                blocks.append((current, '\n'.join(buffer)))
            current, buffer = match.group(1), [line]
        elif current:
            buffer.append(line)
    if current:
        blocks.append((current, '\n'.join(buffer)))
    return blocks


def _prereg_carriers(text, contracts):
    carriers = {}
    if ARMS_TABLE.search(text):
        carriers['arms_table'] = True
    if SEED_RANGE.search(text):
        carriers['seed_range'] = True
    hypotheses = _hypotheses(text)
    if CRITERION.search(text) and (QUANTITY.search(text) or any(QUANTITY.search(block) for _, block in hypotheses)):
        carriers['criterion'] = True
    if STOPPING_STRUCT.search(text) or any(contract.get('stop') or contract.get('stopping') for contract in contracts):
        carriers['stopping'] = True
    if ANALYSIS_PLAN.search(text):
        carriers['analysis'] = True
    if contracts and all(contract.get('control_budget') and contract.get('seeds') for contract in contracts):
        carriers['contract'] = True
    return carriers


def _verifier_payloads(folder: Path):
    payloads, scripts = [], []
    for path in folder.rglob('*.json'):
        if not path.is_file() or path.is_symlink():
            continue
        name = path.name.lower()
        if not (name.startswith('verify') or name.startswith('analysis') or 'audit' in name):
            continue
        try:
            payloads.append((path, json.loads(_read(path, 2_000_000)[0] or '{}')))
        except ValueError:
            payloads.append((path, None))
        if len(payloads) >= 8:
            break
    for path in folder.rglob('*.py'):
        name = path.name.lower()
        if name.startswith(('verify', 'analyze', 'audit', 'validate')):
            scripts.append(path)
    return payloads, scripts


def _verifier_state(payloads):
    judged = []
    for path, payload in payloads:
        if not isinstance(payload, dict):
            judged.append((path, 'unreadable', None))
            continue
        failures = None
        for key in ('failed', 'failures', 'error_count', 'errors'):
            value = payload.get(key)
            if isinstance(value, int):
                failures = value
                break
            if isinstance(value, list):
                failures = len(value)
                break
        ok = payload.get('ok')
        passed = payload.get('passed')
        verdict = payload.get('verdict')
        if isinstance(ok, bool):
            judged.append((path, 'pass' if ok else 'fail', failures))
        elif isinstance(passed, bool):
            judged.append((path, 'pass' if passed else 'fail', failures))
        elif failures is not None:
            judged.append((path, 'pass' if failures == 0 else 'fail', failures))
        else:
            judged.append((path, 'legacy', failures))
    return judged


def evaluate(root: Path, folder: Path, reviews=None) -> dict:
    root = Path(root).resolve()
    folder = Path(folder).resolve()
    reviews = reviews or {}
    files = _files(folder)
    prereg = [p for p in files if p.name.upper().startswith('PREREG') and p.suffix.lower() == '.md']
    results = [p for p in files if p.name.upper().startswith('RESULT') and p.suffix.lower() == '.md']
    deviations = [p for p in files if 'DEVIATION' in p.name.upper()]

    prereg_text, prereg_problem = ('', None)
    for path in prereg:
        text, problem = _read(path)
        prereg_text += text
        prereg_problem = prereg_problem or problem
    result_text = '\n'.join(_read(p)[0] for p in results)
    deviation_text = '\n'.join(_read(p)[0] for p in deviations)

    runs, excluded = _run_dirs(folder)
    contracts, episodes = [], []
    for run in runs:
        contract_path = run / 'contract.json'
        contract = {}
        if contract_path.is_file():
            try:
                contract = json.loads(_read(contract_path, 500_000)[0] or '{}')
            except ValueError:
                contract = {}
        contracts.append(contract)
        planned = len(contract['seeds']) if isinstance(contract.get('seeds'), list) else None
        try:
            rows = [json.loads(line) for line in
                    (run / 'episodes.jsonl').read_text(encoding='utf-8', errors='replace').splitlines() if line.strip()]
        except (OSError, ValueError):
            rows = []
        episodes.append({'run': run.relative_to(root).as_posix(), 'contract': contract,
                         'planned': planned, 'rows': rows})

    stages = {}

    hypotheses = _hypotheses(prereg_text)
    testable = [hid for hid, block in hypotheses if QUANTITY.search(block)]
    prediction = re.search(r'^#{1,4}[^\n]*(?:prediction|hypothes|假设|预测)[^\n]*\n(.*?)(?=^#{1,4}\s|\Z)',
                           prereg_text, re.M | re.S | re.I)
    if testable:
        stages['hypothesis'] = ('pass', f'{len(testable)} 条假设含可检验的量/方向', '')
    elif hypotheses:
        stages['hypothesis'] = ('pass', f'{len(hypotheses)} 条假设（回退判定：未含数值或比较符）', '')
    elif prediction and QUANTITY.search(prediction.group(1)):
        stages['hypothesis'] = ('pass', '预测小节含可检验的量或方向', '')
    elif prereg and re.search(r'H1|假设|hypothes|prediction|预测', prereg_text, re.I):
        stages['hypothesis'] = ('pass', '预注册提到假设（回退判定）', '')
    elif prereg:
        stages['hypothesis'] = ('fail', '预注册存在，但未写明可检验假设（H1/预测方向）', '')
    else:
        stages['hypothesis'] = ('fail', '缺少 PREREG*.md', '')

    carriers = _prereg_carriers(prereg_text, contracts)
    legacy = (bool(CRITERION.search(prereg_text)) and bool(SEED_RANGE.search(prereg_text) or re.search(r'种子|seed', prereg_text, re.I))
              and bool(STOPPING_LEGACY.search(prereg_text)))
    missing = []
    if not prereg:
        missing.append('预注册文件')
    elif not legacy and len(carriers) < 4:
        if 'criterion' not in carriers:
            missing.append('成功判据')
        if 'seed_range' not in carriers:
            missing.append('种子集合')
        if 'stopping' not in carriers:
            missing.append('停止规则')
    if prereg_problem == 'too_large':
        stages['prereg'] = ('warn', '预注册超过 400 KB，未解析', '')
    elif missing:
        stages['prereg'] = ('fail', '缺少：' + '、'.join(missing), '')
    else:
        stages['prereg'] = ('pass', '判据/种子/停止规则齐备' + ('' if legacy else '（结构判定）'), '')

    started = [item for item in episodes if item['rows']]
    mismatched = []
    for item in started:
        seeds = item['contract'].get('seeds')
        if not isinstance(seeds, list) or not item['contract'].get('kind'):
            continue
        observed = {str(row.get('seed')) for row in item['rows']}
        if observed != {str(seed) for seed in seeds} or len(item['rows']) != len(seeds):
            mismatched.append(f"{item['run'].split('/')[-1]} {len(item['rows'])}/{len(seeds)}")
    if started and mismatched:
        stages['execution'] = ('warn', '种子集合与逐集行不一致：' + '；'.join(mismatched[:3]), '')
    elif started:
        stages['execution'] = ('pass', f'{len(started)} 个运行已有逐集记录（排除 {excluded} 个 smoke/audit）', '')
    elif contracts:
        stages['execution'] = ('fail', '已有合同但尚无逐集记录', '')
    else:
        stages['execution'] = ('fail', '未发现 contract.json 或 episodes.jsonl', '')

    incomplete = [item for item in episodes if item['planned'] and len(item['rows']) < item['planned']]
    payloads, scripts = _verifier_payloads(folder)
    judged = _verifier_state(payloads)
    failing = [path.relative_to(root).as_posix() for path, state, _ in judged if state == 'fail']
    if incomplete:
        stages['integrity'] = ('fail', '；'.join(
            f"{item['run'].split('/')[-1]} {len(item['rows'])}/{item['planned']}" for item in incomplete[:3]), '')
    elif failing:
        stages['integrity'] = ('fail', '校验工件报告失败：' + '、'.join(failing[:2]), '')
    elif any(state == 'pass' for _, state, _ in judged):
        stages['integrity'] = ('pass', f'{len(judged)} 份校验工件，集数完整', '')
    elif judged:
        stages['integrity'] = ('pass', f'{len(judged)} 份历史校验工件（无结论字段，按存在受理）', '')
    elif scripts:
        stages['integrity'] = ('warn', '有校验脚本但无结论工件：' + '、'.join(p.name for p in scripts[:2]), '')
    else:
        stages['integrity'] = ('fail', '缺少独立校验工件（verify/analyze/audit 输出）', '')

    result_hyps = _hypotheses(result_text)
    verdict_section = re.search(r'^#{1,4}[^\n]*(?:裁决|结论|conclusion|verdict)[^\n]*\n(.*?)(?=^#{1,4}\s|\Z)',
                                result_text, re.M | re.S | re.I)
    section_verdicts = len(VERDICT.findall(verdict_section.group(1))) if verdict_section else 0
    if section_verdicts >= 2:
        stages['report'] = ('pass', f'结果文档以裁决小节给出 {section_verdicts} 条判定', '')
    elif result_hyps:
        missing_verdict = [hid for hid, block in result_hyps if not VERDICT.search(block)]
        if missing_verdict:
            stages['report'] = ('warn', '下列假设未给出裁决：' + '、'.join(missing_verdict[:4]), '')
        else:
            stages['report'] = ('pass', f'{len(result_hyps)} 条假设均有裁决', '')
    elif results and NEGATIVE.search(result_text + '\n' + deviation_text):
        stages['report'] = ('pass', '结果与偏差/负结果已归档（回退判定）', '')
    elif results:
        stages['report'] = ('warn', '有结果文档，但无假设裁决或负结果记录', '')
    else:
        stages['report'] = ('fail', '缺少 RESULTS*.md', '')

    record = (reviews or {}).get((folder.name, 'external'))
    direction = _direction_state(root, folder, reviews)
    generalization = _review_state('external', folder.name, reviews, '未见第二物体/场景/真机的复现结论')
    if record and not record.get('stale') and record.get('action') in ('confirm', 'refute'):
        stages['external'] = ('pass' if record['action'] == 'confirm' else 'fail',
                              record.get('note') or ('人工确认' if record['action'] == 'confirm' else '人工否证'), '')
    else:
        states = [direction, generalization]
        worst = min(states, key=lambda item: {'fail': 0, 'warn': 1, 'manual': 2, 'pass': 3}[item[0]])
        stages['external'] = (worst[0], '；'.join(item[1] for item in states if item[1]), '')

    evidence_state = _evidence_state(folder, reviews)
    stages['evidence'] = evidence_state

    order = [key for key, _ in STAGES]
    reached = 0
    for key in order:
        if stages[key][0] == 'pass':
            reached += 1
        else:
            break
    next_gate = STAGES[min(reached, len(STAGES) - 1)][1]
    stage_name = '已达成' if reached == len(order) else next_gate
    stage_label = '已过 ' + STAGES[reached - 1][1] if reached else '未立项'

    states_map = {key: {'state': stages[key][0], 'detail': stages[key][1],
                        'evidence': _gate_evidence(root, key, folder, prereg, results, payloads, judged)}
                  for key in order}
    blocking = [{'gate': key, 'label': label, 'state': stages[key][0], 'detail': stages[key][1],
                 'evidence': states_map[key]['evidence']}
                for key, label, _ in GATES if stages[key][0] in ('fail', 'warn')]
    manual = [f'{label}：{stages[key][1]}' for key, label, _ in GATES if stages[key][0] == 'manual']
    counts = {state: sum(1 for key in order if stages[key][0] == state)
              for state in ('pass', 'warn', 'fail', 'manual')}

    return {'id': folder.name, 'stage': reached, 'stage_max': len(order),
            'stage_name': stage_name, 'stage_label': stage_label,
            'd_stage': _d_stage(states_map, root),
            'stages': states_map, 'blocking': blocking,
            'blockers': [f"{item['label']}：{item['detail']}" for item in blocking],
            'manual': manual, 'counts': counts,
            'runs': len(episodes), 'runs_excluded': excluded,
            'reviews': sum(1 for key in MANUAL_GATES if _review_state(key, folder.name, reviews)[0] == 'pass')}


def _gate_evidence(root, key, folder, prereg, results, payloads, judged):
    evidence = []
    if key in ('hypothesis', 'prereg') and prereg:
        evidence.append({'path': prereg[0].relative_to(root).as_posix()})
    if key in ('report',) and results:
        evidence.append({'path': results[0].relative_to(root).as_posix()})
    if key == 'integrity' and payloads:
        for path, _ in payloads[:3]:
            evidence.append({'path': path.relative_to(root).as_posix()})
    if key == 'external':
        evidence.append({'path': 'docs/reviews/STANDARD_REVIEWS.jsonl'})
    return evidence


def _review_state(stage, experiment, reviews, fallback=''):
    record = (reviews or {}).get((experiment, stage))
    if not record or record.get('stale'):
        return ('manual', record.get('note') if record and record.get('stale') else fallback)
    action = record.get('action')
    if action == 'confirm':
        return ('pass', record.get('note') or '人工确认')
    if action == 'partial':
        return ('warn', record.get('note') or '人工标注为部分成立')
    if action == 'refute':
        return ('fail', record.get('note') or '人工标注为不成立')
    return ('manual', fallback)


def _direction_state(root, folder, reviews):
    analysis = root / 'analysis' / 'threshold_sensitivity.json'
    if not analysis.is_file():
        return ('manual', '尚无阈值敏感性结果（D1 未完成）')
    try:
        payload = json.loads(analysis.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return ('manual', '阈值敏感性结果不可解析')
    contrasts = payload.get('contrasts') or []
    mine = [item for item in contrasts if item.get('experiment') == folder.name]
    if not mine:
        return ('manual', '阈值敏感性结果未覆盖本实验')
    robust = [item for item in mine if item.get('verdict_robust')]
    if len(robust) == len(mine):
        return ('pass', f'{len(mine)} 个主对比在阈值网格内裁决稳健')
    return ('warn', f"{len(mine) - len(robust)}/{len(mine)} 个主对比在阈值扰动下翻转")


def _evidence_state(folder, reviews):
    figures = folder / 'FIGURES.json'
    if not figures.is_file():
        return ('manual', '缺少 FIGURES.json（图表来源与哈希）')
    try:
        payload = json.loads(figures.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return ('manual', 'FIGURES.json 不可解析')
    items = payload.get('figures') if isinstance(payload, dict) else payload
    if not isinstance(items, list) or not items:
        return ('manual', 'FIGURES.json 未列出图表')
    missing = [item.get('id', '?') for item in items if not item.get('sha256') or not item.get('source')]
    if missing:
        return ('warn', '图表缺少来源或哈希：' + '、'.join(missing[:3]))
    record = (reviews or {}).get((folder.name, 'evidence'))
    if record and not record.get('stale') and record.get('action') == 'confirm':
        return ('pass', '图表哈希齐备且经人工确认')
    return ('manual', f'{len(items)} 张图表哈希齐备，待人工确认')


def _d_stage(states_map, root):
    def ok(key):
        return states_map[key]['state'] == 'pass'
    if ok('evidence'):
        return 4
    if ok('external'):
        return 3
    if ok('report') and (root / 'analysis' / 'threshold_sensitivity.json').is_file():
        return 1
    if all(ok(key) for key in D_STAGE_GATES[0]):
        return 0
    return -1


def evaluate_all(root: Path, reviews=None) -> dict:
    root = Path(root).resolve()
    discovery = root / 'experiments/discovery'
    items = []
    if discovery.is_dir():
        for folder in sorted(discovery.iterdir()):
            if folder.is_dir() and not folder.is_symlink():
                try:
                    items.append(evaluate(root, folder, reviews))
                except OSError:
                    continue
    items.sort(key=lambda item: (item['stage'], item['id']), reverse=True)
    keys = [key for key, _ in STAGES]
    counts = {key: sum(1 for item in items if item['stages'][key]['state'] == 'pass') for key in keys}
    counts_by_state = {key: {state: sum(1 for item in items if item['stages'][key]['state'] == state)
                             for state in ('pass', 'warn', 'fail', 'manual')} for key in keys}
    signed = sum(1 for record in (reviews or {}).values() if not record.get('stale'))
    stale = sum(1 for record in (reviews or {}).values() if record.get('stale'))
    return {'stages': [{'key': key, 'label': label, 'd_stage': d} for key, label, d in GATES],
            'd_stages': [{'stage': index, 'label': label} for index, label in sorted(D_STAGE_LABELS.items())],
            'counts': counts, 'counts_by_state': counts_by_state,
            'reviews': {'signed': signed, 'stale': stale},
            'experiments': items}
