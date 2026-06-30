---
name: tmux-omx-runtime-doctor
description: Use when OMX team, tmux panes, worker startup scripts, green-light events, omx-api exec, or codex exec workers fail, hang, miss artifacts, or leave stale runtime state.
---

# Tmux OMX Runtime Doctor

## Overview

Diagnose OMX/tmux runtime failures as staged execution problems, not as generic
agent confusion. Green-light means activation only; proof requires pane
readiness, prompt delivery, artifact creation, exit evidence, and cleanup.

## Workflow

1. Capture the workspace, team id, session name, command, and expected artifacts.
2. Preserve current evidence before cleanup: launch logs, worker logs, `.omx`
   state summaries, pane list, and process list.
3. Check stages in order:

   | Stage | Evidence |
   | --- | --- |
   | activation | green-light event and command line |
   | pane ready | `tmux list-panes -t <session>` |
   | runtime materialized | worker startup scripts and manifests exist |
   | prompt delivered | worker log shows accepted prompt or first action |
   | artifact written | expected output files exist and pass readback |
   | exit recorded | log ends with `EXIT:<code>` or status JSON |
   | cleanup done | no proof tmux session or worker process remains |

4. For official `omx team` failures, distinguish dirty worktree gates,
   wrapper argument issues, pane notification failures, and missing startup
   scripts.
5. For direct tmux `omx-api exec` workers, verify each pane has its own output
   file and log file.
6. Record the blocker as a repair order in the workspace `validation.md`,
   `progress.md`, or a dedicated handoff.

## Diagnostic Commands

```bash
tmux list-sessions 2>/dev/null || true
tmux list-panes -t <session> -F '#{pane_id}\t#{pane_current_command}\t#{pane_start_command}'
ps -axo pid,ppid,stat,command | rg 'omx|codex exec|team-runtime-repo' | rg -v 'rg'
grep -H 'EXIT:' <worker-logs>
find <workspace> -maxdepth 2 -type f \( -name '*launch*.log' -o -name '*worker*.log' -o -name '*.md' \)
```

## Failure Families

- `leader_workspace_dirty_for_worktrees`: commit, stash, or use a clean proof
  repo before team worktree launch.
- `unrecognized subcommand`: wrapper argument forwarding is wrong, often from
  passing Codex-style `-C` through to OMX.
- `worker_notify_failed` or `can't find pane`: pane lifecycle or tmux target
  resolution failed before prompt delivery.
- missing `worker-*-startup.sh`: runtime materialization is non-atomic, deleted,
  or pointed at the wrong team id.
- no artifact with green-light present: activation happened, execution did not
  reach the task.

## Stop Rule

Do not call `omx team` reliable until a proof shows pane readiness, prompt
delivery, required artifacts, exit markers, and cleanup. Direct tmux
`omx-api exec` can be used as a supervised fallback when each worker has
isolated logs and artifacts.
