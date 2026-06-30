# Workspace Rules

This file is the local operating surface for the multiagent parallel proof workspace.

## Scope

- Workspace root: this directory.
- Keep edits inside this workspace unless the parent lab rules or user task name another path.
- Do not read, print, copy, or migrate secrets, auth files, session files, cookies, OTPs, or API keys.

## Scenario Boundary

- Scenario type: runtime proof workspace.
- This workspace may contain bounded evidence for parallel or multiagent execution experiments.
- It must not redefine the root lab identity or promote a runtime mode without reusable evidence.

## Codex Claude Amplification

- Use this workspace to keep proof artifacts narrow, restartable, and easy for Codex or Claude to review.
- Scripts, reports, and harnesses should amplify model-agent reasoning and execution, not replace final review or recovery.

## Routing

- Default workflow mode: OMX CLI runtime only when a proof needs durable parallel execution.
- Use App-safe review for short status checks and report reading.

## Progress And Validation

- Keep current state in `progress.md`.
- Record completion evidence in `brief.md`, `progress.md`, or a dedicated validation file.
- Do not claim completion without fresh verification or an explicit validation gap.
