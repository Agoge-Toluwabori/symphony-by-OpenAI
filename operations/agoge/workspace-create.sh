#!/bin/bash
set -euo pipefail
# Runs on trusted host, never inside worker; credentials stay on host.
case "$PWD" in /home/toluadmin/services/symphony-workspaces/agoge-business-systems/GH-*) ;; *) exit 70;; esac
case "$(basename "$PWD")" in GH-[0-9]*) ;; *) exit 70;; esac
# after_create runs only for a new workspace. Never reuse an existing Git checkout.
test ! -e .git || exit 72
expected=Agoge-Toluwabori/Agoge-Business-Systems
branch=$(python3 -c 'import json,os; c=json.load(open(os.environ["AGOGE_FACTORY_STATE"]+"/batch.json")); print(c.get("integration_branch",""))')
if test -z "$branch"; then branch=$(gh repo view "$expected" --json defaultBranchRef --jq .defaultBranchRef.name); fi
test -n "$branch"
gh repo clone "$expected" . -- --branch "$branch" --single-branch
origin=$(git remote get-url origin)
case "$origin" in https://github.com/Agoge-Toluwabori/Agoge-Business-Systems.git|git@github.com:Agoge-Toluwabori/Agoge-Business-Systems.git) ;; *) exit 71;; esac
test "$(git branch --show-current)" = "$branch"
git switch -c "symphony/$(basename "$PWD")-$(date -u +%Y%m%dT%H%M%SZ)"
git config user.name 'Agoge Symphony'
git config user.email 'symphony@localhost'
# Worker gets no GitHub auth. Publication is a host-broker operation after #235.
git remote set-url --push origin PUBLICATION-REQUIRES-VERIFIED-HOST-BROKER
