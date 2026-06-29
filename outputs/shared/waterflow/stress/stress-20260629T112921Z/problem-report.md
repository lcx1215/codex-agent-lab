# Waterflow Auditor Report

- Generated: `2026-06-29T11:29:22.477901+00:00`
- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T112921Z/problem-lab`
- Nodes: `17`
- Edges: `16`
- Findings: `13`

## Findings

### P1 MISSING_CORE_PATH

Required core path is missing: README.md

Evidence:
- `README.md`

Repair brief:

Create `README.md` or update the lab contract if this path is intentionally removed.

### P2 DUPLICATE_AGENT_NAME

Duplicate custom agent name: duplicate-agent

Evidence:
- `.codex/agents/duplicate-a.toml`
- `.codex/agents/duplicate-b.toml`

Repair brief:

Rename one agent so Codex has an unambiguous custom-agent target.

### P1 AGENT_TOML_INVALID

Agent TOML cannot be parsed: .codex/agents/invalid-agent.toml

Evidence:
- `.codex/agents/invalid-agent.toml`
- `Invalid value (at end of document)`

Repair brief:

Fix the TOML syntax, then rerun the waterflow scan.

### P1 AGENT_MISSING_FIELD

Agent is missing required field(s): name, description, developer_instructions

Evidence:
- `.codex/agents/invalid-agent.toml`

Repair brief:

Add `name, description, developer_instructions` to `.codex/agents/invalid-agent.toml` with narrow, role-specific content.

### P1 AGENT_MISSING_FIELD

Agent is missing required field(s): developer_instructions

Evidence:
- `.codex/agents/missing-field.toml`

Repair brief:

Add `developer_instructions` to `.codex/agents/missing-field.toml` with narrow, role-specific content.

### P2 DUPLICATE_SKILL_NAME

Duplicate skill name: duplicate-skill

Evidence:
- `.agents/skills/duplicate-skill-a/SKILL.md`
- `.agents/skills/duplicate-skill-b/SKILL.md`

Repair brief:

Rename or remove one skill so skill selection is unambiguous.

### P2 SKILL_MISSING_FIELD

Skill is missing required frontmatter field(s): description

Evidence:
- `.agents/skills/missing-description/SKILL.md`

Repair brief:

Add `description` to the skill frontmatter.

### P1 SKILL_MISSING_ENTRYPOINT

Skill directory has no SKILL.md: .agents/skills/missing-entrypoint

Evidence:
- `.agents/skills/missing-entrypoint`

Repair brief:

Add `SKILL.md` with `name` and `description`, or remove the stale skill directory.

### P2 SCRIPT_NOT_EXECUTABLE

Script is not user-executable: scripts/unvalidated-script

Evidence:
- `scripts/unvalidated-script`

Repair brief:

Run `chmod +x scripts/unvalidated-script` or document why this script is not executable.

### P3 SCRIPT_WITHOUT_VALIDATION_REFERENCE

Script has no explicit validation reference: unvalidated-script

Evidence:
- `scripts/unvalidated-script`
- `registry/VALIDATION.md`

Repair brief:

Add the command or validation evidence for `scripts/unvalidated-script` to `registry/VALIDATION.md`.

### P2 EMPTY_REGISTRY_FILE

Registry file is empty: registry/EMPTY.md

Evidence:
- `registry/EMPTY.md`

Repair brief:

Add durable evidence or remove the empty registry artifact.

### P2 CROSS_PROJECT_REFERENCE

Lab workflow references lcx-s-openclaw even though the first Waterflow Auditor scope excludes it.

Evidence:
- `AGENTS.md`

Repair brief:

Remove the reference or document why this path is allowed for this lab-only scan.

### P2 PROGRESS_WITHOUT_VALIDATION

Progress claims completion-like state but validation evidence is missing or too thin.

Evidence:
- `registry/current-progress.md`
- `registry/VALIDATION.md`

Repair brief:

Run the relevant verification commands and record exact evidence in `registry/VALIDATION.md`.

## Graph Summary

| Kind | Count |
| --- | ---: |
| `agent` | 4 |
| `auditor-code` | 1 |
| `doc` | 1 |
| `registry` | 3 |
| `root` | 1 |
| `rules` | 1 |
| `script` | 1 |
| `skill` | 3 |
| `test` | 1 |
| `workspace-root` | 1 |
