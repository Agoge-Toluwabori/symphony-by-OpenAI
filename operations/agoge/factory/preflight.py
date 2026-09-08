#!/usr/bin/env python3
"""No generic broker prerequisite: check the concrete native-policy installation."""
import os
from pathlib import Path
import sys

factory = Path(__file__).resolve().parent
state = Path(os.environ.get('AGOGE_FACTORY_STATE', str(Path.home() / '.local/state/agoge-factory')))
if os.geteuid() == 0:
    sys.exit('Factory blocked: run as non-root toluadmin')
for name in ('launcher.py', 'native-policy.toml', 'queue.py', 'workspace.py'):
    if not (factory / name).is_file(): sys.exit('Factory blocked: incomplete reviewed checkout')
policy = state / 'codex-home/config.toml'
if not policy.is_file() or policy.read_bytes() != (factory / 'native-policy.toml').read_bytes():
    sys.exit('Factory blocked: native policy not installed; run install.py from a permitted host session')
if not (state / 'codex-home/auth.json').is_symlink():
    sys.exit('Factory blocked: existing Codex auth reference absent; credentials were not provisioned')
# This checks installed files, NOT a successful live canary. Batch execution hold is separate.
