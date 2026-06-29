# Workspace Rules

This file is the local operating surface for this task workspace.
Use the lab template at ../../docs/project-rule-template.md when this workspace becomes a longer project.

## Scope

- Workspace root: this directory.
- Keep edits inside this workspace unless the parent lab rules or user task name another path.
- Do not read, print, copy, or migrate secrets, auth files, session files, cookies, OTPs, or API keys.

## Routing

- Default workflow mode: multi-agent-review / omx-long-horizon
- Use Codex App for short review and GUI work.
- Use codex-api for simple terminal diagnostics.
- Use omx-api for durable, multi-step, risky, or multi-agent work.

## Team Proof Boundary

- This workspace is for a bounded `omx team` / tmux proof.
- Team workers may inspect parent lab docs, scripts, registry files, and previous proof artifacts read-only.
- Team workers must write only inside this workspace.
- Required worker artifacts are `team-worker-1.md` and `team-worker-2.md`.
- If a worker identifies a parent-lab improvement, record it as a recommendation; do not edit parent files.

## Progress And Validation

- Keep current state in progress.md.
- Record completion evidence in brief.md, progress.md, or a dedicated validation file.
- Do not claim completion without fresh verification or an explicit validation gap.
