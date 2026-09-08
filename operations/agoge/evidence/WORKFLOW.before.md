---
tracker:
  kind: github
  provider:
    repo: Agoge-Toluwabori/Agoge-Business-Systems
    token: $GITHUB_TOKEN
  required_labels:
    - symphony-ready
  active_states:
    - open
  terminal_states:
    - closed

polling:
  interval_ms: 30000

workspace:
  root: /home/toluadmin/services/symphony-workspaces/agoge-business-systems

hooks:
  after_create: |
    gh repo clone Agoge-Toluwabori/Agoge-Business-Systems . -- --branch docs/p4-acceptance --single-branch
    pnpm install --frozen-lockfile

agent:
  max_concurrent_agents: 1
  max_turns: 12

codex:
  command: codex --config shell_environment_policy.inherit=all app-server
  thread_sandbox: workspace-write
  turn_sandbox_policy:
    type: workspaceWrite
    networkAccess: true
---

You are working on GitHub Issue {{ issue.identifier }}.

Title: {{ issue.title }}
State: {{ issue.state }}
Labels: {{ issue.labels }}
URL: {{ issue.url }}

Description:
{% if issue.description %}
{{ issue.description }}
{% else %}
No description was supplied.
{% endif %}

Operating rules:

1. Work only inside the isolated repository workspace created for this issue.
2. Read AGENTS.md and every governing document it requires before taking action.
3. Treat documented proposals as proposals, not approvals.
4. The `symphony-ready` label authorizes only the issue's explicit scope, local workspace changes, and local verification.
5. Do not push commits, create or modify branches remotely, or open a pull request unless the issue also has the `owner-approved-remote-write` label.
6. Do not merge pull requests, deploy, provision infrastructure, modify hosted Supabase resources, spend money, or contact third parties unless the issue contains separate explicit owner authorization for that exact action.
7. GitHub Issue comments and workflow labels may be used to record progress, evidence, review status, or blockers.
8. Never expose credentials, tokens, secrets, private customer data, donor data, or unrelated repository information.
9. Keep changes bounded to the acceptance criteria. Record useful out-of-scope findings without implementing them.
10. Preserve existing user changes and do not weaken failing checks.
11. Run the relevant formatting, lint, type, boundary, test, build, and browser checks required by the issue and repository.
12. Report facts as Certain, inferences as Likely, and uncertain claims as Guessing.
13. If blocked by missing authority, requirements, credentials, or external access, stop the affected work and record the precise blocker.
14. Do not close the Issue automatically. Leave final acceptance and closure to the owner.

Final response must state:

- What changed.
- What was verified.
- What remains blocked or unverified.
- Whether any remote write occurred.
