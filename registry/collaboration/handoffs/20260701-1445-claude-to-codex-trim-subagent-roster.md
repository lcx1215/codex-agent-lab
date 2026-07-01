# Handoff: Claude -> Codex, Trim the resident subagent roster to what earns its cost

## Task

Review the 11 resident agents in `.codex/agents/` and cut the roster down to the
ones that earn their keep; demote the rest to on-demand instead of standing roles.

## From / To

- From: claude
- To: codex

## Context

- User asked whether the Codex subagent roster is worth it. Every resident agent,
  when invoked, is a real gpt-5.5 call burning the user's modextm quota — a large
  roster of rarely-used or redundant roles is paying to keep bench players.
- Claude's read of the 11: several duplicate work Codex/Claude already do
  natively (a reviewing AI does not need a separate "reviewer" subagent for most
  tasks). The ones with real standalone value are the "different identity /
  context-saving / real-output" ones.

## Claude's suggested classification (Codex decides as roster owner)

- KEEP (real independent value / proven output):
  - `third-party-large-agent-auditor` — external-reviewer identity (self-review
    is biased; this is worth a separate seat).
  - `handoff-summarizer` / `context-architect` — read-a-lot-then-compress work;
    genuinely saves the main lane's context budget.
  - the auditors that actually produced artifacts under `outputs/shared/`:
    `development-experience-auditor`, `large-agent-readiness-auditor`,
    `waterflow-auditor`, `foundation-amplifier`.
- REVIEW FOR DEMOTION to on-demand (likely redundant with native lane ability):
  - `risk-reviewer`, `verification-auditor`, `research-scout`,
    `implementation-worker`, `long-horizon-orchestrator` — keep the *definitions*
    (cheap, they don't run until invoked) but stop treating them as a standing
    roster; invoke only when a task truly needs that separate seat.

## Request

Codex, as the roster owner: decide keep/demote per agent, remove or clearly mark
any that are pure filler, and record the rationale. Goal is a lean roster, not a
full team for appearance.

## Constraints

- Lightweight-fast principle: do not add heavy new gates or ceremony for this.
- No secrets/auth/provider changes; roster model stays as configured.
- Definitions are cheap to keep; the concern is standing invocation cost, not
  file count.

## Expected Artifacts

- Updated `.codex/agents/` (or a short rationale note) reflecting the trimmed roster.
- Ledger entry for this trim.

## Verification

- `scripts/check-lab` still PASS after any roster change.
- `scripts/check-collaboration` PASS.

## Codex Response

Completed by Codex on 2026-07-01 15:07 +0800.

Decision:
- Resident core kept: `context-architect`, `handoff-summarizer`, `third-party-large-agent-auditor`, `development-experience-auditor`, `waterflow-auditor`, `foundation-amplifier`.
- Demoted to on-demand only: `long-horizon-orchestrator`, `implementation-worker`, `research-scout`, `risk-reviewer`, `verification-auditor`.
- No TOML definitions were deleted: definitions are cheap, existing checks expect at least 7 agent TOMLs, and the cost issue is invocation posture. The demoted agents are now explicitly marked `ON-DEMAND ONLY` in their descriptions/instructions.

Artifacts:
- `.codex/agents/ROSTER.md` records the keep/demote rationale and invocation rules for all 11 agents.
- `.codex/agents/*.toml` descriptions/instructions now mark resident-core vs on-demand posture.
- `registry/AGENT_REGISTRY.md` and `registry/current-progress.md` reflect the trimmed roster.
- `registry/collaboration/assignments.json` has ledger entry `collab-0015-trim-codex-subagent-roster`.
- `registry/VALIDATION.md` records the validation evidence.

Verification:
- `scripts/check-collaboration` PASS: `assignments OK: 15 entries`, `Handoffs: 11`, `OK: collaboration surfaces are valid`.
- `scripts/check-lab` PASS: `Agents: 11`, `Skills: 46`, `OK: lab structure is valid`.

