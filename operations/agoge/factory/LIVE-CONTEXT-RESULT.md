# Live dispatch-context repair result

Repair commit: 203e6ce11b37da588589725bde6f15aee5ac1e39 on
codex/agoge-delivery-factory-v1 in the durable factory worktree.
Reinstalled successfully. Exactly one actual App Server session launched through
the installed symphony-agoge.service; no manual Codex simulation substituted for it.

The prior context/attestation defect is repaired and live-verified. Host preflight
passed, the reconciler automatically restored only #236 after the documented
pre-claim failure, and factory_context delivered verified service, invocation,
approved batch, workspace, native preflight, concurrency and actual session IDs.
The worker claimed the issue, edited harmless documentation, validated local
files and created a local evidence commit without interactive approval.

Service invocation: 131b8426f3644a27bba2f5578cc87432.
App Server PID: 44316.
Thread: 01a0846f-81df-7d02-8767-b685f203cd33.
Turn: 01a0846f-83c4-7fd0-bfb6-6748dc61acbb.
Session: 01a0846f-81df-7d02-8767-b685f203cd33-01a0846f-83c4-7fd0-bfb6-6748dc61acbb.
Canary branch: symphony/GH-236-20260909T043134Z.
Canary local commit: 8ef880f00c74395e262ef9eb702d2eca7290bec0.
Workspace: /home/toluadmin/services/symphony-workspaces/agoge-business-systems/GH-236.

## Canary acceptance remains blocked

Lifecycle: Claimed → Implementing → Validating → Blocked. Human Review success
was not claimed. The unchanged supplied probe raised OSError EINVAL on setuid(0),
which its PermissionError-only handler does not catch. It stopped before the
network check and results-file write. This is an unhandled probe result, not
proof that root privileges were obtained or a reason to widen permissions.

All four GitHub negative calls returned the generic redacted error. Source review
and passing local transport-sentinel tests establish that these requests are
rejected before Client.request; however the returned error text does not let the
worker distinguish a policy rejection from other failures. The live canary
therefore correctly declined to certify those tests. The missing safe explicit
factory_operation_denied response is a separate diagnostic defect.

These two newly exposed probe/reporting defects were not treated as a passing
canary. No second dispatch was authorized or performed. No true host-permission
blocker was found; another start command alone would not repair these defects.
They require local code/test repair before a separately authorized new canary.
The repair-specific recovery receipt prevents automatically clearing this new
validation failure on a restart.

Final issue evidence:
https://github.com/Agoge-Toluwabori/Agoge-Business-Systems/issues/236#issuecomment-5595845752

## Completed verification

Full local make all: 300 tests, zero failures, six existing skips, 100% reported
coverage, passing formatting/lint/build and zero Dialyzer errors. Factory tests:
36 passed, including missing-context reproduction, actual App Server tool-call
round trip, substituted identity rejection, one-launch guard and narrow recovery.

The host batch report records boundary=true with no selected or ready task.
The supervisor stopped and disabled Symphony. Independent final service check:
MainPID=0, ActiveState=inactive, UnitFileState=disabled. Exactly one session-start
event was observed in this invocation. Earlier workspaces and issue comments are
preserved. #235 was not executed, prepared or changed. No application push,
Vercel invocation, provider mutation, deployment, production, DNS/firewall action,
paid operation or credential expansion occurred. Only the authorized GitHub issue
lifecycle/evidence updates and private control-plane/canary files changed.

Raw retained evidence: evidence/dispatch-context/live-*.json and *.txt.
