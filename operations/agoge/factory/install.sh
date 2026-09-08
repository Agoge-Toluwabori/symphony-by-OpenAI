#!/bin/bash
# Owner-side installation only. Does not activate; never provisions credentials.
set -euo pipefail
factory_dir=$(cd -- "$(dirname -- "$0")" && pwd)
python3 "$factory_dir/preflight.py"
systemctl --user disable --now symphony-agoge.service
unit_dir="$HOME/.config/systemd/user"
mkdir -p "$unit_dir"
if test -f "$unit_dir/symphony-agoge.service"; then
  cp -p "$unit_dir/symphony-agoge.service" "$unit_dir/symphony-agoge.service.before-factory-$(date -u +%Y%m%dT%H%M%SZ)"
fi
sed "s|@FACTORY_DIR@|$factory_dir|g" "$factory_dir/../symphony-agoge.service" > "$unit_dir/symphony-agoge.service"
systemctl --user daemon-reload
printf '%s\n' 'Installed, disabled and stopped. Owner activation: systemctl --user enable --now symphony-agoge.service'
