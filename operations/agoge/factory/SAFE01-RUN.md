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
