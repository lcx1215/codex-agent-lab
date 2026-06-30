# Task Brief

Created: 2026-06-30 13:33 +0800

## Objective

Record and contain the multiagent parallel proof workspace so lab validation can track it as a durable long-horizon artifact.

## Scenario

- Scenario type: runtime proof workspace.
- Inside boundary: bounded reports, progress notes, and validation evidence for multiagent or parallel runtime proof work.
- Outside boundary: global Codex auth, provider configuration, plugin state, and App process control.
- Codex/Claude amplification: use this workspace to keep parallel proof evidence isolated and restartable without replacing model-agent review or final verification.

## Constraints

- Keep work inside this workspace unless explicitly assigned otherwise.
- Do not read, print, copy, or migrate secrets, auth files, session files, cookies, OTPs, or API keys.
- Record verification evidence before completion.

## Acceptance Checks

- `scripts/check-lab`
- `scripts/waterflow-scan --root . --compare-last`
