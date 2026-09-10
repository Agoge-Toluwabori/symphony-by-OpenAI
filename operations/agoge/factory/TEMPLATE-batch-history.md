# Delivery Factory V1 — current adoption contract

DESIGN COMPLETE; ACTIVATION BLOCKED until installation and a live containment
canary pass. Phase 1's generic external-broker requirement is superseded. Its
original template is preserved in TEMPLATE.phase1.md as historical evidence.

## Onboarding and authority

Record exact repository, Project, default branch, baseline, validation commands,
workspace root and runtime paths. Preserve all history and existing governance.
Approve one explicit ordered batch, with Autonomous Development / Owner Gate /
Prohibited classifications and normalized dependencies. Do not derive authority
from Project status or a manually applied execution label. The current publication
batch remains approved but execution_enabled=false until containment is proven.

Development authority permits ordinary edits, approved free dependencies, builds,
tests, development-only PostgreSQL/synthetic data, local commits and private VM
services. Historical task-by-task prohibitions do not revoke this standing grant.
Production, customer data, DNS/firewall, paid activation, credential expansion,
destructive material changes, history rewriting, unresolved product decisions and
milestone acceptance remain owner gates. The worker has no production capability.

## Implemented containment route

Use the existing trusted Symphony/Codex App Server architecture. Native named
permissions deny host filesystem reads, permit minimal toolchain reads and allow
writes only in the task workspace. Shell environment inheritance is disabled.
The App Server's isolated CODEX_HOME has only the reviewed config and a symlink to
existing host authentication; credential contents are neither copied nor emitted.
Worker commands cannot read that home. Native profiles and legacy sandbox fields
must not be serialized together. Config supports codex.permissions and sends the
profile at both thread/start and turn/start; legacy workflows remain compatible.

The canary has no command network access. GitHub metadata goes through the existing
repository/current-issue restricted Symphony tool. No additional inference broker
is needed. No provider, deployment or publication tool is exposed in this canary.
No placeholder /opt launcher is required: launcher.py is included in this checkout.

Keep non-root execution, AppArmor/bubblewrap remediation, NoNewPrivileges, private
workspaces and service memory/process/CPU limits. Denial rules and credential
protection remain UNPROVEN on this VM until the actual canary executes. This
canary profile does not claim general dependency-download or provider access;
those capabilities require separately bounded, tested operations before use.

## Installation and rollback

Build with make all in elixir. Run install.py from a host session permitted to write
user-service/state directories. --canary installs only dedicated issue #236's
one-task batch. Default installation leaves the #235 batch paused. No installation
command starts a service. Existing service contents are backed up in a private
manifest; exact installed hashes prevent overwriting later owner edits. Reruns
are idempotent for unchanged installed files. --rollback stops/disables Symphony,
restores prior service/config content, and removes only factory-owned references
and files. It never removes the target authentication file or workspaces/evidence.
Do not claim installation success when required files or destinations are absent.

## Queue, evidence and recovery

Approved Batch → Eligible → Claimed → Implementing → Validating → VM Integrated →
Human Review → owner Accepted/Done. Concurrency and controller lock remain one.
The queue combines manifest/native dependencies, skips independent blocked tasks,
bounds retries and stops at the batch boundary. It cannot grant execution while
execution_enabled=false. Workers cannot grant ready labels or claim another issue.
Each attempt archives the prior workspace including dirty evidence and Git objects,
then creates a fresh clone/branch. Preserve evidence URLs, baseline/final validation,
local commit, session ID and exact failures. Never delete dirty material to retry.

## Private integration, publication and release

Use synthetic data, development-only local DB instances and loopback apps. Owner
access uses ssh -N -L 3000:127.0.0.1:3000 toluadmin@VM_HOST. Never open firewall/DNS
as a development convenience. VM integration is not production authorization.
Application pushes remain blocked until #235 proves the publication guard; previews
additionally require isolation proof. No arbitrary provider endpoints or credentials
may be added to this worker. Production release uses a separate owner-controlled
process. This package has not implemented or proven provider/publication access.

## Canary and emergency stop

#236 must run through the actual installed service/App Server, commit a harmless
marker, run the unchanged supplied negative probe, post lifecycle/evidence, reach
human-review and stop its one-task batch. A timeout is not a passing denial test.
Never use #235 as the canary. Keep #235 paused until external verification of the
live canary evidence, then prepare it unclaimed and leave Symphony stopped.

Emergency stop: systemctl --user disable --now symphony-agoge.service.
Verify no live PID, archive evidence and preserve claims until process death is
known. Roll back only factory files; never reactivate the old workflow implicitly.
