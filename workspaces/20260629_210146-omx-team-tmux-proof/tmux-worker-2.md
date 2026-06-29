# Tmux Worker 2: Failure Modes And Hardening

Verdict: **FAIL for real team/tmux execution proof; useful as blocker evidence.** The clean team launch reached OMX activation and worker-startup resolution, but failed before a worker prompt was delivered or any parallel team work completed.

## Files Inspected

- `team-runtime-repo/TASK.md`
- `team-runtime-repo/source/previous-proof/validation.md`
- `team-runtime-repo/source/previous-proof/app-audit.md`
- `team-clean-launch.log`
- `worker-debug.log`

## Team / Tmux Blockers

1. **Worker pane notification failed.** `team-clean-launch.log` ends with `worker_notify_failed...tmux_send_keys_failed...can't find pane: %1` and `LAUNCH_EXIT:1`. This is a team/tmux routing failure, not a worker task failure.
2. **Worker startup script was missing.** `worker-debug.log` reports `.omx/state/team/.../runtime/worker-1-startup.sh: No such file or directory` and `EXIT:127`, suggesting non-atomic runtime materialization, cleanup/race behavior, or a path mismatch.
3. **No team execution value was proven.** The prior proof showed a useful single `omx-api exec` run, but `validation.md` and `app-audit.md` both state it was not an attached tmux/team runtime and did not prove parallel throughput.
4. **Activation signal can be misleading.** `team-clean-launch.log` shows `OMX ACTIVE`, but the launch still failed before useful worker execution. Green-light events should not be treated as proof of task progress.
5. **Shell safety remains a local risk.** Prior evidence recorded unquoted here-doc backtick expansion that accidentally invoked `omx-api`, plus a zsh `status` read-only variable wrapper error.

## Local OMX Hardening Recommendations

- Add a **team preflight gate**: list tmux panes, verify each target pane id exists, and abort before notification if any pane is missing.
- Make worker runtime setup **atomic and verified**: create/chmod startup scripts, write a manifest, then assert every worker script path exists before any `send-keys`.
- Emit **stage-specific status**: `green_light`, `pane_ready`, `startup_script_ready`, `prompt_delivered`, `artifact_written`, `commit_done`, `team_complete`.
- Preserve failed team state for audit: on launch failure, write a compact failure manifest under workspace `.omx/state/...` instead of leaving only stdout/stderr fragments.
- Harden generated shell writes: require single-quoted here-docs or a Python/pathlib writer; lint for Markdown backticks in shell heredocs and avoid `status=$?` under zsh.
- Normalize worker contract inputs: output path, commit requirement, and “do not modify other files” should be explicit launch parameters so team workers do not inherit contradictory task/report/commit rules.

## Stop Condition For Next Proof

Count the next team/tmux proof as passing only if worker panes are verified, prompts are delivered, required worker artifacts are written by the team runtime, and the requested commit behavior is completed or explicitly disabled by the active task instruction.
