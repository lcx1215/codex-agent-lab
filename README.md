# Codex Agent Lab

**English | [简体中文](README.zh-CN.md)**

Clean, project-scoped workbench for Codex and Claude agent development.

The root layer should stay thin: safety locks, placement rules, small proof
loops, and fast health gates. Scenario history, company details, release notes,
and heavy harness evidence belong in workspaces, docs, outputs, or registry
records.

## What This Is

- Governance and collaboration layer, not a production agent runtime.
- Shared lab root for Codex and Claude with durable state and validation gates.
- Scenario-neutral maximum environment; product or company work starts under
  `workspaces/`.
- Evidence-first workflow: use the smallest harness or check that proves the
  current claim, then stop or iterate.

## Start

| Need | Command or file |
| --- | --- |
| Root fast health | `./scripts/check-lab` |
| Clean-home Codex lane | `./scripts/start-clean-home` |
| API-relay Codex lane | `./scripts/start-api-relay` |
| Workflow mode help | `./scripts/workflow-mode list` |
| Current dashboard | `./scripts/lab-dashboard` |
| Clink context entry | `workspaces/clink-internal-dev-context/README.md` |

Do not use the Clink context or `.current-agent` pointer unless the task is
actually about Clink company work.

## Rules And Placement

- Codex root overlay: `AGENTS.md`
- Claude root overlay: `CLAUDE.md`
- Placement contract: `docs/environment-layering.md`
- Rule inheritance: `docs/rule-inheritance.md`
- Scenario workspace contract: `docs/scenario-workspace-contract.md`
- Collaboration protocol: `docs/codex-claude-collaboration-protocol.md`
- Mission and promotion bar: `docs/agent-lab-mission.md`

Root assets must be scenario-neutral. Workspaces hold product or company
context. Agent packages live inside workspaces under `agents/` or `subagents/`.

## Fast Checks

Use these in normal edit loops:

| Check | Command |
| --- | --- |
| Project rules | `./scripts/check-project-rules` |
| Runtime compatibility | `./scripts/check-runtime-compatibility` |
| Rule ladder | `./scripts/check-rule-ladder` |
| Agent packages | `./scripts/check-agent-packages` |
| Sandbox | `./scripts/check-sandbox` |
| Sandbox skills | `./scripts/check-sandbox-skills` |
| Speed contract | `./scripts/check-speed-contract` |
| Task state | `./scripts/check-task-state` |
| Secrets | `./scripts/check-secrets` |

Use targeted tests for changed behavior before wider suites.

## Boundary Checks

Run heavier checks only at commit, release, promotion, handoff, or explicit audit
boundaries:

| Boundary | Command |
| --- | --- |
| Workspace safety | `./scripts/check-workspace-safety` |
| Async execution | `./scripts/check-async-execution` |
| IDE-loop benchmark | `./scripts/benchmark-ide-loop` |
| Waterflow scan | `./scripts/waterflow-scan --root . --compare-last` |
| Waterflow verification | `./scripts/waterflow-verify` |
| Waterflow stress | `./scripts/waterflow-stress --scale-paths 1200` |
| Waterflow incident | `./scripts/waterflow-incident` |
| Collaboration surfaces | `./scripts/check-collaboration` |

`docs/waterflow-speed-contract.md` defines why these are not default per-edit
steps. Heavy harnesses prove boundaries; they should not slow ordinary work.

## Agents And Skills

Resident support agents:

- `foundation-amplifier`
- `development-experience-auditor`
- `third-party-large-agent-auditor`
- `context-architect`
- `handoff-summarizer`
- `waterflow-auditor`

Audit entrypoints:

- `./scripts/development-experience-audit`
- `./scripts/large-agent-readiness-audit`

Lab skills live under `.agents/skills/`. Current sandbox skills are
`secret-boundary-auditor`, `async-race-detector`, and
`sandbox-artifact-hygiene`.

## Reports

- Durable progress: `registry/current-progress.md`
- Validation evidence: `registry/VALIDATION.md`
- Agent registry: `registry/AGENT_REGISTRY.md`
- Runtime compatibility: `outputs/shared/compatibility/runtime-compatibility.md`
- Workspace safety: `outputs/shared/workspace-safety/workspace-safety.md`
- Dashboard: `outputs/shared/dashboard/lab-dashboard.md`
- Benchmark history: `outputs/shared/benchmarks/ide-loop/history.md`

Reports are evidence stores, not root rules.

## Boundaries

- Do not read, copy, print, or migrate secrets, auth files, tokens, cookies,
  OTPs, API keys, provider config, or account sessions.
- Do not mutate company repositories, branches, deployment config, or
  TEST/UAT/PROD state without exact current authorization.
- Jenkins is user-manual-only. Codex may only analyze user-supplied Jenkins
  screenshots, copied logs, or status text.
- Do not touch default App/Plus lane, API-relay auth, provider config,
  LaunchAgents, or plugins unless the user names that exact local task.
