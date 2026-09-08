# Agoge Delivery Factory V1 review report — 2026-09-08

**Certain: the control-plane review package is implemented, and #235 is prepared
but not executed. Live activation remains blocked by missing verified worker
containment and scoped brokers. This is not a claim of production isolation or
successful live unattended factory execution. The installed service remains
inactive/dead and disabled.**

## 1. Former approval-loop root cause

The installed workflow treated a manually applied symphony-ready label as the sole
business grant, unconditionally prohibited pushes/Vercel/provider actions, and
classified sandbox failures as owner blockers. #235 explicitly authorized the
opposite narrow guard work. Historical AGENTS.md, Project README and Batch1 records
also retained planning-only/per-task authorization. Technical inability and
business authority were conflated. #235's prior comment proves the instruction
conflict; it does not prove authentication failure. The later successful #234
canary proves the prior bubblewrap failure was remediated for that execution;
it does not prove host credential/network isolation.

Reviewed: original workflow and activation evidence; both repository statuses;
AGENTS.md, Status, Decision Register, master instruction; Batch1 completion report
in `_worktrees/batch1-96/docs/05-delivery/vm-batch-1`; live #234/#235 comments and
native dependencies; Project #1 fields and README. Historical evidence is retained.

## 2. Files and configuration

All code changes are in the independent local review clone
`/tmp/agoge-delivery-factory-v1`, on `codex/agoge-delivery-factory-v1`.
The existing Symphony `.git` is mounted read-only; its branch-creation attempt
failed once. A no-hardlinks local clone safely preserved all history without
changing either original repository, branch, worktree or commit. No Git history
was rewritten. Keep this /tmp review clone until it is adopted to durable storage.

Changed: scoped GitHub AgentTool and tests; root/Elixir README, SPEC and example
workflow extension documentation; operations/agoge WORKFLOW, service template,
workspace-create hook and historical-report supersession. Added factory manifest,
queue/supervisor, activation preflight, installer, workspace archive hook, tests,
reusable template, #235 comment, prior Project README and evidence. A local
.gitignore excludes Python bytecode; generated builds/caches are not committed.

No original application AGENTS/governance file was edited because this run performs
no application work and its original Git metadata is read-only. The new worker
contract and Project supersession explicitly govern approved batches. Repository
onboarding instructions describe adding the standing contract before future batches.

## 3–5. Authority, lifecycle and automatic batch selection

The host-controlled batch manifest grants Autonomous Development standing authority
once for an ordered batch; Owner Gate and Prohibited are explicit alternatives.
The sole initial approved task is #235. Ordinary issue prose does not silently
revoke development capabilities; actual product scope is still preserved. Project
Ready or assignment alone grants nothing. The new Factory Authority Project field
preserves the legacy Authority field and existing records rather than overwriting
their historical meanings. Positive authority is canonical in the host manifest;
explicit issue Owner Gate/Prohibited labels also stop selection.

Approved Batch → Eligible → Claimed → Implementing → Validating → VM Integrated →
Human Review / In Review → owner Accepted/Done. Running means claimed; completed
issues stay open in review. A closed dependency must also carry accepted. Native
blocked_by and manifest dependencies are combined; text-only dependencies must be
normalized during batch approval and checked again by the worker before claim.
Unresolved independent issues do not block one another.

The reconciler derives ready labels, removes stale out-of-batch readiness, respects
live controller running/retrying entries, and uses manifest order. A lifetime flock
and concurrency one prevent multiple controllers/tasks. Prior workspaces, Git
objects and dirty evidence are archived before each fresh attempt. Runtime retry
budget is three attempts; reconciliation failures stop the controller after three
consecutive failures. At an exhausted, review-only or blocked batch boundary the
supervisor stops and retains a consolidated batch report with task/evidence links.
It never automatically approves or enters another batch.

## 6–7. Permissions and technical protections

Workflow validation accepts concurrency one, approval_policy=never,
thread_sandbox=workspace-write, turn workspaceWrite, networkAccess=false,
excludeSlashTmp=true and excludeTmpdirEnvVar=true. The existing installed Codex
protocol schema supports never; existing App Server tests exercise no-approval
behavior. The launch command requires an administrator-controlled isolated launcher.
The service uses NoNewPrivileges, restrictive umask, control-group termination,
no automatic restart and a fail-closed preflight.

The new host API filter enforces exact repository paths, canonical paths, a batch
issue allowlist AND the trusted current issue ID for writes. It permits repository
reads and current-task evidence/lifecycle operations. It rejects production,
billing, unrelated repositories, merges, authority grants, out-of-task claims,
issue closure and path-encoding/traversal bypasses. The worker cannot add ready.
Raw upstream error details are suppressed. Direct Git push URLs stay disabled;
publication must go through a verified host broker. No application publication is
possible through this API filter; the publication broker has not been installed.

**Remaining prerequisite:** provision and verify the isolated launcher, separate
worker visibility/identity, default-deny egress and credential-free inference,
dependency, GitHub publication and narrow provider brokers described in TEMPLATE.md.
No scoped credentials were provisioned or expanded in this run. Existing broad
credentials, same-UID read access and App Server authentication cannot safely be
converted into those capabilities through a workflow flag. The required executable
is absent and preflight rejects activation. Host configuration outside writable
roots cannot be installed here. No unrestricted host access was substituted.
Changing containment.json to “verified” cannot bypass preflight. The trusted
launcher must actually execute --verify-boundaries probes; a success stub is invalid.

