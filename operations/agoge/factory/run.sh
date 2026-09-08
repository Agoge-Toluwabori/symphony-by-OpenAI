#!/bin/bash
set -euo pipefail
factory_dir=$(cd -- "$(dirname -- "$0")" && pwd)
export AGOGE_FACTORY_DIR="$factory_dir"
python3 "$factory_dir/preflight.py"
# Lock spans both processes; two controllers cannot lease the same repository.
exec 9>"${XDG_RUNTIME_DIR:?}/agoge-factory.lock"
flock -n 9 || exit 75
python3 "$factory_dir/queue.py" --prepare --state-dir "${XDG_STATE_HOME:-$HOME/.local/state}/agoge-factory" || { code=$?; test "$code" = 10 && exit 0; exit "$code"; }
cd "$factory_dir/../../../elixir"
./bin/symphony "$factory_dir/../WORKFLOW.md" --port 4000 --logs-root "${XDG_STATE_HOME:-$HOME/.local/state}/agoge-factory/logs" --i-understand-that-this-will-be-running-without-the-usual-guardrails &
controller_pid=$!
trap 'kill "$controller_pid" 2>/dev/null || true; wait "$controller_pid" 2>/dev/null || true' EXIT
trap 'exit 0' TERM INT
failures=0
while kill -0 "$controller_pid" 2>/dev/null; do
  if python3 "$factory_dir/queue.py" --apply --state-dir "${XDG_STATE_HOME:-$HOME/.local/state}/agoge-factory"; then
    failures=0
  else
    code=$?
    if (( code == 10 )); then exit 0; fi
    failures=$((failures + 1))
    if (( failures >= 3 )); then exit 75; fi
  fi
  sleep 30 & wait $!
done
wait "$controller_pid"
