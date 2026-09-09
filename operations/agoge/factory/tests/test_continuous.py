import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'continuous'))
import control as c
import runtime
import publish

class ContinuousTests(unittest.TestCase):
    def setUp(self):
        self.c=json.loads((ROOT/'continuous/project.json').read_text())
        self.item={'content':{'repository':self.c['repository'],'number':240},'status':'Ready','factory Authority':'Autonomous Development','id':'item240'}
        self.issue={'number':240,'state':'open','labels':[]}
    def test_standing_authority_needs_no_batch_or_execution_label(self):
        self.assertTrue(c.eligible(self.c,self.item,self.issue,[]))
        self.assertNotIn('approved',self.c)
    def test_exclusions_and_field_authority_fail_closed(self):
        for label in c.EXCLUDED:
            self.assertFalse(c.eligible(self.c,self.item,dict(self.issue,labels=[label]),[]))
        for field,value in [('status','Blocked'),('factory Authority','Owner Gate'),('factory Authority','Prohibited'),('factory Authority','Authorized'),('task Type','Planning')]:
            item=dict(self.item);item[field]=value;self.assertFalse(c.eligible(self.c,item,self.issue,[]))
        item=copy.deepcopy(self.item);item['content']['repository']='unrelated/repo';self.assertFalse(c.eligible(self.c,item,self.issue,[]))
        self.assertFalse(c.eligible(self.c,self.item,dict(self.issue,state='closed'),[]))
        for n in (234,235,236):self.assertFalse(c.eligible(self.c,self.item,dict(self.issue,number=n),[]))
    def test_dependencies_and_withdrawn_tasks(self):
        dep={'number':239,'state':'closed','state_reason':'completed','repository_url':'https://api.github.com/repos/'+self.c['repository']}
        self.assertTrue(c.eligible(self.c,self.item,self.issue,[dep]))
        for changed in ({'state':'open'},{'state_reason':'not_planned'},{'labels':['human-review']},{'repository_url':'https://api.github.com/repos/other/repo'}):
            self.assertFalse(c.eligible(self.c,self.item,self.issue,[dict(dep,**changed)]))
        self.assertFalse(c.eligible(self.c,dict(self.item,**{'depends On':'unverified predecessor'}),self.issue,[]))
    def test_blocked_does_not_stall_unrelated_and_empty_queue_is_normal(self):
        other=copy.deepcopy(self.item);other['content']['number']=241
        def api(config,path,*args):return dict(self.issue,number=int(path.split('/')[1]),labels=['symphony-blocked'] if '240' in path else [])
        with patch.object(c,'api',side_effect=api),patch.object(c,'pages',return_value=[]):
            self.assertEqual(c.select(self.c,[self.item,other])['number'],241)
            self.assertIsNone(c.select(self.c,[self.item,other],active={'number':240}))
            self.assertIsNone(c.select(self.c,[]))
    def test_refs_and_security_paths(self):
        self.assertTrue(c.permitted_ref(self.c,'refs/heads/symphony/GH-240-abc'))
        for ref in ['refs/heads/main','refs/heads/develop','refs/tags/v1','refs/heads/symphony/GH-240-a:main','refs/heads/other']:
            self.assertFalse(c.permitted_ref(self.c,ref))
        for kw in ({'force':True},{'delete':True}):self.assertFalse(c.permitted_ref(self.c,'refs/heads/symphony/GH-240-a',**kw))
        for name in ['.github/workflows/steal.yml','.githooks/pre-push','AGENTS.md','.env.production','x/private.pem']:
            self.assertFalse(c.safe_changes(self.c,[name]))
        self.assertTrue(c.safe_changes(self.c,['apps/web/app/page.tsx','tests/integration/example.test.ts']))
    def test_latest_required_ci_cannot_be_overridden_by_old_success(self):
        name=self.c['required_checks'][0]
        self.assertFalse(c.checks_pass(self.c,[],[]))
        self.assertTrue(c.checks_pass(self.c,[{'context':name,'state':'success'}],[]))
        self.assertFalse(c.checks_pass(self.c,[{'context':name,'state':'failure'},{'context':name,'state':'success'}],[]))
    def test_dependency_requests_cannot_execute_scripts_git_or_arbitrary_urls(self):
        self.assertTrue(runtime.manifests_safe({'package.json':{'dependencies':{'react':'19.2.4'}}}))
        for version in ['git+ssh://host/repo','https://billing.example/evil','file:/home/toluadmin/.codex','npm:other@1']:
            self.assertFalse(runtime.manifests_safe({'package.json':{'dependencies':{'bad':version}}}))
        self.assertFalse(runtime.manifests_safe({'package.json':{'pnpm':{'hooks':'evil'}}}))
    def test_request_symlink_and_oversize_are_denied(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'target').write_text('{}');(p/'request').symlink_to(p/'target')
            with self.assertRaises(ValueError):runtime.read_request(p,'request')
            (p/'request').unlink();(p/'request').write_text('x'*8193)
            with self.assertRaises(ValueError):runtime.read_request(p,'request')
    def test_concurrency_and_merge_gate_cannot_be_weakened(self):
        for change in ({'max_concurrency':2},{'integration_branch':'main'},{'required_checks':[]},{'merge_method':'rebase'}):
            with self.assertRaises(ValueError):c.validate(dict(self.c,**change))
    def test_prohibited_push_never_invokes_git(self):
        with patch.object(publish,'git') as run:
            for branch in ['main','develop','refs/tags/v1','symphony/GH-240-x:main']:
                with self.assertRaises(ValueError):publish.push(self.c,Path('/synthetic'), 'a'*40,branch)
            run.assert_not_called()
    def test_installer_continuous_mode_keeps_containment_and_rollback(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('continuous_installer',ROOT/'install.py')
        install=importlib.util.module_from_spec(spec);spec.loader.exec_module(install)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);auth=p/'auth';auth.write_text('synthetic')
            install.install(p/'state',p/'units',auth,control=False,continuous=True)
            config=json.loads((p/'state/batch.json').read_text())
            self.assertEqual(config['mode'],'continuous');self.assertTrue(config['execution_enabled'])
            self.assertIn('factory-dispatch',(p/'state/WORKFLOW.md').read_text())
            unit=(p/'units/symphony-agoge.service').read_text()
            for setting in ('Restart=on-failure','NoNewPrivileges=yes','LockPersonality=yes','RestrictSUIDSGID=yes'):self.assertIn(setting,unit)
            self.assertIn('[features.network_proxy]',(p/'state/codex-home/config.toml').read_text())
            install.rollback(p/'state',control=False)
            self.assertEqual(auth.read_text(),'synthetic')
    def test_continuous_attestation_rechecks_project_authority_and_dependencies(self):
        sys.path.insert(0,str(ROOT));import attestation
        props='ActiveState=active\nUnitFileState=enabled\nControlGroup=/\nInvocationID=fixture\nRestart=on-failure\nNoNewPrivileges=yes\nLockPersonality=yes\nRestrictSUIDSGID=yes\n'
        import os
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'INVOCATION_ID':'fixture'}):
            state=Path(d);(state/'codex-home').mkdir();(state/'codex-home/config.toml').write_bytes(attestation.policy.render())
            (state/'batch.json').write_text(json.dumps(self.c));(state/'lease.json').write_text(json.dumps({'number':240,'item_id':'item240','nonce':'nonce'}))
            with patch.object(attestation.subprocess,'check_output',return_value=props),patch.object(c,'snapshot',return_value=[self.item]),patch.object(c,'api',return_value=self.issue),patch.object(c,'pages',return_value=[]):
                proof=attestation.service_context(state)
                self.assertEqual(proof['issue_id'],'240');self.assertTrue(proof['batch_stop']['service_enabled'])
                self.assertEqual(proof['preflight']['service_enablement'],'verified')
                self.item['factory Authority']='Owner Gate'
                with self.assertRaises(ValueError):attestation.service_context(state)
    def test_registry_proxy_rejects_provider_and_billing_targets_before_connect(self):
        import registry_proxy
        self.assertEqual(registry_proxy.target('registry.npmjs.org:443'),('registry.npmjs.org',443))
        for route in ['api.vercel.com:443','api.github.com:443','billing.example:443','registry.npmjs.org.evil:443','registry.npmjs.org:80','127.0.0.1:443']:
            with self.assertRaises(ValueError):registry_proxy.target(route)
    def test_project_blocked_revokes_dispatch_even_without_a_label(self):
        import attestation,os
        with tempfile.TemporaryDirectory() as d:
            state=Path(d);(state/'batch.json').write_text(json.dumps(self.c));(state/'lease.json').write_text(json.dumps({'number':240,'item_id':'item240','nonce':'n'}))
            item=dict(self.item,status='Blocked')
            with patch.object(attestation.subprocess,'check_output',return_value=''),patch.object(c,'snapshot',return_value=[item]),patch.object(c,'api',return_value=self.issue),patch.object(c,'pages',return_value=[]):
                with self.assertRaisesRegex(ValueError,'revoked'):attestation.service_context(state)

    def test_controller_waits_for_live_worker_and_preserves_bounded_failure(self):
        import os
        with patch.dict(os.environ,{'AGOGE_FACTORY_STATE':'/tmp/synthetic','INVOCATION_ID':'fixture'}):
            import supervisor
        with tempfile.TemporaryDirectory() as d:
            state=Path(d);lease={'number':240,'item_id':'item240','nonce':'n','attempt':3}
            c.write(state/'lease.json',lease);c.write(state/'attempt-fixture-n.json',{'pid':os.getpid()})
            with patch.object(supervisor,'STATE',state),patch.dict(os.environ,{'INVOCATION_ID':'fixture'}),patch.object(supervisor.publish,'deliver') as deliver,patch.object(c,'remove_label'),patch.object(c,'api',return_value=self.issue),patch.object(supervisor,'block') as block:
                supervisor.tick(self.c,[]);deliver.assert_not_called();block.assert_not_called()
                c.write(state/'attempt-fixture-n.json',{})
                supervisor.tick(self.c,[]);block.assert_called_once()
                self.assertIn('Bounded technical recovery exhausted',block.call_args.args[2])

    def test_idle_controller_keeps_polling_and_records_health(self):
        import os
        with patch.dict(os.environ,{'AGOGE_FACTORY_STATE':'/tmp/synthetic'}):import supervisor
        with tempfile.TemporaryDirectory() as d,patch.object(supervisor,'STATE',Path(d)),patch.object(c,'snapshot',return_value=[]),patch.object(c,'pages',return_value=[]):
            supervisor.tick(self.c,[]);supervisor.tick(self.c,[])
            health=json.loads((Path(d)/'continuous-health.json').read_text())
            self.assertEqual(health['status'],'idle');self.assertIsNone(health['selected'])
