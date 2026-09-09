# Autonomous GitHub delivery — 2026-09-09

Owner decision supersedes SAFE-01 and one-task batches. Issue #235 was closed as
not planned and its Project item archived, preserving investigation and commits.
Vercel is outside Symphony. No provider operation was performed in this redesign.

Verified accepted foundation: 4919ab4cfb78e8408bfc405134ba219f53c34cc2.
f9e26887249cf80dfac2b656e37d27e106b38c49 →
806ef8387a0e0c82e1927a56b484baa22b1eae45 →
c41764004c603a8bb18f439d62b9b1d6841a2b43 → foundation ancestry verified.
Remote develop was created at the foundation without reset or main modification.

The continuous controller uses Project Ready plus Factory Authority Autonomous
Development. Legacy planning/held records are not silently promoted. The current
snapshot contains no eligible development issue, so healthy operation initially
means continuous idle polling, not a fabricated task dispatch.

Native Node captured subprocesses previously failed EPERM because the network-off
seccomp policy denied socket buffer/shutdown operations. The managed native proxy
with an empty destination allowlist restores IPC, isolates direct networking, and
returns HTTP 403 for prohibited destinations. NO_PROXY applies only to loopback
private tests. Full application CI passes within that boundary. Existing root,
credential, unrelated-repository, systemd and AppArmor restrictions are retained.

See TEMPLATE.md for standing policy/install/rollback, continuous/ for the reusable
implementation, and evidence/continuous-v2/ for validation and activation evidence.
Prior canary and SAFE-01 reports/bundles remain intact. No incremental paid resource
was activated; existing VM and authentication are used.

Live activation exposed excessive GraphQL cost in the broad gh Project query.
The controller now paginates only required fields and backs off to GitHub reset
when its budget is low. Stale health and the initial failure are preserved; a
healthy running process alone is not evidence of a healthy queue.
