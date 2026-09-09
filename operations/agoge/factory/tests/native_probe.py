#!/usr/bin/env python3
"""Harmless native sandbox diagnostic, no model/issue dispatch or credentials."""
import json
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
    (workspace/'probe.py').write_bytes((FACTORY/'canary-probe.py').read_bytes())
    command=['systemd-run','--user','--wait','--pipe','--collect',
        '-p','NoNewPrivileges=yes','-p','LockPersonality=yes','-p','RestrictSUIDSGID=yes',
        '/usr/bin/env','-i','HOME=/home/toluadmin','CODEX_HOME='+str(home),'PATH=/usr/bin:/bin',
        str(policy.CODEX),'sandbox','-P','factory-canary','-C',str(workspace),'/usr/bin/python3','probe.py']
    run=subprocess.run(command,capture_output=True,text=True,timeout=20)
    print(json.dumps({'exit':run.returncode,'output':run.stdout+run.stderr}))
    assert run.returncode==0
    result=json.loads((workspace/'factory-containment-results.json').read_text())
    assert all(v=='DENIED' for v in result['checks'].values())
    assert result['root_identity']['before']==result['root_identity']['after']
    print('PASS: native UID denial diagnostic; no App Server/model or issue dispatch')
