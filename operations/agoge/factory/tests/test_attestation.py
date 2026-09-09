import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import attestation as a
spec=importlib.util.spec_from_file_location('factory_queue',ROOT/'queue.py')
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)

class AttestationTests(unittest.TestCase):
    def test_field_diagnostics_and_fail_closed(self):
        import contextlib,io
        output=io.StringIO()
        with contextlib.redirect_stderr(output):
            with self.assertRaises(ValueError): a.check({'issue_id':'verified','service':'missing','workspace':'invalid'})
        self.assertEqual([json.loads(s)['status'] for s in output.getvalue().splitlines()],['verified','missing','invalid'])

    def test_private_dispatch_receipt_rejects_second_launch(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d);workspace=a.policy.WORKSPACES/'GH-236'
            context={'issue_id':'236','invocation_id':'fixture'}
            with patch.object(a,'service_context',return_value=context):
                result=a.dispatch(state,workspace)
                self.assertEqual(result['workspace'],str(workspace))
                with self.assertRaises(FileExistsError): a.dispatch(state,workspace)
                with self.assertRaises(ValueError): a.dispatch(state,a.policy.WORKSPACES/'GH-235')

    def test_failed_canary_recovers_only_after_current_preflight_and_once(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,{'INVOCATION_ID':'fixture'}):
            state=Path(d)
            batch=json.loads((ROOT/'canary-batch.json').read_text());batch['execution_enabled']=True
            issues={236:{'state':'open','labels':['symphony-blocked'],'dependencies_verified':True},235:{'state':'open','labels':[]}}
            self.assertIsNone(q.select(batch,issues))
            with self.assertRaises(FileNotFoundError): q.recover_canary(batch,issues,state)
            proof={'repair':a.REPAIR,'invocation_id':'fixture','preflight':{'native_policy':'verified'}}
            (state/'service-preflight.json').write_text(json.dumps(proof))
            with patch.object(q,'pages',return_value=[{'body':'CANARY FAILED parent_uid_mapping {"1000":0} errno=null'}]),patch.object(q,'gh') as gh:
                q.recover_canary(batch,issues,state)
                self.assertEqual(q.select(batch,issues),236)
                self.assertEqual(gh.call_count,2)
                self.assertTrue(all('/issues/236/' in call.args[0] for call in gh.call_args_list))
                q.recover_canary(batch,issues,state)
                self.assertEqual(gh.call_count,2)
            self.assertEqual(issues[235]['labels'],[])

    def test_unknown_blocker_or_gate_is_never_cleared(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,{'INVOCATION_ID':'fixture'}):
            state=Path(d)
            batch=json.loads((ROOT/'canary-batch.json').read_text());batch['execution_enabled']=True
            proof={'repair':a.REPAIR,'invocation_id':'fixture','preflight':{'native_policy':'verified'}}
            (state/'service-preflight.json').write_text(json.dumps(proof))
            issues={236:{'state':'open','labels':['symphony-blocked'],'dependencies_verified':True}}
            with patch.object(q,'pages',return_value=[{'body':'Different external blocker'}]),patch.object(q,'gh') as gh:
                with self.assertRaises(ValueError): q.recover_canary(batch,issues,state)
                gh.assert_not_called()
                issues[236]['labels'].append('authority:owner-gate')
                with self.assertRaises(ValueError): q.recover_canary(batch,issues,state)

    def test_specific_failed_review_is_reopened_but_acceptance_is_not(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,{'INVOCATION_ID':'fixture'}):
            state=Path(d)
            batch=json.loads((ROOT/'canary-batch.json').read_text());batch['execution_enabled']=True
            proof={'repair':a.REPAIR,'invocation_id':'fixture','preflight':{'native_policy':'verified'}}
            (state/'service-preflight.json').write_text(json.dumps(proof))
            issue={'state':'open','labels':['symphony-blocked','human-review','accepted'],'dependencies_verified':True}
            with patch.object(q,'pages',return_value=[{'body':'CANARY FAILED parent_uid_mapping {"1000":0} errno=null'}]),patch.object(q,'gh') as gh:
                with self.assertRaises(ValueError):q.recover_canary(batch,{236:issue},state)
                gh.assert_not_called()
                issue['labels'].remove('accepted')
                q.recover_canary(batch,{236:issue},state)
                self.assertEqual(gh.call_count,3)
                self.assertEqual(issue['labels'],[])
                self.assertEqual(q.select(batch,{236:issue}),236)

    def test_safe01_is_an_exact_scope_not_a_general_batch_override(self):
        batch=json.loads((ROOT/'batch.json').read_text())
        self.assertTrue(a.approved_task(batch))
        batch['tasks'][0]['number']=237
        self.assertFalse(a.approved_task(batch))
        batch=json.loads((ROOT/'batch.json').read_text())
        batch['tasks'][0]['dependencies']=[]
        self.assertFalse(a.approved_task(batch))

    def test_safe01_requires_closed_and_accepted_canary(self):
        batch=json.loads((ROOT/'batch.json').read_text());batch['execution_enabled']=True
        issues={235:{'state':'open','labels':[],'dependencies_verified':True},236:{'state':'closed','labels':['human-review']}}
        self.assertIsNone(q.select(batch,issues))
        issues[236]['labels']=['accepted']
        self.assertEqual(q.select(batch,issues),235)
        issues[235]['labels']=['human-review']
        self.assertIsNone(q.select(batch,issues))
