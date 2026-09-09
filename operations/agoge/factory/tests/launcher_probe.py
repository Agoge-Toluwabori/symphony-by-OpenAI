#!/usr/bin/env python3
"""Explicit harmless host diagnostic. Never starts Symphony or uses authentication.
Run separately from unittest: python3 tests/launcher_probe.py
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

FACTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FACTORY))
import policy

hardening = ['systemd-run', '--user', '--wait', '--pipe', '--collect',
             '-p', 'NoNewPrivileges=yes', '-p', 'LockPersonality=yes',
             '-p', 'RestrictSUIDSGID=yes']

with tempfile.TemporaryDirectory(prefix='agoge-launcher-proof-') as d:
    root = Path(d)
    home = root/'home'; home.mkdir()
    workspace = root/'workspace'; workspace.mkdir()
    legacy = (FACTORY/'native-policy.before-launcher-repair.toml').read_text()
    path_fixed = legacy.replace('include_only = []',
        'include_only = []\n[shell_environment_policy.set]\nPATH = "/usr/bin:/bin"')
    directories_fixed = path_fixed.replace('".agents" = "deny"\n', '').replace('".codex" = "deny"\n', '')
    cases = [('original', legacy, 'RTM_NEWADDR'),
             ('system_path_only', path_fixed, 'Is a directory'),
             ('directory_collision_fixed', directories_fixed, 'No such file or directory'),
             ('repaired', policy.render().decode(), None)]
    base = hardening + ['/usr/bin/env', '-i', 'HOME=/home/toluadmin',
                       'CODEX_HOME='+str(home), 'PATH=/usr/bin:/bin']
    native = [str(policy.CODEX), 'sandbox', '-P', 'factory-canary', '-C', str(workspace)]
    for name, config, expected in cases:
        (home/'config.toml').write_text(config)
        trace_before = root/'before.trace'
        tracing = ['/usr/bin/strace', '-f', '-s', '120', '-e', 'trace=execve', '-o', str(trace_before)] if name == 'original' else []
        result = subprocess.run(base + tracing + native + ['/bin/true'], capture_output=True, text=True)
        output = result.stdout + result.stderr
        if name == 'original':
            bundled = [line for line in trace_before.read_text().splitlines() if 'execve("/proc/self/fd/' in line and '"bwrap"' in line]
            assert bundled, 'Expected bundled Bubblewrap fallback was not observed'
            print(json.dumps({'before_bundled_bwrap_exec_trace': bundled}), flush=True)
        print(json.dumps({'case': name, 'exit': result.returncode, 'output': output}), flush=True)
        assert (result.returncode == 0 if expected is None else result.returncode != 0 and expected in output)
    trace = root/'exec.trace'
    result = subprocess.run(base + ['/usr/bin/strace', '-f', '-s', '200', '-e', 'trace=execve',
                            '-o', str(trace)] + native + ['/bin/true'], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    system_bwrap = [line for line in trace.read_text().splitlines() if 'execve("/usr/bin/bwrap"' in line]
    assert system_bwrap, 'System Bubblewrap was not observed'
    print(json.dumps({'system_bwrap_exec_trace': system_bwrap}), flush=True)
    checks = r'''
import os, pathlib, socket, subprocess
assert os.geteuid() != 0
for name in ('GH_TOKEN', 'GITHUB_TOKEN', 'OPENAI_API_KEY', 'VERCEL_TOKEN', 'SUPABASE_ACCESS_TOKEN'):
    assert name not in os.environ
for name in ('/home/toluadmin/.codex/auth.json', '/home/toluadmin/projects/Agoge-Business-Systems/README.md'):
    try:
        fd = os.open(name, os.O_RDONLY)
    except OSError:
        pass
    else:
        os.close(fd)
        raise AssertionError('Protected host path readable')
# Socket creation is denied before any production/billing/DNS endpoint can be contacted.
try:
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except OSError:
    pass
else:
    connection.close()
    raise AssertionError('Network socket allowed')
assert subprocess.run(['/usr/bin/sudo', '-n', '/bin/true'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0
subprocess.run(['git', 'init', '-q'], check=True)
pathlib.Path('launcher-marker.txt').write_text('harmless launcher fixture\n')
assert pathlib.Path('launcher-marker.txt').read_text() == 'harmless launcher fixture\n'
subprocess.run(['git', 'add', 'launcher-marker.txt'], check=True)
subprocess.run(['git', '-c', 'user.name=Factory Diagnostic', '-c', 'user.email=factory@localhost', 'commit', '-qm', 'Test native launcher containment'], check=True)
print('PASS: harmless edit, validation, local commit; protected paths, credentials, network and root denied')
'''
    result = subprocess.run(base + native + ['/usr/bin/python3', '-c', checks], capture_output=True, text=True)
    print(json.dumps({'case': 'development_and_negative_checks', 'exit': result.returncode,
                      'output': result.stdout + result.stderr}), flush=True)
    assert result.returncode == 0
print('PASS: launcher diagnostic only; no Symphony dispatch or credentials used')
