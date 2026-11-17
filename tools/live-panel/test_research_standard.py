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


class StructureTest(unittest.TestCase):
    def test_hypothesis_block_with_quantity_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make(root, 'e8', prereg='# 预注册\n### H1 静态精度\n预期 max |误差| ≤ 1.5°\n')
            result = research_standard.evaluate(root, folder)
            self.assertEqual(result['stages']['hypothesis']['state'], 'pass')

    def test_conditional_stopping_counts_as_stop_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prereg = ('# 预注册\n### H1 精度\nmax ≤ 1.5°\n'
                      '| 臂 | yaw |\n|---|---|\n| est15 | 15 |\n'
                      '种子 12850–12869。判据：成功率 ≥18/20。\n'
                      '若静态误差超限则先修估计器，不跑闭环。\n')
            folder = make(root, 'e8b', prereg=prereg)
            result = research_standard.evaluate(root, folder)
            self.assertEqual(result['stages']['prereg']['state'], 'pass')

    def test_analysis_verdict_is_not_a_verifier_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make(root, 'e7b',
                          prereg='# P\n## 3. Predictions\n成功率 ≥ 16/20\n',
                          runs=[([1, 2], 2)])
            (folder / 'analysis.json').write_text(
                '{"verdict": "CHECKPOINT_INELIGIBLE", "h1_passed": false}', encoding='utf-8')
            (folder / 'preflight.json').write_text('{"passed": true}', encoding='utf-8')
            result = research_standard.evaluate(root, folder)
            self.assertEqual(result['stages']['integrity']['state'], 'pass')

    def test_failed_verifier_payload_blocks_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make(root, 'e9', prereg='# P\n## 3. Predictions\n≤ 1.5°\n', runs=[([1], 1)])
            (folder / 'verify_e9.json').write_text('{"failed": 0}', encoding='utf-8')
            self.assertEqual(research_standard.evaluate(root, folder)['stages']['integrity']['state'], 'pass')
            (folder / 'verify_e9.json').write_text('{"failed": 2}', encoding='utf-8')
            self.assertEqual(research_standard.evaluate(root, folder)['stages']['integrity']['state'], 'fail')

    def test_verdict_section_satisfies_report_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make(root, 'e10',
                          prereg='# P\n### H1 精度\n≤ 1.5°\n',
                          results='# R\n## 裁决\n- H1 SUPPORTED\n- H2 FAILED\n')
            result = research_standard.evaluate(root, folder)
            self.assertEqual(result['stages']['report']['state'], 'pass')

    def test_smoke_runs_are_excluded_from_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make(root, 'e11',
                          prereg='# P\n## 3. Predictions\n≤ 1.5°\n',
                          runs=[([1], 1)])
            smoke = folder / 'runs/smoke-a'
            smoke.mkdir(parents=True)
            (smoke / 'contract.json').write_text('{"seeds": [1], "tag": "smoke"}', encoding='utf-8')
            (smoke / 'episodes.jsonl').write_text('{"seed": 1}\n', encoding='utf-8')
            result = research_standard.evaluate(root, folder)
            self.assertEqual(result['runs'], 1)
            self.assertEqual(result['runs_excluded'], 1)

    def test_oversized_prereg_is_warn_not_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make(root, 'e12', prereg='# P\n' + ('x' * 500_000))
            result = research_standard.evaluate(root, folder)
            self.assertEqual(result['stages']['prereg']['state'], 'warn')
            self.assertIn('超过', result['stages']['prereg']['detail'])

    def test_review_upgrades_manual_but_never_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make(root, 'e13', prereg='# P\n## 3. Predictions\n≤ 1.5°\n')
            confirmed = {('e13', 'external'): {'action': 'confirm', 'stale': False, 'note': 'ok'}}
            self.assertEqual(research_standard.evaluate(root, folder, confirmed)['stages']['external']['state'], 'pass')
            stale = {('e13', 'external'): {'action': 'confirm', 'stale': True, 'note': 'changed'}}
            self.assertEqual(research_standard.evaluate(root, folder, stale)['stages']['external']['state'], 'manual')
            bad_prereg = {('e13', 'prereg'): {'action': 'confirm', 'stale': False}}
            self.assertEqual(research_standard.evaluate(root, folder, bad_prereg)['stages']['prereg']['state'], 'fail')

    def test_evaluate_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make(root, 'e14', prereg='# P\n## 3. Predictions\n≤ 1.5°\n', runs=[([1], 1)])
            before = sorted(p.as_posix() for p in root.rglob('*'))
            research_standard.evaluate(root, folder)
            self.assertEqual(before, sorted(p.as_posix() for p in root.rglob('*')))


class DocTest(unittest.TestCase):
    def setUp(self):
        self.doc = (Path(__file__).resolve().parents[2] / 'docs/RESEARCH_STANDARD.md').read_text(encoding='utf-8')

    def test_doc_has_five_stages_with_required_sections(self):
        for index in range(5):
            self.assertIn(f'### D{index}', self.doc)
        for marker in ('退出谓词', 'kill criterion', '降级映射'):
            self.assertGreaterEqual(self.doc.count(marker), 5, marker)

    def test_doc_mapping_matches_code(self):
        for gate in research_standard.D_STAGE_GATES[0]:
            self.assertIn(gate, self.doc)
        self.assertIn('D4 论文级', self.doc)
        self.assertIn('manual', self.doc)


if __name__ == '__main__':
    unittest.main()
