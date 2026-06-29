# OMX Retrospective

Last updated: 2026-06-29 21:35 +0800

## Question

Did OMX materially help in the previous setup and upper-layer expansion steps?

## Evidence Reviewed

- `outputs/shared/omx-green-light/events.tsv` shows CLI OMX runtime was used for version checks, `doctor`, and a real `omx-api exec` smoke task.
- `codex-architecture-doctor --deep` verified `omx-api doctor` with `18 passed, 0 warnings, 0 failed`.
- Most lab file edits were performed inside Codex App using the App-safe OMX spine rather than an OMX team or worker runtime.
- Shared state was recorded in `/Users/liuchengxu/.codex/lane-guard/current-progress.md` and synced to the API-relay lane.

## What Helped

- Routing discipline: App stayed the main surface, while CLI/OMX was reserved for complex or durable work.
- Auditability: the green-light log made OMX activation visible and reviewable.
- Runtime confidence: `omx-api doctor` and the real exec smoke test proved the CLI runtime can call the model and use the API-relay home.
- Shared continuity: lane-guard updates made App and CLI resume from the same non-secret context.
- Verification habit: the OMX rule set pushed each step toward explicit doctor/check/test evidence before declaring completion.

## What Did Not Help Yet

- OMX did not significantly accelerate the App-side file edits; those were normal Codex App tool edits.
- OMX team/swarm mode was not used.
- OMX specialist delegation was not necessary for the first two layers because the work was narrow and local.
- The benefit so far is mostly architecture, governance, and verification, not parallel implementation throughput.

## Practical Conclusion

OMX has been useful as a workflow spine and CLI runtime readiness layer. It has not yet proven extra value as a multi-agent execution engine on this machine because we have not run a real multi-agent or overnight task through it.

## Next Proof Point

Layer 2 should make the routing explicit. After that, the first real proof should be a bounded `omx-long-horizon` or `multi-agent-review` task with:

- a dedicated workspace,
- visible green-light activation,
- progress and validation artifacts,
- a measurable comparison against doing the same work only in App.

## Proof 1: Bounded `omx-api exec`

Date: 2026-06-29 20:50 +0800

Workspace: `workspaces/20260629_204008-omx-execution-proof`

Result: mixed but useful.

Evidence:

- `omx-api exec` launched a real CLI Codex session through the API-relay lane.
- Green-light events were written for the proof run.
- The run produced `omx-execution-report.md`, `validation.md`, `benefit-matrix.json`, and `progress.md`.
- App-side audit added `app-audit.md`.
- App-side re-ran `scripts/check-workflow-modes`, `scripts/check-lab`, and `scripts/workflow-mode omx-long-horizon`; all required checks passed.

Value observed:

- Useful for bounded CLI execution, durable artifacts, auditability, restartability, and explicit routing.
- The agent recovered from a small shell-wrapper mistake (`status` is read-only in zsh).

Limits observed:

- No OMX team/swarm or parallel multi-agent throughput was used.
- A here-doc quoting mistake accidentally invoked `omx-api` from Markdown backticks; those accidental invocations failed before doing useful work but did emit green-light log entries.
- A temporary `/tmp/benefit-matrix-check.txt` was created and later removed by App-side audit.

Updated conclusion:

OMX has now proven modest execution-layer value for CLI-bounded artifact work. It has not yet proven enough value to route small App-sized edits through OMX by default, and it still needs a stricter long-running or team/tmux proof before claiming parallel execution benefit.

## Proof 2: Team/Tmux And Parallel Exec Probe

Date: 2026-06-29 21:35 +0800

Workspace: `workspaces/20260629_210146-omx-team-tmux-proof`

Result: mixed; useful blocker evidence.

Evidence:

- `team-clean-launch.log` shows `omx-api team` reached green-light activation and worker startup resolution, then failed with `worker_notify_failed...tmux_send_keys_failed...can't find pane: %1` and `LAUNCH_EXIT:1`.
- `tmux-worker-1.md` and `tmux-worker-2.md` were produced by two direct tmux-launched `omx-api exec` workers against independent prompts.
- `tmux-worker-1.log` and `tmux-worker-2.log` both ended with `EXIT:0` for those direct parallel exec workers.
- Worker 2 recorded a separate startup-script blocker from `worker-debug.log`: `.omx/state/team/.../runtime/worker-1-startup.sh: No such file or directory`.

Value observed:

- Direct tmux parallel `omx-api exec` can produce independent, conflict-free worker artifacts in the lab workspace.
- The reports sharpened the next hardening targets: pane preflight, atomic worker runtime setup, stage-specific status, and clearer worker contracts.

Limits observed:

- Official OMX team/tmux runtime still did not prove useful parallel team execution.
- Green-light activation is not proof that worker prompts were delivered or artifacts were produced.
- Runtime debug logs should stay transient unless deliberately summarized into durable proof artifacts.

Updated conclusion:

OMX remains useful for CLI-bounded artifact execution and App/CLI routing discipline. Direct tmux-parallel `omx-api exec` is promising for supervised parallel review, but official `omx team` still needs runtime hardening before this lab should treat it as a reliable multi-agent execution engine.
