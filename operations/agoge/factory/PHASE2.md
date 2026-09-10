> Launcher repair update (2026-09-09): see [LAUNCHER-REPAIR.md](LAUNCHER-REPAIR.md). The owner installed the factory after the historical report below; #236 attempts failed. Native launcher diagnostics now pass, but reinstall and a successful live canary remain required. Normal delivery is not authorized. Historical evidence below is retained unchanged.

# Phase 2 — DESIGN COMPLETE, ACTIVATION BLOCKED

The design is preserved and native containment integration is implemented in a
durable isolated worktree. Canonical Git import and actual user-service installation
are blocked by this session's read-only mounts. Dedicated canary #236 has NOT run.
No operational containment or activation-readiness claim is made.

## 1–2. Preservation

Requested Phase 1 commit: 22f1128d6954f8d9634232c8293d72f6a36ddb98.
Temporary clone /tmp/agoge-delivery-factory-v1 remains unchanged at that commit.

Durable independent repository:
/home/toluadmin/services/symphony/.factory-preservation/repository.git

Durable isolated worktree (not /tmp):
/home/toluadmin/services/symphony/.factory-preservation/worktree

Branch: codex/agoge-delivery-factory-v1. Phase 2 is a new descendant commit, never
a rewritten Phase 1 commit. The final response identifies its SHA.

Durable self-contained bundle:
/home/toluadmin/services/symphony/.factory-preservation/phase1.bundle

Git bundle verification and full Git fsck passed. preservation.json verifies all
36 Phase 1 file blobs byte-for-byte against the original temporary checkout and
confirms every path exists in the durable worktree. Phase 2 intentionally updates
some current files; all original versions remain in commit 22f1128 and the bundle.

The requested transfer into canonical /home/toluadmin/services/symphony/.git did
NOT succeed: one local fetch failed with “Read-only file system”, without a ref
update. The canonical branch remains codex/agoge-controlled-activation at 9920669;
its only new untracked material is the deliberate .factory-preservation directory.
No existing tracked file, branch, commit or worktree was overwritten. The separate
application checkout and all prior task worktrees are unchanged.

Canonical import/worktree creation is packaged as restore-canonical.sh for a
permitted host session. It uses a non-force local fetch, checks Phase 1 ancestry,
and creates a separate canonical-worktree path without touching the existing
checkout or main. It was syntax-checked, not executed past the denied import here.

## 3–5. Components and installer

Staged in the durable worktree, NOT installed into the user service:

- Native permission-profile support in Symphony config and App Server serialization.
  Explicit codex.permissions sends permissions at both thread/start and turn/start,
  omitting legacy sandbox/sandboxPolicy fields; legacy behavior stays compatible.
- native-policy.toml: root filesystem denied, minimal runtime readable, task workspace
  writable, protected configuration/environment/key patterns denied; command network
  disabled; no inherited shell environment; host apps disabled.
- launcher.py: non-root, exact workspace-root validation, rejected repository config
  overrides, fresh App Server CODEX_HOME and allowlisted process environment.
- Existing scoped GitHub tool: exact repository/current-issue operations, denied
  authority grants, out-of-task claims, unrelated repos and sensitive endpoints.
- install.py/install.sh: prerequisites, destination-write checks, atomic own-file
  replacements, retained original-service/config backups, installed-file hash checks,
  idempotent reruns, --rollback, and canary-only --canary mode selecting #236.
- run.sh: installed state/workflow selection, controller lock, bounded queue,
  one-task batch stop. Service has NoNewPrivileges, restrictive umask, memory/CPU/
  process limits, control-group cleanup and no automatic restart.
- Canary probe/brief, paused canary manifest and paused approved #235 manifest.

External inference, dependency and provider brokers are eliminated as mandatory
canary prerequisites. Inference authentication belongs to the existing trusted
App Server; worker commands receive native sandbox restrictions. GitHub already
has a host tool enforcing scope. The installer references existing auth through a
private symlink; it does not read/copy/print/replace authentication contents.
No new credentials or authentication reference was actually installed in this run.

This narrower canary policy does not claim general dependency downloads or provider
operations. No Vercel/publication operation is implemented or enabled here. Those
must be bounded and proven before normal tasks requiring them can execute.

Official profile documentation explains the mutually exclusive legacy/profile
settings and native filesystem/network controls:
https://learn.chatgpt.com/docs/permissions
The installed experimental App Server schema independently exposes permissions on
both request types; focused schema excerpts are saved with the evidence. These are
configuration facts, not evidence that a worker command was contained on this VM.

Installer location: operations/agoge/factory/install.py (install.sh wrapper).
Rollback: python3 operations/agoge/factory/install.py --rollback.
Rollback stops/disables the service, restores backed-up original files, removes only
factory-created files/references, and never removes the underlying auth file,
repositories, workspaces or evidence. Modified installed files are preserved and
reported instead of overwritten.

