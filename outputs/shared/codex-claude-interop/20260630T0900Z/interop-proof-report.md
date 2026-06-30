# Codex-Claude OMC<->OMX Interop Proof

Generated: 2026-06-30 17:03 +0800
Lane: Claude/OMC leader (full base + memory) driving Codex/OMX worker.
Verdict: **PROVEN** — a real tmux interop session ran a real OMC->OMX task
round-trip processed by the real Codex model.

## What Was Proven

This is the first real runtime proof of the Codex-Claude collaboration layer
(Capability Layer 6). Earlier state was "capabilities installed, runtime
unproven" (the prior OMC team run was `blocked` with
`worker_start_submit_unverified`). This run closes that gap.

## How

A real detached tmux session was created, and `omc interop` was launched inside
a genuine tmux pane. It initialized the interop shared-state session and split
the window into two real panes:

```
%2 zsh    110x50   <- left  pane: Claude Code (OMC)
%3 codex  109x50   <- right pane: Codex CLI (OMX)
```

`omc interop` banner (observe mode, fail-closed):

```
[interop] mode=observe, enabled=1, tools=0, failClosed=1
Initializing interop session: interop-0bd076ec
Splitting pane: Left (Claude Code) | Right (Codex)
Interop session ready!
```

Then a real task round-trip was driven through the file-based interop
shared-state protocol (`.omc/state/interop`):

1. **OMC posts** (leader): `omc-interop-driver.mjs place` created task
   `task-1782809987353-7b9a7e408` (`source=omc`, `target=omx`, `type=analyze`)
   via the package's own `addSharedTask` API. Status: `pending`.
2. **OMX processes** (worker): `omx-interop-worker.mjs` picked the pending
   omc->omx task, set it `in_progress`, ran the **real Codex model** through
   `omx-api exec` (provider `custom`, model `gpt-5.5`, reasoning `xhigh`), and
   wrote the model answer back via `updateSharedTask`. Status: `completed`.
3. **OMC collects** (leader): `omc-interop-driver.mjs collect` read the
   completed task back from shared-state. Exit code 0.

Lifecycle timestamps (real, ~29s end to end):
`createdAt 2026-06-30T08:59:47.353Z` -> `completedAt 2026-06-30T09:00:16.642Z`.

## The Model's Answer (returned through interop)

```
File-based interop makes handoff durable: tasks/messages survive terminal restarts and context loss.
Artifact descriptors give explicit inputs/outputs instead of fragile pasted blobs.
Atomic writes reduce partial-state/race failures between agents.
Audit logs make ownership, timing, and decisions reviewable later.
Retention policy separates useful artifacts from transient chatter.
INTEROP-PROOF-OK high
```

The result (415 chars) was under the 2048-byte artifact threshold, so it was
stored inline (`resultArtifact: null`) — exactly the protocol's designed
behavior. Larger results would have spilled to an artifact descriptor.

## Evidence Files

- `interop-config.json` — the live interop session config.
- `task.json` — the full task lifecycle (pending -> in_progress -> completed).
- `interop-result.json` — what OMC read back from shared-state.
- `tmux-panes.txt` — proof the split-pane (zsh + codex) existed.
- `omc-interop-launch.log` — the real `omc interop` launch banner.
- `interop-run.log` — the orchestration timeline.

Reproduce: `workspaces/20260630_164221-omc-omx-interop-proof/run-interop-proof.sh`.

## Boundaries Respected

- No secrets read or copied; no `auth.json`, tokens, or provider config touched.
- Codex `~/.codex` / `~/.codex-api-relay` auth and provider config left intact;
  OMX ran through the existing API-relay lane via `omx-api`, not by copying
  credentials into the lane.
- All writes stayed inside the lab root.
- The unrelated `customer-ai-gateway` tmux session was left untouched; only the
  proof's own `omcomx-proof-*` session was created and torn down.

## Lane Relationship Note (OMC + OMX as the two "小弟")

OMC (this Claude lane) acted as leader/orchestrator; OMX (Codex lane) acted as
the model worker. The interop protocol is the neutral ground between them: OMC
decides and verifies, OMX executes with its model, and the file-based
shared-state is the contract neither lane has to trust the other's memory for.

## Known Limitation

This proof used `observe` mode and drove the shared-state protocol directly via
the package's own APIs (the same functions the interop MCP tools call). It did
not exercise the `active`-mode MCP tool path (`interop_send_task` etc.), which
additionally requires `OMC_INTEROP_TOOLS_ENABLED=1` and an MCP client. That is
the natural next proof if active-mode tool calls need their own evidence.
