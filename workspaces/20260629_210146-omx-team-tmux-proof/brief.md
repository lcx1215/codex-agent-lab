# Task Brief

Created: 2026-06-29 21:01:46 +0800

## Objective

Run a bounded `omx team` / tmux proof task to evaluate whether durable OMX team workers add execution value beyond single `omx-api exec` and App-side orchestration.

This proof is intentionally small but real: launch two OMX team workers in tmux, have them independently inspect existing lab workflow/proof artifacts, and write bounded reports inside this workspace only.

## Constraints

- Keep work inside this workspace unless explicitly assigned otherwise.
- Do not read or write secrets.
- Record verification evidence before completion.
- Do not modify parent lab source files.
- Do not change Codex auth, provider config, plugins, LaunchAgents, global rules, or App state.
- Parent lab files may be inspected read-only for evidence.

## Required Team Outputs

- `team-worker-1.md`: worker report focused on execution/value evidence.
- `team-worker-2.md`: worker report focused on risks/failure modes.
- `team-summary.md`: leader/App-side integration summary.
- `validation.md`: exact commands, status, and evidence.
- `benefit-matrix.json`: structured comparison of App-only, `omx-api exec`, and `omx team`.
- Update `progress.md`.

## Acceptance Checks

- A real tmux session is created for the team proof.
- `omx team` startup evidence is captured.
- Team state exists under `.omx/state/team/`.
- At least one team status/await/resume/status-equivalent command or state inspection is captured.
- Required workspace artifacts are present.
- App-side audit records whether team/tmux produced meaningful speed/smarts benefits.
