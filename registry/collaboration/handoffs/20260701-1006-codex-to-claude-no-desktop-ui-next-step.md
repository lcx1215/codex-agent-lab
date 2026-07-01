# Handoff: Codex -> Claude, No Desktop UI For Current Phase

## Task

Record the user's current product direction and the next useful Claude lane work.

## From / To

- From: codex
- To: claude

## Context

The user reviewed an external critique saying a two-day "desktop Agent IDE" is
too broad and should be cut down to a minimal desktop wrapper. Codex checked the
current lab state and confirmed that the lab is not currently a desktop UI
product: there is no Electron, Tauri, Vite, or desktop-app entrypoint in the
root lab.

The user then clarified: **desktop UI is not needed right now**.

Current framing:

- Do not start an Electron/Tauri/Desktop UI MVP in this phase.
- Treat `codex-agent-lab` as the local long-horizon agent development lab:
  governance, collaboration, isolation, harnesses, checks, audit, and real
  agent-package hardening.
- The lab can later support a desktop shell, but that is not the next task.

Claude has already opened the next useful Codex-facing handoff:

- `registry/collaboration/handoffs/20260701-0958-claude-to-codex-support-runs-auth-state.md`

That handoff reports two real customer-support package gaps:

- unauthenticated `/assistant/runs`, `/assistant/runs/{id}`, and `/agent/query`
  endpoints;
- volatile in-memory run state in `runStore.mjs`.

## Request

Do not pivot into desktop UI work. Continue the controlled-pilot hardening track.

Claude's next best work:

1. Finish the root-layer self-audit honesty hardening already in progress:
   `lab_agents/large_agent_readiness.py` should score real verification evidence
   instead of file existence.
2. Keep the user-facing verdict honest: development/governance environment is
   strong; controlled pilot is close; production multi-agent runtime is still
   not done.
3. Leave the customer-support package auth and durable-run-state fixes to Codex
   unless the user explicitly reassigns ownership.
4. After Codex fixes the support package handoff, review the result from the
   Claude lane with `scripts/audit-agent-code`, package tests, and root gates.

## Constraints

- No desktop UI, Electron, Tauri, or large frontend build in this phase.
- Do not edit Codex-owned customer-support package files unless the user
  explicitly reassigns that lane.
- Do not touch global auth, provider config, plugin state, Codex/Claude homes,
  API keys, cookies, tokens, or session files.
- Keep root default checks fast; do not re-add workspace-wide sweeps to
  `scripts/check-lab`.
- Workspaces are local/private by default; do not push or upload without the
  user explicitly asking.

## Expected Artifacts

If continuing Claude's current root-layer work:

- Updated `lab_agents/large_agent_readiness.py`.
- Updated `tests/test_large_agent_readiness_auditor.py`.
- Updated `registry/VALIDATION.md` or existing collaboration ledger entry with
  evidence.

If reviewing Codex's future support-package fix:

- A short review note appended to
  `registry/collaboration/handoffs/20260701-0958-claude-to-codex-support-runs-auth-state.md`
  or a new dated review handoff.

## Verification

For Claude's root-layer hardening:

- `python3 -m unittest tests.test_large_agent_readiness_auditor`
- `python3 -m unittest discover -s tests`
- `scripts/check-lab`
- `scripts/check-collaboration`
- `scripts/check-secrets`

For later support-package review:

- `scripts/audit-agent-code workspaces/agent-dev-workspace/agents/customer-support`
- `npm test` from
  `workspaces/agent-dev-workspace/agents/customer-support/services/gateway`
- `scripts/check-agent-packages`
- `scripts/check-rule-ladder`
