#!/usr/bin/env python3
"""Trusted before_run hook: archive prior attempt, then make a fresh clone."""
import datetime
import os
from pathlib import Path
import re
import subprocess
import uuid

DEFAULT_ROOT = Path('/home/toluadmin/services/symphony-workspaces/agoge-business-systems')

def archive_attempt(workspace, root):
    workspace, root = Path(workspace), Path(root)
    if workspace.is_symlink() or workspace.resolve().parent != root.resolve():
        raise ValueError('Workspace must be a direct non-symlink child of root')
    if not re.fullmatch(r'GH-[1-9][0-9]*', workspace.name):
        raise ValueError('Invalid issue workspace')
    entries = list(workspace.iterdir())
    if not entries:
        return None
    archives = root / '.factory-archives'
    if archives.is_symlink():
        raise ValueError('Archive root cannot be a symlink')
    archives.mkdir(mode=0o700, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    archive = archives / f'{workspace.name}-{stamp}-{uuid.uuid4().hex}'
    archive.mkdir(mode=0o700)
    for entry in entries:
        entry.rename(archive / entry.name)  # preserves symlinks, Git objects and dirty evidence
    return archive

if __name__ == '__main__':
    archive_attempt(Path.cwd(), DEFAULT_ROOT)
    hook = Path(__file__).resolve().parents[1] / 'workspace-create.sh'
    subprocess.run(['/bin/bash', str(hook)], check=True)
