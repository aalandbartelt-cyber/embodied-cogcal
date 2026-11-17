import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import review  # noqa: E402


def fixture(tmp):
    root = Path(tmp)
    folder = root / 'experiments/discovery/demo'
    folder.mkdir(parents=True)
    (folder / 'PREREG.md').write_text('# P\n### H1\n≤ 1.5°\n', encoding='utf-8')
    (folder / 'RESULTS.md').write_text('# R\n', encoding='utf-8')
    return root, folder


class SignTest(unittest.TestCase):
    def test_sign_appends_without_touching_existing_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, folder = fixture(tmp)
            review.sign(root, 'demo', 'external', 'confirm', [folder / 'PREREG.md'], 'r1', 'ok')
            ledger = root / review.LEDGER
            before = ledger.read_bytes()
            review.sign(root, 'demo', 'external', 'partial', [folder / 'RESULTS.md'], 'r1', 'partial')
            after = ledger.read_bytes()
            self.assertTrue(after.startswith(before))
            self.assertEqual(len(after.splitlines()), 2)

    def test_rejects_absolute_and_escaping_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, folder = fixture(tmp)
            with self.assertRaises(ValueError):
                review.sign(root, 'demo', 'external', 'confirm', ['/etc/passwd'])
            with self.assertRaises(ValueError):
                review.sign(root, 'demo', 'external', 'confirm', ['../outside.md'])

    def test_rejects_symlink_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, folder = fixture(tmp)
            link = folder / 'link.md'
            link.symlink_to(folder / 'PREREG.md')
            with self.assertRaises(ValueError):
                review.sign(root, 'demo', 'external', 'confirm', [link])

    def test_rejects_automatic_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, folder = fixture(tmp)
            with self.assertRaises(ValueError):
                review.sign(root, 'demo', 'prereg', 'confirm', [folder / 'PREREG.md'])

    def test_rejects_unknown_experiment_and_bad_reviewer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, folder = fixture(tmp)
            with self.assertRaises(ValueError):
                review.sign(root, 'nope', 'external', 'confirm', [folder / 'PREREG.md'])
            with self.assertRaises(ValueError):
                review.sign(root, 'demo', 'external', 'confirm', [folder / 'PREREG.md'], 'bad reviewer!')

    def test_fold_last_wins_and_revoke_clears(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, folder = fixture(tmp)
            review.sign(root, 'demo', 'external', 'confirm', [folder / 'PREREG.md'], 'r1')
            review.sign(root, 'demo', 'external', 'partial', [folder / 'PREREG.md'], 'r1')
            state = review.fold(root)
            self.assertEqual(state[('demo', 'external')]['action'], 'partial')
            review.revoke(root, 'demo', 'external')
            self.assertEqual(review.fold(root), {})

    def test_stale_when_evidence_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, folder = fixture(tmp)
            review.sign(root, 'demo', 'external', 'confirm', [folder / 'PREREG.md'], 'r1')
            self.assertFalse(review.fold(root)[('demo', 'external')]['stale'])
            (folder / 'PREREG.md').write_text('# P\nchanged\n', encoding='utf-8')
            self.assertTrue(review.fold(root)[('demo', 'external')]['stale'])

    def test_ledger_holds_no_absolute_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, folder = fixture(tmp)
            review.sign(root, 'demo', 'external', 'confirm', [folder / 'PREREG.md'], 'r1', 'checked')
            text = (root / review.LEDGER).read_text(encoding='utf-8')
            self.assertNotIn('/home/', text)
            self.assertNotIn(str(root), text)

    def test_verify_flags_bad_line_and_stale_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, folder = fixture(tmp)
            review.sign(root, 'demo', 'external', 'confirm', [folder / 'PREREG.md'], 'r1')
            self.assertTrue(review.verify(root)['ok'])
            (folder / 'PREREG.md').write_text('changed', encoding='utf-8')
            self.assertFalse(review.verify(root)['ok'])
            with (root / review.LEDGER).open('a', encoding='utf-8') as handle:
                handle.write('{not json\n')
            self.assertFalse(review.verify(root)['ok'])

    def test_missing_ledger_folds_to_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = fixture(tmp)
            self.assertEqual(review.fold(root), {})


if __name__ == '__main__':
    unittest.main()
