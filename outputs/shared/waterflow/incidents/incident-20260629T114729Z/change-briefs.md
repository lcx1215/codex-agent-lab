# Waterflow Change Briefs

Use these briefs with Codex or Claude when changed paths need validation or scoped follow-up.

## Brief 1: ADDED .agents/skills/duplicate-skill-a/SKILL.md

Route kind: `skill`
Risk: `P2`

Task for Codex or Claude:
Validate the `added` path `.agents/skills/duplicate-skill-a/SKILL.md`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/check-lab`
- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify skill discovery only."`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 2: ADDED .agents/skills/duplicate-skill-b/SKILL.md

Route kind: `skill`
Risk: `P2`

Task for Codex or Claude:
Validate the `added` path `.agents/skills/duplicate-skill-b/SKILL.md`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/check-lab`
- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify skill discovery only."`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 3: ADDED .agents/skills/missing-description/SKILL.md

Route kind: `skill`
Risk: `P2`

Task for Codex or Claude:
Validate the `added` path `.agents/skills/missing-description/SKILL.md`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/check-lab`
- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify skill discovery only."`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 4: ADDED .codex/agents/broken-syntax.toml

Route kind: `agent`
Risk: `P2`

Task for Codex or Claude:
Validate the `added` path `.codex/agents/broken-syntax.toml`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/check-lab`
- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify agent discovery only."`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 5: ADDED .codex/agents/duplicate-owner-a.toml

Route kind: `agent`
Risk: `P2`

Task for Codex or Claude:
Validate the `added` path `.codex/agents/duplicate-owner-a.toml`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/check-lab`
- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify agent discovery only."`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 6: ADDED .codex/agents/duplicate-owner-b.toml

Route kind: `agent`
Risk: `P2`

Task for Codex or Claude:
Validate the `added` path `.codex/agents/duplicate-owner-b.toml`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/check-lab`
- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify agent discovery only."`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 7: ADDED .codex/agents/missing-owner.toml

Route kind: `agent`
Risk: `P2`

Task for Codex or Claude:
Validate the `added` path `.codex/agents/missing-owner.toml`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/check-lab`
- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify agent discovery only."`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 8: ADDED registry/empty-claim.md

Route kind: `registry`
Risk: `P3`

Task for Codex or Claude:
Validate the `added` path `registry/empty-claim.md`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 9: ADDED scripts/release-handoff

Route kind: `script`
Risk: `P2`

Task for Codex or Claude:
Validate the `added` path `scripts/release-handoff`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `python3 -m unittest discover -s tests`
- `scripts/check-lab`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 10: ADDED tests/test_incident.py

Route kind: `auditor-code`
Risk: `P2`

Task for Codex or Claude:
Validate the `added` path `tests/test_incident.py`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `python3 -m unittest discover -s tests`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 11: ADDED workspaces/release-repair

Route kind: `unknown`
Risk: `P3`

Task for Codex or Claude:
Validate the `added` path `workspaces/release-repair`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 12: REMOVED .agents/skills/handoff-skill/SKILL.md

Route kind: `skill`
Risk: `P2`

Task for Codex or Claude:
Validate the `removed` path `.agents/skills/handoff-skill/SKILL.md`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/check-lab`
- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify skill discovery only."`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 13: REMOVED .codex/agents/handoff-owner.toml

Route kind: `agent`
Risk: `P2`

Task for Codex or Claude:
Validate the `removed` path `.codex/agents/handoff-owner.toml`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/check-lab`
- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify agent discovery only."`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 14: REMOVED README.md

Route kind: `documentation`
Risk: `P3`

Task for Codex or Claude:
Validate the `removed` path `README.md`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 15: REMOVED tests/test_baseline.py

Route kind: `auditor-code`
Risk: `P2`

Task for Codex or Claude:
Validate the `removed` path `tests/test_baseline.py`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `python3 -m unittest discover -s tests`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 16: REMOVED workspaces/handoff-check

Route kind: `unknown`
Risk: `P3`

Task for Codex or Claude:
Validate the `removed` path `workspaces/handoff-check`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 17: CHANGED AGENTS.md

Route kind: `documentation`
Risk: `P3`

Task for Codex or Claude:
Validate the `changed` path `AGENTS.md`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 18: CHANGED docs/design.md

Route kind: `documentation`
Risk: `P3`

Task for Codex or Claude:
Validate the `changed` path `docs/design.md`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 19: CHANGED registry/VALIDATION.md

Route kind: `registry`
Risk: `P3`

Task for Codex or Claude:
Validate the `changed` path `registry/VALIDATION.md`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 20: CHANGED registry/current-progress.md

Route kind: `registry`
Risk: `P3`

Task for Codex or Claude:
Validate the `changed` path `registry/current-progress.md`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 21: CHANGED scripts/smoke-check

Route kind: `script`
Risk: `P2`

Task for Codex or Claude:
Validate the `changed` path `scripts/smoke-check`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `python3 -m unittest discover -s tests`
- `scripts/check-lab`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.

## Brief 22: CHANGED waterflow/auditor.py

Route kind: `auditor-code`
Risk: `P2`

Task for Codex or Claude:
Validate the `changed` path `waterflow/auditor.py`. Keep any fix scoped to this route family unless validation proves wider impact.

Recommended checks:
- `python3 -m unittest discover -s tests`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Completion evidence:
- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.
