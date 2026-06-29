# Workspace Rules

This file is the local operating surface for this task workspace.
Use the lab template at ../../docs/project-rule-template.md when this workspace becomes a longer project.

## Scope

- Workspace root: /Users/liuchengxu/Desktop/codex-agent-lab/workspaces/20260629_204008-omx-execution-proof
- Keep edits inside this workspace unless the parent lab rules or user task name another path.
- Do not read, print, copy, or migrate secrets, auth files, session files, cookies, OTPs, or API keys.

## Routing

- Default workflow mode: omx-long-horizon
- Use Codex App for short review and GUI work.
- Use codex-api for simple terminal diagnostics.
- Use omx-api for durable, multi-step, risky, or multi-agent work.

## Proof Boundary

- This workspace is an OMX execution proof. The CLI OMX runtime may inspect parent lab docs and scripts, but may only write files inside this workspace.
- Required output files are `omx-execution-report.md`, `validation.md`, and `benefit-matrix.json`.
- Treat any need to modify parent lab source as a recommendation in the report, not as permission to edit it.

## Progress And Validation

- Keep current state in progress.md.
- Record completion evidence in brief.md, progress.md, or a dedicated validation file.
- Do not claim completion without fresh verification or an explicit validation gap.
