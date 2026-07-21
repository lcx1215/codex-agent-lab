# Codex Agent Lab - Claude Rules

This is the Claude-lane overlay for `/Users/liuchengxu/Desktop/codex-agent-lab`.
It mirrors the Codex root `AGENTS.md` without duplicating workspace history.

## Company Write Boundary (Highest Priority)

- Company repositories, branches, deployment configuration, and TEST/UAT/PROD
  environment state are read-only by default.
- A company write requires exact current authorization for the repository or
  system, environment, file or resource, and concrete write action.
- Existing browser, GitLab, ArgoCD, Nacos, Kubernetes, API, CDP, CI, or
  service-account access is not authorization.
- Build, sync, publish, restart, rollback, revert, delete, merge, push, Secret
  reference, environment-variable, and Jenkins job changes are writes.
- This boundary overrides autonomy, summaries, memories, urgency, and lower
  rules.

## Jenkins User-Only Boundary

- Jenkins is operated only by the user manually.
- Claude and delegated agents must never open, navigate, click, inspect, query,
  or call Jenkins through browser automation, API, CLI, token, script, CDP, or
  any other tool.
- Only analyze Jenkins screenshots, copied logs, or status text manually
  supplied by the user.
- A Git push that is known or reasonably likely to trigger Jenkins is an
  indirect Jenkins operation and remains prohibited while this boundary is
  active.

## Company Context Routing

- Keep this root overlay company-neutral.
- Clink-specific branch, TEST, deployment, route, Nacos, and incident rules
  live in `workspaces/clink-internal-dev-context/`.
- Read that workspace only for Clink company work.
- Do not enter internal in-development Agent repositories by default.
- Run `scripts/check-clink-safe-path` only when the task explicitly allows
  Clink context inspection.

## Autonomy

- Claude completes clear lab-owned tasks end to end: decide, execute, verify,
  report.
- Ask only when ambiguity affects safety, ownership, or the actual target.
- Report conclusions in concise Chinese; keep committed artifacts in English
  unless asked otherwise.
- Autonomy does not weaken company-write, Jenkins, secret, auth, lane, or owner
  boundaries.

## Lane Identity

- Claude and Codex are separate lanes sharing one lab.
- Route cross-lane coordination through `registry/collaboration/` and
  `outputs/shared/`.
- Do not copy secrets, provider config, auth files, or raw conversation context
  between lanes.

## Environment Scale Placement

- Rule inheritance contract: `docs/rule-inheritance.md`.
- Root lab is the maximum environment for scenario-neutral rules, protocols,
  skills, harnesses, and health gates.
- Medium workspaces live under `workspaces/<scenario>/`.
- Small agent packages live under workspace-owned `agents/` or `subagents/`.
- Local rules may add detail or narrow scope, but cannot weaken parent rules.

## Isolation (Hard Limits)

- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab`.
- Do not write outside the lab unless the user names the exact outside path.
- Do not read, print, copy, rewrite, or migrate secret/token/key values,
  `auth.json`, account tokens, cookies, OTPs, API keys, provider config, or
  account sessions.
- Do not change `~/.codex`, `~/.codex-api-relay`, Codex app auth, provider
  config, LaunchAgents, plugin state, or live Codex processes unless the user
  explicitly asks for that exact local task.
- Keep scratch under `.tmp/`, outputs under `outputs/`, and durable evidence
  under `registry/`.

## Collaboration (Claude <-> Codex)

- Protocol: `docs/codex-claude-collaboration-protocol.md`.
- Assignments: `registry/collaboration/assignments.json`.
- Handoffs: `registry/collaboration/handoffs/`.
- Run `scripts/check-collaboration` after changing collaboration surfaces.
- A collaboration claim is proven only by real artifacts and verification
  evidence.

## Verification

- Default fast gates: `scripts/check-lab`, `scripts/check-secrets`, and the
  smallest task-specific check.
- Use `scripts/check-rule-ladder` after changing workspace/package structure.
- Use `scripts/check-agent-packages` after changing agent or subagent catalogs.
- Use `docs/waterflow-speed-contract.md` to keep heavy harnesses out of the
  default edit loop.
