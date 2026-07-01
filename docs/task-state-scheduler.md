# Task-State Scheduler Contract

Last updated: 2026-07-01 14:05 +0800
Owner lane: codex (root-layer orchestration surface)
Status: v1 active, lightweight gate only

Related: `registry/tasks/tasks.json`, `lab_agents/task_state.py`,
`scripts/check-task-state`, `scripts/lab-dashboard`.

## Why

The lab needs durable long-horizon task state before it can become a
production-grade multi-agent runtime. This contract adds the shared headless
state layer without adding a daemon, queue worker, desktop UI, or automatic
agent launcher.

Codex and Claude can both read the registry and agree on what is pending,
running, blocked, under review, verified, done, or cancelled. Human judgment and
agent execution still own implementation; this layer only records and validates
the coordination state.

## Storage

- Canonical registry: `registry/tasks/tasks.json`.
- Schema version: `1`.
- Each task is a JSON object with `id`, `title`, `state`, `lane`, `priority`,
  `depends_on`, `created_at`, `updated_at`, optional `lease_expires_at`, and
  ordered `history`.
- The registry is durable root-layer state and may be committed.
- High-volume run output, logs, and generated scheduler traces belong under
  `outputs/`, not in `registry/tasks/`.

## State Machine

Valid states:

- `pending`: defined but not currently owned by a running lane.
- `running`: actively owned by a lane; should have a fresh lease when work may
  span sessions.
- `blocked`: cannot move without external state or a prerequisite repair.
- `review`: implementation exists and needs review.
- `verified`: review and verification are complete, but final closeout has not
  been recorded.
- `done`: terminal success.
- `cancelled`: terminal non-success closeout.

Valid transitions:

- `null -> pending`
- `pending -> running | blocked | cancelled`
- `running -> blocked | review | cancelled`
- `blocked -> pending | cancelled`
- `review -> running | blocked | verified | cancelled`
- `verified -> done | running | cancelled`

`done` and `cancelled` are terminal.

## Scheduler View

The scheduler view is deterministic and advisory:

1. Only `pending` tasks can be runnable.
2. All dependencies must be `done`.
3. The next task is the highest `priority`; ties break by oldest `created_at`,
   then task id.
4. Running tasks with `lease_expires_at` before the current time are reported as
   stale. Stale leases make the report `warn`, not `fail`, so another lane can
   repair the task without blocking unrelated safe work.

This is not a process scheduler. It does not launch Codex, Claude, OMX, OMC,
tmux, or subagents.

## Health Gate

Run:

```bash
./scripts/check-task-state
```

The gate returns:

- `pass`: registry is valid and no stale running leases exist.
- `warn`: registry is valid, but at least one running lease is stale.
- `fail`: unreadable JSON, invalid schema, duplicate task ids, unknown
  dependencies, bad timestamps, invalid transitions, or state/history mismatch.

`scripts/check-lab` runs this gate as part of the root fast path. It is a small
JSON parse and graph check, so it should not slow Codex or Claude's normal edit
loop.

## Boundaries

- Do not store prompts, tool output, secrets, or run logs here.
- Do not use this registry as a hidden approval system; agents still proceed
  under the lab autonomy and safety rules.
- Do not mark OMC team bootstrap proven unless there is a fresh real runtime
  proof. Blocked upstream runtime work stays `blocked`.
