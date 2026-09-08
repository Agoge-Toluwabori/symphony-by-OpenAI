#!/usr/bin/env python3
"""Idempotent own-file installation with a retained rollback manifest. Never starts delivery."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import shutil
import tomllib

FACTORY = Path(__file__).resolve().parent

def atomic(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        temporary = Path(f.name)
        f.write(data)
        os.fchmod(f.fileno(), 0o600)
    temporary.replace(path)

def install(state, units, auth, control=True, canary=False):
    if os.geteuid() == 0: raise ValueError('Run as non-root toluadmin')
    for name in ('launcher.py', 'native-policy.toml', 'canary-batch.json', 'queue.py', 'workspace.py', 'canary-probe.py'):
        if not (FACTORY/name).is_file(): raise ValueError('Required component missing: '+name)
    policy_config=tomllib.loads((FACTORY/'native-policy.toml').read_text())
    if policy_config.get('default_permissions') != 'factory-canary' or 'sandbox_mode' in policy_config:
        raise ValueError('Native profile configuration is missing or mixed with legacy sandbox settings')
    if control:
        for executable in ('python3','git','gh','flock','systemctl'):
            if not shutil.which(executable): raise ValueError('Required executable absent: '+executable)
        for path in ('/home/toluadmin/.local/bin/codex','/usr/bin/bwrap'):
            if not os.access(path,os.X_OK): raise ValueError('Required executable unavailable: '+path)
        if not Path('/home/toluadmin/.config/symphony/agoge.env').is_file():
            raise ValueError('Existing Symphony environment file absent; no credentials provisioned')
    if control and not (FACTORY.parents[2]/'elixir/bin/symphony').is_file():
        raise ValueError('Build Symphony with make all before installation')
    if not auth.is_file(): raise ValueError('Existing Codex auth unavailable; no credentials were provisioned')
    if control:
        active = subprocess.run(['systemctl','--user','is-active','--quiet','symphony-agoge.service']).returncode
        if active == 0: raise ValueError('Stop Symphony before installing')
    # Probe all destination roots BEFORE changing any factory/service files.
    for directory in (state, units):
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=directory): pass
    home = state / 'codex-home'; home.mkdir(mode=0o700, exist_ok=True)
    manifest = state / 'installation.json'
    unit = units / 'symphony-agoge.service'
    rendered = (FACTORY.parent/'symphony-agoge.service').read_text().replace('@FACTORY_DIR@',str(FACTORY)).encode()
    policy = (FACTORY/'native-policy.toml').read_bytes()
    batch=json.loads((FACTORY/('canary-batch.json' if canary else 'batch.json')).read_text())
    batch['execution_enabled']=bool(canary)
    numbers=[t['number'] for t in batch['tasks']]
    if canary and numbers != [236]: raise ValueError('Canary install must select only issue 236')
    workflow=(FACTORY.parent/'WORKFLOW.md').read_text().replace('agent_issue_numbers: [235]', 'agent_issue_numbers: '+json.dumps(numbers))
    targets = {unit: rendered, home/'config.toml': policy,
               state/'batch.json': (json.dumps(batch,indent=2)+'\n').encode(), state/'WORKFLOW.md': workflow.encode()}
    if manifest.exists():
        record = json.loads(manifest.read_text())
        if record['factory'] != str(FACTORY): raise ValueError('Installation belongs to another checkout; rollback first')
        for path, previous in record['installed'].items():
            p = Path(path)
            if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != previous:
                raise ValueError('Installed factory file changed; preserve/review it before reinstalling')
    else:
        record = {'factory':str(FACTORY), 'backups':{}, 'installed':{}, 'auth_link':str(home/'auth.json')}
        for p in targets:
            record['backups'][str(p)] = p.read_bytes().hex() if p.exists() else None
        # Persist original contents before any replacement, including on interrupted installation.
        atomic(manifest,json.dumps(record,indent=2).encode())
    link = home/'auth.json'
    if link.is_symlink():
        if link.resolve() != auth.resolve(): raise ValueError('Existing auth reference differs; not replacing it')
    elif link.exists(): raise ValueError('Refusing to replace authentication material')
    else: link.symlink_to(auth)
    for path, data in targets.items():
        atomic(path,data)
        record['installed'][str(path)] = hashlib.sha256(data).hexdigest()
        atomic(manifest,json.dumps(record,indent=2).encode())
    if control:
        subprocess.run(['systemctl','--user','daemon-reload'],check=True)
        subprocess.run(['systemctl','--user','disable','--now','symphony-agoge.service'],check=True)
    return record

def rollback(state, control=True):
    manifest=state/'installation.json'
    record=json.loads(manifest.read_text())
    for path,digest in record['installed'].items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest:
            raise ValueError('Modified installed file retained; review before rollback')
    if control: subprocess.run(['systemctl','--user','disable','--now','symphony-agoge.service'],check=True)
    for path,backup in record['backups'].items():
        p=Path(path)
        if backup is None: p.unlink(missing_ok=True)
        else: atomic(p,bytes.fromhex(backup))
    link=Path(record['auth_link'])
    if link.is_symlink(): link.unlink()  # only factory reference, never target credential
    manifest.rename(state/'installation.rolled-back.json')
    if control: subprocess.run(['systemctl','--user','daemon-reload'],check=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--rollback',action='store_true');parser.add_argument('--canary',action='store_true');args=parser.parse_args()
    state=Path.home()/'.local/state/agoge-factory'
    try:
        if args.rollback: rollback(state)
        else: install(state,Path.home()/'.config/systemd/user',Path.home()/'.codex/auth.json',canary=args.canary)
    except OSError as error:
        raise SystemExit(f'Factory installation blocked: filesystem operation denied at {error.filename}; rerun in a permitted non-root host session. No activation performed')
    except ValueError as error:
        raise SystemExit('Factory installation blocked: '+str(error))
    except subprocess.SubprocessError:
        raise SystemExit('Factory installation blocked: user systemd operation failed; restore user-service access before retrying')
    print('Factory files installed/restored; service stopped. Live containment canary is still required.')
