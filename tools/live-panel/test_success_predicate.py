import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import success_predicate as sp  # noqa: E402


def synthetic(ticks=120, hold=60, free_tail=20, final_z=0.014, xy=(0.2, 0.075), penetration=0.0, dt=0.01):
    xyz = np.zeros((ticks, 3))
    xyz[:, 0] = 0.19
    xyz[:, 1] = -0.07
    xyz[:, 2] = 0.014
    xyz[ticks - free_tail:, 0] = xy[0]
    xyz[ticks - free_tail:, 1] = xy[1]
    xyz[ticks - free_tail:, 2] = final_z
    xyz[ticks - free_tail - hold:ticks - free_tail, 2] = 0.12
    mask = np.zeros(ticks, dtype=np.int32)
    mask[ticks - free_tail - hold:ticks - free_tail] = 3
    contact = np.zeros(ticks, dtype=bool)
    contact[:ticks - free_tail] = True
    return {'xyz': xyz, 'finger_mask': mask, 'robot_contact': contact,
            'penetration': np.full(ticks, penetration),
            'control_step': np.arange(ticks),
            'time': np.arange(ticks) * dt, 'dt': dt}


class PredicateTest(unittest.TestCase):
    def test_synthetic_success_at_defaults(self):
        result = sp.predicate(synthetic(), 0.01, 0.014, [0.2, 0.075, 0.014])
        self.assertTrue(result['task_success'])
        self.assertTrue(result['placed'])
        self.assertTrue(result['released'])

    def test_tighter_placement_flips_verdict(self):
        loose = sp.predicate(synthetic(xy=(0.233, 0.075)), 0.01, 0.014, [0.2, 0.075, 0.014])
        tight = sp.predicate(synthetic(xy=(0.233, 0.075)), 0.01, 0.014, [0.2, 0.075, 0.014],
                             place_xy_m=0.030)
        self.assertTrue(loose['placed'])
        self.assertFalse(tight['placed'])

    def test_release_window_is_monotone(self):
        physics = synthetic(free_tail=3)           # 0.03 s of freedom at dt=0.01
        strict = sp.predicate(physics, 0.01, 0.014, [0.2, 0.075, 0.014], release_s=0.05)
        lax = sp.predicate(physics, 0.01, 0.014, [0.2, 0.075, 0.014], release_s=0.005)
        self.assertFalse(strict['released'])
        self.assertTrue(lax['released'])

    def test_penetration_ceiling(self):
        ok = sp.predicate(synthetic(penetration=0.0012), 0.01, 0.014, [0.2, 0.075, 0.014])
        bad = sp.predicate(synthetic(penetration=0.0018), 0.01, 0.014, [0.2, 0.075, 0.014],
                           penetration_m=0.0015)
        self.assertTrue(ok['task_success'])
        self.assertFalse(bad['task_success'])

    def test_truncate_reports_undefined_beyond_budget(self):
        physics = synthetic()
        self.assertIsNotNone(sp.truncate(physics, 5))
        self.assertIsNone(sp.truncate(physics, 0))

    def test_longest_run_matches_gold_semantics(self):
        self.assertEqual(sp.longest_run([True, True, False, True]), 2)
        self.assertEqual(sp.longest_run([]), 0)
        self.assertEqual(sp.longest_run([False, False]), 0)


if __name__ == '__main__':
    unittest.main()
