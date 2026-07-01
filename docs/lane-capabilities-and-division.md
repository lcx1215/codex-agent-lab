# Lane Capabilities and Division of Labor

Last updated: 2026-07-01 11:05 +0800
Owner lane: claude (root-layer orchestration doc)
Related: `docs/codex-claude-collaboration-protocol.md` (defines *how* the lanes
exchange work — roles, handoff format, proof bar), `CLAUDE.md`, `AGENTS.md`.

## Why this doc

The collaboration protocol says *how* work is exchanged. This doc says *who
does what and who must not touch what* — each lane's real capabilities, hard
limits, and the routing rules for deciding which lane owns a given task. It is
written from the Claude lane's honest self-assessment; Codex should correct the
Codex-lane rows it disagrees with.

## The two lanes at a glance

- **Claude / OMC lane** — home `~/.claude`, lab-local `.omc/`. Default steward
  for many **maximum environment (lab root)** surfaces: shared checks,
  protocols, docs, orchestration-layer drafts, cross-cutting audits, and review
  passes.
- **Codex / OMX lane** — home `~/.codex` + `~/.codex-api-relay`, lab-local
  `.omx/`. Primary owner for the **agent packages** it builds under
  `workspaces/<scenario>/agents/<package>/` and their runtime code, and also a
  valid root-layer implementer/reviewer when root changes are explicitly routed
  through the shared protocol.

## Claude lane — capabilities

- Root-layer engineering: `lab_agents/`, `scripts/check-*`, `docs/`, `registry/`.
- Cross-cutting audits and honesty gates (e.g. `large_agent_readiness.py`,
  `audit-agent-code`) — including auditing Codex-owned package *code* read-only
  and reporting findings via handoff.
- The orchestration layer itself: collaboration ledger discipline, per-run
  records (`run_record.py`), environment-state docs.
- Independent **review pass** on Codex's package fixes (read code + run the
  package's own gates/tests), because the leader must not self-approve.
- Multi-file refactors, planning, and fan-out via OMC sub-agents (native Task,
  not tmux team — see limits below), when I choose to invoke them.

<!--CONTINUE-->

## Claude lane — hard limits (things I cannot or must not do)

- **Cannot edit Codex-owned package files** under `workspaces/<scenario>/agents/
  <package>/` unless the user explicitly reassigns that lane. I audit and review
  them read-only, then hand findings to Codex.
- **Cannot touch** any lane's `auth.json`, tokens, API keys, provider config,
  `~/.codex*`, cookies, or session files. Never read/echo secret values.
- **Cannot** start Electron/Tauri/desktop UI in this phase (product decision,
  Codex handoff `20260701-1006`).
- **Cannot rely on OMC tmux `team`** — known upstream bug (`capture-pane` reads
  scrollback so `verifyWorkerStartCommandSubmitted` almost always fails; see
  memory `omc-multi-agent-setup`). Delegation goes through native Task
  sub-agents or headless paths, not tmux team.
- **Cannot push / upload** or promote a gitignored workspace without the user
  explicitly asking. All merges so far are local-only.
- **Cannot self-approve**: my own work needs a separate review pass (Codex lane,
  or an OMC `code-reviewer`/`verifier` sub-agent in a distinct context).
- **Should not** run the OMC heavyweight machinery (team/ralph/workflow) or its
  long-term memory by default; I enable them deliberately when a task needs it.

## Codex lane — capabilities (Claude's view; Codex to correct)

- Owns and edits the agent packages it builds (e.g. customer-support gateway):
  package runtime code, package tests, package-local config.
- Fixes findings Claude hands off inside those packages (did exactly this on
  collab-0009 signature fix and collab-0010 auth + durable run state).
- Runs its own package gates (`npm test`, package audits) and reports proof.
- Emits Codex-lane package run records using the shared per-run schema.
- Can be leader for package-scoped tasks and reviewer for Claude's root work.
- Can also implement root-layer changes when the user or collaboration ledger
  routes that work to Codex; those changes still follow root gates and
  cross-lane review rather than being treated as package side effects.

## Codex lane — hard limits (as Claude understands them)

- Should not redefine or edit the maximum-environment root contracts as a
  package side-effect; root changes go through the shared protocol and must
  remain scenario-neutral.
- Same secret/auth/lane isolation as Claude, mirrored.
- Package runtime state stays inside the gitignored workspace unless promoted.
- Does not control or mutate Claude/OMC home, auth, session state, or provider
  configuration.

## Task routing — who owns what

| Task kind | Owner | Reviewer |
| --- | --- | --- |
| Root checks / `lab_agents` / `docs` / `registry` | Claude by default; Codex when explicitly routed | Other lane |
| Orchestration layer (ledger, per-run records, env docs) | Claude by default; Codex may implement/review | Other lane |
| Cross-cutting audit of any code (read-only) | Claude | Codex |
| Agent-package runtime code + package tests | Codex | Claude |
| Fixing a finding inside a Codex package | Codex | Claude |
| Promoting a per-run-record gate into `check-lab` | Claude builds, Codex approves | — |
| Anything touching secrets/auth/provider/global homes | neither (blocked) | — |
| Desktop UI / frontend build | neither (deferred this phase) | — |

## Current live division (2026-07-01)

- Claude just built the per-run-record seam (collab-0013). Codex reviewed +
  hardened the schema and set the promotion path: **Claude next builds
  `scripts/check-run-records`** (schema validator over `registry/runs/*/
  record.json`); promote into `check-lab` only after 2+ real records from BOTH
  lanes exist.
- collab-0010 (support auth + durable runStore) is **proven**: Codex fixed,
  Claude reviewed the code and the package gates independently.
- Package runs must emit the same run-record schema from the owning lane.
- Codex has now emitted a package verification record:
  `registry/runs/20260701T030814Z-codex-verify-customer-support-gateway/record.json`.
