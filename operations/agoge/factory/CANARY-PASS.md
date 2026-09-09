# PASS — Delivery Factory V1 containment canary

Host verification:
https://github.com/Agoge-Toluwabori/Agoge-Business-Systems/issues/236#issuecomment-5596061913

Successful worker evidence:
https://github.com/Agoge-Toluwabori/Agoge-Business-Systems/issues/236#issuecomment-5596038288

Repair branch: codex/agoge-delivery-factory-v1.
Repair commit: 2fd84106d90edf13c25d69121f402673e50bac36
(first denial-evidence implementation: 836f7c06420b83e02a3fa0299e86090b849776e6).
Durable worktree: /home/toluadmin/services/symphony/.factory-preservation/worktree.

Successful canary branch: symphony/GH-236-20260909T045317Z.
Canary local commit: 5cc507a336ee4146df0bcd4e2db45849cad2d924.
Workspace: /home/toluadmin/services/symphony-workspaces/agoge-business-systems/GH-236.
Committed evidence: docs/05-delivery/checkpoints/GH-236/ (ten files).
Tracked checkout is clean; original supplied probe and generated results are also
retained untracked. No application branch was pushed.

Service invocation: 58882b4cdb0e4d9c9a952468ddc5045b.
App Server PID: 51354.
Actual session: 01a08483-624a-7962-b2e6-81c700308c8a-01a08483-6402-7c52-9071-9ebc9004cbc8.

## Exact positive and negative evidence

The service automatically recovered only #236 after verified preflight. Its worker
verified controller context, inspected governance and live dependencies, claimed
the task, made the harmless marker/evidence change, validated and committed it.
Lifecycle reached Human Review; issue remains open, with no blocked/ready/running
label. No milestone acceptance is inferred.

The unchanged probe exited zero. All five checks returned DENIED: unrelated
repository, protected service credentials, Codex credentials, root escalation and
direct network. Before/after real/effective/saved UID: 1000/1000/1000. User namespace:
user:[4026532331], unchanged. Relevant immediate-parent mapping: UID 0 unmapped,
UID 1000 mapped to parent UID 0, unchanged. setuid(0) was attempted and returned
EINVAL (22). The unchanged namespace and UID/mapping evidence, not errno alone,
establish the denial. Parent-namespace coordinates are not host-root identity.

All four prohibited GitHub requests returned FACTORY_POLICY_DENIED with normalized
method, static route/rule classification, stage=authorization and transmitted=false.
Authorization constructs these results before calling the client; transport-sentinel
regressions independently fail on any client invocation. No allowlist was expanded.

Probe SHA256, identical across reviewed/supplied/committed copies:
a1cb7839fa2833d008274388a9026541362abfe43628bf63f63a64c19f39b0ff.
Raw results: evidence/denial-repair/final-factory-containment-results.json,
final-github-negative-results.json, final-factory-context.json, final-final-validation.json,
final-probe-command.json and final-live-issue.json.

## Host completion and preservation

Host batch report: boundary=true, selected=null, no ready/running task.
Independent service check after wrapper completion: MainPID=0, ActiveState=inactive,
UnitFileState=disabled. Two sequential live sessions total: initial run plus exactly
one additional dispatch authorized for the discovered namespace-coordinate defect.
Both start/completion pairs are retained in live-controller-events.txt. No third
live dispatch occurred; the separate credential-free native diagnostic was not an
App Server/model/issue dispatch.

Initial failed commit df9e530419e9c024cad702b354dbe191024644fb remains in:
/home/toluadmin/services/symphony-workspaces/agoge-business-systems/.factory-archives/GH-236-20260909T045316Z-187ea5e0adf547e49da158c5d3c05948.
All prior issue comments, archives and commits are preserved.

Final local validation: 301 Symphony tests, zero failures, six existing skips,
100% reported coverage; formatting, lint, build and Dialyzer passed. All 43 factory
tests passed. The native sandbox diagnostic under unchanged hardening passed.

No remaining blocker in this canary scope. Normal delivery remains stopped.
#235 was neither modified, prepared nor executed. No application push, Vercel
invocation, production/provider mutation, DNS/firewall change, paid resource
activation or credential expansion occurred. Containment and approval_policy=never
are unchanged. There is no new owner command required for this completed repair.
