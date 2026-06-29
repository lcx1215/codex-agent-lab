#!/usr/bin/env bash
set -euo pipefail

cd /Users/liuchengxu/Desktop/codex-agent-lab

export TERM="${TERM:-xterm-256color}"
export OMX_GREEN_LIGHT_NOTIFY=0
export OMX_TEAM_WORKER_LAUNCH_ARGS='-c model_reasoning_effort="low"'
export OMX_DEFAULT_SPARK_MODEL="${OMX_DEFAULT_SPARK_MODEL:-gpt-5.3-codex-spark}"

TASK=$(cat <<'TASK_EOF'
Bounded team/tmux proof. Read .omx/context/team-tmux-proof-20260629T130307Z.md and workspaces/20260629_210146-omx-team-tmux-proof/AGENTS.md first.

You are a two-worker OMX Team. Keep all writes inside workspaces/20260629_210146-omx-team-tmux-proof.

Worker 1 focus: inspect docs/workflow-modes.md, registry/OMX_RETROSPECTIVE.md, and workspaces/20260629_204008-omx-execution-proof; write workspaces/20260629_210146-omx-team-tmux-proof/team-worker-1.md with execution/value evidence for Team vs App-only vs omx-api exec.

Worker 2 focus: inspect the same surfaces plus validation.md/app-audit.md from the previous proof; write workspaces/20260629_210146-omx-team-tmux-proof/team-worker-2.md with risks, failure modes, and recommended local OMX hardening.

Do not modify parent lab source. Do not read secrets. Keep each report concise, evidence-backed, and include exact files inspected plus pass/fail verdict.
TASK_EOF
)

./scripts/start-api-relay team 2:executor "$TASK"

echo "omx team command exited with status $?"
exec "${SHELL:-/bin/zsh}" -l
