---
name: async-race-detector
description: Use when sandbox checks, tests, scans, workers, tmux panes, or validation runners run concurrently, share temp paths, emit unexpected stderr, hang, time out, or leave residual processes.
---

# Async Race Detector

## Overview

Find hidden concurrency failures before they are normalized as successful runs.
An async gate passes only when independent tasks are isolated, quiet where
expected, time-bounded, and cleaned up.

## Workflow

1. Map all concurrent tasks and classify their writes: temp files, output
   artifacts, logs, process state, network state, and repo files.
2. Reject shared write targets unless the writer has locking or a unique output
   directory per task.
3. Require per-task `TMPDIR` and lab-local scratch paths under `.tmp/`.
4. Run:

   ```bash
   ./scripts/check-async-execution
   ```

5. Read the JSON or Markdown result, not only the terminal summary.
6. Treat unexpected stderr from quiet checks as failure even if the exit code is
   zero.
7. Check for residual processes and tmux sessions when async work launches
   workers:

   ```bash
   ps -axo pid,ppid,stat,command | rg 'omx|codex-agent-lab|team-runtime-repo' | rg -v 'rg'
   tmux list-sessions 2>/dev/null || true
   ```

## Pass Contract

| Field | Required |
| --- | --- |
| exit code | zero for every task |
| timeout | zero timed out tasks |
| stderr | empty unless explicitly allow-listed |
| temp paths | unique per task |
| outputs | unique per task or read-only |
| cleanup | no residual lab worker process or tmux session |

## Known Red Flags

- `find: ... No such file or directory` from a concurrent temp cleanup race.
- Two scans writing the same `outputs/shared/waterflow/*` files.
- A task writes under `/tmp` or relies on inherited `TMPDIR`.
- A worker log ends without an explicit `EXIT:<code>` marker.
- A green-light or startup line appears but no artifact is written.

## Common Mistakes

- Counting a run as pass because the wrapper exited zero while a child wrote
  unexpected stderr.
- Running a non-compare Waterflow scan last and accidentally deleting diff
  evidence needed for handoff.
- Killing a process before preserving the evidence needed to diagnose it.
