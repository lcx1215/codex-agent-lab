# Waterflow Repair Briefs

Use these briefs with Codex or Claude. Keep fixes scoped to the cited evidence unless the user expands scope.

## Brief 1: SKILL_MISSING_FIELD

Severity: `P2`

Problem: Skill is missing required frontmatter field(s): description

Evidence:
- `.agents/skills/needle-missing-description/SKILL.md`

Requested fix:
Add `description` to the skill frontmatter.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 2: SCRIPT_NOT_EXECUTABLE

Severity: `P2`

Problem: Script is not user-executable: scripts/needle-unvalidated-script

Evidence:
- `scripts/needle-unvalidated-script`

Requested fix:
Run `chmod +x scripts/needle-unvalidated-script` or document why this script is not executable.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 3: SCRIPT_WITHOUT_VALIDATION_REFERENCE

Severity: `P3`

Problem: Script has no explicit validation reference: needle-unvalidated-script

Evidence:
- `scripts/needle-unvalidated-script`
- `registry/VALIDATION.md`

Requested fix:
Add the command or validation evidence for `scripts/needle-unvalidated-script` to `registry/VALIDATION.md`.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.

## Brief 4: EMPTY_REGISTRY_FILE

Severity: `P2`

Problem: Registry file is empty: registry/needle-empty.md

Evidence:
- `registry/needle-empty.md`

Requested fix:
Add durable evidence or remove the empty registry artifact.

Verification:
- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
- Confirm the finding is gone or explicitly documented as accepted risk.
