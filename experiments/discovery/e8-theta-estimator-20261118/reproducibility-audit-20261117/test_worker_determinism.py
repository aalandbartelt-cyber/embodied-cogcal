import unittest
import numpy as np
from worker_determinism import summarize


class TestDeterminism(unittest.TestCase):
    def test_identical_chunks_pass_exact_comparison(self):
        data = np.zeros((2, 3, 3, 100, 6), dtype=np.float32)
        result = summarize(data)
        self.assertTrue(result['all_exact_equal'])
        self.assertEqual(result['max_abs_difference'], 0.0)

    def test_changed_chunk_reports_difference(self):
        data = np.zeros((2, 3, 3, 100, 6), dtype=np.float32)
        data[1, 2, 2, 3, 5] = 0.125
        result = summarize(data)
        self.assertFalse(result['all_exact_equal'])
        self.assertEqual(result['max_abs_difference'], 0.125)
        self.assertEqual(result['comparisons_not_exact'], 1)

    def test_nonfinite_and_wrong_shape_are_rejected(self):
        data = np.zeros((2, 3, 3, 100, 6), dtype=np.float32)
        data[0, 0, 0, 0, 0] = np.nan
        with self.assertRaises(ValueError): summarize(data)
        with self.assertRaises(ValueError): summarize(np.zeros((1,)))

if __name__ == '__main__':
    unittest.main()
