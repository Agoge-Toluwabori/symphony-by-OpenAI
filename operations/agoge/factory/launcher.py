#!/usr/bin/env python3
"""Trusted App Server launcher. Native Codex profiles sandbox model commands.
Authentication stays in the host process; credentials are never copied or printed.
"""
import os
from pathlib import Path
import sys

factory = Path(__file__).resolve().parent
state = Path(os.environ.get('AGOGE_FACTORY_STATE', str(Path.home() / '.local/state/agoge-factory')))
workspace = Path.cwd().resolve()
root = Path('/home/toluadmin/services/symphony-workspaces/agoge-business-systems').resolve()
if os.geteuid() == 0 or workspace.parent != root or not workspace.name.startswith('GH-'):
    sys.exit('Factory launcher rejected root identity or workspace boundary')
if (workspace / '.codex/config.toml').exists():
    sys.exit('Factory launcher rejected repository config overrides; review config before dispatch')
private_home = state / 'codex-home'
if not (private_home / 'config.toml').is_file() or not (private_home / 'auth.json').is_symlink():
    sys.exit('Factory launcher prerequisites absent; run install.py from a permitted host session')
env = {name: os.environ[name] for name in ('PATH', 'LANG', 'LC_ALL') if name in os.environ}
env.update(HOME=str(Path.home()), CODEX_HOME=str(private_home))
command = ['/home/toluadmin/.local/bin/codex', '--strict-config', 'app-server']
os.execve(command[0], command, env)
