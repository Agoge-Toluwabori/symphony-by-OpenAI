# SAFE-01 owner-authorized activation, 2026-09-09

Owner Agoge-Toluwabori accepted containment canary #236, recorded at
https://github.com/Agoge-Toluwabori/Agoge-Business-Systems/issues/236#issuecomment-5596300953.
Canary is closed, accepted, Project Done. Its evidence and commits are retained.

Only batch factory-v1-publication-guard / #235 is authorized. Host preflight binds
exact repository, issue, batch and accepted dependency #236; concurrency one,
exclusive launch receipt, native sandbox, no direct network, filtered environment
and existing systemd hardening remain unchanged. Canary-only prose is scoped to
#236. No provider/publication capability or credentials have been added.

Install: `python3 operations/agoge/factory/install.py --safe01` (stops/disables).
Run once: `bash operations/agoge/factory/run-safe01-once.sh`.
Emergency stop: `systemctl --user disable --now symphony-agoge.service`.
Rollback: `python3 operations/agoge/factory/install.py --rollback`; only managed
files/references are restored. Original credentials, evidence and commits survive.
A default reinstall returns to execution hold; no restart is authorized after
this one-task attempt without a new owner instruction.

Host provider evidence is recorded on #235:
https://github.com/Agoge-Toluwabori/Agoge-Business-Systems/issues/235#issuecomment-5596379547.
The existing connector cannot retrieve the historical target project/deployment
(404); current project listing does not identify this repository. This does not
prove deletion or safety. No guard is claimed and no publication test may occur
until ownership, configuration and access can be verified. Worker must investigate
available GitHub evidence and stop Blocked if that requirement remains unmet.

Validation and live outcome are recorded below after completion.

Local validation: full Symphony gate passed (301 tests, zero failures, six existing skips), formatting, Credo, build and Dialyzer passed; 46 factory tests passed; native containment diagnostic passed. New regressions bind exact issue/batch pairs, require closed+accepted canary, reject mixed execution modes, and preserve identical native policy across installation modes.

## Live outcome

Exactly one service invocation: d8c5ebed2c11408f9eb0d5656198705e, App Server
PID 55956, session 01a084b7-f90d-7092-8bed-ca61629bffaa-01a084b7-faf3-7f33-be2b-f31d0f880f4f.
Worker investigation report:
https://github.com/Agoge-Toluwabori/Agoge-Business-Systems/issues/235#issuecomment-5596529213.
Local branch symphony/GH-235-20260909T055043Z, commit
55e16eea299d7d798621030c404b42327d273819. Four documentation files only;
JSON/assertion/link/whitespace/changed-file checks passed; checkout clean.
No claim was made after discovering the existing external access blocker.
Issue is open, symphony-blocked, Autonomous Development, original approved batch;
Project status Blocked. No ready/running/human-review label. Batch boundary true;
service MainPID=0, inactive, disabled. No second dispatch is authorized or performed.

No guard was implemented, publication test performed, provider setting changed,
or no-deployment guarantee established. Therefore Human Review success is not
claimed. No provider rollback is required. Existing Vercel project/team visibility
must be resolved through the existing connection before resuming. A bounded
provider-configuration/publication capability remains absent; no credentials were
expanded or generic provider write access installed.

The run also exposed two avoidable GitHub read limitations. The controller now
permits only SAFE-01 GETs to its bound repository metadata and exact deployments,
deployment-ID and statuses routes. Other issues, malformed/other-repository routes
and deployment writes remain denied before transport. Regression transport
sentinels verify this. No additional live attempt was used to test the repair.

## Preservation incident and exact recovery

Closing #236 made it terminal. On the next service startup the pre-existing
Symphony terminal-workspace cleanup deleted GH-236 rather than archiving it.
This was found during independent post-run verification; the earlier acceptance
comment's workspace-retention statement was therefore no longer accurate.

Its committed host evidence and original App Server session transcript survived.
Decoding the original file-writing string literals (without executing recorded
commands), combining copied JSON/probe bytes, and restoring the recorded original
parent/author/committer/timestamp/message reproduced the exact original commit:
5cc507a336ee4146df0bcd4e2db45849cad2d924. Matching the original Git SHA proves the
complete original ten-file tree, parent and commit metadata were recovered.
The original two untracked probe/results files were also restored.

Durable recovered checkout outside controller cleanup:
/home/toluadmin/services/symphony/.factory-preservation/recovered-canary-236
Original branch symphony/GH-236-20260909T045317Z; git fsck --full passed.
Complete-history accepted-canary-236.bundle and safe01-investigation-235.bundle
are retained in the same .factory-preservation directory. Original canary SHA and
branch were restored, not replaced by a new purported canary commit. No history
was rewritten and no evidence was rerun or fabricated.

Factory local terminal cleanup now atomically renames the whole workspace into
.factory-archives. If archiving fails or the archive path is a symlink, cleanup
returns an error and retains the source. Normal non-factory behavior is unchanged.
A real filesystem regression verifies Git-object bytes, untracked evidence and
failure preservation. The current factory is local-only; remote execution is not
configured. The recovery incident and correction are also recorded on #236.

Final post-run repair validation: 303 Symphony tests, zero failures, six existing skips; 46 factory tests; formatting, lint, build, Dialyzer and native diagnostic passed. Initial synthetic fixture/lint failures are retained beside final passing output. Evidence token-pattern check passed. Reinstall uses the default execution hold and does not start delivery.
