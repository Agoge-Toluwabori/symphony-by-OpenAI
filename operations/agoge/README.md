# Phase 2 status — DESIGN COMPLETE, ACTIVATION BLOCKED

See [current Phase 2 report](factory/PHASE2.md). Native permission profiles replace
the old placeholder broker prerequisite, but installation is blocked by read-only
host paths. Canary #236 is prepared, not run. #235 is approved but not executable.
All older activation/readiness statements below are retained historical evidence.

---

# Delivery Factory V1 supersession — 2026-09-08

The current review package is [factory/REPORT.md](factory/REPORT.md), with the
reusable [template](factory/TEMPLATE.md). Its tracked workflow replaces the
bootstrap approval rules below. The installed service remains DISABLED and STOPPED;
the package is not installed because verified worker containment is unavailable.
Historical reports below are retained and do not describe current runtime state.
The later successful #234 canary supersedes the initial failed canary below.

---

# Agoge Symphony controlled activation — 2026-09-08

Certain: configuration and controlled dispatch established; successful sandbox canary BLOCKED.
Owner accepted VM Batch1 as preparation/evidence only. No frontend implementation,
PostgreSQL 17.6 compatibility, hosted migration readiness, backend implementation,
VM application deployment, Vercel remediation, Supabase integration or production readiness is complete.

## Installation and controls

Symphony: /home/toluadmin/services/symphony, local branch codex/agoge-controlled-activation,
parent 2335be66766fef5847b0d8d583465f4d07b2bb03. Existing history preserved.
Tracked operations/agoge/WORKFLOW.md is installed at
/home/toluadmin/services/symphony-configs/agoge-business-systems/WORKFLOW.md.
The tracked service definition is installed at ~/.config/systemd/user/symphony-agoge.service.
No changes to Symphony application code. Runtime: existing mise Elixir 1.19.5-otp-28,
Erlang 28.5; Codex 0.153.4. No dependency installations.

Dispatch requires an open native GitHub issue in Agoge-Toluwabori/Agoge-Business-Systems
with symphony-ready. required_labels contains only that label; closed is terminal.
The adapter matches normalized complete label names, never substrings or Project status.
GitHub Project #1 remains the owner planning surface, not an independent dispatch grant.
Concurrency 1. Each issue gets an isolated GH-N clone outside the canonical repository.
The hook verifies origin/default branch, creates a local symphony/GH-N branch and sets an
invalid push URL. It does not install dependencies. Workflow requires live authorization,
instruction/dependency preflight before running; blocked issues lose authorization;
finished delivery work goes to human-review and is not closed automatically.

Host credential: ~/.config/symphony/agoge.env, mode 0600, parent 0700, owned by toluadmin;
loaded through systemd EnvironmentFile. Existing gh/Codex host credentials remain protected.
No token is stored in tracked files, workflow, evidence or workspace. The installed adapter
scrubs GitHub token environment aliases from the App Server child and offers github_api
through the host. The clone hook uses host authentication. Same-UID host credential files
are not a separate security principal from the worker; do not treat mode 0600 as protection
against a malicious process running as toluadmin.

App Server approvalPolicy is granular with sandbox_approval, rules, mcp_elicitations,
request_permissions and skill_approval all false. The installed schema and live thread/start
accepted it. Symphony's older default reject shape is overridden. Thread workspace-write,
turn workspaceWrite/networkAccess=true; /tmp and TMPDIR extra write grants excluded;
empty explicit writableRoots retains the current workspace as the implicit write root.
No danger-full-access or approval escalation. The startup acknowledgement CLI flag is an
upstream startup banner gate, not a sandbox override.

Network access is enabled, not a domain allowlist. Workflow limits its authorized use.
The installed github_api tool accepts general REST requests; repository/issue write scope
is an agent instruction, not a hard API authorization filter. Likewise the invalid Git push
URL is an accidental-push guard, not a malicious-agent boundary. Stronger transport and
credential isolation remains a review item before broad delivery dispatch.

## Validation and canary

Configuration validation: :ok. Live GitHub adapter: 228 open issues, zero eligible before
canary. Initial standalone adapter read lacked Req startup; corrected validation starts Req
explicitly, and passes. Existing adapter/App Server/workspace tests: 81 tests, zero failures.
Service definition validates after environment quoting correction; shell hook bash -n passes.
Installed protocol schemas generated locally; ephemeral no-inference handshake succeeded.

Canary https://github.com/Agoge-Toluwabori/Agoge-Business-Systems/issues/234 was the only
dispatch, with one GH-234 workspace. App Server session:
01a0821f-dd6f-73c0-a2a0-be91440c6458-01a0821f-ddfd-7100-8650-34ee366a39da.
Its first required repository read failed: bwrap: setting up uid map: Permission denied.
No marker, no running label (preflight did not pass), no task commit, no application changes.
The agent posted exact evidence, removed ready, added symphony-blocked, left canary OPEN.
The orchestrator stopped it after label removal. No interactive approval or fallback was used.
Workspace remains clean at 4919ab4 on symphony/GH-234. No human-review success claim.
All original 228 open issue states and labels are unchanged; none is ready/running.
Post-canary dashboard has zero running/retrying workers. Evidence files record the snapshots.

kernel.unprivileged_userns_clone=1 and kernel.apparmor_restrict_unprivileged_userns=1.
AppArmor is a likely cause, not confirmed: this account cannot read system kernel audit logs.
Owner/admin review is required for a narrowly scoped sandbox compatibility remedy.
Do not disable AppArmor globally or select full access. Do not label delivery issues until
a safe remedy and successful canary are reviewed. This run did not change kernel security.

## Service operation

Non-root user service symphony-agoge.service is enabled, active and idle after canary.
Restart=on-failure, RestartSec=15, bounded start retries; KillMode=control-group.
Linger=yes verifies login-independent reboot startup configuration without rebooting.
Actual reboot recovery and crash injection were not tested. Dashboard 127.0.0.1:4000 only;
no firewall changes. OTP rotates logs at 10 MiB x 5 under
/home/toluadmin/services/symphony-logs/agoge/log/symphony.log.*.

Owner commands (as toluadmin):

```sh
systemctl --user start symphony-agoge.service
systemctl --user stop symphony-agoge.service
systemctl --user restart symphony-agoge.service
systemctl --user status symphony-agoge.service --no-pager
journalctl --user -u symphony-agoge.service -n 100 --no-pager
tail -n 100 /home/toluadmin/services/symphony-logs/agoge/log/symphony.log.1
curl --silent http://127.0.0.1:4000/api/v1/state
```

Emergency stop and prevent reboot dispatch:

```sh
systemctl --user disable --now symphony-agoge.service
```

Also remove symphony-ready from any pending authorized issue before restarting.
Re-enable only after review with systemctl --user enable --now symphony-agoge.service.
Remote dashboard access should use an SSH tunnel to localhost; do not expose port 4000.

No product implementation, application push, PR, merge, deployment, Supabase mutation,
Vercel change, DNS/firewall mutation or paid-service activation. Canary used existing Codex
account capacity; no new paid service was activated and billing was not independently audited.
GitHub mutations were the supporting labels, one canary and its lifecycle/evidence only.

Additional core orchestration tests: 52 tests, zero failures (seed 777846).
Total targeted tests: 133, zero failures; no Symphony code changed.
