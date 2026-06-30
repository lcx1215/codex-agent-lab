# Codex Agent Lab

Clean, project-scoped environment for long-horizon Codex and Claude agent work.

This lab is a scenario-neutral development environment for arbitrarily large agent projects. UCP and commercial customer-service agents are future scenario workspaces, not the boundary of the lab.

The environment is a force multiplier for Codex and Claude: durable progress, isolated workspaces, Waterflow supervision, benchmarks, skills, prompts, and verification gates should help them work faster and more safely. They do not replace the model agents' reasoning, coding, review, or recovery responsibilities.

Under equal effectiveness, the lab should stay lean: fewer rules, fewer generated artifacts, fewer default checks, and fewer always-on processes are preferred when safety, isolation, speed, and verification stay intact.

See `docs/agent-lab-mission.md` for the mission, quality bar, and promotion rules used to grow this environment.

## Autonomy

Agents in this lab run autonomously: they complete tasks end-to-end without asking the user for approval — decide, execute, verify, and report. This is standing authorization, not per-task.

Never end a turn with a yes/no or "want me to…?" permission question — if tempted to ask whether to proceed, just do it and report. Report conclusions, not raw logs: the user is in the CLI without a GUI, so clear presentation is the agent's job (`mas` for environment status, `duo` for side-by-side Claude+Codex panes).

This does not relax the safety boundaries in `AGENTS.md` (`## Isolation`): no secrets/auth handling, no touching `~/.codex` / `~/.codex-api-relay` / provider config / LaunchAgents, and stay within the lab root. Autonomy removes the permission step, not the safety lines.

## Paths

- Lab root: this repository checkout
- Isolated Codex home: `.codex-home`
- Optional global rules source: `~/.codex/AGENTS.md`
- Lab overlay rules: `AGENTS.md`
- Project agents: `.codex/agents`
- Project skills: `.agents/skills`
- Durable progress: `registry/current-progress.md`
- Task workspaces: `workspaces`
- Outputs: `outputs`

## Start

Strict clean-home lane:

```bash
./scripts/start-clean-home
```

Project-isolated API-relay lane, using the existing API relay auth/config home and OMX by default:

```bash
./scripts/start-api-relay
```

Plain non-OMX API-relay fallback, only for diagnostics or explicit bypass:

```bash
./scripts/start-api-relay-plain
```

Check installation:

```bash
./scripts/check-lab
```

Check sandbox boundaries only:

```bash
./scripts/check-sandbox
```

Check runtime compatibility and common setup drift:

```bash
./scripts/check-runtime-compatibility
```

Check workspace-level safety without blocking active in-progress work:

```bash
./scripts/check-workspace-safety
```

Check async execution safety:

```bash
./scripts/check-async-execution
```

Check sandbox-specific skills:

```bash
./scripts/check-sandbox-skills
```

Check Waterflow speed contract:

```bash
./scripts/check-speed-contract
```

Run the IDE-loop benchmark with a real API-relay/OMX model smoke test:

```bash
./scripts/benchmark-ide-loop
```

Run the same benchmark while explicitly skipping the model smoke test:

```bash
./scripts/benchmark-ide-loop --skip-omx
```

Render the one-screen lab dashboard:

```bash
./scripts/lab-dashboard
```

Audit Codex/Claude development comfort in the lab:

```bash
./scripts/development-experience-audit
```

Audit large-agent readiness from a third-party reviewer perspective:

```bash
./scripts/large-agent-readiness-audit
```

List workflow modes:

```bash
./scripts/workflow-mode list
```

Print a workflow mode contract:

```bash
./scripts/workflow-mode omx-long-horizon
```

Run Waterflow Auditor:

```bash
./scripts/waterflow-scan --root .
```

Compare against the previous Waterflow path index:

```bash
./scripts/waterflow-scan --root . --compare-last
```

Run the real validation commands from the latest Waterflow plan:

```bash
./scripts/waterflow-verify
```

Run high-pressure Waterflow fixtures:

```bash
./scripts/waterflow-stress --scale-paths 1200
```

Run a complex Waterflow incident fixture and generate a Codex/Claude handoff:

```bash
./scripts/waterflow-incident
```

Validate the Codex-Claude collaboration surfaces:

```bash
./scripts/check-collaboration
```

The clean-home lane does not copy secrets. If it needs model access, log in or add API auth to that isolated home separately.

## Agents

- `long-horizon-orchestrator`
- `context-architect`
- `research-scout`
- `implementation-worker`
- `verification-auditor`
- `risk-reviewer`
- `handoff-summarizer`
- `waterflow-auditor`
- `foundation-amplifier`
- `development-experience-auditor`
- `third-party-large-agent-auditor`

Use explicit agent names when asking for delegation. Keep each run narrow and write durable state to `registry/current-progress.md`.

## Guidance Layering

Global rules stay in the active Codex home. This lab can use a local reference from `.codex-home/AGENTS.md` to `~/.codex/AGENTS.md` so the clean-home lane inherits global policy without maintaining a divergent copy.

This repo's `AGENTS.md` is only an environment-specific overlay: isolation, lab paths, agent roles, local skills, and validation rules.

Framework:

