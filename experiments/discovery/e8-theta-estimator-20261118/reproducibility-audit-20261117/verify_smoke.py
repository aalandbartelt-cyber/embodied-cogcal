"""Independent read-only verification of four E8 tooling smoke episodes."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path


def check_initial_pair(row_a, trace_a, row_b, trace_b):
    for key in ('seed', 'delta_mm', 'source_xyz_m', 'goal_xyz_m', 'yaw_deg'):
        if row_a[key] != row_b[key]:
            raise ValueError(f'initial row mismatch: {key}')
    for key in ('q_before_rad', 'rgb_sha256'):
        if trace_a[key] != trace_b[key]:
            raise ValueError(f'initial observation mismatch: {key}')


def check_injection(record, bias):
    policy, raw = record['policy_target_rad'], record['raw_target_rad']
    if len(policy) != 6 or len(raw) != 6:
        raise ValueError('expected six-dimensional target')
    if not all(math.isfinite(value) for value in [*policy, *raw]):
        raise ValueError('non-finite target')
    for i in range(6):
        expected = bias if i == 4 else 0.0
        if not math.isclose(raw[i] - policy[i], expected, abs_tol=1e-8, rel_tol=0):
            raise ValueError(f'injection mismatch in joint {i}')


def clipped_joints(record):
    raw, command = record['raw_target_rad'], record['command_rad']
    if len(raw) != 6 or len(command) != 6 or not all(math.isfinite(x) for x in [*raw, *command]):
        raise ValueError('invalid recorded command')
    return [i for i, (a, b) in enumerate(zip(raw, command)) if not math.isclose(a, b, rel_tol=0, abs_tol=1e-9)]


def check_contract_pair(a, b):
    for key in ('checkpoint_sha256', 'carrier_pyc_sha256', 'training_contract_sha256',
                'source_sha256', 'seeds', 'control_budget', 'control_fps', 'horizon', 'execute'):
        if a[key] != b[key]:
            raise ValueError(f'paired contracts differ: {key}')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def run(repo, smoke, out):
    if out.exists():
        raise FileExistsError('refusing to replace verification output')
    audit_path = repo / 'experiments/discovery/e8-theta-estimator-20261118/audit_e8_paired_offline.py'
    spec = importlib.util.spec_from_file_location('old_audit', audit_path)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    datasets = {}
    contracts = {}
    report = {'purpose': 'tooling smoke only; not confirmatory', 'arms': {}, 'pairs': {},
        'limitations': ['The E8 fixed-dose mode also applies an RGB estimator quality gate',
                        'E8 contract points to old E8 preregistration; it is not this smoke protocol',
                        'row q5_bias_est_deg records the visual estimate, not the fixed dose',
                        'Matching recorded initial observations does not prove hidden RNG equivalence',
                        'Contact quantities come from recorded simulation arrays, not independent measurements']}
    for arm, dose in [('zero',0.0), ('half',-7.5)]:
        folder = smoke / 'runs' / arm
        contract = json.loads((folder / 'contract.json').read_text())
        contracts[arm] = contract
        if (smoke / f'{arm}.exit').read_text().strip() != '0':
            raise ValueError(f'{arm}: nonzero exit')
        if contract['tag'] != 'smoke' or contract['yaw_deg'] != -15 or contract['bias_mode'] != 'fixed' or contract['bias_deg_fixed'] != dose or contract['seeds'] != [14100,14101]:
            raise ValueError(f'{arm}: unexpected contract')
        if digest(Path(contract['checkpoint'])) != contract['checkpoint_sha256']:
            raise ValueError(f'{arm}: checkpoint mismatch')
        for path, expected in contract['source_sha256'].items():
            if digest(Path(path)) != expected:
                raise ValueError(f'{arm}: source hash mismatch {path}')
        rows = [json.loads(line) for line in (folder / 'episodes.jsonl').read_text().splitlines()]
        if len(rows) != 2 or {row['seed'] for row in rows} != {14100,14101}:
            raise ValueError(f'{arm}: missing or duplicate seeds')
        datasets[arm] = {}
        entries = []
        for row in rows:
            seed = row['seed']
            trace_path = folder / f'{seed}.trace.jsonl'
            physics_path = repo / row['physics_path']
            if digest(trace_path) != row['trace_sha256'] or digest(physics_path) != row['physics_sha256']:
                raise ValueError(f'{arm}/{seed}: file hash mismatch')
            audit.verify_row(row)
            audit.verify_physics(physics_path, row)
            records = [json.loads(line) for line in trace_path.read_text().splitlines()]
            if len(records) != 330 or [r['control_step'] for r in records] != list(range(330)):
                raise ValueError(f'{arm}/{seed}: incomplete trace')
            per_joint = [0] * 6
            for record in records:
                check_injection(record, math.radians(dose))
                for joint in clipped_joints(record):
                    per_joint[joint] += 1
            datasets[arm][seed] = (row, records[0])
            entries.append({'seed': seed, 'task_success': row['task_success'],
                'trace_sha256': row['trace_sha256'], 'physics_sha256': row['physics_sha256'],
                'max_penetration_m': row['max_object_robot_penetration_m'],
                'clip_events': row['clip_events'], 'command_changed_steps_per_joint': per_joint})
        report['arms'][arm] = {'dose_deg':dose,'entries':entries,
            'contract_sha256': digest(folder/'contract.json'),
            'stdout_sha256': digest(smoke/f'{arm}.stdout.txt'),
            'stderr_sha256': digest(smoke/f'{arm}.stderr.txt')}
    check_contract_pair(contracts['zero'], contracts['half'])
    for seed in (14100,14101):
        check_initial_pair(*datasets['zero'][seed], *datasets['half'][seed])
        report['pairs'][seed] = {'recorded_initial_match':True}
    with out.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print('PASS: four smoke episodes, source/trace/physics hashes, outcome and recorded initial pairing')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--smoke',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    run(args.repo.resolve(),args.smoke.resolve(),args.out)
