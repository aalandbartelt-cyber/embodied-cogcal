import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('research_runs', Path(__file__).with_name('research_runs.py'))
runs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runs)

class RunTest(unittest.TestCase):
    def test_reports_unique_observed_seeds_and_partial_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); p=root/'experiments/discovery/e1/runs/a'; p.mkdir(parents=True)
            (p/'contract.json').write_text(json.dumps({'seeds':[1,2,3], 'yaw_deg':15}))
            (p/'episodes.jsonl').write_text('{"seed":1,"task_success":true}\n{"seed":2,"task_success":false}\n{"seed":2,"task_success":true}\n{"seed":3')
            row=runs.discover_runs(root,'e1')['runs'][0]
            self.assertEqual((row['completed'],row['success'],row['failure']), (2,1,1))
            self.assertEqual(row['duplicates'],1)
            self.assertEqual(row['planned'],3)
            self.assertTrue(row['partial'])
            self.assertEqual(row['conditions']['yaw_deg'],15)
    def test_trace_uses_real_joint_values_and_ignores_unfinished_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); p=root/'experiments/discovery/e1/runs/a'; p.mkdir(parents=True)
            f=p/'1.trace.jsonl'; f.write_text('{"control_step":0,"sim_time_s":0.1,"q_after_rad":[0,0,0,0,1],"command_rad":[0,0,0,0,2]}\n{"control_step":1')
            data=runs.load_trace(root, f.relative_to(root).as_posix())
            self.assertEqual(data['points'], [[0.1,1,2]])
            self.assertTrue(data['partial'])
    def test_appended_complete_trace_is_visible_on_next_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); p=root/'experiments/discovery/e1/runs/a'; p.mkdir(parents=True)
            f=p/'1.trace.jsonl'
            f.write_text('{"control_step":0,"q_after_rad":[0,0,0,0,1]}\n')
            rel=f.relative_to(root).as_posix()
            self.assertEqual(runs.load_trace(root,rel)['total'],1)
            with f.open('a') as stream:
                stream.write('{"control_step":1,"q_after_rad":[0,0,0,0,2]}\n')
            self.assertEqual(runs.load_trace(root,rel)['total'],2)

    def test_empty_episode_index_and_growing_trace_are_visible_before_first_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path=root/'experiments/discovery/e1/runs/live'; path.mkdir(parents=True)
            (path/'episodes.jsonl').write_text('')
            (path/'contract.json').write_text('{"seeds":[123]}')
            trace=path/'123.trace.jsonl'
            trace.write_text('{"control_step":0,"q_after_rad":[0,0,0,0,1]}\n')
            row=runs.discover_runs(root,'e1')['runs'][0]
            self.assertEqual((row['completed'], row['planned']), (0, 1))
            self.assertEqual(row['traces'], [trace.relative_to(root).as_posix()])
            with trace.open('a') as stream:
                stream.write('{"control_step":1,"q_after_rad":[0,0,0,0,2]}\n')
            self.assertEqual(runs.load_trace(root,row['traces'][0])['total'], 2)

    def test_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(runs.load_trace(Path(tmp),'../escape.trace.jsonl'))
            self.assertIsNone(runs.discover_runs(Path(tmp),'../escape'))

if __name__=='__main__': unittest.main()
