#!/usr/bin/env python3
"""Trusted App Server launcher; model commands use one native Codex sandbox."""
import os
from pathlib import Path
import sys

WORKSPACES = Path('/home/toluadmin/services/symphony-workspaces/agoge-business-systems')


def validate_workspace(workspace, root=WORKSPACES):
    if (os.geteuid() == 0 or workspace.is_symlink() or workspace.resolve().parent != root.resolve()
            or not workspace.name.startswith('GH-') or not workspace.name[3:].isdigit()):
        raise ValueError('Factory launcher rejected root identity or workspace boundary')
    if (workspace / '.codex/config.toml').exists():
        raise ValueError('Factory launcher rejected repository config overrides; review config before dispatch')
    git = workspace / '.git'
    if git.is_symlink() or not git.is_dir() or (git / 'objects/info/alternates').exists():
        raise ValueError('Factory launcher requires private clone Git metadata')


def worker_environment(private_home):
    env = {name: os.environ[name] for name in ('LANG', 'LC_ALL') if name in os.environ}
    env.update(PATH='/usr/bin:/bin', HOME=str(Path.home()), CODEX_HOME=str(private_home))
    return env


def main():
    state = Path(os.environ.get('AGOGE_FACTORY_STATE', str(Path.home() / '.local/state/agoge-factory')))
    validate_workspace(Path.cwd())
    private_home = state / 'codex-home'
    if not (private_home / 'config.toml').is_file() or not (private_home / 'auth.json').is_symlink():
        raise ValueError('Factory launcher prerequisites absent; run install.py from a permitted host session')
    from policy import matches
    if not matches((private_home / 'config.toml').read_bytes()):
        raise ValueError('Factory launcher policy is stale; reinstall before dispatch')
    if not os.access('/usr/bin/bwrap', os.X_OK):
        raise ValueError('Factory launcher requires /usr/bin/bwrap; restore the approved system executable')
    command = ['/home/toluadmin/.local/bin/codex', '--strict-config', 'app-server']
    os.execve(command[0], command, worker_environment(private_home))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        sys.exit(str(error))
