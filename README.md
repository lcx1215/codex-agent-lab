# Codex Agent Lab

Clean, project-scoped environment for long-horizon Codex agent work.

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

Use explicit agent names when asking for delegation. Keep each run narrow and write durable state to `registry/current-progress.md`.

## Guidance Layering

Global rules stay in the active Codex home. This lab can use a local reference from `.codex-home/AGENTS.md` to `~/.codex/AGENTS.md` so the clean-home lane inherits global policy without maintaining a divergent copy.

This repo's `AGENTS.md` is only an environment-specific overlay: isolation, lab paths, agent roles, local skills, and validation rules.

Framework:

- Global: `~/.codex/AGENTS.md`
- Lab overlay: `AGENTS.md`
- Lab operating notes: `README.md`
- Custom agents: `.codex/agents/*.toml`
- Environment-specific skills: `.agents/skills/*/SKILL.md`
- Durable progress and validation: `registry/`
- Task-specific work: `workspaces/`
- Waterflow reports and repair briefs: `outputs/shared/waterflow/`
- Waterflow change briefs: `outputs/shared/waterflow/waterflow-change-briefs.md`
- Waterflow validation plan: `outputs/shared/waterflow/waterflow-validation-plan.md`
- Waterflow changed-only validation plan: `outputs/shared/waterflow/waterflow-validation-plan-changed.md`
- Waterflow validation results: `outputs/shared/waterflow/waterflow-validation-results.md`
- Waterflow route index: `outputs/shared/waterflow/waterflow-route-index.md`
- Waterflow stress results: `outputs/shared/waterflow/stress/*/waterflow-stress-results.md`
- Waterflow incident handoffs: `outputs/shared/waterflow/incidents/*/codex-claude-handoff.md`
- Waterflow harness philosophy: `docs/waterflow-harness-philosophy.md`
- Waterflow path index and diff: `outputs/shared/waterflow/waterflow-path-index.json` and `outputs/shared/waterflow/waterflow-path-diff.json`

Waterflow scans its own `waterflow/`, `tests/`, and `docs/` paths. Generated `outputs/` are evidence artifacts, not source waterways, so they are excluded from the graph to avoid constant self-diff noise.

For large path counts, use route index and changed-only validation first. The stress harness can generate arbitrary scale fixtures; the number is a pressure parameter, not a target architecture.

For realistic failure rehearsal, use the incident harness. It creates an isolated bad fixture, records expected command failures and timeouts, and writes an actionable handoff for Codex or Claude. An incident harness pass means detection and reporting worked; it does not mean the fixture or the real lab is healthy.

## Skills And Plugins

Codex can use its normal global skills and plugins when they are available in the active lane. Skills specific to this lab or to a task inside it should live under `.agents/skills/`.

## Secret Safety

Do not commit API keys, GitHub tokens, `.env` files, private keys, cookies, or auth/session files. Run this before committing:

```bash
./scripts/check-secrets
```

The repository also includes a GitHub Actions secret scan that blocks common GitHub, OpenAI, AWS, private-key, `.env`, and auth-file leaks.

## Boundaries

This lab must not mutate the user's default App/Plus lane or API-relay lane. It can use the API-relay launcher for model access while keeping project files, outputs, custom agents, and task workspaces inside this lab.
