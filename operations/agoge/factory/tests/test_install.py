import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('installer',Path(__file__).resolve().parents[1]/'install.py')
i=importlib.util.module_from_spec(spec);spec.loader.exec_module(i)

class InstallerTests(unittest.TestCase):
    def test_idempotent_install_and_rollback_preserve_original_service_and_auth(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);state=root/'state';units=root/'units';units.mkdir()
            auth=root/'auth.json';auth.write_text('synthetic-fixture')
            unit=units/'symphony-agoge.service';unit.write_text('original service')
            first=i.install(state,units,auth,control=False)
            self.assertEqual(i.install(state,units,auth,control=False),first)
            self.assertEqual(auth.read_text(),'synthetic-fixture')
            i.rollback(state,control=False)
            self.assertEqual(unit.read_text(),'original service')
            self.assertEqual(auth.read_text(),'synthetic-fixture')
            self.assertFalse((state/'codex-home/config.toml').exists())
    def test_canary_install_selects_only_dedicated_issue(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);auth=root/"auth.json";auth.write_text("fixture")
            i.install(root/"state",root/"units",auth,control=False,canary=True)
            batch=json.loads((root/"state/batch.json").read_text())
            self.assertEqual([t["number"] for t in batch["tasks"]],[236])
            self.assertTrue(batch["execution_enabled"])
            self.assertIn("agent_issue_numbers: [236]",(root/"state/WORKFLOW.md").read_text())
    def test_missing_auth_fails_before_any_change(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaises(ValueError): i.install(root/'state',root/'units',root/'missing',control=False)
            self.assertEqual(list(root.iterdir()),[])
    def test_modified_service_is_preserved_on_reinstall_and_rollback(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);auth=root/'auth.json';auth.write_text('fixture')
            state=root/'state';units=root/'units'
            i.install(state,units,auth,control=False)
            unit=units/'symphony-agoge.service';unit.write_text('owner edit')
            with self.assertRaises(ValueError): i.install(state,units,auth,control=False)
            with self.assertRaises(ValueError): i.rollback(state,control=False)
            self.assertEqual(unit.read_text(),'owner edit')
    def test_codex_trust_metadata_survives_reinstall_and_is_archived_on_rollback(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);auth=root/'auth.json';auth.write_text('fixture')
            state=root/'state';units=root/'units'
            i.install(state,units,auth,control=False)
            config=state/'codex-home/config.toml'
            config.write_text(config.read_text()+'\n[projects."/home/toluadmin/services/symphony-workspaces/agoge-business-systems/GH-236"]\ntrust_level="trusted"\n')
            before=config.read_bytes()
            record=i.install(state,units,auth,control=False)
            self.assertIn(b'trust_level = "trusted"',config.read_bytes())
            self.assertIn(before.hex(), [r.get(str(config)) for r in record['revisions']])
            i.rollback(state,control=False)
            import json
            archived=json.loads((state/'installation.rolled-back.json').read_text())
            self.assertIn('trust_level',bytes.fromhex(archived['revisions'][-1][str(config)]).decode())

    def test_security_policy_drift_is_not_treated_as_trust_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);auth=root/'auth.json';auth.write_text('fixture')
            state=root/'state';units=root/'units'
            i.install(state,units,auth,control=False)
            config=state/'codex-home/config.toml'
            config.write_text(config.read_text().replace('apps = false', 'apps = true'))
            with self.assertRaises(ValueError): i.install(state,units,auth,control=False)
            with self.assertRaises(ValueError): i.rollback(state,control=False)

    def test_legacy_trust_only_drift_is_migrated_with_original_retained(self):
        import hashlib
        import json
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);auth=root/'auth.json';auth.write_text('fixture')
            state=root/'state';units=root/'units'
            record=i.install(state,units,auth,control=False)
            config=state/'codex-home/config.toml'
            legacy=(i.FACTORY/'native-policy.before-launcher-repair.toml').read_bytes()
            record.pop('policy_base')
            record['installed'][str(config)]=hashlib.sha256(legacy).hexdigest()
            (state/'installation.json').write_text(json.dumps(record))
            config.write_bytes(legacy+b'\n[projects."/home/toluadmin/services/symphony-workspaces/agoge-business-systems/GH-236"]\ntrust_level="trusted"\n')
            previous=config.read_bytes()
            record=i.install(state,units,auth,control=False,canary=True)
            self.assertTrue(i.native_policy.matches(config.read_bytes()))
            self.assertEqual(record['revisions'][-1][str(config)],previous.hex())
    def test_repeated_rollback_keeps_prior_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);auth=root/'auth.json';auth.write_text('fixture')
            state=root/'state';units=root/'units'
            i.install(state,units,auth,control=False)
            i.rollback(state,control=False)
            original=(state/'installation.rolled-back.json').read_bytes()
            i.install(state,units,auth,control=False)
            i.rollback(state,control=False)
            self.assertEqual((state/'installation.rolled-back.json').read_bytes(),original)
            self.assertEqual(len(list(state.glob('installation.rolled-back*.json'))),2)

    def test_safe01_install_preserves_native_policy_and_selects_only_235(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);auth=root/'auth.json';auth.write_text('fixture')
            state=root/'state';units=root/'units'
            i.install(state,units,auth,control=False,canary=True)
            policy=(state/'codex-home/config.toml').read_bytes()
            i.install(state,units,auth,control=False,safe01=True)
            batch=json.loads((state/'batch.json').read_text())
            self.assertTrue(batch['execution_enabled'])
            self.assertEqual([t['number'] for t in batch['tasks']],[235])
            self.assertEqual(batch['tasks'][0]['dependencies'],[236])
            self.assertEqual((state/'codex-home/config.toml').read_bytes(),policy)
            self.assertIn('agent_issue_numbers: [235]',(state/'WORKFLOW.md').read_text())
            with self.assertRaises(ValueError):i.install(state,units,auth,control=False,canary=True,safe01=True)
