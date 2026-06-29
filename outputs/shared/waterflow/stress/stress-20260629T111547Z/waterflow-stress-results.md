# Waterflow Stress Results

- Generated: `2026-06-29T11:15:49.063468+00:00`
- Status: `pass`
- Run dir: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111547Z`

## Harness Philosophy

- Purpose: Turn Waterflow confidence into falsifiable evidence by injecting known defects, clean scale, and expected command failures.
- Pass definition: A stress pass means expected defects were detected, clean scale produced no unexpected findings, and expected validation failures/timeouts were recorded.
- Non-goal: A stress pass is not a claim that the real lab, a product, or a live agent workflow has no defects.
- Isolation: Generated fixtures stay under outputs/shared/waterflow/stress so negative evidence cannot contaminate the real lab graph.

## Harness Criteria

### expected_problem_codes_detected: pass

Problem fixture must detect every expected defect family.

### implemented_detector_codes_covered: pass

Every implemented detector code must have a matching injected problem, and every expected injected problem must map to a detector.

### clean_scale_stays_clean: pass

Scale fixture must reach the requested node count without unexpected findings.

### validation_failures_are_recorded: pass

Validation stress must record one pass, one failing command, and one timeout.

### fixtures_are_generated_evidence: pass

Problem and scale fixtures must stay inside the generated stress run directory.

## Detector Coverage

- Implemented detector codes: `12`
- Expected problem codes: `12`
- Uncovered implemented codes: `0`
- Expected codes without implementation: `0`

## Problem Lab

- Findings: `13`
- Missing expected codes: `0`

Detected codes:
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

## Scale Lab

- Requested scale paths: `1200`
- Nodes: `1209`
- Edges: `1208`
- Findings: `0`

## Validation Runner

- Checks: `3`
- Passed: `1`
- Failed: `2`
- Timed out: `1`
- Max exit code: `124`

## Artifacts

- `problem_repair_briefs`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111547Z/problem-repair-briefs.md`
- `problem_report_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111547Z/problem-report.json`
- `problem_report_markdown`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111547Z/problem-report.md`
- `scale_report_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111547Z/scale-report.json`
- `scale_report_markdown`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111547Z/scale-report.md`
- `validation_results_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111547Z/validation-results.json`
- `validation_results_markdown`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111547Z/validation-results.md`
