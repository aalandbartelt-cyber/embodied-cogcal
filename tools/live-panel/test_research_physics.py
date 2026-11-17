import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import research_runs


class PhysicalReplayTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.run = self.root / 'experiments/discovery/e/runs/r'
        self.run.mkdir(parents=True)
        self.trace = self.run / '42.trace.jsonl'
        self.trace.write_text('{"control_step":0}\n')
        self.physics = self.root / 'experiments/discovery/e/physics/r/42.npz'
        self.physics.parent.mkdir(parents=True)
        np.savez_compressed(self.physics, time=np.array([0., 1., 2.]),
                            xyz=np.array([[0., 0., .01], [0., .1, .06], [0., .2, .01]]),
                            finger_mask=np.array([0, 3, 0], dtype=np.uint8),
                            robot_contact=np.array([False, True, False]),
                            penetration=np.array([0., .0002, .0001]))
        self.row = {'seed': 42, 'physics_path': str(self.physics.relative_to(self.root)),
                    'physics_sha256': hashlib.sha256(self.physics.read_bytes()).hexdigest(),
                    'trace_sha256': hashlib.sha256(self.trace.read_bytes()).hexdigest()}
        self.write_row()

    def tearDown(self):
        self.temp.cleanup()

    def write_row(self):
        (self.run / 'episodes.jsonl').write_text(json.dumps(self.row) + '\n')

    def load(self):
        return research_runs.load_physics(self.root, str(self.trace.relative_to(self.root)))

    def test_recorded_physics_and_provenance(self):
        result = self.load()
        self.assertEqual(result['status'], 'verified')
        self.assertEqual(result['total'], 3)
        self.assertEqual(result['points'][1], [1., 0., .1, .06, 3, True, .0002])
        self.assertAlmostEqual(result['max_z_m'], .06)
        self.assertAlmostEqual(result['max_penetration_m'], .0002)

    def test_hash_mismatch_never_returns_points(self):
        self.row['physics_sha256'] = '0' * 64
        self.write_row()
        result = self.load()
        self.assertEqual(result['status'], 'hash_mismatch')
        self.assertNotIn('points', result)

    def test_trace_mismatch_and_incomplete_index_are_not_shown(self):
        self.trace.write_text('{"control_step":1}\n')
        self.assertEqual(self.load()['status'], 'hash_mismatch')
        (self.run / 'episodes.jsonl').write_text(json.dumps(self.row))
        self.assertEqual(self.load()['status'], 'incomplete_episode_index')

    def test_rejects_paths_outside_project_and_duplicate_rows(self):
        self.row['physics_path'] = '/etc/passwd'
        self.write_row()
        self.assertEqual(self.load()['status'], 'invalid_source')
        (self.run / 'episodes.jsonl').write_text((json.dumps(self.row)+'\n') * 2)
        self.assertEqual(self.load()['status'], 'ambiguous_episode')

    def test_missing_and_nonfinite_arrays_not_displayed(self):
        np.savez_compressed(self.physics, time=np.array([0.]), xyz=np.array([[0., 0., float('nan')]]),
                            finger_mask=np.array([0]), robot_contact=np.array([False]), penetration=np.array([0.]))
        self.row['physics_sha256'] = hashlib.sha256(self.physics.read_bytes()).hexdigest()
        self.write_row()
        self.assertEqual(self.load()['status'], 'invalid_physics')


if __name__ == '__main__':
    unittest.main()
