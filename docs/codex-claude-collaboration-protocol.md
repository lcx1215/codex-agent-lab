# Codex-Claude Collaboration Protocol

Last updated: 2026-07-01 14:25 +0800

This document defines how the Claude/OMC lane and the Codex/OMX lane collaborate inside this lab without
crossing the isolation boundaries in `AGENTS.md` (Codex lane) and `CLAUDE.md` (Claude lane).

## Purpose

The two lanes share one lab but run as separate agents with separate homes, auth, and provider config. This
protocol makes their collaboration durable and auditable: work is exchanged through files in the repo, never
through copied secrets or copied conversation context.

## Related Contracts

This protocol governs *how* the two lanes exchange work. It sits alongside:

- `docs/environment-layering.md` — *where* a skill, protocol, interface, kernel, or check belongs (maximum /
  medium / small environment) and the one-way promotion direction.
- `docs/rule-inheritance.md` — how Codex and Claude keep root, workspace, and package rules active when work
  starts from a nested directory.
- `docs/task-state-scheduler.md` — the shared task-state registry and next-runnable-task view.
- `docs/run-record-schema.md` — the structured evidence record for meaningful lane runs.
- `AGENTS.md` (`## Environment Scale Placement`, `## Isolation`) — the Codex/OMX lane-local contract.
- `CLAUDE.md` (`## Environment Scale Placement`, `## Collaboration`) — the Claude/OMC lane-local contract.

Together these are the unified development-environment protocol: placement (layering), inheritance, exchange
(this doc), task state, run evidence, and the two lane-local operating contracts that adopt them.

## Shared Environment Understanding

Codex and Claude must describe the lab the same way:

- `codex-agent-lab` is the single maximum environment.
- `workspaces/<scenario>/` entries are medium workspaces/projects.
- `workspaces/<scenario>/agents/<package>/` entries are small agent packages.
- All three levels are sandboxed work surfaces; do not reserve the word
  "sandbox" for one medium workspace.
- A lane may enter the maximum environment by reading its lane-local root rules,
  `docs/environment-layering.md`, `docs/rule-inheritance.md`, and this
  protocol. It must not copy or infer the other lane's auth, secrets, provider
  config, or runtime state.

## Roles

- **Leader**: the lane that currently owns the task end-to-end. It writes the assignment, splits work, and
  records the final verdict. Either lane can be leader for a given task.
- **Worker**: a lane (or sub-agent) that performs a scoped, named piece of work from a brief and reports back
  through a handoff note. Workers do not redefine the task.
- **Reviewer**: a lane that audits the worker output in a separate pass. The leader must not self-approve in the
  same active context; the reviewer is a distinct pass (OMC `code-reviewer`/`verifier`, or the other lane).

## Lane Boundaries

- Claude/OMC drives only `~/.claude` context and lab-local `.omc/`.
- Codex/OMX drives only `~/.codex`, `~/.codex-api-relay`, and lab-local `.omx/`.
- Neither lane reads or copies the other lane's secrets, `auth.json`, tokens, or provider config.
- Cross-lane data moves only through `registry/collaboration/` and `outputs/shared/`.

## Handoff Format

Each handoff is a dated English markdown file under `registry/collaboration/handoffs/`, named
`YYYYMMDD-HHMM-<from>-to-<to>-<slug>.md` (e.g. `20260630-1600-claude-to-codex-interop-proof.md`).

Required sections:

- `## Task` — one-line statement of what is being handed off.
- `## From / To` — lane names (`claude` or `codex`).
- `## Context` — what is already done and where the artifacts are (paths, not pasted content).
- `## Request` — the exact scoped work the receiving lane should do.
- `## Constraints` — isolation/safety limits that still apply.
- `## Expected Artifacts` — files the receiving lane should produce.
- `## Verification` — how completion will be checked.

## Assignments Ledger

`registry/collaboration/assignments.json` is the durable record of collaboration tasks. Each entry has:
`id`, `title`, `leader`, `workers`, `reviewer`, `status` (`pending|in_progress|blocked|proven|abandoned`),
`handoff` (path or null), `artifacts` (list of paths), and `updated` (timestamp). The `check-collaboration`
script validates this file's shape.

## Workbench State Surfaces

The collaboration protocol remains the lane-exchange contract. Newer workbench surfaces add state and evidence;
they do not replace handoffs, reviewer duties, or proof requirements.

| Surface | Path | Owns | Does not replace |
| --- | --- | --- | --- |
| Collaboration assignments | `registry/collaboration/assignments.json` | Who leads, who works, who reviews, collaboration status | Task scheduling or run logs |
| Handoffs | `registry/collaboration/handoffs/` | Exact cross-lane request, constraints, expected artifacts, verification | Task-state entries or chat summaries |
| Task state | `registry/tasks/tasks.json` | Long-horizon task state, dependencies, stale running leases, next runnable task | Cross-lane assignment, handoff, or review approval |
| Run records | `registry/runs/*/record.json` | Structured evidence of what a lane actually ran and changed | Reviewer approval or collaboration status |
| Dashboard | `outputs/shared/dashboard/` | One-screen observation of current health and next task | Source-of-truth ledgers |

Non-substitution rules:

- A `pending` or `running` task-state entry does not authorize a lane to bypass `assignments.json` when the work is cross-lane.
- A run record proves execution evidence, not cross-lane approval. It can support a review, but it is not the review.
- A handoff remains required when one lane asks the other lane to implement, verify, or repair something.
- A dashboard health `ok` means gates are green; it does not promote blocked runtime capabilities to proven.
- `collab-0001-omc-team-bootstrap` remains `blocked` until a fresh real OMC team runtime proof succeeds.

## Proof Bar

A collaboration capability is only **proven** when there is a real runtime artifact, not just an installed
command. Examples of proof:

- A real tmux-based `omc interop` session that produced split-pane output, with an artifact recorded under
  `outputs/shared/` and an assignment entry moved to `proven`.
- An OMC leader plus a Codex/OMX worker where the worker wrote a real handoff file and the reviewer recorded a
  verdict.

Installed-but-unproven capabilities (e.g. `omc team`, `omc interop` that never ran to completion) stay at
`pending` or `blocked` with the failure reason recorded, exactly as the audit found for the earlier OMC team
run (`worker_start_submit_unverified`).

## Runtime Entry Points

- `omc ask <lane> ...` — single-shot cross-model question; artifacts land under `.omc/artifacts/ask/`.
- `omc team N:agent-type[:role] ...` — OMC implicit agent team.
- `omc interop` — Claude/OMC + Codex/OMX split-pane tmux session; must be launched from inside tmux in a real
  terminal, so it cannot be proven from a GUI-only session.
- Codex/OMX side: `omx-api exec` and `omx-api team` from the API-relay lane.

## Verification

Run `scripts/check-collaboration` after changing any collaboration surface. It checks that the protocol doc,
assignments ledger, handoffs directory, and `CLAUDE.md` collaboration section all exist and are well-formed.
