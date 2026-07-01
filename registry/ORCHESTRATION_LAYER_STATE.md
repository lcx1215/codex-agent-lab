# Orchestration-Layer State: What This Lab Already Is, and What It Is Not Yet

Last updated: 2026-07-01 10:20 +0800
Owner lane: claude (root-layer positioning doc)
Related: `docs/agent-lab-mission.md`, `registry/CAPABILITY_LAYERS.md`,
`docs/codex-claude-collaboration-protocol.md`, `docs/environment-layering.md`.

## Why this document exists

An external critique framed the goal as "build a super desktop Agent" and
warned that the hard part is not calling Codex/Claude (a one-line `spawn`) but
the *orchestration layer* around them: state, files, multi-agent handoff,
context isolation, failure recovery, audit, rollback. That framing is correct.

The critique's blind spot: it assumed we are starting from zero and stuck. We
are not. This lab has already built most of that orchestration layer — as
**files, scripts, and protocols**, not as a GUI. This doc is the honest ledger
of what exists, what is partial, and what is genuinely missing, so the
"should we build a desktop UI now?" decision is made against reality, not vibes.

The execution engine (Codex/Claude Code) is the "worker". This lab is the
"factory": task organization, audit, division of labor, change boundaries,
rollback. That is the right target, and it is the track we are already on.

## The critique's 11 "hard problems" vs. what exists here

| Hard problem (external critique) | Status in this lab | Where |
| --- | --- | --- |
| Multi-agent management / who does what | DONE (file-form) | `assignments.json` ledger, `codex-claude-collaboration-protocol.md` |
| Task queueing across agents | PARTIAL | ledger tracks ownership+status; no live scheduler |
| File-permission / write control | DONE | `sandbox-boundaries.md`, `check-sandbox`, `check-workspace-safety` |
| Change rollback | PARTIAL | git is the rollback substrate; no one-click/typed rollback record |
| Context isolation | DONE | `environment-layering.md` (max/medium/small), `rule-inheritance.md` |
| Log / execution tracing | PARTIAL | `VALIDATION.md` evidence chain + `check-*` output; not per-run structured logs |
| Failure recovery | PARTIAL | fail-closed gates (collab-0005, exit-code gating collab-0011); no auto-retry/resume |
| Tool registration | DONE | `AGENT_REGISTRY.md`, `.codex/agents/*.toml`, 46 lab-local skills |
| User observation of the process | PARTIAL (CLI) | `lab-dashboard`, gate output; no live visual stream |
| Multi-project switching | PARTIAL | `workspaces/<scenario>/` layering; no project switcher UI |
| Agent-to-agent handoff | DONE | dated `handoffs/` notes + ledger status transitions |

<!--CONTINUE-->

## What is genuinely DONE (the orchestration layer already works, headless)

- **Division of labor + handoff protocol.** Two lanes (Claude root, Codex
  packages) coordinate through `assignments.json` (typed status enum) and dated
  `handoffs/` notes with enforced section headers, gated by
  `scripts/check-collaboration`. This is a working "who owns what / who does it
  next / what's the proof" system.
- **Context isolation by scale.** `environment-layering.md` + `rule-inheritance.md`
  define max/medium/small environments; local rules can only narrow, never
  weaken parent safety. `check-rule-ladder` makes a broken chain a hard failure.
- **Write boundaries + secret boundary.** `check-sandbox`, `check-workspace-safety`,
  `check-secrets` enforce where agents may write and that no secrets are
  committed. Fail-closed on error (collab-0005).
- **Audit / honesty.** `scripts/audit-agent-code` catches real package vulns
  (found the customer-support fail-open signature bug). As of collab-0011, the
  self-audit no longer scores "file exists" as "capability real": `verification`
  executes the gate and is exit-code gated; `model-proof` checks content+recency.
- **Tool + agent registry.** `AGENT_REGISTRY.md`, `.codex/agents/*.toml`,
  `check-agent-packages` validating manifests/registry coverage, 46 skills.
- **Evidence chain.** `registry/VALIDATION.md` + `current-progress.md` are the
  durable record of what was verified and how.

## What is PARTIAL (works headless, but thin or CLI-only)

- **Execution logging.** Evidence is captured as prose in `VALIDATION.md` and as
  gate stdout, not as structured per-run records (prompt → commands → stdout/err
  → diff → result). This is the biggest gap the critique correctly identified.
- **Rollback.** Git is the real rollback substrate, but there is no typed
  "this run changed files X,Y; revert = these SHAs" record. Rollback is manual.
- **Observation.** `lab-dashboard` reports build/health; there is no live view of
  an agent run in progress. CLI-only by design this phase.
- **Scheduler / task queue.** The ledger records ownership+status but nothing
  runs the queue; sequencing is human + "wait for lanes quiet".
- **Failure recovery.** Gates fail closed, but there is no auto-retry, no resume
  from a checkpoint, no partial-run state machine.

## What is genuinely NOT DONE

- **Desktop UI / GUI shell.** No Electron/Tauri/Vite/desktop entrypoint. Per
  Codex handoff `20260701-1006`, deliberately NOT this phase.
- **Live multi-agent runtime** (real scheduler + per-agent worktree isolation +
  merge queue + durable long-horizon task state machine). This is the "(c)
  production runtime" tier — still far off, honestly.
- **One-click rollback / visual diff stream** — the GUI-shaped items the critique
  wants; correct as a *later* layer, not now.

## Recommendation (the actual decision)

The critique's method is right (orchestration > calling; record before
orchestrate; controllable before intelligent) but its premise is stale: the
headless orchestration layer mostly exists. The two suggestions in tension are:

- Critique: "build a GUI Agent Run Recorder first."
- Codex `20260701-1006`: "no desktop UI this phase; keep hardening the pilot."

These are not mutually exclusive, and the right ordering is Codex's: **make the
kernel trustworthy first, then add a shell.** Building a pretty dashboard on top
of a system that could still score itself falsely green (the exact bug just
fixed in collab-0011) would visualize lies. The highest-value *headless* next
step that also feeds a future Run Recorder is: **turn the prose evidence chain
into structured per-run records** (the PARTIAL "execution logging" gap). That is
the real seam between "what we have" (audit/handoff) and "what a Run Recorder /
GUI would later render". Do that in files first; a UI can render it later.

## Honest user-facing verdict (unchanged)

Development/governance environment: strong. Controlled pilot: close. Production
multi-agent runtime: not done. A desktop UI is a valid *later* layer, not the
next task.
