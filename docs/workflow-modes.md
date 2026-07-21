# Workflow Modes

This lab now uses a lightweight App plus Codex API surface. The old extra orchestration runtime has been removed from this machine.

## Mode Index

| Mode | Default Surface | Entry |
| --- | --- | --- |
| `daily-app` | Codex App | Open the project in App and use the nearest `AGENTS.md` |
| `cli-diagnosis` | Terminal/API-relay | `codex-api` |
| `multi-agent-review` | Codex App first | App-native subagents for bounded slices when useful |
| `overnight-checkpoint` | Codex App or `codex-api` | Dedicated workspace plus progress/validation files |

## `daily-app`

Use for ordinary development, quick debug, GUI review, and short feedback loops.

- Entry command: none; stay in Codex App.
- Expected artifacts: changed project files plus optional notes when useful.
- Verification path: targeted tests or local checks for the changed behavior.
- Stop condition: requested change is implemented, verified, and summarized.

## `cli-diagnosis`

Use for bounded terminal checks, environment diagnosis, command output, and quick API-relay probes.

- Entry command: `codex-api`.
- Expected artifacts: terminal evidence or a small note under `outputs/api-relay/` when another lane needs it.
- Verification path: exact command output, exit code, or a short smoke test.
- Stop condition: diagnosis is answered or the next concrete action is identified.

## `multi-agent-review`

Use when independent review, verification, research, or implementation slices can improve correctness or speed.

- Entry command: App-native subagents for bounded slices.
- Expected artifacts: bounded briefs, results, integration notes, and validation evidence.
- Verification path: leader integrates findings, runs targeted checks, and records accepted/rejected recommendations.
- Stop condition: all slices are resolved, conflicts are integrated, and remaining risks are explicit.

## `overnight-checkpoint`

Use for long-running work that should survive interruption, compaction, or handoff.

- Entry command: create or reuse a dedicated folder under `workspaces/`; use Codex App or `codex-api`.
- Expected artifacts: local `AGENTS.md`, `brief.md`, `progress.md`, validation file, and final handoff.
- Verification path: checkpointed commands plus a final project-specific gate.
- Stop condition: the handoff states status, evidence, blockers, and the exact next action.
