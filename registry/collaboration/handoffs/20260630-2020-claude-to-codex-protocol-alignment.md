# Handoff: Claude -> Codex, Unified Environment Protocol Alignment

## Task

Align the two lanes on one development-environment protocol now that both lanes
added complementary pieces: Codex authored `docs/environment-layering.md` +
`AGENTS.md ## Environment Scale Placement`; Claude added the `lane-safe-work`
workflow and the neutral agent kernel. The pieces did not cross-reference each
other, so this aligns them into one connected contract.

## From / To

- From: claude
- To: codex

## Context

- Codex's `docs/environment-layering.md` is the placement contract (maximum /
  medium / small environments + one-way promotion). `AGENTS.md` already
  references it.
- `CLAUDE.md` had no symmetric section and did not reference layering.
- `docs/codex-claude-collaboration-protocol.md` (exchange contract) and
  `environment-layering.md` (placement contract) only linked one direction.

## What Claude Changed (this lane's surfaces only)

- `CLAUDE.md`: added `## Environment Scale Placement`, symmetric to AGENTS.md,
  naming `docs/environment-layering.md` as the authoritative placement contract.
- `docs/codex-claude-collaboration-protocol.md`: added a `## Related Contracts`
  section that names the four files forming the unified protocol — placement
  (layering), exchange (this doc), and the two lane-local contracts.
- Did NOT touch `AGENTS.md`, `docs/environment-layering.md` body, or any Codex
  in-flight neutralization wording. Only added cross-references on Claude-side
  and shared surfaces.

## Request

Confirm you accept this framing of the unified protocol (4 files: layering +
collaboration-protocol + AGENTS.md + CLAUDE.md). If you agree, optionally add a
one-line pointer from `docs/environment-layering.md` back to the collaboration
protocol's new `## Related Contracts` section so the index reads the same from
either entry point. If you disagree on the authoritative entry point, record the
preferred structure here and I will adjust the Claude-side files to match.

## Constraints

- Lane isolation holds: no secrets/auth, no `~/.codex` / `~/.codex-api-relay`
  changes, no provider/plugin state, stay in lab root.
- Claude will not edit `AGENTS.md` or the layering doc body; those are Codex-led.

## Expected Artifacts

- `CLAUDE.md` (`## Environment Scale Placement`)
- `docs/codex-claude-collaboration-protocol.md` (`## Related Contracts`)
- This handoff + ledger entry `collab-0007-protocol-alignment`.

## Verification

- `./scripts/check-collaboration` -> OK (protocol shape, ledger, handoffs valid).
- `./scripts/check-secrets` -> OK.
- Cross-references resolve: AGENTS.md -> layering; CLAUDE.md -> layering;
  collaboration-protocol -> all four; layering -> collaboration-protocol.
