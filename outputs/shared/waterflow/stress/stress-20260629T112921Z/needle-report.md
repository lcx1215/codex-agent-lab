# Waterflow Auditor Report

- Generated: `2026-06-29T11:29:24.851073+00:00`
- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T112921Z/needle-lab`
- Nodes: `2412`
- Edges: `2411`
- Findings: `4`

## Findings

### P2 SKILL_MISSING_FIELD

Skill is missing required frontmatter field(s): description

Evidence:
- `.agents/skills/needle-missing-description/SKILL.md`

Repair brief:

Add `description` to the skill frontmatter.

### P2 SCRIPT_NOT_EXECUTABLE

Script is not user-executable: scripts/needle-unvalidated-script

Evidence:
- `scripts/needle-unvalidated-script`

Repair brief:

Run `chmod +x scripts/needle-unvalidated-script` or document why this script is not executable.

### P3 SCRIPT_WITHOUT_VALIDATION_REFERENCE

Script has no explicit validation reference: needle-unvalidated-script

Evidence:
- `scripts/needle-unvalidated-script`
- `registry/VALIDATION.md`

Repair brief:

Add the command or validation evidence for `scripts/needle-unvalidated-script` to `registry/VALIDATION.md`.

### P2 EMPTY_REGISTRY_FILE

Registry file is empty: registry/needle-empty.md

Evidence:
- `registry/needle-empty.md`

Repair brief:

Add durable evidence or remove the empty registry artifact.

## Graph Summary

| Kind | Count |
| --- | ---: |
| `agent` | 288 |
| `auditor-code` | 1 |
| `doc` | 289 |
| `readme` | 1 |
| `registry` | 3 |
| `root` | 1 |
| `rules` | 1 |
| `script` | 529 |
| `skill` | 817 |
| `test` | 289 |
| `workspace` | 192 |
| `workspace-root` | 1 |