- Global: `~/.codex/AGENTS.md`
- Lab overlay: `AGENTS.md`
- Lab operating notes: `README.md`
- Lab mission and quality bar: `docs/agent-lab-mission.md`
- Sandbox boundary contract: `docs/sandbox-boundaries.md`
- Runtime compatibility contract: `docs/runtime-compatibility.md`
- Workspace safety contract: `docs/workspace-safety-contract.md`
- Scenario workspace contract: `docs/scenario-workspace-contract.md`
- Reasoning speed playbook: `docs/reasoning-speed-playbook.md`
- Waterflow speed contract: `docs/waterflow-speed-contract.md`
- Custom agents: `.codex/agents/*.toml`
- Foundation amplifier agent: `docs/foundation-amplifier-agent.md`
- Development experience auditor agent: `docs/development-experience-auditor-agent.md`
- Third-party large-agent auditor: `docs/third-party-large-agent-auditor.md`
- Environment-specific skills: `.agents/skills/*/SKILL.md`
- Sandbox skills: `.agents/skills/secret-boundary-auditor`, `.agents/skills/async-race-detector`, `.agents/skills/tmux-omx-runtime-doctor`, `.agents/skills/sandbox-artifact-hygiene`
- Durable progress and validation: `registry/`
- Task-specific work: `workspaces/`
- Waterflow reports and repair briefs: `outputs/shared/waterflow/`
- Waterflow change briefs: `outputs/shared/waterflow/waterflow-change-briefs.md`
- Waterflow validation plan: `outputs/shared/waterflow/waterflow-validation-plan.md`
- Waterflow changed-only validation plan: `outputs/shared/waterflow/waterflow-validation-plan-changed.md`
- Waterflow validation results: `outputs/shared/waterflow/waterflow-validation-results.md`
- Waterflow route index: `outputs/shared/waterflow/waterflow-route-index.md`
- Runtime compatibility report: `outputs/shared/compatibility/runtime-compatibility.md`
- Workspace safety report: `outputs/shared/workspace-safety/workspace-safety.md`
- Waterflow stress results: `outputs/shared/waterflow/stress/*/waterflow-stress-results.md`
- Waterflow incident handoffs: `outputs/shared/waterflow/incidents/*/codex-claude-handoff.md`
- Waterflow harness philosophy: `docs/waterflow-harness-philosophy.md`
- Waterflow path index and diff: `outputs/shared/waterflow/waterflow-path-index.json` and `outputs/shared/waterflow/waterflow-path-diff.json`
- IDE-loop benchmark history: `outputs/shared/benchmarks/ide-loop/history.md`
- Lab dashboard: `outputs/shared/dashboard/lab-dashboard.md`
- Development experience audit: `outputs/shared/development-experience-auditor/latest.md`
- Workflow mode catalog: `docs/workflow-modes.md`
- OMX retrospective: `registry/OMX_RETROSPECTIVE.md`

Waterflow scans its own `waterflow/`, `tests/`, and `docs/` paths. Generated `outputs/` are evidence artifacts, not source waterways, so they are excluded from the graph to avoid constant self-diff noise.

For large path counts, use route index and changed-only validation first. The stress harness can generate arbitrary scale fixtures; the number is a pressure parameter, not a target architecture.

For realistic failure rehearsal, use the incident harness. It creates an isolated bad fixture, records expected command failures and timeouts, and writes an actionable handoff for Codex or Claude. An incident harness pass means detection and reporting worked; it does not mean the fixture or the real lab is healthy.

## Skills And Plugins

Codex can use its normal global skills and plugins when they are available in the active lane. Skills specific to this lab or to a task inside it should live under `.agents/skills/`.

## Scenario Workspaces

Workspaces under `workspaces/` can target any large agent family. Current examples may include UCP-style or commercial customer-service foundations, but those examples do not define the lab's full scope. Promote only reusable patterns from a scenario workspace back into the shared lab.

Use `docs/scenario-workspace-contract.md` and `scripts/new-workspace` so every serious scenario declares its boundary and how it amplifies Codex/Claude work.

## Workflow Modes

Use `docs/workflow-modes.md` and `scripts/workflow-mode` to choose between daily App work, CLI diagnosis, OMX long-horizon execution, multi-agent review, and overnight checkpointed work. These modes are routing contracts; they do not override the global safety rules.

## Secret Safety

Do not commit API keys, GitHub tokens, `.env` files, private keys, cookies, or auth/session files. Run this before committing:

```bash
./scripts/check-secrets
```

The repository also includes a GitHub Actions secret scan that blocks common GitHub, OpenAI, AWS, private-key, `.env`, and auth-file leaks.

## Sandbox Safety

The clean-home lane uses `workspace-write` scoped to this repository checkout. System temp directories are excluded; lab-local temporary files belong under `.tmp/`. Run `./scripts/check-sandbox` after changing sandbox config, symlinks, temporary-file behavior, or workspace boundaries.

## Speed Strategy

Use `docs/reasoning-speed-playbook.md` to keep `gpt-5.5` + `xhigh` for genuinely hard reasoning while moving lookup, validation, scans, and independent checks onto faster or parallel lanes.

Use `docs/waterflow-speed-contract.md` to keep Waterflow supervision from slowing active Codex or Claude work. Default checks stay metadata-only or changed-only; full Waterflow validation, stress fixtures, and incident fixtures are boundary tools.

Use `scripts/benchmark-ide-loop` to measure the lab's RED/GREEN edit loop, health gates, Waterflow checks, and API-relay/OMX model smoke test over time. Use `scripts/lab-dashboard` for a compact current-state view.

## Boundaries

This lab must not mutate the user's default App/Plus lane or API-relay lane. It can use the API-relay launcher for model access while keeping project files, outputs, custom agents, and task workspaces inside this lab.