## 8. Validation

| Check | Result and practical limit |
|---|---|
| Workflow/schema | PASS: Config.validate! = :ok; never / concurrency 1 / restricted writes / direct network off |
| Python queue/workspace suite | PASS: 20 tests, including authority precedence, dependency acceptance/native/unknown state, blocked continuation, batch boundary, concurrency, retry budget, idempotence, Git history preservation and symlink escape |
| Targeted Symphony suite | PASS: 126 tests at initial stage; subsequent API changes covered by full suite |
| Full Symphony tests | PASS: 299 tests, zero failures, six opt-in live tests skipped |
| Coverage | PASS: 100% on final code, including trusted current-issue binding |
| Format, lint, public specs, build | PASS: final make all exit 0; evidence/full-gates.txt |
| Dialyzer | PASS: zero errors; final make all exit 0 |
| Service syntax | systemd-analyze verify exit 0; emitted private-socket address-in-use warning in this session |
| Hook/supervisor shell syntax | PASS |
| Synthetic edit/build/test/local commit | PASS in temporary Git fixture; preserves commit and dirty evidence on archival. Not a live Codex worker proof |
| Production/paid rejection | PASS at scoped GitHub transport; no real production/paid operation attempted |
| Credential redaction | PASS: injected upstream sentinel is absent from tool results. Not a full host credential isolation proof |
| Dispatch dry run | PASS: synthetic and live read-only queue select only #235; no inference or product execution |
| Live isolated-worker dispatch | NOT RUN: required launcher/brokers absent; activation preflight fails closed |
| #235 execution / application push | Neither performed |
| Service final state | inactive / dead / disabled |

Initial validation issues were repaired without approval prompts: wrong clone
working-directory commands, mise trust-cache writes (used explicit installed
runtime paths), Hex cache permission (used disposable copied package/cache roots),
API filter complexity (factored helpers), and missing lifecycle coverage (added
behavior tests). No denied original Git operation was retried. Existing AppArmor,
credentials, system configuration and application worktrees were preserved.

## 9. Branch and commit

Branch: `codex/agoge-delivery-factory-v1` in the independent clone. The final response
and `git log -1` give the local commit SHA. The report is part of that same commit;
embedding its own SHA would change the SHA. No branch was pushed.

## 10. Issue #235

Open; Factory Authority = Autonomous Development; approved batch
factory-v1-publication-guard; Project Status Ready; symphony-ready present;
symphony-blocked removed; symphony-running absent. Native blocked_by is empty.
No #235 worker was dispatched. Provider ownership/access and publication isolation
remain unverified. The initial batch has no other tasks. Old conflict evidence was
preserved and superseded only by a new explanatory comment:
https://github.com/Agoge-Toluwabori/Agoge-Business-Systems/issues/235#issuecomment-5592339515

## 11–12. Owner installation/activation and emergency stop

One guarded owner command after review and completion of the containment prerequisite:

```sh
bash /tmp/agoge-delivery-factory-v1/operations/agoge/factory/install.sh && systemctl --user enable --now symphony-agoge.service
```

It currently refuses installation because the required isolated launcher/brokers
are missing. It does not provision them or request/expand credentials. This command
cannot alone resolve the integration prerequisite. Do not start the old installed
unit directly: it still references the obsolete bootstrap workflow. The installer
backs up that unit, installs the reviewed unit and reloads systemd, leaving it
stopped until the explicit enable/start portion. A durable clone location is
recommended before installation; scripts discover their own location.

Emergency stop:

```sh
systemctl --user disable --now symphony-agoge.service
```

## 13–16. Template, blockers, spend and mutations

Reusable template: `operations/agoge/factory/TEMPLATE.md` (onboarding, boundaries,
authority, batches, lifecycle, credentials, VM/private testing, preview/release,
evidence, emergency stop, rollback and recovery).

Genuine remaining blocker: the host containment/scoped-broker integration and live
boundary verification above. This also prevents proving real worker edit/build/test
and provider/publication flows. No per-task development approval is required.
This review package is not a substitute for that missing technical work.

Zero incremental resource spend was activated by this redesign: no paid resources,
new accounts, billable provider operations or live worker inference runs. Used
existing VM/tooling and GitHub metadata APIs. Account billing was not audited.

No product implementation, application push, application deployment, provider
configuration mutation, production action, DNS/firewall change, hosted database
mutation or credential change occurred. GitHub issue labels/comment and Project
fields/README were explicitly authorized and changed. Therefore a literal claim
of “no hosted mutation” would be false; the only hosted mutations were that requested
GitHub control-plane metadata. No issue was accepted or closed by this run.


Adversarial review specifically checked traversal/encoded API paths, out-of-batch
and out-of-current-task writes, worker-created ready/accepted labels, ambiguous
closed dependencies, stale running/retry claims, duplicate workspace IDs and
symlink escapes. Reproduced API-scope and lifecycle-coverage gaps were fixed before
final validation; tests now reject those operations. The unresolved host boundary
is explicitly excluded from the passing security claims.
