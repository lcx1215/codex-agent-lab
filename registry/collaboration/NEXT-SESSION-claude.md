# NEXT SESSION — Claude resume point

Last updated: 2026-07-01 10:00 (+0800).
Read this first, then `registry/collaboration/assignments.json` for full state.

## Where we are

The lab is **finished as a development/governance environment (a)**, and the
current goal is to **harden it to a real "controlled pilot (b)"**. The
self-audit honesty gap, customer-support run/query auth + durable run state, and
structured per-run record v1 review, lane division review, and run-record gate
promotion are now **CLOSED**.

## DONE this session (2026-07-01)

**Self-audit no longer scores "files exist" as "ready."**
File: `lab_agents/large_agent_readiness.py`.
- `verification` now *executes* `scripts/check-lab` via `_run_lab_gate` and is
  exit-code gated: green (exit 0) → `pass`, non-zero → `fail`, and if no real
  `rg` binary is found to run the gate → `mixed` (can't-verify, not a false
  pass). `_verification_signal` takes an injectable `gate_runner` for tests.
- `model-proof` (`_model_proof_signal`) now validates artifact **content +
  recency** (min content lines, required markers, `MODEL_PROOF_MAX_AGE_DAYS=21`)
  instead of passing on a matching filename.
- Locked with tests: verification fails-when-red, passes-only-when-green,
  missing-gate-fails; model-proof flags thin/stale artifacts. Codex review
  then added an all-required-markers regression and root path hardening for
  `_run_lab_gate`. Full suite = 81 pass.

**ENV GOTCHA:** `rg` in Claude's zsh is a shell function; the real binary is in
`/Applications/Codex.app/Contents/Resources`. bash subprocesses have no `rg`, so
run check-lab/pytest with `export PATH="/Applications/Codex.app/Contents/Resources:$PATH"`
or the suite looks falsely red. The new `_gate_environment` handles this inside
the auditor automatically. (macOS has no `timeout` binary.)

## Closed this session after Codex review

Ledger `collab-0010` is now **PROVEN**. Current customer-support workspace state
protects assistant work endpoints with gateway auth before body reads, fails
closed when no token is configured, and persists assistant run state to
package-local JSONL with idempotency reload. Codex verification: 22 gateway
tests pass, `audit-agent-code` fail=0 warn=0, `check-rule-ladder` pass,
`check-agent-packages` pass with `exports/` ignored, workspace safety warn-only
failed=0. The support package remains in the gitignored medium workspace.

Ledger `collab-0013` is now **PROVEN**. Claude built structured per-run record
v1; Codex approved it as a draft schema/writer, tightened blob SHA validation,
strengthened common secret value scrubbing, and corrected the first dogfood
record to use real `git hash-object` values.

Ledger `collab-0014` is now **PROVEN**. Claude built `scripts/check-run-records`
and the lane-division doc. Codex corrected the Codex-lane rows, emitted the
Codex package run record
`registry/runs/20260701T030814Z-codex-verify-customer-support-gateway/record.json`,
and wired `scripts/check-run-records` into `scripts/check-lab`. Verification:
15 run-record tests, 96 full unittest, check-run-records with 3 valid records,
lanes=claude,codex, check-lab, check-secrets, and check-collaboration all
passed. The run-record gate now also requires `registry/runs/`, `latest.json`,
both lanes, and latest pointing to the newest run id.

## Historical findings now closed

Ledger `collab-0010`, handoff
`registry/collaboration/handoffs/20260701-0958-claude-to-codex-support-runs-auth-state.md`
(distinct from the collab-0009 inbox-signature fix Codex already shipped):

1. **Unauthenticated run/query endpoints**: `services/gateway/src/server.mjs` —
   `/assistant/runs` (118), `/assistant/runs/{id}` (133), `/agent/query` (148)
   have no auth; only `/inbox/messages` (154) verifies a signature.
2. **Volatile run state**: `services/gateway/src/agent/runStore.mjs:3-4` keeps
   runs + idempotency in module-level `Map`s, lost on restart.
   Re-verified present 2026-07-01 09:58. That workspace had a fresh export at
   09:55 today, so Codex's lane was NOT fully quiet — factor that in.

## Remaining (b)/(c) gap list (from the audit, prioritized)

- (b) self-audit honesty — **DONE** (above).
- (b) gateway auth + durable run state — **DONE** (collab-0010).
- (b) structured per-run records — **DONE**, now active in `check-lab`
  (collab-0013/collab-0014).
- (c) reliable scheduler — absent.
- (c) per-agent worktree isolation + merge queue — absent (we coordinate by
  "wait for quiet + atomic ledger writes", a manual stopgap).
- (c) durable long-horizon task state machine — only flat markdown today.
- (c) agent-level observability (tokens/tools/failures/file-impact/rollback) —
  `scripts/lab-dashboard` only reports build timings.

## Operating reminders (learned — see memory)

- `assignments.json` gets concurrent writes from Codex: use a python
  read-modify-write (load → check id absent → insert → dump → revalidate JSON),
  NOT the Edit tool. Status enum = pending/in_progress/blocked/proven/abandoned;
  every entry needs an `updated` field. Handoffs need exact section headers
  `## Task` / `## Request` / `## Expected Artifacts` / `## Verification`.
- `workspaces/*` is gitignored (except `workspaces/README.md`).
- Wait for both lanes quiet (find -mmin) before any commit/merge.
- `export PATH="/Applications/Codex.app/Contents/Resources:$PATH"` for a real `rg`.
- Merges so far are LOCAL only (HEAD ce38ef4); never `git push` without the user.
