# Project Rule Template

Use this as the starting point for a project-local `AGENTS.md`. Keep global policy in the active Codex home; put only project-specific boundaries and workflows here.

## Project Identity

- Project path: `TBD`
- Project purpose: `TBD`
- Scenario type: `TBD`
- Primary lane: `Codex App`, `codex-api`, or `omx-api`
- OMX level: `none`, `App-safe spine`, or `CLI runtime`
- Durable state file: `TBD`
- Output directory: `TBD`
- Environment scale: `medium environment` or `small agent package`
- Parent environment: `TBD`

## Rule Inheritance

- Effective rules are the machine/global rules, root lab rules, this local file, and any narrower package-local rules.
- Parent lab contracts still apply: `../../AGENTS.md`, `../../CLAUDE.md`, `../../docs/environment-layering.md`, `../../docs/rule-inheritance.md`, and `../../docs/codex-claude-collaboration-protocol.md` when this file is in `workspaces/<scenario>/`.
- Local rules can only add detail or narrow scope. They must not weaken parent rules for secrets, auth, provider config, plugin state, lane isolation, sandbox boundaries, collaboration, or promotion.
- If Claude needs a local entrypoint, keep a `CLAUDE.md` pointer beside this file that tells Claude to read this local surface plus the root `CLAUDE.md`.

## Scenario Boundary

- State what belongs inside this scenario workspace.
- State what is explicitly outside this scenario workspace.
- Keep scenario-specific assumptions local until they prove reusable across scenarios.
- Do not promote UCP, commercial support, research, workflow, or any other single domain into root lab policy without cross-scenario value.
- Use `docs/scenario-workspace-contract.md` as the shared contract for scenario workspaces.
- Use `docs/environment-layering.md` to place skills, plugins, protocols, interfaces, Waterflow artifacts, and outputs at the correct scale.

## Codex Claude Amplification

- State how this workspace amplifies Codex and Claude: focused context, deterministic harnesses, validation commands, route indexes, dashboards, or handoff files.
- Do not replace Codex/Claude reasoning, coding, review, or recovery responsibilities with opaque automation.
- Keep final integration owner and verification owner explicit.

## Boundaries

- Keep edits inside this project unless the user names another path.
- Do not read, print, copy, or migrate secrets, auth files, session files, cookies, OTPs, or API keys.
- Do not change global Codex provider, auth, plugins, LaunchAgents, or App process state from this project.
- Use shared handoff files only when another lane needs the context.

## Runtime Routing

- Use Codex App for ordinary daily edits, GUI review, and short feedback loops.
- Use `codex-api` for simple terminal diagnostics or API-relay one-off work.
- Use `omx-api` when work is long-horizon, multi-agent, multi-file, risky, automation-heavy, or needs durable checkpoints.
- When OMX architecture is active, show the green-light signal required by the global rules.

## Local Workflow

- Start by reading this file plus the nearest `README.md`, `brief.md`, or progress file.
- Define the task objective, constraints, expected output, and verification path before broad edits.
- Prefer small reversible changes and existing project patterns.
- Write durable handoff notes for work that may cross sessions or lanes.

## Verification

- Record the exact commands or checks used to prove completion.
- Use targeted tests first, then broader lint/typecheck/build checks when applicable.
- If verification cannot run, record the reason and the next-best evidence.
- Do not claim completion without fresh evidence or an explicit validation gap.

## Handoff

- Handoff file: `TBD`
- Include current status, changed files, verification evidence, known risks, and next action.
- Keep the handoff concise enough for App, CLI, or OMX to resume without rereading the whole project.
