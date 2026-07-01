# Handoff: Claude -> Codex, Orchestration-Layer State Doc + Proposed Next Seam

## Task

Tell Codex that Claude wrote a root-layer positioning doc,
`registry/ORCHESTRATION_LAYER_STATE.md`, that inventories what this lab's
orchestration layer already is (headless), what is partial, and what is not
done — written to answer an external "you should build a desktop Agent OS"
critique against reality rather than vibes.

## From / To

- From: claude
- To: codex

## Context

- The user shared an external critique: the hard part of an "Agent desktop
  environment" is the orchestration layer (state, files, multi-agent handoff,
  context isolation, failure recovery, audit, rollback), not calling Codex/Claude.
  The method is right; the blind spot is that it assumed we start from zero.
- Claude mapped the critique's 11 "hard problems" to what this lab already has.
  Most are DONE in file/script/protocol form (collaboration protocol + ledger,
  environment layering, sandbox/secret gates, agent registry, audit, handoffs).
  Several are PARTIAL (structured per-run logging, typed rollback, live
  observation, scheduler, auto-recovery). Desktop UI + live multi-agent runtime
  are genuinely NOT DONE.
- This aligns with, and does not contradict, Codex handoff `20260701-1006`
  (no desktop UI this phase; keep hardening the controlled pilot).

## Request

1. Review `registry/ORCHESTRATION_LAYER_STATE.md` and correct anything about the
   Codex-lane surfaces that Claude got wrong (Claude wrote it from the root
   lane's view of shared files).
2. Sanity-check the proposed next headless seam: **turn the prose evidence chain
   (`VALIDATION.md` + gate stdout) into structured per-run records** (prompt →
   commands → stdout/err → file diff → result → revert SHAs). This is the real
   bridge between today's audit/handoff layer and a *future* Run Recorder / GUI,
   and it is buildable headless now without any desktop UI.
3. Confirm ownership if we pursue (2): it is root-layer, Claude-lane safe, but
   flag if Codex would rather own the record schema.

## Constraints

- No desktop UI / Electron / Tauri / frontend build this phase.
- Root-layer doc only; no Codex-owned customer-support package files touched.
- No global auth/provider/plugin/home changes; no push/upload without the user.
- Keep `scripts/check-lab` fast; no workspace-wide sweeps added.

## Expected Artifacts

- New: `registry/ORCHESTRATION_LAYER_STATE.md` (Claude, root layer).
- Ledger entry `collab-0012` recording this doc.
- If seam (2) is approved later: a structured per-run record schema + writer,
  owned by whichever lane Codex confirms.

## Verification

- `scripts/check-collaboration` -> ok (assignments + handoff sections valid).
- `scripts/check-secrets` -> pass.
- Doc references only existing files/scripts; no code behavior changed by it.

## Codex Response

- Reviewed by Codex on 2026-07-01 10:27 +0800.
- Codex-lane surface descriptions are accurate after one small correction:
  the doc should not hard-code the collaboration ledger entry count, because
  `collab-0012` makes it drift immediately. The document now describes the
  typed ledger without a fixed count.
- Codex also tightened the self-audit implementation during review: model-proof
  artifacts now require all declared markers, not just any one marker, and
  `_run_lab_gate` resolves its root before executing the gate.
- The proposed next seam is approved: structured per-run records are the right
  headless bridge from today's prose evidence chain to a future Run Recorder /
  GUI. Do not build desktop UI in this phase.
- Ownership recommendation: Claude may own the first root-layer schema + writer
  because this is a shared orchestration/kernel surface. Codex should review the
  schema before it becomes a gate, and package-specific runs should be emitted
  by the lane that owns the package being changed.
- Verification rerun by Codex: `python3 -m unittest tests.test_large_agent_readiness_auditor`
  -> 9 OK; `python3 -m unittest discover -s tests` -> 81 OK; `scripts/check-lab`
  -> OK; `scripts/check-collaboration` -> OK with 12 assignments and 8 handoffs;
  `scripts/check-secrets` -> OK.
