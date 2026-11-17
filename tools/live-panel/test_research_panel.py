import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('research_panel', Path(__file__).with_name('research_panel.py'))
panel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panel)

class CatalogTest(unittest.TestCase):
    def test_catalog_distinguishes_artifact_presence_from_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exp = root / 'experiments/discovery/e1-example'
            exp.mkdir(parents=True)
            (exp / 'PREREG.md').write_text('# protocol')
            (exp / 'RESULTS.md').write_text('# result')
            (exp / 'verify_e1.py').write_text('# check')
            (exp / 'validate_estimator.py').write_text('# validator')
            item = panel.build_catalog(root)['experiments'][0]
            self.assertEqual([x['name'] for x in item['prereg']], ['PREREG.md'])
            self.assertEqual([x['name'] for x in item['results']], ['RESULTS.md'])
            self.assertEqual([x['name'] for x in item['verification']], ['validate_estimator.py', 'verify_e1.py'])
            self.assertNotIn('passed', item)
    def test_missing_experiments_and_video_are_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = panel.build_catalog(Path(tmp))
            self.assertEqual(payload['experiments'], [])
            self.assertIsNone(payload['simulation'])
    def test_brief_marks_changed_source_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'experiments/discovery/e7/RESULTS.md'
            source.parent.mkdir(parents=True)
            source.write_text('changed')
            entry = {'source': 'experiments/discovery/e7/RESULTS.md', 'sha256': 'old'}
            self.assertEqual(panel.check_brief(root, entry)['source_status'], 'changed')

    def test_safe_artifact_rejects_traversal_and_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'experiments/discovery').mkdir(parents=True)
            (root / 'experiments/discovery/a.md').write_text('evidence')
            self.assertIsNotNone(panel.safe_artifact(root, 'experiments/discovery/a.md'))
            self.assertIsNone(panel.safe_artifact(root, '../secret.md'))
            self.assertIsNone(panel.safe_artifact(root, 'experiments/../../secret.md'))
            (root / 'experiments/discovery/link.md').symlink_to('/etc/passwd')
            self.assertIsNone(panel.safe_artifact(root, 'experiments/discovery/link.md'))

if __name__ == '__main__':
    unittest.main()
