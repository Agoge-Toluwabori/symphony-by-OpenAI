#!/bin/bash
set -euo pipefail
case "$PWD" in /home/toluadmin/services/symphony-workspaces/agoge-business-systems/GH-*) ;; *) exit 70;; esac
expected=Agoge-Toluwabori/Agoge-Business-Systems
branch=$(gh repo view "$expected" --json defaultBranchRef --jq .defaultBranchRef.name)
test -n "$branch"
gh repo clone "$expected" . -- --branch "$branch" --single-branch
origin=$(git remote get-url origin)
case "$origin" in https://github.com/Agoge-Toluwabori/Agoge-Business-Systems.git|git@github.com:Agoge-Toluwabori/Agoge-Business-Systems.git) ;; *) exit 71;; esac
test "$(git branch --show-current)" = "$branch"
git switch -c "symphony/$(basename "$PWD")"
git config user.name 'Agoge Symphony'
git config user.email 'symphony@localhost'
git remote set-url --push origin DISABLED-BY-OWNER-NO-PUSH
