# Waterflow Stress Results

- Generated: `2026-06-29T11:10:29.919351+00:00`
- Status: `pass`
- Run dir: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111028Z`

## Harness Philosophy

- Purpose: Turn Waterflow confidence into falsifiable evidence by injecting known defects, clean scale, and expected command failures.
- Pass definition: A stress pass means expected defects were detected, clean scale produced no unexpected findings, and expected validation failures/timeouts were recorded.
- Non-goal: A stress pass is not a claim that the real lab, a product, or a live agent workflow has no defects.
- Isolation: Generated fixtures stay under outputs/shared/waterflow/stress so negative evidence cannot contaminate the real lab graph.

## Problem Lab

- Findings: `12`
- Missing expected codes: `0`

Detected codes:
- `AGENT_MISSING_FIELD`
- `AGENT_TOML_INVALID`
- `CROSS_PROJECT_REFERENCE`
- `DUPLICATE_AGENT_NAME`
- `DUPLICATE_SKILL_NAME`
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

- `problem_repair_briefs`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111028Z/problem-repair-briefs.md`
- `problem_report_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111028Z/problem-report.json`
- `problem_report_markdown`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111028Z/problem-report.md`
- `scale_report_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111028Z/scale-report.json`
- `scale_report_markdown`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111028Z/scale-report.md`
- `validation_results_json`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111028Z/validation-results.json`
- `validation_results_markdown`: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T111028Z/validation-results.md`
