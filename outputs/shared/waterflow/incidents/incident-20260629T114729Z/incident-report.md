# Waterflow Complex Incident Results

- Generated: `2026-06-29T11:47:30.587494+00:00`
- Status: `pass`
- Run dir: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z`
- Findings: `14`
- Missing expected codes: `0`

## Philosophy

- Purpose: Exercise the full Waterflow incident loop: inject a realistic multi-route failure, detect it, capture failing command evidence, and produce a handoff for Codex or Claude.
- Pass definition: An incident pass means the intentionally broken fixture was detected and reported with actionable evidence; it does not mean the fixture or the real lab is repaired.
- Isolation: The broken fixture is generated under outputs/shared/waterflow/incidents and is not part of the real lab source graph.

## Criteria

### baseline_starts_clean: pass

The comparison baseline should be clean so diff and finding evidence point to the injected incident.

### expected_incident_codes_detected: pass

The complex fixture should trigger every expected Waterflow defect family.

### diff_contains_added_removed_changed_paths: pass

The incident should create a realistic changed-path surface, not just a static bad snapshot.

### validation_failures_are_captured: pass

The incident validation plan should record one pass, one failing command, and one timeout.

### route_index_prioritizes_repair_surface: pass

The route index should collapse the incident into route families with a high-risk summary.

### fixtures_are_isolated: pass

Broken incident fixtures must stay inside the generated incident run directory.

## Detected Codes

- `AGENT_MISSING_FIELD`
- `AGENT_TOML_INVALID`
- `CROSS_PROJECT_REFERENCE`
- `DUPLICATE_AGENT_NAME`
- `DUPLICATE_SKILL_NAME`
- `EMPTY_REGISTRY_FILE`
- `MISSING_CORE_PATH`
- `PROGRESS_WITHOUT_VALIDATION`
- `SCRIPT_NOT_EXECUTABLE`
- `SCRIPT_WITHOUT_VALIDATION_REFERENCE`
- `SKILL_MISSING_ENTRYPOINT`
- `SKILL_MISSING_FIELD`

## Path Diff

- Added: `11`
- Removed: `5`
- Changed: `6`

## Validation Runner

- Checks: `3`
- Passed: `1`
- Failed: `2`
- Timed out: `1`
- Max exit code: `124`

## Artifacts

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
