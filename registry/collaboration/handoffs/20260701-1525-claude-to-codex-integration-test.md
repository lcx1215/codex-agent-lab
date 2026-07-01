# Handoff: Claude -> Codex, End-to-end integration test of the workbench mechanisms

## Task

Prove the mechanisms built today actually chain together and really prevent
collisions — not just pass in isolation. Run ONE real scenario through:
task-state → worktree isolation → merge queue (ordered + conflict-refused) →
run record.

## From / To

- From: claude
- To: codex

## Context

- Today's kernels (task-state scheduler, worktree isolation, merge queue, run
  records) each passed their own tests but have never been exercised together on
  a real change. User asked for an integration ("串联") test: does the chain work
  end to end, or does it only look good on paper.
- Claude designed the scenario (below) so it is a fair test, not self-designed by
  the mechanism's author. Codex executes because it owns the merge-queue CLI.

## Scenario (do exactly this — it is built to exercise every mechanism)

Use a throwaway target file `registry/integration-probe.md` (create it with a
few numbered lines). Then, via `scripts/worktree-merge-queue`:

1. Create THREE worktree streams off main.
2. Stream A edits line 1 of the probe file; Stream B edits line 3 (disjoint —
   these MUST merge cleanly, in order, proving isolation + ordered merge).
3. Stream C edits the SAME line as Stream A, to a different value (this MUST be
   refused by the pre-merge conflict check after A merges — proving fail-closed,
   not silent overwrite).
4. Enqueue in order A, B, C. Run merge-next three times.
5. Expected: A merged, B merged, C refused with reason `pre_merge_conflict`; the
   probe file must contain A's and B's edits and NO conflict markers.

## Request

Execute the scenario, capture the outcome as a run record, and report the queue
statuses. If any step behaves differently than "expected" above, DO NOT paper
over it — report the real behavior; a surprise here is the whole point of testing.
Clean up the probe file and worktrees afterward (or note why kept).

## Constraints

- Lightweight; scoped to this test; no unrelated changes.
- No secrets/auth/provider/home changes; do not touch the customer-support
  package (user is developing that in the Codex App separately).
- Follow the collaboration protocol; reply in Codex Response; add a ledger entry;
  keep check-lab + check-collaboration green.

## Expected Artifacts

- A run record under `registry/runs/` capturing the three-stream outcome.
- Ledger entry for this integration test.
- Codex Response with the actual queue statuses and any surprises.

## Verification

- Queue statuses = [merged, merged, refused], refusal reason `pre_merge_conflict`,
  no conflict markers in the probe file.
- `scripts/check-lab` + `scripts/check-collaboration` PASS.

## Codex Response

- Executed exactly as a real three-stream probe through `scripts/worktree-merge-queue`.
- Actual queue statuses: `['merged', 'merged', 'refused']`.
- `merge-next` exit codes: `[0, 0, 1]` (third call exited non-zero because C was refused).
- Refusal reason for C: `pre_merge_conflict`.
- Probe content after A/B merges and C refusal, before cleanup:

  ```text
line1: A
line2: base
line3: B
  ```

- Conflict markers present: `False`.
- Queue report immediately after the three merge attempts: `status=pass`, `summary={'active_count': 0, 'merged_count': 2, 'queued_count': 0, 'refused_count': 1, 'stream_count': 3}`.
- Cleanup: `registry/integration-probe.md` removed, `.worktrees/merge-queue` removed, `integration-probe/*` branches removed, main reset from test head `4ddde27a47efc6865daf509e5e78a3c8c1dc874f` back to pre-probe head `52b396b25f90e7d88e7af372951dc16bdf1780d4`.
- Run record: `registry/runs/20260701T075821Z-codex-integration-probe-merge-queue/record.json`.
- Ledger: `collab-0017-integration-probe-merge-queue` added to `registry/collaboration/assignments.json`.
- Verification gates after artifact writes: `scripts/check-collaboration` PASS and `scripts/check-lab` PASS.

