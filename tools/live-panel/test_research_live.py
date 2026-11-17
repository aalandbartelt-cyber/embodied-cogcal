import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import research_runs  # noqa: E402
import research_live  # noqa: E402


def write_trace(path, rows):
    with path.open('w', encoding='utf-8') as stream:
        for row in rows:
            stream.write(json.dumps(row) + '\n')


class TailReaderTest(unittest.TestCase):
    def test_small_file_is_read_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'a.trace.jsonl'
            write_trace(path, [{'control_step': i, 'q_after_rad': [0, 0, 0, 0, 1]} for i in range(5)])
            rows, meta = research_runs.read_tail_lines(path, 2_000_000)
            self.assertEqual(len(rows), 5)
            self.assertFalse(meta['truncated_head'])
            self.assertEqual(meta['size'], path.stat().st_size)

    def test_window_drops_the_partial_head_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'a.trace.jsonl'
            write_trace(path, [{'control_step': i, 'q_after_rad': [0, 0, 0, 0, i]} for i in range(4000)])
            rows, meta = research_runs.read_tail_lines(path, 20_000)
            self.assertLessEqual(meta['bytes_read'], 20_000)
            self.assertTrue(meta['truncated_head'])
            self.assertGreater(len(rows), 0)
            self.assertIsInstance(rows[0]['control_step'], int)

    def test_trailing_half_line_is_not_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'a.trace.jsonl'
            write_trace(path, [{'control_step': 0, 'q_after_rad': [0, 0, 0, 0, 1]}])
            with path.open('a', encoding='utf-8') as stream:
                stream.write('{"control_step":1,"q_after_rad":[0,0,0,0,2')
            rows, meta = research_runs.read_tail_lines(path, 2_000_000)
            self.assertTrue(meta['partial_line'])
            self.assertEqual([row['control_step'] for row in rows], [0])

    def test_broken_line_is_counted_and_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'a.trace.jsonl'
            path.write_text('{"control_step":0,"q_after_rad":[0,0,0,0,1]}\nnot json\n'
                            '{"control_step":2,"q_after_rad":[0,0,0,0,3]}\n', encoding='utf-8')
            rows, meta = research_runs.read_tail_lines(path, 2_000_000)
            self.assertEqual(meta['invalid'], 1)
            self.assertEqual([row['control_step'] for row in rows], [0, 2])

    def test_window_of_only_a_half_line_yields_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'a.trace.jsonl'
            path.write_text('{"control_step":0,"q_after', encoding='utf-8')
            rows, meta = research_runs.read_tail_lines(path, 2_000_000)
            self.assertEqual(rows, [])
            self.assertTrue(meta['partial_line'])


