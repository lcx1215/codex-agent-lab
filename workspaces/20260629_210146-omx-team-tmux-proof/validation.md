# Validation

## Official OMX Team Attempts

- Command: `tmux new-session ... ./launch-team.sh`
  - Result: fail.
  - Evidence: initial launch blocked on `[omx] Enjoying oh-my-codex? Star it on GitHub? [Y/n]`.

- Command: `tmux new-session ... ./launch-team.sh` after star-prompt state existed.
  - Result: fail.
  - Evidence: `team-launch.log` recorded `error: unrecognized subcommand '2:executor'`, caused by passing Codex-style `-C` through to `omx`.

- Command: `tmux new-session ... ./launch-team.sh` after wrapper `-C` hardening.
  - Result: fail as expected safety gate.
  - Evidence: `team-launch.log` recorded `leader_workspace_dirty_for_worktrees...commit_or_stash_before_omx_team`.

- Command: `tmux new-session ... ./launch-team-clean.sh` from clean proof repo.
  - Result: fail before useful worker execution.
  - Evidence: `team-clean-launch.log` recorded worker startup resolution, then `worker_notify_failed...tmux_send_keys_failed...can't find pane: %1` and `LAUNCH_EXIT:1`.

## Direct Tmux Parallel OMX Exec Fallback

- Command: direct tmux pane 1 running `omx-api -C <proof> exec <worker-1 prompt>`.
  - Result: pass.
  - Evidence: `tmux-worker-1.md` exists and has 36 lines.
  - Evidence: `tmux-worker-1.log` ended with `EXIT:0`.

- Command: direct tmux pane 2 running `omx-api -C <proof> exec <worker-2 prompt>`.
  - Result: pass.
  - Evidence: `tmux-worker-2.md` exists and has 32 lines.
  - Evidence: `tmux-worker-2.log` ended with `EXIT:0`.

## Local Hardening Checks

- Command: `/Users/liuchengxu/.local/bin/codex-architecture-doctor`
  - Result: pass.
  - Evidence: `68 passed, 0 warnings, 0 failed`.

- Command: `CODEX_API_RELAY_DISABLE_CONTEXT_SYNC=1 /Users/liuchengxu/.local/bin/codex-sync-api-relay-context --quiet`
  - Result: pass.
  - Evidence: command completed without output or rm noise.

- Command: filename-only check for synced secret config copies.
  - Result: pass.
  - Evidence: no `auth.json` or `config.toml` files remained under API-relay mirrored `lane-guard`, `memories`, `skills`, `prompts`, or `agents` trees.

## Cleanup Checks

- Command: `tmux list-sessions`
  - Result: pass.
  - Evidence: no proof tmux sessions remained after the direct parallel exec completed.

- Command: process scan for lab OMX/Codex proof workers.
  - Result: pass.
  - Evidence: no `omx exec`, `codex exec`, `team-runtime-repo`, or proof tmux worker processes remained.

## Lab Health Checks After Recording Artifacts

- Command: `scripts/check-secrets`
  - Result: pass.
  - Evidence: `OK: no committable secrets or README-local user paths detected`.

- Command: `scripts/check-lab`
  - Result: pass.
  - Evidence: `OK: lab structure is valid`.

- Command: `python3 -m unittest discover -s tests`
  - Result: pass.
  - Evidence: `Ran 12 tests` and `OK`.

- Command: `scripts/waterflow-verify`
  - Result: pass.
  - Evidence: 5 checks, 5 passed, 0 failed.

- Command: `scripts/waterflow-scan --root . --compare-last`
  - Result: pass.
  - Evidence: final scan reported `findings: 0`.
