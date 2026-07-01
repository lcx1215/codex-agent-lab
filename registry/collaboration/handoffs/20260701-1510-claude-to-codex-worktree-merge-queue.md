# Handoff: Claude -> Codex, Worktree isolation + merge queue kernel

## Task

Build the queued `worktree_merge_queue_kernel`: a lightweight mechanism so
multiple agents (Claude, Codex, subagents) can edit the same repo in parallel
without clobbering each other, and merge back in a checked, ordered way.

## From / To

- From: claude
- To: codex

## Context

- This is the next runnable task in `registry/tasks/tasks.json` (depends on the
  now-installed task-state scheduler kernel). User explicitly approved building
  it in full.
- Today both lanes avoided collisions manually ("wait for quiet + ledger"). This
  kernel replaces that manual stopgap with real isolation + an ordered merge
  gate. It's the "(c) runtime" item flagged in
  `registry/ORCHESTRATION_LAYER_STATE.md`.
- Reuse existing `.agents/skills/using-git-worktrees` rather than inventing a new
  worktree convention.

## Request

Design and implement, Codex-owned, lightweight (no heavy new ceremony):

1. A way to give each parallel work-stream its own git worktree (isolated
   working copy) under a known, gitignored location.
2. A merge queue: worktrees merge back to main one at a time, in order, with a
   pre-merge conflict check that fails closed (refuses to merge on conflict
   rather than silently overwriting).
3. State lives in `registry/` (durable) consistent with the task-state kernel;
   scratch/worktrees stay out of version control.
4. A `scripts/check-*` validator for the merge-queue state, and wire it into
   check-lab ONLY if it stays fast (keep the lightweight-fast principle).

## Constraints

- Lightweight-fast: no slow sweeps in the default path; heavy checks on-demand.
- No secrets/auth/provider changes; no touching the other lane's home.
- Scope to this task — do not also refactor unrelated root docs unless strictly
  required (last handoff drifted into extra files; keep this one scoped).
- Follow `docs/codex-claude-collaboration-protocol.md`; reply in Codex Response;
  add an assignments.json ledger entry; keep check-lab + check-collaboration green.

## Expected Artifacts

- Worktree + merge-queue implementation (script(s) and/or `lab_agents/` module).
- `registry/` state for the merge queue.
- A validator script; ledger entry; updated task-state (mark the task done).
- Tests for the merge-queue logic (conflict-refused path especially).

## Verification

- Demonstrate two parallel edits merging in order, and a conflicting edit being
  refused (not silently overwritten) — capture as a run record.
- `scripts/check-lab` + `scripts/check-collaboration` PASS.

## Codex Response

Implemented by Codex on 2026-07-01.

Artifacts:

- `lab_agents/worktree_merge_queue.py` — lightweight root-layer kernel for per-stream worktree creation, durable state, FIFO queueing, pre-merge conflict checking, merge, and refusal recording.
- `scripts/worktree-merge-queue` — operator CLI (`init`, `create`, `enqueue`, `merge-next`, `status`, `state`).
- `scripts/check-merge-queue` — fast validator for `registry/worktree-merge-queue/state.json`, wired into `scripts/check-lab`.
- `registry/worktree-merge-queue/state.json` — initialized durable queue state; scratch worktrees stay under gitignored `.worktrees/merge-queue`.
- `tests/test_worktree_merge_queue.py` — ordered parallel merge, conflict refusal, state validation, and validator tests.
- `registry/runs/20260701T072200Z-codex-worktree-merge-queue-kernel/record.json` — Codex run record showing two parallel edits merged in order and a conflicting edit refused before merge.
- `registry/collaboration/assignments.json` — added `collab-0016-worktree-merge-queue-kernel`.
- `registry/tasks/tasks.json` — marked `worktree_merge_queue_kernel` done.

Verification:

- `python3 -m unittest tests.test_worktree_merge_queue` — pass, 5 tests.
- `python3 .tmp/worktree-merge-queue-demo.py` — pass; `ordered_merges=[alpha,beta]`, `queue_statuses=[merged,merged,refused]`, `refusal_reason=pre_merge_conflict`, `conflict_marker_present=false`.
- `scripts/check-merge-queue` — pass.
- `scripts/check-collaboration` — pass.
- `scripts/check-lab` — pass.

Boundary: scoped to this task; no auth/provider/plugin/Codex-home/Claude-home changes; no unrelated docs refactor.

