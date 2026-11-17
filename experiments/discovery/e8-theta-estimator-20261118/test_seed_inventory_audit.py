import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).with_name('seed_inventory_audit.py')
spec = importlib.util.spec_from_file_location('seed_inventory_audit', MODULE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class TestSeedInventory(unittest.TestCase):
    def test_inventory_and_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'a.json').write_text(json.dumps({'seed': 14001, 'seeds': [2, 14002],
                                                       'score': 14003}), encoding='utf-8')
            (root / '.ignored.jsonl').write_text('{"seed": 14004}\n{"seed": 7}\n', encoding='utf-8')
            (root / 'plan.md').write_text('正式 seed 14005–14007\n坐标 14008\n', encoding='utf-8')
            (root / 'blob.bin').write_bytes(b'\0' + b'14009')
            (root / 'large.log').write_text('seed 14010 ' * 20, encoding='utf-8')
            (root / '14011.trace.jsonl').write_text('{"step": 0}\n', encoding='utf-8')
            (root / '.git').mkdir()
            (root / '.git' / 'hidden').write_text('seed 14012', encoding='utf-8')
            result = audit.scan(root, 14000, 14012, max_bytes=100)
            hits = {(h['value'], h['kind']) for h in result['hits']}
            for seed in (14001, 14002, 14004):
                self.assertIn((seed, 'structured_seed'), hits)
            for seed in (14005, 14006, 14007):
                self.assertIn((seed, 'text_seed_reference'), hits)
            self.assertIn((14011, 'numeric_filename'), hits)
            self.assertFalse(any(v in (14003, 14008, 14009, 14010, 14012) for v, _ in hits))
            self.assertEqual(result['coverage']['binary_skipped'], 1)
            self.assertEqual(result['coverage']['oversize_skipped'], 1)
            self.assertEqual(result['coverage']['git_directory_skipped'], 1)
            self.assertEqual(result['status'], 'incomplete_no_freshness_claim')

    def test_structured_range_and_repeatability(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'contract.json').write_text(json.dumps({
                'seed_start': 14001, 'seed_count': 3,
                'nested': {'evaluation_seeds': [14006, 9]},
            }), encoding='utf-8')
            a = audit.scan(root, 14000, 14010)
            self.assertEqual(a, audit.scan(root, 14000, 14010))
            hits = {(h['value'], h['kind']) for h in a['hits']}
            for value in (14001, 14002, 14003):
                self.assertIn((value, 'structured_seed_range'), hits)
            self.assertIn((14006, 'structured_seed'), hits)
    def test_jsonl_bad_line_and_symlink_are_disclosed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'broken.jsonl').write_text('{"seed": 14002}\ninvalid\n', encoding='utf-8')
            (root / 'alias').symlink_to(root / 'broken.jsonl')
            result = audit.scan(root, 14000, 14003, max_bytes=1000)
            self.assertEqual(result['coverage']['json_parse_errors'], 1)
            self.assertEqual(result['coverage']['symlink_skipped'], 1)
            self.assertTrue(any(h['value'] == 14002 for h in result['hits']))


if __name__ == '__main__':
    unittest.main()
