# Waterflow Incident Handoff for Codex or Claude

This is an actionable repair packet for a deliberately broken Waterflow incident fixture.
Do not treat `status: pass` as repaired; it means Waterflow successfully detected and reported the incident.

## Incident Summary

- Run dir: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z`
- Fixture root: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/incident-lab`
- Status: `pass`
- Findings: `14`
- Severity counts: `{"P0": 0, "P1": 5, "P2": 7, "P3": 2}`
- Validation failures captured: `2`
- Validation timeouts captured: `1`

## Route Families

| Route | Risk | Paths | Findings | Checks |
| --- | --- | ---: | --- | ---: |
| `agent` | `P1` | 4 | `AGENT_MISSING_FIELD`, `AGENT_TOML_INVALID`, `DUPLICATE_AGENT_NAME` | 3 |
| `auditor-code` | `P2` | 2 | - | 2 |
| `documentation` | `P1` | 2 | `CROSS_PROJECT_REFERENCE`, `MISSING_CORE_PATH` | 1 |
| `registry` | `P2` | 3 | `EMPTY_REGISTRY_FILE`, `PROGRESS_WITHOUT_VALIDATION` | 1 |
| `script` | `P2` | 2 | `SCRIPT_NOT_EXECUTABLE`, `SCRIPT_WITHOUT_VALIDATION_REFERENCE` | 3 |
| `skill` | `P2` | 3 | `DUPLICATE_SKILL_NAME`, `SKILL_MISSING_FIELD` | 3 |
| `unknown` | `P1` | 0 | `SKILL_MISSING_ENTRYPOINT` | 0 |

## Findings

### 1. P1 MISSING_CORE_PATH

Required core path is missing: README.md

Evidence: `README.md`

Repair: Create `README.md` or update the lab contract if this path is intentionally removed.

### 2. P1 AGENT_TOML_INVALID

Agent TOML cannot be parsed: .codex/agents/broken-syntax.toml

Evidence: `.codex/agents/broken-syntax.toml`, `Invalid value (at end of document)`

Repair: Fix the TOML syntax, then rerun the waterflow scan.

### 3. P1 AGENT_MISSING_FIELD

Agent is missing required field(s): name, description, developer_instructions

Evidence: `.codex/agents/broken-syntax.toml`

Repair: Add `name, description, developer_instructions` to `.codex/agents/broken-syntax.toml` with narrow, role-specific content.

### 4. P2 DUPLICATE_AGENT_NAME

Duplicate custom agent name: duplicate-owner

Evidence: `.codex/agents/duplicate-owner-a.toml`, `.codex/agents/duplicate-owner-b.toml`

Repair: Rename one agent so Codex has an unambiguous custom-agent target.

### 5. P1 AGENT_MISSING_FIELD

Agent is missing required field(s): developer_instructions

Evidence: `.codex/agents/missing-owner.toml`

Repair: Add `developer_instructions` to `.codex/agents/missing-owner.toml` with narrow, role-specific content.

### 6. P2 DUPLICATE_SKILL_NAME

Duplicate skill name: duplicate-repair-skill

Evidence: `.agents/skills/duplicate-skill-a/SKILL.md`, `.agents/skills/duplicate-skill-b/SKILL.md`

Repair: Rename or remove one skill so skill selection is unambiguous.

### 7. P2 SKILL_MISSING_FIELD

Skill is missing required frontmatter field(s): description

Evidence: `.agents/skills/missing-description/SKILL.md`

Repair: Add `description` to the skill frontmatter.

### 8. P1 SKILL_MISSING_ENTRYPOINT

Skill directory has no SKILL.md: .agents/skills/missing-entrypoint

Evidence: `.agents/skills/missing-entrypoint`

Repair: Add `SKILL.md` with `name` and `description`, or remove the stale skill directory.

### 9. P2 SCRIPT_NOT_EXECUTABLE

Script is not user-executable: scripts/release-handoff

Evidence: `scripts/release-handoff`

Repair: Run `chmod +x scripts/release-handoff` or document why this script is not executable.

