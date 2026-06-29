#!/usr/bin/env bash
set -euo pipefail

PROOF_ROOT="/Users/liuchengxu/Desktop/codex-agent-lab/workspaces/20260629_210146-omx-team-tmux-proof"
REPO="$PROOF_ROOT/team-runtime-repo"

cd "$REPO"

export TERM="${TERM:-xterm-256color}"
export OMX_GREEN_LIGHT_NOTIFY=0
export OMX_TEAM_WORKER_LAUNCH_ARGS='-c model_reasoning_effort="low"'

TASK=$(cat TASK.md)

/Users/liuchengxu/.local/bin/omx-api -C "$REPO" team 2:executor "$TASK"

echo "omx team command exited with status $?"
exec "${SHELL:-/bin/zsh}" -l
