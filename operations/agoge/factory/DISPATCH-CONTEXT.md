# Dispatch context repair — live result recorded separately

The complete latest journal confirms selector success at 04:00:35 UTC, App Server
PID 38430/session start at 04:00:42, and normal turn completion at 04:01:59.
The newest #236 comment (5595585486) identifies missing controller evidence before
claim. Missing rg was bypassable. The earlier Bubblewrap problem was repaired.
No selector repair or broader sandbox permissions are required.

The worker was asked to verify service identity, native preflight, concurrency,
App Server session and batch stop/disable, but received only the issue prompt,
workspace and probe. The launcher deliberately filters environment; host state is
unreadable under root-deny. Symphony knew the protocol session IDs but supplied
them only to logs/controller telemetry, not to the worker. Requiring a completed
batch stop before claim created an impossible temporal dependency.

The revised service verifies local installation before selection, then records
systemd invocation/cgroup identity, disabled unit state, unchanged hardening,
no-restart policy, approved one-task batch, concurrency and native policy. The
launcher verifies the exact private workspace and writes a protected dispatch
receipt before exec. Exclusive creation limits actual App Server launch to one
per invocation. No auth or secret environment values appear in the receipt.

`factory_context {}` is a read-only native dynamic tool advertised only for the
bound Agoge tracker policy. The host reads its protected receipt and checks issue,
workspace and invocation against the live controller context. It adds thread and
turn IDs from actual protocol responses and their Symphony session ID. Tool
arguments cannot substitute identities. Every verification field is logged as
verified, missing or invalid; missing evidence fails closed.

Host installation checks do not require a session that does not exist yet.
Worker claim checks run after thread/start and turn/start have returned. Batch
stop is a host post-run check, not a pre-claim prerequisite. The installed workflow
explains these phases, authorizes the supplied negative probe and identifies
ordinary search-tool fallback as bypassable.

Only the documented #236 controller-evidence pre-claim failure is automatically
cleared after current repaired service preflight succeeds. A repair receipt makes
that recovery single-use. Unknown blockers, dependencies, gates and review states
are not cleared. A new explanatory comment preserves old evidence. The queue
terminates the invocation after its first worker exits even if a retry is queued;
the launcher independently prevents another actual launch. No #235 write occurs.

Containment, approval_policy=never, native permissions, environment filtering,
repository/API restrictions and systemd limits remain unchanged. No outer sandbox
or credential broker is added. Host state and historical workspaces are retained.

Validation: `bash operations/agoge/factory/validate.sh`. Tests reproduce missing
context, validate actual App Server tool-call round trips and thread/turn identity,
reject substituted arguments/issues, check one-launch receipts, and test narrow
blocked-canary recovery after preflight. Full test output is retained under
`evidence/dispatch-context/`.

Install and execute only the authorized one-task canary, always stopping/disabling
the service afterward (ten-minute observation limit, no retry):

```sh
bash /home/toluadmin/services/symphony/.factory-preservation/worktree/operations/agoge/factory/run-canary-once.sh
```

Rollback remains `install.py --rollback`; new dispatch/recovery receipts and all
historical evidence are deliberately retained. Normal delivery and #235 execution
remain unauthorized in this run.

Local validation completed before installation: 300 Symphony tests, zero failures,
six existing live-test skips, 100% reported coverage, clean formatting/lint/build
and zero Dialyzer errors. All 36 factory tests pass. Live execution is not inferred
from these local results.
