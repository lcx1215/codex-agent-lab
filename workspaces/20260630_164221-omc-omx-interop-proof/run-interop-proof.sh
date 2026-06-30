#!/usr/bin/env bash
# Real tmux OMC<->OMX interop proof.
#
# Launches a real tmux session, runs `omc interop` to create the split-pane
# layout and interop shared-state, then drives a real task round-trip:
# OMC posts a task -> OMX (real Codex model) answers it -> OMC reads it back.
set -euo pipefail

LAB_ROOT="/Users/liuchengxu/Desktop/codex-agent-lab"
WS="$LAB_ROOT/workspaces/20260630_164221-omc-omx-interop-proof"
SESSION="omcomx-proof-$$"
LOG="$WS/interop-run.log"
RESULT="$WS/interop-result.json"
TASK_ID_FILE="$WS/task-id.txt"
INTEROP_DIR="$LAB_ROOT/.omc/state/interop"
CODEX_BIN_DIR="/Applications/Codex.app/Contents/Resources"

export PATH="$CODEX_BIN_DIR:$PATH"
export OMX_OMC_INTEROP_ENABLED=1
export OMX_OMC_INTEROP_MODE=observe

cd "$LAB_ROOT"
: >"$LOG"
log() { printf '%s %s\n' "$(date +%H:%M:%S)" "$*" | tee -a "$LOG"; }

tmux kill-session -t "$SESSION" 2>/dev/null || true
rm -f "$INTEROP_DIR/config.json" 2>/dev/null || true

# --- 1. start a real detached tmux session ---
log "[proof] starting tmux session $SESSION"
tmux new-session -d -s "$SESSION" -c "$LAB_ROOT" -x 220 -y 50

# --- 2. run omc interop in the pane. Note: PATH is passed with the value
#        expanded HERE (double quotes) so the pane shell inherits the Codex
#        bin dir; we do not rely on the pane's own $PATH. ---
log "[proof] launching 'omc interop' inside tmux"
PANE_CMD="export PATH=\"$CODEX_BIN_DIR:\$PATH\"; export OMX_OMC_INTEROP_ENABLED=1 OMX_OMC_INTEROP_MODE=observe; omc interop > '$WS/omc-interop-launch.log' 2>&1"
tmux send-keys -t "$SESSION" "$PANE_CMD" Enter

# --- 3. poll for interop config.json (bounded wait, no blocking wait-for) ---
log "[proof] waiting for interop config.json"
i=0
until [ -f "$INTEROP_DIR/config.json" ] || [ "$i" -ge 30 ]; do sleep 1; i=$((i+1)); done
if [ -f "$INTEROP_DIR/config.json" ]; then
  log "[proof] interop config.json created after ${i}s"
  cp "$INTEROP_DIR/config.json" "$WS/interop-config.json"
else
  log "[proof] WARNING: interop config.json not found after ${i}s"
fi
sleep 2

# Capture pane layout (proves the split happened) and the launch banner.
tmux list-panes -t "$SESSION" -F '#{pane_id} #{pane_current_command} #{pane_width}x#{pane_height}' \
  | tee "$WS/tmux-panes.txt" | tee -a "$LOG" || true
tmux capture-pane -t "$SESSION" -p >"$WS/tmux-left-pane.txt" 2>/dev/null || true

# --- 4. OMC posts a real task into interop shared-state ---
log "[proof] OMC posting task into interop shared-state"
SESSION_ID="interop-proof-$$"
TASK_ID="$(node "$WS/omc-interop-driver.mjs" place "$LAB_ROOT" "$SESSION_ID" "$WS/task.md")"
echo "$TASK_ID" >"$TASK_ID_FILE"
log "[proof] task id: $TASK_ID"

# --- 5. OMX worker (real Codex model) processes the task ---
log "[proof] OMX worker running real Codex model (this takes ~1-2 min)"
if node "$WS/omx-interop-worker.mjs" "$LAB_ROOT" 200 >>"$LOG" 2>&1; then
  log "[proof] OMX worker reported completion"
else
  log "[proof] OMX worker exited non-zero (see log)"
fi

# --- 6. OMC collects the result from shared-state ---
log "[proof] OMC collecting result"
set +e
node "$WS/omc-interop-driver.mjs" collect "$LAB_ROOT" "$TASK_ID" 60000 >"$RESULT" 2>>"$LOG"
COLLECT_RC=$?
set -e
log "[proof] collect rc=$COLLECT_RC"

# --- 7. snapshot interop shared-state tree ---
find "$INTEROP_DIR" -type f 2>/dev/null | sort >"$WS/interop-state-tree.txt" || true

# --- 8. tear down tmux ---
log "[proof] killing tmux session $SESSION"
tmux kill-session -t "$SESSION" 2>/dev/null || true

log "[proof] done. result -> $RESULT"
exit "$COLLECT_RC"