class LoadTraceTest(unittest.TestCase):
    def _build(self, root, count=4, step=1):
        path = root / 'experiments/discovery/e1/runs/a'
        path.mkdir(parents=True)
        trace = path / '1.trace.jsonl'
        write_trace(trace, [{'control_step': i * step, 'sim_time_s': i * 0.5,
                             'q_after_rad': [0, 0, 0, 0, i], 'command_rad': [0, 0, 0, 0, i + 1]}
                            for i in range(count)])
        return trace, trace.relative_to(root).as_posix()

    def test_auto_mode_matches_full_mode_for_small_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace, rel = self._build(root)
            auto = research_runs.load_trace(root, rel)
            full = research_runs.load_trace(root, rel, mode='full')
            self.assertEqual(auto['points'], full['points'])
            self.assertEqual(auto['total'], full['total'])
            self.assertEqual(auto['live']['mode'], 'full')
            self.assertFalse(auto['live']['truncated_head'])

    def test_large_file_switches_to_tail_and_keeps_newest_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace, rel = self._build(root, count=40_000)
            self.assertGreater(trace.stat().st_size, research_runs.LIVE_TRACE_BYTES)
            data = research_runs.load_trace(root, rel)
            self.assertEqual(data['live']['mode'], 'tail')
            self.assertTrue(data['live']['truncated_head'])
            self.assertEqual(data['last_step'], 39_999)
            self.assertEqual(data['points'][-1][1], 39_999)

    def test_downsampling_keeps_the_last_point(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace, rel = self._build(root, count=6000)
            data = research_runs.load_trace(root, rel, mode='full', max_points=1500)
            self.assertEqual(len(data['points']), 1500)
            self.assertEqual(data['points'][-1][0], 2999.5)

    def test_appended_line_becomes_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace, rel = self._build(root, count=1)
            first = research_runs.load_trace(root, rel)
            with trace.open('a', encoding='utf-8') as stream:
                stream.write(json.dumps({'control_step': 1, 'sim_time_s': 0.5,
                                         'q_after_rad': [0, 0, 0, 0, 9]}) + '\n')
            second = research_runs.load_trace(root, rel)
            self.assertEqual(first['total'], 1)
            self.assertEqual(second['total'], 2)
            self.assertGreater(second['live']['file_bytes'], first['live']['file_bytes'])


class GrowthTest(unittest.TestCase):
    def test_growth_is_three_state(self):
        key = '/tmp/does-not-matter'
        research_live._LIVE.clear()
        self.assertIsNone(research_live.observe_growth(key, 100, 10, 0.0))
        self.assertTrue(research_live.observe_growth(key, 200, 20, 1.0))
        self.assertFalse(research_live.observe_growth(key, 200, 20, 7.0))
        self.assertGreater(research_live.growth_rate(key), 0)

    def test_active_trace_uses_mtime_not_lexicographic_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'experiments/discovery/e1/runs/a'
            folder.mkdir(parents=True)
            older = folder / '9.trace.jsonl'
            newer = folder / '10.trace.jsonl'
            write_trace(older, [{'control_step': 0}])
            write_trace(newer, [{'control_step': 0}])
            os.utime(older, (1_000, 1_000))
            os.utime(newer, (2_000, 2_000))
            traces = [older.relative_to(root).as_posix(), newer.relative_to(root).as_posix()]
            self.assertEqual(research_live.active_trace(root, traces),
                             newer.relative_to(root).as_posix())


class CacheTest(unittest.TestCase):
    def setUp(self):
        for cache in (research_live._CATALOG, research_live._RUNS, research_live._TRACE,
                      research_live._PROCESSES, research_live._EPISODES, research_live._ACTIVE):
            cache.clear()
        research_live._LIVE.clear()

    def test_trace_cache_skips_repeat_reads_until_the_file_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'experiments/discovery/e1/runs/a'
            folder.mkdir(parents=True)
            trace = folder / '1.trace.jsonl'
            write_trace(trace, [{'control_step': 0, 'q_after_rad': [0, 0, 0, 0, 1]}])
            rel = trace.relative_to(root).as_posix()
            with mock.patch.object(research_runs, 'load_trace', wraps=research_runs.load_trace) as spy:
                research_live.load_trace_cached(root, rel)
                research_live.load_trace_cached(root, rel)
                self.assertEqual(spy.call_count, 1)
                with trace.open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps({'control_step': 1, 'q_after_rad': [0, 0, 0, 0, 2]}) + '\n')
                research_live.load_trace_cached(root, rel)
                self.assertEqual(spy.call_count, 2)

    def test_catalog_cache_honours_ttl_and_detects_source_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'experiments/discovery').mkdir(parents=True)
            calls = []
            builder = lambda: calls.append(1) or {'n': len(calls)}
            first = research_live.catalog_cached(root, builder)
            second = research_live.catalog_cached(root, builder)
            self.assertEqual(first, second)
            self.assertEqual(len(calls), 1)

            source = root / 'experiments/discovery/e1'
            source.mkdir()
            os.utime(root / 'experiments/discovery', ns=(1_000_000_000, 2_000_000_000))
            research_live.catalog_cached(root, builder)
            self.assertEqual(len(calls), 2)

    def test_digest_cache_recomputes_after_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'PREREG.md'
            path.write_text('one', encoding='utf-8')
            first = research_live.digest_cached(path)
            time.sleep(0.01)
            path.write_text('two-two', encoding='utf-8')
            second = research_live.digest_cached(path)
            self.assertNotEqual(first, second)


class PhysicsProbeTest(unittest.TestCase):
    def setUp(self):
        for cache in (research_live._RUNS, research_live._TRACE, research_live._EPISODES):
            cache.clear()

    def test_probe_reports_writing_while_the_episode_is_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'experiments/discovery/e1/runs/a'
            folder.mkdir(parents=True)
            (folder / 'episodes.jsonl').write_text('', encoding='utf-8')
            trace = folder / '1.trace.jsonl'
            write_trace(trace, [{'control_step': 0, 'q_after_rad': [0, 0, 0, 0, 1]}])
            rel = trace.relative_to(root).as_posix()
            run = {'id': folder.relative_to(root).as_posix(),
                   'episodes': folder.relative_to(root).as_posix() + '/episodes.jsonl',
                   'traces': [rel]}
            probe = research_live.physics_probe(root, run, rel, {'live': {'partial_line': True}})
            self.assertEqual(probe['state'], 'writing')
            self.assertEqual(probe['why'], 'episode_open')

    def test_probe_never_opens_the_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'experiments/discovery/e1/runs/a'
            folder.mkdir(parents=True)
            npz = folder / '1.npz'
            npz.write_bytes(b'0' * (4 * 1024 * 1024))
            (folder / 'episodes.jsonl').write_text(json.dumps({
                'seed': 1, 'physics_path': npz.relative_to(root).as_posix(),
                'physics_sha256': 'a' * 64}) + '\n', encoding='utf-8')
            trace = folder / '1.trace.jsonl'
            write_trace(trace, [{'control_step': 0, 'q_after_rad': [0, 0, 0, 0, 1]}])
            rel = trace.relative_to(root).as_posix()
            run = {'id': folder.relative_to(root).as_posix(),
                   'episodes': folder.relative_to(root).as_posix() + '/episodes.jsonl', 'traces': [rel]}
            started = time.monotonic()
            probe = research_live.physics_probe(root, run, rel, {'live': {'partial_line': False}})
            self.assertEqual(probe['state'], 'ready')
            self.assertLess(time.monotonic() - started, 0.5)


if __name__ == '__main__':
    unittest.main()
