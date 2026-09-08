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
