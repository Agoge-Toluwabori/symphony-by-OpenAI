#!/bin/bash
set -euo pipefail
factory_dir=$(cd -- "$(dirname -- "$0")" && pwd)
export PATH=/home/toluadmin/.local/share/mise/installs/elixir/1.19.5-otp-28/bin:/home/toluadmin/.local/share/mise/installs/erlang/28.5/bin:/usr/bin:/bin
export ERL_FLAGS='+S 2:2'
export MIX_HOME=/tmp/agoge-factory-mix
export HEX_HOME=/tmp/agoge-factory-hex
evidence_dir=${AGOGE_VALIDATION_EVIDENCE:-$factory_dir/evidence/denial-repair}
mkdir -p "$evidence_dir"
cd "$factory_dir/../../../elixir"
mix format
make all > "$evidence_dir/symphony-suite.txt" 2>&1
python3 -m unittest discover -s "$factory_dir/tests" -v > "$evidence_dir/factory-tests.txt" 2>&1
python3 "$factory_dir/tests/native_probe.py" > "$evidence_dir/native-probe.txt" 2>&1
