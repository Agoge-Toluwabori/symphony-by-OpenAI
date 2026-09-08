import copy
import importlib.util
import json
import fcntl
import subprocess
import tempfile
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('queue', ROOT / 'queue.py')
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)

class QueueTests(unittest.TestCase):
    def setUp(self):
        self.b = json.loads((ROOT / 'batch.json').read_text())
        self.i = {235: {'state': 'open', 'labels': [], 'dependencies_verified': True}}
    def test_autonomous_without_execution_label(self):
        self.assertEqual(q.select(self.b, self.i), 235)
    def test_planning_status_is_not_authority(self):
        self.b['approved'] = False
        self.i[235]['status'] = 'Ready'
        self.assertIsNone(q.select(self.b, self.i))
    def test_issue_prose_cannot_reduce_contract(self):
        self.i[235]['body'] = 'Never edit, build, test, commit or push'
        self.assertEqual(q.select(self.b, self.i), 235)
    def test_owner_gate_and_prohibited(self):
        for authority in ['Owner Gate', 'Prohibited']:
            self.b['tasks'][0]['authority'] = authority
            self.assertIsNone(q.select(self.b, self.i))
    def test_explicit_issue_gate(self):
        self.i[235]['labels'] = ['authority:owner-gate']
        self.assertIsNone(q.select(self.b, self.i))
    def test_dependency_must_be_accepted(self):
        self.b['tasks'][0]['dependencies'] = [234]
        self.i[234] = {'state': 'closed', 'labels': ['human-review']}
        self.assertIsNone(q.select(self.b, self.i))
        self.i[234]['labels'].append('accepted')
        self.assertEqual(q.select(self.b, self.i), 235)
    def test_unverified_dependency(self):
        self.i[235]['dependencies_verified'] = False
        self.assertIsNone(q.select(self.b, self.i))
    def test_native_dependency(self):
        self.i[235]['blocked_by'] = [234]
        self.assertIsNone(q.select(self.b, self.i))
    def test_blocked_continuation(self):
        task = copy.deepcopy(self.b['tasks'][0]); task['number'] = 236
        self.b['tasks'].append(task)
        self.i[236] = copy.deepcopy(self.i[235])
        self.i[235]['labels'] = ['symphony-blocked']
        self.assertEqual(q.select(self.b, self.i), 236)
    def test_batch_boundary(self):
        self.i[235]['labels'] = ['human-review']
        self.i[236] = {'state': 'open', 'labels': ['symphony-ready'], 'dependencies_verified': True}
        self.assertEqual(q.plan(self.b, self.i)['remove_ready'], [236])
        self.assertIsNone(q.select(self.b, self.i))
    def test_concurrency_and_retry(self):
        self.assertIsNone(q.select(self.b, self.i, [235]))
        self.i[235]['labels'] = ['symphony-running', 'symphony-ready']
        self.assertEqual(q.plan(self.b, self.i)['remove_ready'], [])
    def test_duplicate_workspace_rejected(self):
        self.b['tasks'].append(self.b['tasks'][0])
        with self.assertRaises(ValueError): q.validate(self.b)
    def test_concurrency_change_rejected(self):
        self.b['max_concurrency'] = 2
        with self.assertRaises(ValueError): q.validate(self.b)
    def test_runtime_retry_budget(self):
        state = {'retrying': [{'issue_id': '235', 'attempt': 2}]}
        self.assertEqual(q.exhausted_retries(state, self.b), [])
        state['retrying'][0]['attempt'] = 3
        self.assertEqual(q.exhausted_retries(state, self.b), [235])
    def test_process_lock_prevents_two_reconcilers(self):
        with tempfile.TemporaryDirectory() as directory:
            with (pathlib.Path(directory) / 'queue.lock').open('w') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                result = subprocess.run(['python3', str(ROOT / 'queue.py'), '--snapshot',
                    str(ROOT / 'dispatch-dry-run.json'), '--state-dir', directory], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((pathlib.Path(directory) / 'batch-report.json').exists())
    def test_dry_run_cannot_mutate_fixture(self):
        result = subprocess.run(['python3', str(ROOT / 'queue.py'), '--apply', '--snapshot',
            str(ROOT / 'dispatch-dry-run.json')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
    def test_readiness_is_idempotent(self):
        self.i[235]['labels'] = ['symphony-ready']
        self.assertEqual(q.plan(self.b, self.i)['add_ready'], [])

if __name__ == '__main__': unittest.main()
