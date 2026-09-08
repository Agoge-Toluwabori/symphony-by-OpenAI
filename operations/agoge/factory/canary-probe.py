#!/usr/bin/env python3
"""Run only inside the actual canary worker. Never reads credential bytes."""
import json
import os
from pathlib import Path
import socket

results = {}
for name, path in {
    'unrelated_repository': '/home/toluadmin/services/symphony/README.md',
    'protected_credentials': '/home/toluadmin/.config/symphony/agoge.env',
    'codex_credentials': '/home/toluadmin/.codex/auth.json',
}.items():
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        results[name] = 'DENIED'
    else:
        os.close(descriptor)
        results[name] = 'FAIL: open succeeded; no bytes read'
try:
    os.setuid(0)
except PermissionError:
    results['root'] = 'DENIED'
else:
    results['root'] = 'FAIL: root identity obtained'
# Numeric TEST-NET address: no DNS/provider invocation; network must reject socket use.
try:
    sock = socket.socket()
    sock.settimeout(0.2)
    sock.connect(('192.0.2.1', 443))
except PermissionError:
    results['direct_network'] = 'DENIED'
except OSError as error:
    results['direct_network'] = 'UNPROVEN: errno ' + str(error.errno)
else:
    results['direct_network'] = 'FAIL: connection succeeded'
finally:
    if 'sock' in locals(): sock.close()
Path('factory-containment-results.json').write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps(results, sort_keys=True))
raise SystemExit(0 if all(v == 'DENIED' for v in results.values()) else 1)
