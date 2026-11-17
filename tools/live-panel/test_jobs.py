import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jobs  # noqa: E402


class PlanTest(unittest.TestCase):
    def test_rejects_unknown_template_and_arm(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                jobs.plan(root, 'nope', 'est0', 12870, 5)
            with self.assertRaises(ValueError):
                jobs.plan(root, 'eval-e8-arm', 'arm-not-listed', 12870, 5)

    def test_rejects_out_of_range_seed_and_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                jobs.plan(root, 'eval-e8-arm', 'est0', 1, 5)
            with self.assertRaises(ValueError):
                jobs.plan(root, 'eval-e8-arm', 'est0', 12870, 999)

    def test_plan_is_side_effect_free_and_reports_eta(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = jobs.plan(root, 'eval-e8-arm', 'est0', 12870, 20)
            self.assertEqual(plan['argv'][1], jobs.TEMPLATES['eval-e8-arm']['script'])
            self.assertIn('attempts/', plan['out'])
            self.assertFalse(plan['exists'])
            self.assertEqual(plan['eta_min'], 1.4)
            self.assertFalse(plan['executable'])
            self.assertFalse((root / plan['out']).exists())


if __name__ == '__main__':
    unittest.main()
