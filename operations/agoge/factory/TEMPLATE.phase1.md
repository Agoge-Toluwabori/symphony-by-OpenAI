# Agoge Delivery Factory V1 adoption template

Status: control-plane implementation for review. The VM containment and provider
brokers described below are required integration work, not capabilities supplied
by this template. Do not activate an ordinary same-user Codex process in their place.

## Repository onboarding

Create a separate controller checkout, workspace root, evidence root and service
for each business. Record owner, exact repository slug, Project ID, default branch,
approved requirements, baseline commit, validation commands and development DB
version. Preserve existing branches, commits, worktrees and governance. Add a
current standing-contract section to repository AGENTS.md and governance before
onboarding product batches; retain dated historical records. The controller
workflow contract overrides obsolete planning prohibitions within an approved
batch, never unrelated product constraints. No application work is approved by
onboarding alone.

Copy batch.json and WORKFLOW.md; replace repository/path/Project values. Explicitly
approve the batch once with its source, ordered issue list, authority and verified
dependencies. Match provider.agent_issue_numbers to the approved task IDs. The
manifest is outside worker mounts and is never editable through the agent API.
GitHub Project Factory Authority displays the three classifications; legacy
Authority is historical context. The manifest is canonical for positive grants;
explicit issue gate/prohibited labels can stop work. Do not grant authority from
Project Ready, an assignee, or a bare symphony-ready label. New projects should use
Authority directly with Autonomous Development, Owner Gate, Prohibited options.

## Standing development authority

Autonomous Development tasks in an approved batch may inspect repositories and
governance; create isolated branches/workspaces; edit; install approved pinned free
dependencies; build/test/lint/security-check; run local PostgreSQL with synthetic
data and development migrations; commit; run private VM development services;
use SSH tunnels; publish development branches/PRs after publication verification;
create previews after preview isolation; update task evidence and Project fields;
retry bounded transient failures and continue through the approved batch.
No ordinary command requires interactive approval. Historical “Never push” and
blanket provider-inspection prohibitions are replaced by environment-specific gates.
An ordinary issue can narrow what to build, but cannot silently revoke these
capabilities. Explicit Owner Gate/Prohibited classifications stop the task.

Owner Gate: production promotion/deployment, production/customer-data access,
external DNS/firewall, paid activation/incremental spend, credential provision or
expansion, destructive data, rewritten history, permanent material deletion,
unresolved product decisions and milestone acceptance. A worker records one
concrete decision and supporting evidence; it cannot execute production actions.
Prohibited: unrelated repositories, production customer data, direct production
deploy/DNS/billing, root escalation, credential exposure. No issue can override the
technical boundary. An owner-controlled release process is a separate principal.

## Queue and concurrency

Approved Batch → Eligible → Claimed → Implementing → Validating → VM Integrated →
Human Review (Project In Review) → owner Accepted/Done. Keep completed issues open
until acceptance. Represent accepted dependency evidence with accepted plus closed;
closed alone and human-review alone do not qualify dependencies.

queue.py queries paginated issues and native blocked_by relations, combines them
with manifest dependencies, fails closed on unknown/cross-repository dependencies,
and picks the first eligible task in manifest order. The batch owner must migrate
text-only dependencies from issue prose/Project Depends On into this manifest before
approval; the worker also verifies live dependencies before claim. Missing API data
is not an empty dependency list. Labels are maintained by the controller, not the
owner. Blocked tasks do not stall independent work. No approved batch means no work.

run.sh takes a lifetime flock, reconciles stale labels before starting Symphony,
then maintains the derived queue with a 30-second poll. Symphony concurrency is one;
active/retrying entries prevent another selection. symphony-running means a live
claim, not generic intent. Never clear a stale running label until the prior process
and task services are proven dead. Unknown controller health fails closed; three
consecutive reconciler failures stop its controller. When no eligible task remains,
stop and retain batch-report.json. This includes completed/review-only and externally
blocked boundaries; it never starts another batch automatically. The worker prompt bounds command retries; the reconciler retires execution labels
after three runtime attempts and records an infrastructure blocker. The controller
then releases that retry and selects unrelated eligible work.

## Credential and environment boundary

The controller holds a short-lived GitHub App installation token restricted to this
repository. Issues write/metadata read suffice for the included API tool. Contents
and PR writes belong to a separate publication broker; no administration, Actions,
organization or unrelated-repository grants enter the worker. Project updates use a
separate controller credential and cannot change the canonical batch authority.
Keep all secrets outside worker mounts, scrub inherited environment, disable user
MCP/plugin inheritance, redact headers and upstream error payloads. Mode 0600 alone
is not a boundary for processes sharing an identity.

