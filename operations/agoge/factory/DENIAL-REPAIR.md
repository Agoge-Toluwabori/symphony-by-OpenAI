# Canary denial-evidence repair

The prior run's dispatch attestation is accepted as proven. This repair changes
only the probe and rejection evidence, with narrow recovery of the documented
#236 validation failure. Containment, credentials and GitHub allowlists are unchanged.

## Root probe

Version 2 records getresuid() before and after setuid(0): real, effective and saved
UIDs must be identical, nonzero and mapped to nonzero parent UIDs. It projects
/proc/self/uid_map onto only those UIDs and UID 0, never records unrelated ranges.
EPERM/EACCES are accepted only with this complete unchanged identity evidence.
EINVAL additionally requires UID 0 to be unmapped. Unknown errors, ambiguous or
unreadable mapping, any UID/mapping change, already privileged identity, or an
unexpected successful syscall cannot pass. Results are written with all check
statuses and root_identity; expected EINVAL no longer skips the network check.
No credentials are read, even when attempting protected-file opens.

## GitHub denial result

Factory authorization failures return error fields only:
code=FACTORY_POLICY_DENIED, normalized method, route_class, policy_rule,
stage=authorization, transmitted=false. Static route/rule classifications are:

| Route class | Matched restriction |
| --- | --- |
| outside_repository | repository_scope |
| noncanonical | canonical_route_required |
| deployments | development_operations_only |
| issue_lifecycle | assigned_issue_lifecycle_only |
| account_resource / repository_other | default_deny |

These values are produced by the existing rejecting authorization branch before
Client.request can execute. Transport-sentinel tests fail if any denied request
reaches the client. The allow/deny predicates themselves are unchanged. No request
path, credential, header, body or upstream response is included in denial evidence.
Non-policy upstream errors retain redaction; they are not mislabeled as denials.

## Recovery and execution

Recovery version canary-denial-evidence-v1 is single-use and requires verified
current service preflight, the one-task approved batch, live dependency checks,
no gate/review state and the documented EINVAL plus suppressed-denial failure.
It does not clear arbitrary blockers or modify #235. Earlier receipts, issue
comments and archived workspaces remain intact. The launcher still allows one
actual App Server launch per invocation; the wrapper stops/disables afterward.
The current owner instruction permits at most one additional live dispatch if
another code defect is discovered. No automatic retry broadens that limit.

Regression tests cover expected denial errnos, each privileged/changed UID,
mapped parent root, unknown/success outcomes, unreadable/ambiguous mapping, continued
network/result execution, exact redacted denial schemas, and pre-transmission
rejection for all four canary cases. Run validate.sh for full Symphony/factory
checks. Evidence for this repair is under evidence/denial-repair/.

Local validation: 301 Symphony tests, zero failures, six existing live-test skips,
100% reported coverage, formatting/lint/build and Dialyzer passed. All 41 factory
tests passed before installation. Live results are recorded separately.
