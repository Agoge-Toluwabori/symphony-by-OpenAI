#!/bin/bash
# Owner-side Git preservation only; does not install or start a service.
set -euo pipefail
canonical=/home/toluadmin/services/symphony
preserved="$canonical/.factory-preservation"
branch=codex/agoge-delivery-factory-v1
git -C "$canonical" fetch --no-tags --no-write-fetch-head "$preserved/repository.git" "refs/heads/$branch:refs/heads/$branch"
git -C "$canonical" merge-base --is-ancestor 22f1128d6954f8d9634232c8293d72f6a36ddb98 "$branch"
if test -e "$preserved/canonical-worktree"; then
  test "$(git -C "$preserved/canonical-worktree" rev-parse --git-common-dir)" = "$canonical/.git" || exit 70
else
  git -C "$canonical" worktree add "$preserved/canonical-worktree" "$branch"
fi
