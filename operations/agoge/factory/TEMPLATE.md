# Agoge Delivery Factory — autonomous GitHub template

This is the current standing operating model. The earlier batch template is
preserved in TEMPLATE-batch-history.md as historical evidence, not active policy.

## Business binding

Copy continuous/project.json for onboarding. Set the exact repository identity,
integration branch and verified foundation ancestry, Project/control-plane IDs and
status/Authority mappings, full test commands and required check names, protected
paths, production/provider exclusions, and authorized concurrency (currently one).
Node, package-manager and browser/runtime cache paths are installation defaults;
reuse the installed pinned tools. No new orchestrator or generic broker is needed.
The current ABS binding is separate from reusable Python policy under continuous/.
Use the configured Project Authority field (ABS: Factory Authority); the older ABS
Authority field remains historical and does not grant execution.

## Standing authority and queue

An exact-repository open issue is eligible only with Project Ready and Autonomous
Development authority, satisfied native/Project dependencies, and no planning-only,
blocked, human-review, owner-gate, prohibited or canary classification. No approved
batch, execution label or individual owner confirmation is required. The controller
derives factory-dispatch and routine labels. Never infer provider authority.

Ready → Claimed → Implementing → Validating → GitHub Integrated → Completed.
Existing Project equivalents are used: Claimed/Implementing/Validating map to
In Progress; GitHub Integrated maps to In Review; Completed maps to Done. Evidence
records the exact phase. The selector verifies dependencies again before dispatch.
A single persistent lease plus service locks and Symphony concurrency one prevent
two issues from sharing a workspace. Empty queues poll again. Bounded recoverable
failures retain the issue branch and dirty work. External blockers are consolidated
on the issue; unrelated eligible issues continue. A missing worker launch times out
with preserved evidence instead of silently wedging the queue.

## Worker and environment boundaries

Non-root Codex App Server has approval_policy=never and a native workspace-write
profile: root denied, minimal runtime readable, only the assigned workspace/private
Git metadata writable, credentials and unrelated repositories inaccessible. The
managed Codex network namespace permits local IPC; an empty destination allowlist
rejects all external requests. This is required for Node subprocess capture and
private Playwright tests; it does not grant provider or direct GitHub access.
Local tests bind loopback and use NO_PROXY only for loopback. Private owner testing
uses the established SSH tunnel; no public listener/firewall change is authorized.
Existing systemd hardening/resource limits and AppArmor remain intact.

The App Server's existing model authentication is referenced outside the worker
filesystem. Host GitHub credentials are filtered from the worker environment.
The dynamic GitHub tool permits exact-repository reads and only assigned-issue
comments/lifecycle labels. Host code performs fixed-repository/ref publication.
No arbitrary host shell, credential expansion or model-controlled API route exists.
Zero-cost semver dependencies use a credential-free staging sandbox, scripts and
Git disabled, and an npm-only CONNECT proxy; application code runs only inside the
native worker/validation sandbox. No package manifests may select arbitrary URLs.

## Validation and GitHub delivery

Run baseline checks, implement documented acceptance criteria, run relevant tests
and full required CI, commit locally, and hand off the exact SHA. The host makes a
fresh private validation clone, checks accepted ancestry, current integration base,
protected paths, secret signatures, unchanged acceptance scripts, and reruns CI.
It pushes only symphony/GH-number-scoped branches, creates an integration PR, waits
for configured automated checks, rechecks authority/head/base, and merges using
repository governance (merge or squash). It records tested SHA, PR, merge SHA,
validation log and rollback instructions before closing the issue.

Force pushes, branch/tag deletion, direct main/integration pushes, repository
transfer/deletion, secrets/billing changes and unrelated repositories are denied.
A worker cannot manufacture completion by closing its issue directly. GitHub
integration is not production deployment or production acceptance. All deployment,
preview publication, Vercel/provider configuration and production releases are
owner-managed outside this factory. Production data never enters a workspace.

## Decisions

Resolve naming, ordinary engineering choices, reversible trade-offs, safe dependency
selection, scoped conflicts and repairable failures autonomously. Ask one consolidated
owner decision only for materially contradictory product requirements, production or
main release, paid resources, unavailable access, real customer/donor data, live
provider/DNS/firewall changes, irreversible destruction, or weakening a gate.

## Installation, stop and recovery

From the durable reviewed checkout run `python3 operations/agoge/factory/install.py
--continuous` (on one line), then `systemctl --user enable --now symphony-agoge.service`.
The installer validates concrete components/runtime before replacement, retains
original and intervening versions, preserves credentials, and leaves the service
stopped until explicit activation. Rerunning is idempotent and rejects unexplained
drift. Never substitute a temporary checkout for the durable branch.

Emergency stop: `systemctl --user disable --now symphony-agoge.service`.
Rollback: stop, then `python3 operations/agoge/factory/install.py --rollback`.
Rollback restores only manifest-owned files and removes only the factory auth
symlink, never its target. Workspaces, branches, commits, evidence and logs remain.
Task cleanup archives complete private checkouts; never delete shared Git objects.
Code rollback is a new revert PR into the integration branch, never a history reset.
After an interrupted delivery, reconcile the existing exact-SHA PR and lease before
retrying; a confirmed already-merged PR is finalized idempotently.

Project polling requests only required control fields, with explicit pagination.
When the GraphQL budget is low, polling waits until reset while remaining enabled;
health records the next poll delay. No credential rotation/expansion is needed.
