#!/usr/bin/env python3
"""Harmless native sandbox diagnostic, no model/issue dispatch or credentials."""
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile

FACTORY=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(FACTORY))
import policy

with tempfile.TemporaryDirectory(prefix='agoge-uid-proof-') as d:
    root=Path(d);home=root/'home';home.mkdir();workspace=root/'workspace';workspace.mkdir()
    (home/'config.toml').write_bytes(policy.render())
    (workspace/'host-netns.txt').write_text(os.readlink('/proc/self/ns/net'))
    (workspace/'probe.py').write_bytes((FACTORY/'canary-probe.py').read_bytes())
    command=['systemd-run','--user','--wait','--pipe','--collect',
        '-p','NoNewPrivileges=yes','-p','LockPersonality=yes','-p','RestrictSUIDSGID=yes',
        '/usr/bin/env','-i','HOME=/home/toluadmin','CODEX_HOME='+str(home),'PATH=/usr/bin:/bin','FACTORY_HOST_NETNS='+os.readlink('/proc/self/ns/net'),
        str(policy.CODEX),'sandbox','-P','factory-canary','-C',str(workspace),'/usr/bin/python3','probe.py']
    run=subprocess.run(command,capture_output=True,text=True,timeout=20)
    print(json.dumps({'exit':run.returncode,'output':run.stdout+run.stderr}))
    assert run.returncode==0
    result=json.loads((workspace/'factory-containment-results.json').read_text())
    assert all(v=='DENIED' for v in result['checks'].values())
    assert result['root_identity']['before']==result['root_identity']['after']
    print('PASS: native UID denial diagnostic; no App Server/model or issue dispatch')

# Regression: Node captured subprocess output must work; outbound proxy must deny.
with tempfile.TemporaryDirectory(prefix='agoge-ipc-proof-') as d:
    root=Path(d);home=root/'home';home.mkdir();workspace=root/'workspace';workspace.mkdir()
    (home/'config.toml').write_bytes(policy.render())
    binding=json.loads((FACTORY/'continuous/project.json').read_text())
    shutil.copy2(binding['node'],workspace/'node')
    (workspace/'ipc.py').write_text("""
import http.client,json,os,subprocess
from urllib.parse import urlsplit
r=subprocess.run(['./node','-e',"let r=require('child_process').spawnSync('/usr/bin/printf',['ipc-ok']);if(r.error||r.status!==0||r.stdout.toString()!=='ipc-ok')process.exit(1)"],check=True)
proxy=urlsplit(os.environ['HTTPS_PROXY'])
for destination in ('billing.factory.invalid:443','production.factory.invalid:443','api.github.com:443'):
    c=http.client.HTTPConnection(proxy.hostname,proxy.port,timeout=5)
    c.request('CONNECT',destination)
    response=c.getresponse()
    assert response.status==403, response.status
    c.close()
print('PASS: Node captured IPC; proxy rejects billing, production and direct GitHub before upstream transmission')
""")
    command=['systemd-run','--user','--wait','--pipe','--collect',
        '-p','NoNewPrivileges=yes','-p','LockPersonality=yes','-p','RestrictSUIDSGID=yes',
        '/usr/bin/env','-i','HOME=/home/toluadmin','CODEX_HOME='+str(home),'PATH=/usr/bin:/bin',
        str(policy.CODEX),'sandbox','-P','factory-canary','-C',str(workspace),'/usr/bin/python3','ipc.py']
    run=subprocess.run(command,capture_output=True,text=True,timeout=20)
    print(run.stdout+run.stderr)
    assert run.returncode==0
