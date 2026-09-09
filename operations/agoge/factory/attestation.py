"""Host-only preflight evidence. No credentials, worker mounts or new permissions."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import policy

SERVICE = 'symphony-agoge.service'
REPAIR = 'dispatch-context-v1'


def check(fields):
    for name, status in fields.items():
        print(json.dumps({'preflight_field': name, 'status': status}), file=sys.stderr, flush=True)
    if any(status != 'verified' for status in fields.values()):
        raise ValueError('Factory preflight failed; see individual field statuses')


def write(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2)+'\n')
    temporary.chmod(0o600)
    temporary.replace(path)


def service_context(state):
    batch = json.loads((state/'batch.json').read_text())
    invocation = os.environ.get('INVOCATION_ID', '')
    properties = subprocess.check_output(['systemctl', '--user', 'show', SERVICE,
        '-p', 'InvocationID', '-p', 'ActiveState', '-p', 'UnitFileState', '-p', 'ControlGroup',
        '-p', 'Restart', '-p', 'NoNewPrivileges', '-p', 'LockPersonality', '-p', 'RestrictSUIDSGID'], text=True)
    props = dict(line.split('=', 1) for line in properties.splitlines() if '=' in line)
    cgroup = Path('/proc/self/cgroup').read_text()
    fields = {
        'service_identity': 'verified' if props.get('ActiveState') in ('active','activating') and props.get('ControlGroup') and props['ControlGroup'] in cgroup else 'invalid',
        'dispatch_invocation': 'verified' if invocation and props.get('InvocationID') == invocation else 'missing' if not invocation else 'invalid',
        'service_disabled': 'verified' if props.get('UnitFileState') == 'disabled' else 'invalid',
        'approved_batch': 'verified' if batch.get('approved') is True and batch.get('execution_enabled') is True and batch.get('batch') == 'factory-v1-containment-canary' and batch.get('repository') == 'Agoge-Toluwabori/Agoge-Business-Systems' and batch.get('tasks') == [{'number':236,'authority':'Autonomous Development','dependencies':[]}] else 'invalid',
        'hardening': 'verified' if all(props.get(name) == 'yes' for name in ('NoNewPrivileges','LockPersonality','RestrictSUIDSGID')) else 'invalid',
        'stop_policy': 'verified' if props.get('Restart') == 'no' and props.get('UnitFileState') == 'disabled' else 'invalid',
        'concurrency': 'verified' if batch.get('max_concurrency') == 1 else 'invalid',
        'native_policy': 'verified' if policy.matches((state/'codex-home/config.toml').read_bytes()) else 'invalid',
    }
    check(fields)
    return {'repair':REPAIR, 'service':SERVICE, 'invocation_id':invocation,
            'batch':batch['batch'], 'repository':batch['repository'], 'issue_id':'236',
            'authority':'Autonomous Development', 'max_concurrency':1,
            'preflight':fields, 'approval_policy':'never', 'permissions':'factory-canary',
            'batch_stop':{'owner':'host supervisor','phase':'after worker completion','service_enabled':False},
            'policy_sha256':hashlib.sha256((state/'codex-home/config.toml').read_bytes()).hexdigest()}


def dispatch(state, workspace):
    context = service_context(state)
    expected = policy.WORKSPACES / ('GH-'+context['issue_id'])
    check({'workspace':'verified' if workspace.resolve() == expected else 'invalid'})
    # This exclusive receipt permits one actual App Server launch per service invocation.
    receipt = state/('attempt-'+context['invocation_id']+'.json')
    with receipt.open('x') as f:
        json.dump({'issue_id':context['issue_id'], 'workspace':str(workspace)},f)
    context.update(workspace=str(workspace), app_server_pid=os.getpid())
    write(state/'dispatch-context.json',context)
    return context


if __name__ == '__main__':
    try:
        state=Path(os.environ['AGOGE_FACTORY_STATE'])
        write(state/'service-preflight.json',service_context(state))
    except (ValueError, OSError, KeyError, subprocess.SubprocessError):
        raise SystemExit('Factory service preflight failed closed; see field diagnostics')
