# Waterflow Repair Briefs

Use these briefs with Codex or Claude. Keep fixes scoped to the cited evidence unless the user expands scope.

## Brief 1: MISSING_CORE_PATH

Severity: `P1`

Problem: Required core path is missing: README.md

Evidence:
- `README.md`

Requested fix:
Create `README.md` or update the lab contract if this path is intentionally removed.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 2: DUPLICATE_AGENT_NAME

Severity: `P2`

Problem: Duplicate custom agent name: duplicate-agent

Evidence:
- `.codex/agents/duplicate-a.toml`
- `.codex/agents/duplicate-b.toml`

Requested fix:
Rename one agent so Codex has an unambiguous custom-agent target.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 3: AGENT_TOML_INVALID

Severity: `P1`

Problem: Agent TOML cannot be parsed: .codex/agents/invalid-agent.toml

Evidence:
- `.codex/agents/invalid-agent.toml`
- `Invalid value (at end of document)`

Requested fix:
Fix the TOML syntax, then rerun the waterflow scan.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 4: AGENT_MISSING_FIELD

Severity: `P1`

Problem: Agent is missing required field(s): name, description, developer_instructions

Evidence:
- `.codex/agents/invalid-agent.toml`

Requested fix:
Add `name, description, developer_instructions` to `.codex/agents/invalid-agent.toml` with narrow, role-specific content.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 5: AGENT_MISSING_FIELD

Severity: `P1`

Problem: Agent is missing required field(s): developer_instructions

Evidence:
- `.codex/agents/missing-field.toml`

Requested fix:
Add `developer_instructions` to `.codex/agents/missing-field.toml` with narrow, role-specific content.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 6: DUPLICATE_SKILL_NAME

Severity: `P2`

Problem: Duplicate skill name: duplicate-skill

Evidence:
- `.agents/skills/duplicate-skill-a/SKILL.md`
- `.agents/skills/duplicate-skill-b/SKILL.md`

Requested fix:
Rename or remove one skill so skill selection is unambiguous.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 7: SKILL_MISSING_FIELD

Severity: `P2`

Problem: Skill is missing required frontmatter field(s): description

Evidence:
- `.agents/skills/missing-description/SKILL.md`

Requested fix:
Add `description` to the skill frontmatter.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 8: SKILL_MISSING_ENTRYPOINT

Severity: `P1`

Problem: Skill directory has no SKILL.md: .agents/skills/missing-entrypoint

Evidence:
- `.agents/skills/missing-entrypoint`

Requested fix:
Add `SKILL.md` with `name` and `description`, or remove the stale skill directory.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 9: SCRIPT_NOT_EXECUTABLE

Severity: `P2`

Problem: Script is not user-executable: scripts/unvalidated-script

Evidence:
- `scripts/unvalidated-script`

Requested fix:
Run `chmod +x scripts/unvalidated-script` or document why this script is not executable.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 10: SCRIPT_WITHOUT_VALIDATION_REFERENCE

Severity: `P3`

Problem: Script has no explicit validation reference: unvalidated-script

Evidence:
- `scripts/unvalidated-script`
- `registry/VALIDATION.md`

Requested fix:
Add the command or validation evidence for `scripts/unvalidated-script` to `registry/VALIDATION.md`.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 11: EMPTY_REGISTRY_FILE

Severity: `P2`

Problem: Registry file is empty: registry/EMPTY.md

Evidence:
- `registry/EMPTY.md`

Requested fix:
Add durable evidence or remove the empty registry artifact.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 12: CROSS_PROJECT_REFERENCE

Severity: `P2`

Problem: Lab workflow references lcx-s-openclaw even though the first Waterflow Auditor scope excludes it.

Evidence:
- `AGENTS.md`

Requested fix:
Remove the reference or document why this path is allowed for this lab-only scan.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 13: PROGRESS_WITHOUT_VALIDATION

Severity: `P2`

Problem: Progress claims completion-like state but validation evidence is missing or too thin.

Evidence:
- `registry/current-progress.md`
- `registry/VALIDATION.md`

Requested fix:
Run the relevant verification commands and record exact evidence in `registry/VALIDATION.md`.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.