Install an administrator-owned /opt/agoge-factory/bin/isolated-codex. It must start
Codex App Server under a dedicated non-root identity or equivalently verified mount,
PID, user and network namespaces. Mount only its task workspace, required read-only
runtime/toolchain and a credential-free private HOME. Do not mount host /home, root
filesystem wholesale, SSH agents, Docker/systemd sockets, host /proc, production
config or unrelated repositories. NoNewPrivileges, empty capabilities, no sudo,
restricted process visibility and default-deny outbound network are mandatory.
Preserve the existing narrowly scoped AppArmor/bubblewrap remediation.

Inference, pinned package downloads and development publication must use host-side
brokers. The worker never receives bearer tokens. The inference broker uses existing
approved capacity, never creates a paid resource. Dependency broker permits approved
zero-cost pinned artifacts. Publication broker permits only this repository's
codex/** and symphony/** branches, denies main/tags/force-push/merge, and checks
trusted #235 evidence before publishing application code. It must refuse workflow
or infrastructure changes that could bypass the guard. A narrow #235 operation
accepts only a harmless branch artifact after the guard is configured. Provider
broker validates the exact team/project and exposes only guard inspection/config
operations; it cannot deploy, promote, alter DNS, change billing or create resources.
No general proxy with a broad provider token qualifies.

The launcher --verify-boundaries must execute adversarial probes: host credential
and sibling-repo reads denied; symlink traversal denied; root/capability attempts
denied; direct outbound connections denied; production, billing and cross-repo
broker calls denied; allowed workspace edit/build/test/local commit succeeds;
AppArmor/bubblewrap works; sentinel credentials do not reach stdout/stderr, tool
results, Git objects or logs. Include an actual App Server no-approval dispatch
using a synthetic task. preflight.py invokes this trusted verification and fails
closed on missing/failing launcher. Do not implement it as a constant-success stub.

## Workspace, VM integration and owner testing

Use one distinct GH-N clone per issue under the configured workspace root; never
run in the source checkout. Preserve failed attempts and committed evidence before
fresh attempts. The trusted before_run workspace manager archives every prior attempt, including
Git objects and dirty evidence, then clones a fresh default-branch workspace.
Resuming a partial implementation requires explicit inspection/import of retained
commits; the prior attempt is never silently reused or erased. Record baseline SHA and checks,
final SHA/checks, commit evidence, active services and test-data provenance. Stop
task services at release. Archive evidence and Git objects before safely removing
only task-specific clean worktrees. Never remove a repository or material resource
as routine cleanup. The workspace hook preserves prior repositories and disables direct push.

Run development PostgreSQL with a workspace-local Unix socket and synthetic data;
never import customer dumps or production connection strings. Pin the approved major
version; PG18 does not prove PG17.6 compatibility. Bind development apps to loopback
only and use the approved SSH pattern:

```sh
ssh -N -L 3000:127.0.0.1:3000 toluadmin@VM_HOST
```

Owner opens http://127.0.0.1:3000 locally. Do not expose VM firewall ports. Isolated
worker network namespaces require a trusted loopback forwarding broker; no public
listener is implied. VM Integrated means the synthetic development flow passed,
not production or hosted migration readiness.

## Preview publication and production release

First prove #235: exact GitHub/Vercel ownership, trigger rules, selected guard,
harmless branch SHA, deployment-history evidence of no production or preview build,
rollback procedure. Store evidence outside worker control. Only then enable the
publication broker. Preview requires a separate isolated provider project, free
approved capacity, synthetic/dev data, scoped auth and proof that promotion to
production is unavailable. Owner reviews the completed milestone. Production release
is a distinct owner-authorized process with separate credentials, backups and gates;
development completion never grants production authority.

## Evidence and recovery

Per task record requirements, dependencies, phase transitions, baseline/final checks,
base/final commits, artifacts, private testing instructions and external blockers.
Consolidate the batch into one report with every task disposition and evidence links.
The included queue report consolidates task dispositions and issue evidence links.
Detailed commands, commits and artifacts remain in the linked task evidence comments.

Emergency stop:

```sh
systemctl --user disable --now symphony-agoge.service
```

Verify inactive/dead, no controller/worker/task-service processes, and retained
workspaces. Remove eligibility only after stopping the worker, without erasing
comments. Preserve stale claims until process death is verified. On recovery inspect
Git status, archive dirty attempts, verify dependencies and retained commits, rerun
boundary probes and resume the same approved batch. Never mark unfinished work Done.

Installation backs up the old unit with a UTC timestamp. Rollback stops/disables the
service, restores the backed-up unit and prior workflow, daemon-reloads, and remains
stopped. Never reactivate the obsolete permissive environment as part of rollback.
Revert control-plane commits normally; never reset/rewrite history. Restore metadata
with a new explanatory comment; preserve the prior Project README in this package.
