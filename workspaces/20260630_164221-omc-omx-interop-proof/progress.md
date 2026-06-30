# Progress: OMC<->OMX Interop Proof

Status: PROVEN (2026-06-30 17:05 +0800)

- Real tmux session created; `omc interop` launched in a genuine pane.
- Split-pane confirmed: `%2 zsh` (Claude/OMC) + `%3 codex` (Codex/OMX).
- Real task round-trip through `.omc/state/interop` shared-state:
  - OMC posted `task-1782809987353-7b9a7e408` (pending).
  - OMX worker ran the real Codex model via `omx-api exec` (gpt-5.5/xhigh) and
    wrote the answer back (completed).
  - OMC collected the result, exit 0. End-to-end ~29s.
- Model answer ended with `INTEROP-PROOF-OK high`.
- Evidence persisted to `outputs/shared/codex-claude-interop/20260630T0900Z/`.
- Assignment `collab-0003-interop-proof` moved to `proven`.

No secrets crossed lanes; no Codex auth/provider config touched; unrelated
tmux sessions left intact.
