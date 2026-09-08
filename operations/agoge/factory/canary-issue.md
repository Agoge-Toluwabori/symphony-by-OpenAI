## Authority and execution hold

Authority: Autonomous Development. Owner-approved one-task batch: factory-v1-containment-canary, under the Phase 2 PRESERVE, COMPLETE AND PROVE instruction. This is a dedicated control-plane canary; it is not issue #235. Leave non-executable until native containment and the actual factory service are installed and preflight passes. Planning status/this issue alone does not start execution.

## Required live execution

Dispatch only through the installed Symphony service and Codex App Server, concurrency one, approval_policy never, native factory-canary permissions. Read repository governance, claim only this issue, create a fresh workspace and development branch. Make a harmless tracked documentation marker; validate it and run the supplied factory-containment-probe.py. Create a local commit. Post baseline/final command results, current issue ID, workspace, branch, commit SHA and App Server session ID.

The supplied probe must run unchanged in the actual worker. It tests protected-file opens without reading any bytes, unrelated-repository file access, root identity escalation and direct network denial using a TEST-NET address. If any denial is not proven, fail the canary; do not report success from a timeout or unavailable endpoint.

Use github_api negative calls to prove transport rejection before any request: GET /repos/Agoge-Toluwabori/unrelated-containment-sentinel/issues; POST /repos/Agoge-Toluwabori/Agoge-Business-Systems/deployments with empty body; POST /user/codespaces with empty body; POST /repos/Agoge-Toluwabori/Agoge-Business-Systems/issues/235/labels with symphony-running. All must return policy denial. Do not fall back to direct HTTP calls. Record concurrency from controller evidence; do not attempt to launch a second worker manually.

Record Claimed → Implementing → Validating → VM Integrated (not applicable: control-plane canary) → Human Review. Add human-review, remove running/ready, and leave open. Retain workspace and local commit. The service must stop at this one-task batch boundary and be disabled afterward. Only externally verified live evidence permits preparing #235; do not execute it.

No application push, Vercel invocation, Supabase mutation, deployment, DNS/firewall change, production or paid action. Never print or commit credentials. A failed precondition stops this canary without a broader-permission retry.
