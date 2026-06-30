# Team/Tmux Proof Summary

Date: 2026-06-29 21:35 +0800

## Verdict

Mixed result.

- Official `omx-api team` did not complete useful worker execution.
- Direct tmux-parallel `omx-api exec` did complete two independent worker reports.
- Local OMX wrappers were hardened during the proof.

## What Worked

- `omx-api` green-light events were emitted for all CLI OMX activations.
- A clean proof repo allowed OMX Team to pass the dirty-worktree gate and create team state/worktree startup material.
- Two direct tmux panes ran independent `omx-api exec` workers concurrently.
- `tmux-worker-1.md` and `tmux-worker-2.md` were written, and both direct worker logs ended with `EXIT:0`.

## What Failed

- The first `omx-api team` attempt was blocked by the one-time GitHub star prompt.
- The second attempt exposed `omx-api` wrapper incompatibility with Codex-style `-C <dir>`.
- The dirty parent lab checkout correctly blocked Team worktree launch.
- The clean proof repo launch reached worker startup resolution, then failed with `worker_notify_failed...tmux_send_keys_failed...can't find pane: %1` and `LAUNCH_EXIT:1`.
- A worker debug attempt later found the runtime startup script had already been removed, recorded as `EXIT:127` in `worker-debug.log`.

## Hardening Applied

- `/Users/liuchengxu/.local/bin/omx` and `/Users/liuchengxu/.local/bin/omx-api` now pre-create the one-time star prompt state if needed.
- Both wrappers now support Codex-style `-C <dir>` by changing directory and stripping `-C` before invoking OMX.
- Both wrappers now add a team-worker project trust override for `omx ... team` / `omx-api ... team`.
- `/Users/liuchengxu/.local/bin/codex-architecture-doctor` now checks the new wrapper behavior.
- `/Users/liuchengxu/.local/bin/codex-sync-api-relay-context` now uses `rsync` and excludes/deletes synced `auth.json` and `config.toml` files from mirrored non-secret context trees.

## Practical Conclusion

For this Mac today, use:

- App-safe OMX spine for normal App work.
- `omx-api exec` for bounded CLI artifact tasks.
- tmux-parallel `omx-api exec` for supervised parallel review slices when useful.

Do not treat official `omx team` as reliable yet. It has useful state/worktree design, but this proof found a worker-pane lifecycle blocker before prompt delivery.
