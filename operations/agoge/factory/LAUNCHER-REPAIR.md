# Launcher repair — reinstall and live canary required

The 2026-09-09 repair passes direct native sandbox diagnostics. Symphony was
never started in this repair; #236 was not dispatched and #235 was not changed
or executed. This is not proof of a completed live containment canary.

## Cause and controlled reproduction

The installed run.sh and launcher do not wrap Codex in an outer network namespace.
Symphony starts the filtered Codex App Server; native permissions are explicitly
selected at thread/start and turn/start. The former native profile set
shell_environment_policy.inherit=none and include_only=[], removing PATH from
model commands even though the host launcher supplied PATH. Codex 0.153.4 then
could not discover /usr/bin/bwrap and executed its bundled fallback via
/proc/self/fd. Under the unchanged service hardening this failed configuring
loopback with `Failed RTM_NEWADDR: Operation not permitted`.

This differs from the owner's successful test, which explicitly executes the
AppArmor-approved /usr/bin/bwrap. It is executable selection, not an outer
factory namespace or incompatible systemd hardening. The before/after execution
traces establish the difference without changing AppArmor, system binaries,
Codex resources, namespace flags or service restrictions.

The diagnostic matrix ran `/bin/true` through `codex sandbox -P factory-canary`
in harmless temporary workspaces under transient systemd units with the exact
NoNewPrivileges, LockPersonality and RestrictSUIDSGID properties:

| Policy | Result |
| --- | --- |
| Original installed profile | Exit 1: RTM_NEWADDR; bundled fallback traced |
| Fixed command PATH only | Exit 1: duplicate .agents/.codex mount targets |
| Also remove duplicate directory denies | Exit 1: hidden Codex executable on sandbox re-entry |
| Also grant exact resolved Codex binary read | Exit 0 |

The native workspace profile already protects .codex and .agents as read-only.
Additional deny rules emitted file masks over those directory mounts. Removing
only those duplicate entries retains their native write protection. Root-deny
also hid the Codex binary needed for seccomp re-entry; the installer now renders
one exact executable read grant, never a grant to the credential directory.
Finally, the harmless Git test identified native read-only .git protection.
An explicit task-local .git write grant permits authorized local commits; the
launcher requires private clone metadata and rejects symlinks and alternates.

## Current architecture

One native Codex workspace sandbox, approval_policy=never, root denied, minimal
runtime readable, workspace and private clone .git writable, exact Codex runtime
readable. Command PATH and host launcher PATH are fixed to /usr/bin:/bin.
Credentials are filtered from model commands and host credential paths remain
unreadable. Canary network access remains entirely disabled, which also blocks
production, billing and DNS endpoints before any connection. Host GitHub tools
retain the repository/current-issue allowlist. Concurrency stays one; all existing
systemd hardening/resource limits remain unchanged. No broker was added.

The App Server strict configuration and initialize handshake pass with the
launcher-filtered environment and rendered profile, without auth or a model turn.
Actual Symphony dispatch remains a separate required live canary.

## Installation and rollback

The installed service points to this durable checkout, but its copied native
policy remains old. The revised launcher/preflight reject that stale policy.
The runtime grant is rendered from the resolved installed Codex binary; upgrading
Codex requires reinstalling the policy. Reinstall checks prerequisites and leaves
the service disabled and stopped. Existing Codex-added trust metadata is accepted
only for direct GH-number workspaces and only when every security setting matches
the recorded baseline. Unknown configuration edits still fail closed.

Original installed files and every replaced version, including trust metadata,
are preserved in installation.json. Rollback retains snapshots in
installation.rolled-back[.unique-id].json, restores original files and removes
only the factory auth symlink, never its credential target. Historical rollback
manifests are not overwritten. Read-only inspection confirmed the currently
installed files have only the supported trust-metadata drift.

Reinstall (non-root host session; does not start Symphony):

```sh
python3 /home/toluadmin/services/symphony/.factory-preservation/worktree/operations/agoge/factory/install.py --canary
```

Only after reinstall succeeds, start the one-task #236 canary without enabling
normal delivery:

```sh
systemctl --user start symphony-agoge.service
```

Emergency stop:

```sh
systemctl --user disable --now symphony-agoge.service
```

Rollback (factory-owned files and service only):

```sh
python3 /home/toluadmin/services/symphony/.factory-preservation/worktree/operations/agoge/factory/install.py --rollback
```

## Validation evidence

Evidence is in `evidence/launcher-repair/`. The repeatable diagnostic is
`python3 operations/agoge/factory/tests/launcher_probe.py`; it uses transient
systemd units, no Symphony dispatch and no credentials. Its temporary clone is
removed after the test. It passes harmless edit, validation and local commit;
protected credential/unrelated repository reads, root escalation and network
socket creation are rejected. Execution tracing verifies system Bubblewrap.
Earlier diagnostic failures remain in separate evidence files.

Factory unit tests: 32 pass, including environment filtering, private Git metadata,
policy rendering, trust-only migration, security-drift refusal, reversible install,
queue selection, authorization precedence, dependencies and concurrency/batch limits.
Full Symphony `make all`: successful setup/build, formatting, lint, coverage and
Dialyzer. 299 tests, zero failures, six existing skips, 100% reported coverage;
Dialyzer zero errors. Complete output is in symphony-suite.txt. Existing live E2E skips
remain skips; they are not a substitute for #236.

No application push, provider mutation, deployment, production action, credential
change or incremental resource spending occurred. #235 remains unexecuted.
Service completion state: disabled, inactive/dead, MainPID=0. Remaining step:
owner-session reinstall followed by the separately authorized live #236 canary.
