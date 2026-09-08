#!/usr/bin/env python3
"""Fail closed while VM containment is unavailable. Never installs credentials."""
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
policy = json.loads((root / 'containment.json').read_text())
wrapper = Path(policy['worker_executable'])
if os.geteuid() == 0:
    sys.exit('Refusing root controller execution')
if not wrapper.is_file():
    sys.exit('Activation blocked: isolated worker/brokers not installed; see REPORT.md')
stat = wrapper.stat()
if stat.st_uid != 0 or stat.st_mode & 0o022 or os.access(wrapper, os.W_OK):
    sys.exit('Activation blocked: worker wrapper must be administrator-owned and immutable to controller')
# Trusted administrator implementation must perform probes; no JSON attestation bypass.
# The contract is documented in TEMPLATE.md. stdout is deliberately suppressed.
result = subprocess.run([str(wrapper), '--verify-boundaries'], stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL, timeout=60)
if result.returncode:
    sys.exit('Activation blocked: containment probes failed')
