import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('workspace', Path(__file__).resolve().parents[1] / 'workspace.py')
w = importlib.util.module_from_spec(spec); spec.loader.exec_module(w)

class WorkspaceTests(unittest.TestCase):
    def test_edit_build_test_commit_and_archive_preserves_history(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); task = root / 'GH-235'; task.mkdir()
            def git(*args):
                return subprocess.check_output(['git', '-C', str(task), *args], stderr=subprocess.DEVNULL, text=True).strip()
            git('init', '-q')
            # Control-plane test fixture, never application implementation.
            (task / 'fixture.txt').write_text('synthetic\n')
            self.assertEqual((task / 'fixture.txt').read_text(), 'synthetic\n')
            (task / 'build.txt').write_text((task / 'fixture.txt').read_text().upper())
            self.assertEqual((task / 'build.txt').read_text(), 'SYNTHETIC\n')
            git('add', '.')
            git('-c', 'user.name=Factory Test', '-c', 'user.email=factory@localhost', 'commit', '-qm', 'Synthetic control-plane fixture')
            sha = git('rev-parse', 'HEAD')
            (task / 'dirty-evidence.txt').write_text('retain')
            archived = w.archive_attempt(task, root)
            self.assertEqual(list(task.iterdir()), [])
            self.assertEqual((archived / 'dirty-evidence.txt').read_text(), 'retain')
            self.assertEqual(subprocess.check_output(['git', '-C', str(archived), 'rev-parse', 'HEAD'], text=True).strip(), sha)
    def test_sibling_and_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'root'; root.mkdir()
            other = Path(d) / 'GH-236'; other.mkdir()
            alias = root / 'GH-235'; alias.symlink_to(other, target_is_directory=True)
            for path in (other, alias):
                with self.assertRaises(ValueError): w.archive_attempt(path, root)
    def test_invalid_workspace_rejected_and_empty_workspace_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); task = root / 'GH-235'; task.mkdir()
            self.assertIsNone(w.archive_attempt(task, root))
            bad = root / 'main'; bad.mkdir()
            with self.assertRaises(ValueError): w.archive_attempt(bad, root)
