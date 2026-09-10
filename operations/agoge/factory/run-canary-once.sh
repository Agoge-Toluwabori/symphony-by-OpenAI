#!/bin/bash
# Owner-authorized install and one #236 run; never enables normal delivery.
set -euo pipefail
factory_dir=$(cd -- "$(dirname -- "$0")" && pwd)
python3 "$factory_dir/install.py" --canary
finish() {
  systemctl --user disable --now symphony-agoge.service
  systemctl --user show symphony-agoge.service -p ActiveState -p UnitFileState -p MainPID
}
trap finish EXIT
systemctl --user start symphony-agoge.service
for (( poll=0; poll<120; poll++ )); do
  if ! systemctl --user is-active --quiet symphony-agoge.service; then
    exit 0
  fi
  sleep 5
done
printf '%s\n' 'Canary exceeded ten-minute observation limit; stopping without retry.' >&2
exit 1
