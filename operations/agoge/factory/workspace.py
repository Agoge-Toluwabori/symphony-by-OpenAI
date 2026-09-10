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
    import json
    state=Path(os.environ.get('AGOGE_FACTORY_STATE',str(Path.home()/'.local/state/agoge-factory')))
    config=json.loads((state/'batch.json').read_text()) if (state/'batch.json').exists() else {}
    continuous=config.get('mode')=='continuous'
    if continuous:
        lease=json.loads((state/'lease.json').read_text())
        expected=Path(config['workspace_root'])/('GH-'+str(lease['number']))
        if Path.cwd()!=expected or Path.cwd().is_symlink():raise ValueError('Unauthorized workspace; no files changed')
    if continuous and (Path.cwd()/'.git').is_dir():
        import sys
        sys.path.insert(0,str(Path(__file__).parent/'continuous'))
        import publish
        # Retry this issue in its own retained checkout; never discard dirty repair work.
        lease=json.loads((state/'lease.json').read_text())
        if Path.cwd().name != 'GH-'+str(lease['number']):raise ValueError('Wrong retry workspace')
        publish.fetch(config,Path.cwd(),config['integration_branch'])
        logs=sorted(state.glob('ci-*.log'),key=lambda p:p.stat().st_mtime)
        if logs:
            target=Path.cwd()/'.factory-runtime';target.mkdir(exist_ok=True)
            (target/'last-ci.log').write_bytes(logs[-1].read_bytes())
        raise SystemExit(0)
    archive = archive_attempt(Path.cwd(), Path(config.get('workspace_root',str(DEFAULT_ROOT))))
    hook = Path(__file__).resolve().parents[1] / 'workspace-create.sh'
    if continuous:
        import sys
        sys.path.insert(0,str(Path(__file__).parent/'continuous'))
        import control,publish
        control.validate(config)
        lease=json.loads((state/'lease.json').read_text())
        if Path.cwd()!=Path(config['workspace_root'])/('GH-'+str(lease['number'])):raise ValueError('Invalid scoped workspace')
        control.command(['gh','repo','clone',config['repository'],'.','--','--branch',config['integration_branch'],'--single-branch'])
        branch='symphony/GH-'+str(lease['number'])+'-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        publish.git(Path.cwd(),'switch','-c',branch)
        publish.git(Path.cwd(),'config','user.name','Agoge Symphony')
        publish.git(Path.cwd(),'config','user.email','symphony@localhost')
        publish.git(Path.cwd(),'remote','set-url','--push','origin','HOST-CONTROLLED-PUBLICATION-ONLY')
    else:
        subprocess.run(['/bin/bash', str(hook)], check=True)
    if continuous:
        import sys
        sys.path.insert(0,str(Path(__file__).parent/'continuous'))
        import runtime
        runtime.prepare(config,Path.cwd())
    if Path.cwd().name == "GH-236":
        probe = Path(__file__).resolve().with_name("canary-probe.py")
        (Path.cwd() / "factory-containment-probe.py").write_bytes(probe.read_bytes())
