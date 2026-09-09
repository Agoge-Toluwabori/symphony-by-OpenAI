import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import launcher
import policy


class LauncherTests(unittest.TestCase):
    def test_environment_ignores_host_path_and_credentials(self):
        with patch.dict('os.environ', {'PATH': '/host/custom/bin', 'GH_TOKEN': 'synthetic',
                                      'OPENAI_API_KEY': 'synthetic', 'LD_PRELOAD': 'bad'}, clear=True):
            env = launcher.worker_environment(Path('/private'))
        self.assertEqual(env['PATH'], '/usr/bin:/bin')
        self.assertEqual(set(env), {'PATH', 'HOME', 'CODEX_HOME'})

    def test_private_git_and_workspace_boundary_required(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); task = root/'GH-236'; task.mkdir()
            with self.assertRaises(ValueError): launcher.validate_workspace(task, root)
            (task/'.git').mkdir()
            launcher.validate_workspace(task, root)
            (task/'.git/objects/info').mkdir(parents=True)
            (task/'.git/objects/info/alternates').write_text('/unrelated')
            with self.assertRaises(ValueError): launcher.validate_workspace(task, root)
            with self.assertRaises(ValueError): launcher.validate_workspace(root, root)

    def test_native_policy_retains_containment_and_pins_system_path(self):
        config, _ = policy.split(policy.render())
        self.assertEqual(config['approval_policy'], 'never')
        self.assertEqual(config['shell_environment_policy']['inherit'], 'none')
        self.assertEqual(config['shell_environment_policy']['set'], {'PATH': '/usr/bin:/bin'})
        profile = config['permissions']['factory-canary']
        self.assertFalse(profile['network']['enabled'])
        self.assertEqual(profile['filesystem'][':root'], 'deny')
        self.assertEqual(profile['filesystem'][str(policy.CODEX.resolve())], 'read')
        self.assertEqual(profile['filesystem'][':workspace_roots']['.git'], 'write')
        self.assertNotIn('.agents', profile['filesystem'][':workspace_roots'])
        self.assertNotIn('.codex', profile['filesystem'][':workspace_roots'])
