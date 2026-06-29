# tmux Worker 1 — Execution/Value Evidence

## Files inspected

- `team-runtime-repo/TASK.md`
- `team-runtime-repo/source/docs/workflow-modes.md`
- `team-runtime-repo/source/registry/OMX_RETROSPECTIVE.md`
- `team-runtime-repo/source/previous-proof/omx-execution-report.md`

## Verdict

Useful, but only tmux-parallel remains the meaningful unproven step in the inspected evidence.

## App-only evidence

- Best fit: `daily-app` for quick development/debug/review; `multi-agent-review` starts App-first and escalates only when durable coordination helps.
- Observed value: fast local edits and App-safe OMX spine produced most earlier lab file work.
- Limit: previous evidence says App-only mostly proved governance, artifact discipline, and verification habits, not independent runtime execution or parallel throughput.

## Single `omx-api exec` evidence

- Best fit: `omx-long-horizon` for durable CLI runtime work with brief/progress/validation/handoff artifacts and green-light activation.
- Observed value: the retrospective records green-light events, `omx-api doctor` success, a real `omx-api exec` smoke/proof, and produced artifacts (`omx-execution-report.md`, `validation.md`, `benefit-matrix.json`, `progress.md`).
- Limit: the previous proof report qualifies the claim: its main execution surface was Codex App outside tmux, and accidental `omx-api` invocations failed before useful work. So the single-exec value is moderate and auditability-heavy, not a clean proof of autonomous CLI completion.

## tmux-parallel `omx-api exec` evidence

- Best fit: `multi-agent-review` when independent slices improve correctness/speed and CLI runtime adds durable coordination.
- Current source evidence: no prior inspected file proves team/swarm or tmux-parallel throughput; both the retrospective and previous proof name this as the next proof point.
- Expected value to measure: two independent worker artifacts, conflict-free writes, leader integration, and validation evidence that work completed faster or with better coverage than App-only or a single `omx-api exec`.

## Bottom line

- App-only: pass for small/ordinary work; weak for execution-layer proof.
- Single `omx-api exec`: useful for durable artifacts, auditability, restartability, and routing; still mixed as runtime proof.
- tmux-parallel `omx-api exec`: potentially most valuable for multi-agent execution, but the inspected files show it is not proven yet.
