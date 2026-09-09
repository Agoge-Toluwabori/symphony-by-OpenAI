# Canary denial-evidence repair

The prior run's dispatch attestation is accepted as proven. This repair changes
only the probe and rejection evidence, with narrow recovery of the documented
#236 validation failure. Containment, credentials and GitHub allowlists are unchanged.

## Root probe

Version 2 records getresuid() before and after setuid(0): real, effective and saved
UIDs must be identical, nonzero and mapped. The current user-namespace identifier
and relevant mappings must also be unchanged. An immediate-parent UID 0 is not
necessarily host root; namespace coordinates must not be conflated. It projects
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

Recovery version canary-denial-evidence-v2 is single-use and requires verified
current service preflight, the one-task approved batch, live dependency checks,
no gate/acceptance state and the specifically documented parent-mapping failure.
The failed human-review label from that attempt is removed with an explanatory
comment, never a successful review or accepted state.
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


The first live attempt proved all four GitHub pre-transmission denials but exposed
a further probe defect: current UID 1000 maps to UID 0 in its immediate parent
user namespace. The probe mistook that coordinate for host privilege and stopped
before setuid. That attempt and commit df9e530419e9c024cad702b354dbe191024644fb
are preserved. The follow-up records the current namespace ID, rejects any UID,
namespace or mapping change, and requires a failed syscall plus unchanged nonroot
current UIDs. EINVAL still additionally requires current UID 0 to be unmapped.
The read-only host launcher independently enforces non-root execution.

A harmless native Codex sandbox diagnostic runs the exact revised probe under
unchanged service hardening with a credential-free temporary CODEX_HOME. It makes
no model turn and dispatches no issue. This validates the kernel UID behavior
before the single additional live #236 dispatch authorized by the owner.

Follow-up validation passed: 301 Symphony tests, zero failures/six skips,
100% reported coverage and clean formatting/lint/build/Dialyzer; 43 factory tests.
The credential-free native diagnostic reproduced mapping 1000→0 in the immediate
parent namespace, attempted setuid, recorded EINVAL and unchanged namespace plus
real/effective/saved UIDs 1000/1000/1000, and passed all five containment checks.
