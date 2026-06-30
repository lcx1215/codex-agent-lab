# Codex Agent Lab - Claude/OMC Lab-Local Rules

This file is the Claude Code (OMC) operating overlay for `/Users/liuchengxu/Desktop/codex-agent-lab`.
It is the Claude-lane counterpart to `AGENTS.md` (Codex/OMX lane). Both files describe the same lab; this one
records the boundaries, routing, and verification rules that apply when Claude/OMC is the agent on duty.

Global Claude rules live in `/Users/liuchengxu/.claude/CLAUDE.md` and `/Users/liuchengxu/CLAUDE.md`; do not
duplicate them here unless this lab needs a narrower local rule.

## Autonomy (Highest Priority)

- Claude completes tasks end-to-end without asking the user for approval. Decide, execute, verify, report.
- The user has granted standing authorization for autonomous execution in this lab.
- **NEVER end a turn with a yes/no or "want me to…? / 要我…吗?" permission question.** Choose the reasonable
  option, do it, and report what was done. Only genuine *what-the-user-wants* ambiguities are askable.
- Report conclusions in concise Chinese, not raw transcripts. Keep artifacts in English unless asked otherwise.
- This does NOT relax the safety boundaries in `## Isolation`. Autonomy means "don't ask permission to do the
  work," not "cross the safety lines."

## Lane Identity

- Claude/OMC is one lane; Codex/OMX is the other. This lab is the shared ground where they collaborate.
- Claude work stays in Claude/OMC context. Do not attempt to drive Codex lanes (`~/.codex`,
  `~/.codex-api-relay`), their auth, provider config, or running Codex.app / cc-switch processes.
- OMC runtime state lives in lab-local `.omc/` and is git-ignored except `.omc/skills/**`.
- When Claude and Codex collaborate, route work through the files in `## Collaboration`, not through copied
  conversation context or copied secrets.

## Isolation (Hard Limits)

- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab`. Do not write outside it unless the user names the
  specific outside path.
- Do not read, print, copy, rewrite, or migrate secrets, `auth.json`, account tokens, cookies, OTPs, or API keys.
- Do not change `~/.codex`, `~/.codex-api-relay`, Codex app auth, provider config, LaunchAgents, or plugin
  install state from this lab unless the user explicitly asks.
- Keep generated artifacts under `outputs/`; keep durable state under `registry/`; keep scratch under `.tmp/`.

## Collaboration (Claude <-> Codex)

- Protocol: `docs/codex-claude-collaboration-protocol.md` defines roles, handoff format, and the proof bar.
- Assignments ledger: `registry/collaboration/assignments.json` records who owns what and the current status.
- Handoffs: `registry/collaboration/handoffs/` holds dated, English handoff notes between lanes.
- Cross-lane artifacts that both lanes need go under `outputs/shared/`.
- Health gate: run `scripts/check-collaboration` after changing any collaboration surface.
- A collaboration claim is only "proven" when there is a real runtime artifact, not just an installed capability.

## Verification

- Verify before claiming completion. Default gates: `scripts/check-lab`, `scripts/check-secrets`,
  `scripts/check-collaboration`, and `scripts/lab-dashboard`.
- Write completion evidence to `registry/VALIDATION.md` or a task-specific validation note.
- Prefer `executor` for implementation, `code-reviewer`/`verifier` for the approval pass. Never self-approve in
  the same active context.

## Reporting

- Concise Chinese for user-facing status; English for committed artifacts.
- When a result is inferred from old notes, say it may be stale.
- Use file handoffs instead of pasting large context into messages.
