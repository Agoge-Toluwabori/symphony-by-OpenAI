# SAFE-01 read-only Vercel identity investigation

Classification: **insufficient evidence**. The current owning project cannot be
identified conclusively from the existing authenticated access. No repair applied.

Machine-readable observations: [identity-discovery-2026-09-09.json](evidence/identity-discovery-2026-09-09.json).

## Local links and authentication

Neither the canonical `/home/toluadmin/projects/Agoge-Business-Systems` repository
nor the retained `/home/toluadmin/services/symphony-workspaces/agoge-business-systems/GH-235`
workspace contains `.vercel/project.json` or `.vercel/repo.json`. A recursive search
excluding Git metadata and generated dependency/build directories found no nested
link files. There are therefore no local configured project/team IDs to compare.

`vercel whoami` was attempted in the canonical repository: exit 127, command not
found. No CLI was installed, login attempted, or link command run. No executable
was found in the inspected common install/cache locations. Standard Vercel CLI
authentication files are absent; contents were not read. No token/environment
values were printed. The connected Vercel app successfully authenticated its team
and project listing requests, so existing connector authentication is available.
The connector has no whoami operation; the authenticated username remains
unverified and must not be inferred from the team's display name.

## Accessible resources

The connector returned one accessible team, and that team was enumerated:

- Name: `agoge-toluwabori's projects`
- Slug: `agoge-toluwaboris-projects`
- ID: `team_71Pod0CQBKz4RAlT1JOFH2m3`

| Project | Non-secret project ID | GitHub link reported by Vercel |
| --- | --- | --- |
| how-assessments | prj_v6trzbxaQ9W5UwDxNPPZFT9nt4Hl | Agoge-Toluwabori/HoW_Assessments |
| eyin-afe | prj_BIXVbmHUEsPtzKEHixgJHT6YjLJI | Agoge-Toluwabori/Eyin-Afe |

No listed project links to Agoge Business Systems. These are discovery metadata;
neither unrelated repository was opened. The connector's project-list tool caps
results at 50; this call returned two with no pagination marker. Discovery is
limited to resources visible through the existing connector, not an account-wide
administrative inventory of hidden or formerly accessible projects.

## Historical GitHub evidence

Read-only REST queries inspected deployment 6316676637, its statuses, commit
4919ab4cfb78e8408bfc405134ba219f53c34cc2/status and that commit's check-runs.

- Creator: `vercel[bot]`; timestamp: 2026-09-07T21:46:09Z.
- Commit status 53697985254: context Vercel, failure.
- Deployment status 17958002590: failure.
- Environment name: `Production`; `production_environment: false` and
  `transient_environment: false`. Naming alone does not prove a production target
  or successful production release.
- Historical team slug: `agoge-toluwaboris-projects`.
- Historical project slug: `2026-09-07-animation-baseline`.
- Vercel deployment ID: `dpl_7MSA8nEQBJjWBwZxaDX3GHZizagC`.
- [Historical dashboard reference](https://vercel.com/agoge-toluwaboris-projects/2026-09-07-animation-baseline/7MSA8nEQBJjWBwZxaDX3GHZizagC).
- Deployment environment/log/target hostname:
  `2026-09-07-animation-baseline-m3pxxdc48.vercel.app`.
- Deployment payload is empty; no immutable Vercel project/team ID is present.
  The commit has zero check-runs providing further identity references.

Current authenticated lookups under `team_71Pod0CQBKz4RAlT1JOFH2m3` returned 404
for the historical project slug, exact deployment ID, and deployment hostname.
The hostname was queried as deployment metadata, not fetched as an application.

## Classification of the 404

| Candidate | Finding |
| --- | --- |
| Wrong team scope | Not established. The current accessible slug matches the historical URL; no different relevant accessible team was returned. Historical immutable team ID is unknown. |
| Stale or incorrect project link | Possible historical reference, but no local link file exists to substantiate or correct a local mislink. |
| Project deleted or renamed | Possible; no deletion/rename history is available. Absence from the visible list is not proof. |
| Authenticated identity lacks access | Possible; connector identity/access history is not independently established. A successful team listing does not establish access to every historical project. |
| GitHub–Vercel connection mismatch | Possible; historical reporting and current visible inventory differ, but no current target configuration can be inspected. |
| Insufficient evidence | **Selected.** Existing observations do not distinguish the preceding possibilities. |

## Required next evidence and bounded repair

One owner action: **provide the current Vercel dashboard project URL from the
account/team that owns Agoge Business Systems, identifying its team and project
IDs**. Do not send tokens or credentials.

No exact configuration repair is justified until that target is verified. A
future scope/link correction must be limited to the verified existing target and
must not create a replacement project or infer publication safety. No repair,
authentication change, `vercel link`, deployment, configuration mutation, issue
relabel, application edit or Symphony restart occurred in this investigation.

Symphony was independently verified inactive and disabled, MainPID=0. Evidence
was saved locally only; no issue comment or new execution attempt was created.
