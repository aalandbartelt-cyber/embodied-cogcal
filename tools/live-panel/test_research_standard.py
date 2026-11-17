import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import research_standard  # noqa: E402


def make(root, name, prereg=None, results=None, runs=None):
    folder = root / 'experiments/discovery' / name
    folder.mkdir(parents=True)
    if prereg is not None:
        (folder / 'PREREG.md').write_text(prereg, encoding='utf-8')
    if results is not None:
        (folder / 'RESULTS.md').write_text(results, encoding='utf-8')
    for index, (seeds, rows) in enumerate(runs or []):
        run = folder / f'runs/a{index}'
        run.mkdir(parents=True)
        (run / 'contract.json').write_text('{"seeds": %s}' % seeds, encoding='utf-8')
        (run / 'episodes.jsonl').write_text('{"seed":1}\n' * rows, encoding='utf-8')
    return folder


class StageTest(unittest.TestCase):
    def test_empty_experiment_blocks_at_hypothesis(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make(root, 'e0')
            result = research_standard.evaluate(root, root / 'experiments/discovery/e0')
            self.assertEqual(result['stage'], 0)
            self.assertIn('缺少 PREREG', result['blockers'][0])

    def test_prereg_requires_criterion_seeds_and_stopping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make(root, 'e1', prereg='# 预注册\n假设 H1：存在差异。\n')
            result = research_standard.evaluate(root, root / 'experiments/discovery/e1')
            self.assertEqual(result['stages']['prereg']['state'], 'fail')
            detail = result['stages']['prereg']['detail']
            self.assertIn('成功判据', detail)
            self.assertIn('停止规则', detail)

    def test_complete_study_reaches_integrity_and_flags_manual(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make(root, 'e2',
                          prereg='# 预注册\n假设 H1：存在差异。\n判据：成功率。\n种子 1-20。\n停止规则：异常即停。\n',
                          results='# 结果\n负结果与偏差已记录。\n',
                          runs=[([1, 2], 2)])
            (folder / 'verify_e2.json').write_text('{}', encoding='utf-8')
            result = research_standard.evaluate(root, folder)
            self.assertEqual(result['stages']['prereg']['state'], 'pass')
            self.assertEqual(result['stages']['integrity']['state'], 'pass')
            self.assertEqual(result['stages']['report']['state'], 'pass')
            self.assertEqual(result['stages']['external']['state'], 'manual')
            self.assertEqual(result['stage'], 5)
            self.assertTrue(result['manual'])

    def test_incomplete_runs_block_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make(root, 'e3',
                          prereg='# 预注册\n假设 H1。\n判据：成功率。\n种子 1-20。\n停止规则：异常即停。\n',
                          runs=[([1, 2, 3], 1)])
            (folder / 'verify_e3.json').write_text('{}', encoding='utf-8')
            result = research_standard.evaluate(root, folder)
            self.assertEqual(result['stages']['integrity']['state'], 'fail')
            self.assertIn('1/3', result['stages']['integrity']['detail'])


if __name__ == '__main__':
    unittest.main()