An actual installer invocation failed before any installation: user-state and
user-service paths are mounted read-only. filesystem-boundaries.json verifies the
read-only flag on canonical .git, ~/.local/state and ~/.config/systemd/user. The
installer has no bypass and cannot truthfully report successful installation here.
The installed old unit was not replaced or started. Reruns were tested using
synthetic files in allowed temporary directories, not by retrying denied host writes.

## 6–9. Canary and validation

Canary: https://github.com/Agoge-Toluwabori/Agoge-Business-Systems/issues/236
Open, Autonomous Development, symphony-canary, no ready/running label. Dedicated
one-task batch is approved but paused. No live lifecycle, workspace, branch, local
canary commit or App Server session exists for this canary. No direct/manual Codex
execution is being substituted for the required service-dispatched proof.

The original #234 evidence and AppArmor rule were inspected. #234 proved a marker
command under the prior sandbox, not local commits or credential/network isolation.
/etc/apparmor.d/usr.bin.bwrap permits user namespace creation in an unconfined
profile. It is compatibility remediation, not a standalone data-access boundary.
It remains unchanged. A nested Codex sandbox CLI probe in this session failed at
its protected synthetic-mount registry lock before command execution. This is not
proof of a regression in #234's host environment, nor a successful containment test.

| Validation | Result |
|---|---|
| Durable bundle / ancestry / 36 Phase 1 files / Git fsck | PASS |
| Canonical Git import and canonical-linked worktree | BLOCKED: read-only .git; durable independent worktree provided |
| Full Symphony make all | PASS: 299 tests, zero failures, six opt-in live tests skipped; 100% coverage; format, lint, specs, build and Dialyzer passed |
| Factory tests | PASS: 25 tests; queue, batch hold, dependencies, locking, retries, workspace preservation, installer rerun/rollback/owner-edit protection and canary selection |
| Native profile request serialization | PASS in App Server test harness; both requests exclude legacy sandbox fields |
| Native policy TOML / shell / Python syntax | PASS |
| Actual installer | BLOCKED before installation; read-only user-state/service roots |
| Actual service-launched native worker | NOT RUN |
| Live no-approval edit/validation/local commit | NOT RUN; synthetic fixtures are not canary proof |
| Scoped API production/billing/unrelated-repo/other-issue denials | PASS in test harness, NOT live worker proof |
| Live protected credentials / root / filesystem/network denial | NOT RUN / UNPROVEN |
| Live concurrency and batch stop | NOT RUN; core/factory tests pass |
| #235 held, #236 unclaimed | PASS: remote state captured |
| Service inactive, dead, disabled, MainPID=0 | PASS |

The queued canary probes never read credential bytes. A successful protected-file
open is failure even if no contents are read. Timeouts/unreachable network targets
are UNPROVEN, not passing access-control tests. Sensitive provider endpoints are
negative calls through the restricted host tool, never direct Vercel or billing
requests. The live canary must pass all of these before #235 is re-enabled.

## 10–13. Final status and commands

Symphony: inactive/dead, disabled, MainPID=0. No service was started in Phase 2.
#235: open, Autonomous Development and its approved batch retained, no ready/running
label, Project status Blocked for the real containment prerequisite. New explanatory
comment supersedes prior readiness; no historical comment or report was deleted.
The source batch's execution_enabled=false prevents automatic re-eligibility.

There is NO authorized normal-delivery activation command while this remains blocked.
After restoring permitted host filesystem access, the concrete canary-only command
from the durable worktree is:

```sh
python3 /home/toluadmin/services/symphony/.factory-preservation/worktree/operations/agoge/factory/install.py --canary && systemctl --user start symphony-agoge.service
```

This installs/starts only #236's one-task canary, not #235 or normal delivery, and
must be followed by live evidence review and the stop command. It cannot run
successfully under this session's current read-only user-service/state mounts.

Canonical import first, when host writes are permitted:

```sh
bash /home/toluadmin/services/symphony/.factory-preservation/worktree/operations/agoge/factory/restore-canonical.sh
```

Emergency stop:

```sh
systemctl --user disable --now symphony-agoge.service
```

## 14–16. Remaining blockers and action limits

Blocking environment restrictions: canonical Git object/ref writes and user-state/
user-service installation. After those are removed in a permitted host session,
actual native-policy worker launch and the complete #236 live containment canary
still must run and pass. Normal development publication/provider access also remains
unimplemented/unproven; no broad network/credential access was substituted.

Zero incremental paid resources or billable provider operations were initiated.
No live inference worker was started. Account billing was not audited.

No application push, Vercel invocation, Supabase mutation, deployment, DNS/firewall
change, credential exposure/replacement, production action or Git history rewrite.
Only authorized GitHub issue/Project control-plane metadata changed, alongside local
control-plane code, tests, preservation artifacts and documentation.
