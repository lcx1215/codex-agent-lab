# Handoff: Claude -> Codex, Real Interop Proof

## Task

Prove a real Codex-Claude collaboration runtime, not just an installed capability.

## From / To

- From: claude
- To: codex

## Context

- The collaboration layer is now installed in the lab: `CLAUDE.md`,
  `docs/codex-claude-collaboration-protocol.md`, `registry/collaboration/assignments.json`,
  `registry/collaboration/handoffs/`, and `scripts/check-collaboration`.
- The earlier OMC team run (assignment `collab-0001-omc-team-bootstrap`) is `blocked`: workers stayed
  `pending` with `worker_start_submit_unverified:worker-1:%1:467cbe2c5fa6`.
- `.omc/state/interop` does not exist and no tmux server was running at audit time, so interop is unproven.

## Request

From a real Terminal (not a GUI-only session), inside tmux:

1. Run `omc interop` (OMC + OMX split-pane) OR an OMC leader + one Codex/OMX `omx-api exec` worker.
2. Have the worker write a real artifact under `outputs/shared/` (no secrets, no copied auth).
3. Record the result by moving assignment `collab-0003-interop-proof` to `proven` (or `blocked` with the
   exact failure reason).

## Constraints

- Stay within lab root; do not touch `~/.codex` / `~/.codex-api-relay` auth or provider config.
- Do not copy secrets between lanes.
- Keep `agents.max_depth = 1`.

## Expected Artifacts

- A real runtime artifact under `outputs/shared/` (e.g. interop transcript or worker report).
- Updated `registry/collaboration/assignments.json` with the new status and artifact path.

## Verification

- `scripts/check-collaboration` passes.
- `scripts/check-lab` and `scripts/check-secrets` pass.
- The assignment status reflects the actual runtime outcome, not the installed capability.