### 10. P3 SCRIPT_WITHOUT_VALIDATION_REFERENCE

Script has no explicit validation reference: release-handoff

Evidence: `scripts/release-handoff`, `registry/VALIDATION.md`

Repair: Add the command or validation evidence for `scripts/release-handoff` to `registry/VALIDATION.md`.

### 11. P3 SCRIPT_WITHOUT_VALIDATION_REFERENCE

Script has no explicit validation reference: smoke-check

Evidence: `scripts/smoke-check`, `registry/VALIDATION.md`

Repair: Add the command or validation evidence for `scripts/smoke-check` to `registry/VALIDATION.md`.

### 12. P2 EMPTY_REGISTRY_FILE

Registry file is empty: registry/empty-claim.md

Evidence: `registry/empty-claim.md`

Repair: Add durable evidence or remove the empty registry artifact.

### 13. P2 CROSS_PROJECT_REFERENCE

Lab workflow references lcx-s-openclaw even though the first Waterflow Auditor scope excludes it.

Evidence: `AGENTS.md`

Repair: Remove the reference or document why this path is allowed for this lab-only scan.

### 14. P2 PROGRESS_WITHOUT_VALIDATION

Progress claims completion-like state but validation evidence is missing or too thin.

Evidence: `registry/current-progress.md`, `registry/VALIDATION.md`

Repair: Run the relevant verification commands and record exact evidence in `registry/VALIDATION.md`.

## Failed Validation Evidence

### Check 2

- command: `python3 -c 'import sys; print("incident-fail: broken handoff reproduced"); sys.exit(9)'`
- exit_code: `9`
- timed_out: `false`
- route_kinds: `incident`

stdout:

```text
incident-fail: broken handoff reproduced
```

### Check 3

- command: `python3 -c 'import time; print("incident-timeout: stuck repair loop"); time.sleep(5)'`
- exit_code: `124`
- timed_out: `true`
- route_kinds: `incident`

stderr:

```text
Timed out after 1 seconds.
```

## Repair Order

1. Restore hard blockers first
   Codes: `MISSING_CORE_PATH`, `AGENT_TOML_INVALID`, `AGENT_MISSING_FIELD`, `SKILL_MISSING_ENTRYPOINT`
   Reason: Codex and Claude cannot route work reliably while core surfaces, agent metadata, or skill entrypoints are broken.

2. Remove ambiguous routing
   Codes: `DUPLICATE_AGENT_NAME`, `DUPLICATE_SKILL_NAME`
   Reason: Duplicate names make delegation nondeterministic and can send repair work to the wrong route.

3. Repair execution and boundary evidence
   Codes: `SCRIPT_NOT_EXECUTABLE`, `SCRIPT_WITHOUT_VALIDATION_REFERENCE`, `CROSS_PROJECT_REFERENCE`, `PROGRESS_WITHOUT_VALIDATION`, `EMPTY_REGISTRY_FILE`, `SKILL_MISSING_FIELD`
   Reason: After routing is unblocked, make commands runnable, remove cross-boundary leakage, and replace claims with evidence.

4. Run the smallest verification spine
   Codes: final verification
   Reason: Re-run the incident harness, unit tests, and the normal Waterflow scan before claiming repair completion.

## Minimal Verification Commands

- `scripts/waterflow-incident --timeout-seconds 1`
- `python3 -m unittest discover -s tests`
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last`
- `scripts/waterflow-verify`

## Artifact Map

- `baseline_report_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/baseline-report.json`
- `change_briefs`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/change-briefs.md`
- `codex_claude_handoff`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/codex-claude-handoff.md`
- `incident_report_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/incident-report.json`
- `incident_report_markdown`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/incident-report.md`
- `path_diff_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/path-diff.json`
- `problem_report_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/problem-report.json`
- `problem_report_markdown`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/problem-report.md`
- `repair_briefs`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/repair-briefs.md`
- `route_index_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/route-index.json`
- `route_index_markdown`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/route-index.md`
- `validation_plan_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/validation-plan.json`
- `validation_results_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/validation-results.json`
- `validation_results_markdown`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/validation-results.md`
