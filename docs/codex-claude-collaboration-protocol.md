# Codex-Claude Collaboration Protocol

Last updated: 2026-06-30 15:55 +0800

This document defines how the Claude/OMC lane and the Codex/OMX lane collaborate inside this lab without
crossing the isolation boundaries in `AGENTS.md` (Codex lane) and `CLAUDE.md` (Claude lane).

## Purpose

The two lanes share one lab but run as separate agents with separate homes, auth, and provider config. This
protocol makes their collaboration durable and auditable: work is exchanged through files in the repo, never
through copied secrets or copied conversation context.

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
