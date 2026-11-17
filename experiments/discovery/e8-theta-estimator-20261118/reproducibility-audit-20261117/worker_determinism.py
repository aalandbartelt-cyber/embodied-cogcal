"""Read-only repeated ACT worker evaluation on three existing demonstrations.

This tests fixed inputs, not closed-loop or cross-machine reproducibility.
Run inside the policy Python environment from the repository root.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import platform
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def summarize(chunks):
    values = np.asarray(chunks, dtype=np.float32)
    if values.shape != (2, 3, 3, 100, 6) or not np.isfinite(values).all():
        raise ValueError('expected 2 workers x 3 observations x 3 trials x 100 x 6 finite values')
    comparisons = []
    for process in range(2):
        for observation in range(3):
            for trial in range(3):
                baseline = values[0, observation, 0]
                sample = values[process, observation, trial]
                comparisons.append({'worker': process, 'observation': observation, 'trial': trial,
                    'exact_equal': bool(np.array_equal(baseline, sample)),
                    'max_abs_difference': float(np.max(np.abs(sample - baseline))),
                    'sha256_float32': hashlib.sha256(sample.astype('<f4').tobytes()).hexdigest()})
    return {'all_exact_equal': all(c['exact_equal'] for c in comparisons),
            'comparisons_not_exact': sum(not c['exact_equal'] for c in comparisons),
            'max_abs_difference': max(c['max_abs_difference'] for c in comparisons),
            'comparisons': comparisons}


def run(repo, destination):
    if destination.exists():
        raise FileExistsError('refusing to overwrite result')
    official = repo / 'experiments/discovery/official-act-20261116'
    source_index = repo / 'experiments/discovery/matched-bc-lowrate-20261114/collection/episodes.jsonl'
    checkpoint = repo / 'checkpoints/official-act-20261116/final-20000.pt'
    contract = official / 'training/contract.json'
    worker = official / 'infer_worker.py'
    row = next(row for row in (json.loads(x) for x in source_index.read_text().splitlines())
               if row['split'] == 'train' and row['seed'] == 4100)
    observation_file = Path(row['path'])
    if digest(observation_file) != row['sha256']:
        raise ValueError('demonstration hash mismatch')
    with np.load(observation_file, allow_pickle=False) as source:
        rgb, q = source['rgb'], source['q']
        if rgb.shape != (285, 2, 128, 128, 3) or q.shape != (285, 6):
            raise ValueError('demonstration shape mismatch')
        observations = [(rgb[index].copy(), q[index].copy()) for index in (0, 90, 180)]
    lines = []
    input_hashes = []
    for rgb_frame, state in observations:
        request = json.dumps({'rgb': base64.b64encode(rgb_frame.tobytes()).decode(), 'q_rad': state.tolist()})
        lines.extend([json.dumps({'reset': True}), request, request, json.dumps({'reset': True}), request])
        input_hashes.append({'rgb_sha256': hashlib.sha256(rgb_frame.tobytes()).hexdigest(),
                             'q_sha256': hashlib.sha256(state.astype('<f4').tobytes()).hexdigest()})
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    env['PYTHONNOUSERSITE'] = '1'
    outputs = []
    ready = []
    for index in range(2):
        result = subprocess.run([sys.executable, '-u', str(worker), '--checkpoint', str(checkpoint),
                                 '--contract', str(contract)], input='\n'.join(lines) + '\n',
                                capture_output=True, text=True, timeout=180, cwd=repo, env=env, check=True)
        responses = [json.loads(line) for line in result.stdout.splitlines()]
        if len(responses) != 16 or not responses[0].get('ready'):
            raise ValueError(f'worker {index} returned unexpected response count or readiness')
        ready.append(responses[0])
        process_chunks = []
        for obs in range(3):
            batch = responses[1 + 5 * obs: 1 + 5 * (obs + 1)]
            if batch[0] != {'reset': True} or batch[3] != {'reset': True}:
                raise ValueError('worker reset response mismatch')
            process_chunks.append([batch[1]['chunk_rad'], batch[2]['chunk_rad'], batch[4]['chunk_rad']])
        outputs.append(process_chunks)
    import torch
    result = {'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
              'description': 'Two fresh official ACT worker processes; three existing training observations; within each worker each input is requested twice without reset and once after reset.',
              'limitations': ['Fixed inputs from a single training demonstration', 'No simulation or rollout',
                              'Does not establish deterministic GPU execution across devices, releases, or full closed-loop trajectories'],
              'input_file': str(observation_file), 'input_file_sha256': digest(observation_file),
              'input_index_sha256': digest(source_index), 'frame_indices': [0, 90, 180],
              'input_hashes': input_hashes, 'checkpoint_sha256': digest(checkpoint),
              'training_contract_sha256': digest(contract), 'worker_sha256': digest(worker),
              'audit_script_sha256': digest(Path(__file__)),
              'python_version': sys.version, 'platform': platform.platform(),
              'numpy_version': np.__version__, 'torch_version': torch.__version__,
              'torch_cuda_build': torch.version.cuda, 'cudnn_version': torch.backends.cudnn.version(),
              'ready': ready, 'result': summarize(outputs)}
    with destination.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(json.dumps({'output': str(destination), **{k: result['result'][k] for k in
          ('all_exact_equal', 'comparisons_not_exact', 'max_abs_difference')}}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.repo.resolve(), args.out)
