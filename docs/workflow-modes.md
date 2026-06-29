# Workflow Modes

These are the default upper-layer work modes for this lab. They turn App / CLI / OMX routing into explicit local contracts without changing global auth, provider, or App state.

## Mode Index

| Mode | Default Surface | OMX Level | Entry |
| --- | --- | --- | --- |
| `daily-app` | Codex App | None or App-safe spine when complexity appears | Open the project in App and use the nearest `AGENTS.md` |
| `cli-diagnosis` | Terminal/API-relay | None by default | `codex-api` |
| `omx-long-horizon` | Terminal/API-relay | CLI runtime | `omx-api` or `./scripts/start-api-relay` |
| `multi-agent-review` | App first, OMX when durable coordination is useful | App-safe spine or CLI runtime | `omx-api` for durable team/runtime work |
| `overnight-checkpoint` | Terminal/API-relay | CLI runtime | `omx-api` from a dedicated workspace |

## `daily-app`

Use for ordinary development, quick debug, GUI review, Computer Use, and short feedback loops.

- Entry command: none; stay in Codex App.
- Expected artifacts: changed project files plus optional App-lane notes when useful.
- Verification path: targeted tests or local checks for the changed behavior.
- Stop condition: requested change is implemented, verified, and summarized.
- OMX rule: no OMX by default; switch to App-safe spine when the task becomes multi-step, multi-file, risky, or needs a handoff.

## `cli-diagnosis`

Use for bounded terminal checks, environment diagnosis, command output, and quick API-relay probes.

- Entry command: `codex-api` for plain API-relay Codex.
- Expected artifacts: terminal evidence or a small note under `outputs/api-relay/` when another lane needs it.
- Verification path: exact command output, exit code, or a short smoke test.
- Stop condition: diagnosis is answered or the next concrete action is identified.
- OMX rule: do not use OMX unless the diagnosis turns into a complex or durable workflow.

## `omx-long-horizon`

Use for large refactors, automation workflows, multi-step implementation, risky migrations, durable planning, and work that benefits from `.omx/` state.

- Entry command: `omx-api` or `./scripts/start-api-relay` from this lab.
- Expected artifacts: workspace brief, progress file, validation evidence, and handoff notes.
- Verification path: `scripts/check-lab`, task-specific tests, `scripts/waterflow-scan --root . --compare-last`, and `scripts/waterflow-verify` when applicable.
- Stop condition: checkpoints are complete, validation evidence is recorded, and the handoff is sufficient for App or CLI resume.
- OMX rule: CLI runtime is active and must show the green-light signal.

## `multi-agent-review`

Use when independent review, verification, research, or implementation slices can improve correctness or speed.

- Entry command: App-native subagents for bounded slices, or `omx-api` when durable terminal coordination is useful.
- Expected artifacts: bounded agent briefs, results, integration notes, and validation evidence.
- Verification path: leader integrates findings, runs targeted checks, and records accepted/rejected recommendations.
- Stop condition: all agent slices are resolved, conflicts are integrated, and remaining risks are explicit.
- OMX rule: start with App-safe spine; use CLI runtime only when durable team/runtime orchestration adds value.

## `overnight-checkpoint`

Use for long-running work that should survive interruption, compaction, or handoff.

- Entry command: create or reuse a dedicated folder under `workspaces/`, then launch `omx-api`.
- Expected artifacts: local `AGENTS.md`, `brief.md`, `progress.md`, validation file, and final handoff.
- Verification path: checkpointed commands plus a final `scripts/check-lab` or project-specific gate.
- Stop condition: the next morning handoff states status, evidence, blockers, and the exact next action.
- OMX rule: CLI runtime is active and should prefer isolated workspaces or worktrees for risky changes.

## Promotion Rules

- A mode can become a skill only after it has been used successfully more than once.
- Do not promote a mode into global rules unless it is useful across projects.
- Add a health check before relying on a mode for unattended work.
