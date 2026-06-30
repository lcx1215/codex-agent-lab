# Async Execution Check

- Generated: `2026-06-30T02:20:21.599600+00:00`
- Run id: `20260630T022018Z-72275`
- Checks: `7`
- Passed: `7`
- Failed: `0`
- Timed out: `0`
- Duration seconds: `3.423`

## 1. sandbox: pass

command: `./scripts/check-sandbox`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `2.726`
tmpdir: `.tmp/async-execution/20260630T022018Z-72275/sandbox`

stdout:

```text
OK: sandbox boundaries are valid
```

## 2. secrets: pass

command: `./scripts/check-secrets`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `1.088`
tmpdir: `.tmp/async-execution/20260630T022018Z-72275/secrets`

stdout:

```text
OK: no committable secrets or README-local user paths detected
```

## 3. project-rules: pass

command: `./scripts/check-project-rules`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.399`
tmpdir: `.tmp/async-execution/20260630T022018Z-72275/project-rules`

stdout:

```text
OK: project rule surfaces are valid
```

## 4. workflow-modes: pass

command: `./scripts/check-workflow-modes`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.727`
tmpdir: `.tmp/async-execution/20260630T022018Z-72275/workflow-modes`

stdout:

```text
OK: workflow modes are valid
```

## 5. unit-tests: pass

command: `python3 -m unittest discover -s tests`
exit_code: `0`
timed_out: `false`
stderr_allowed: `true`
duration_seconds: `3.411`
tmpdir: `.tmp/async-execution/20260630T022018Z-72275/unit-tests`

stderr:

```text
............
----------------------------------------------------------------------
Ran 12 tests in 3.135s

OK
```

## 6. waterflow-scan-a: pass

command: `python3 -m waterflow.auditor --root . --output-dir /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-a --compare-last`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.588`
tmpdir: `.tmp/async-execution/20260630T022018Z-72275/waterflow-scan-a`

stdout:

```text
json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-a/waterflow-report.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-a/waterflow-report.md
repair_briefs: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-a/waterflow-repair-briefs.md
validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-a/waterflow-validation-plan.json
validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-a/waterflow-validation-plan.md
changed_validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-a/waterflow-validation-plan-changed.json
changed_validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-a/waterflow-validation-plan-changed.md
route_index_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-a/waterflow-route-index.json
route_index_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-a/waterflow-route-index.md
path_index: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-a/waterflow-path-index.json
findings: 2
```

## 7. waterflow-scan-b: pass

command: `python3 -m waterflow.auditor --root . --output-dir /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-b`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.503`
tmpdir: `.tmp/async-execution/20260630T022018Z-72275/waterflow-scan-b`

stdout:

```text
json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-b/waterflow-report.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-b/waterflow-report.md
repair_briefs: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-b/waterflow-repair-briefs.md
validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-b/waterflow-validation-plan.json
validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-b/waterflow-validation-plan.md
changed_validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-b/waterflow-validation-plan-changed.json
changed_validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-b/waterflow-validation-plan-changed.md
route_index_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-b/waterflow-route-index.json
route_index_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-b/waterflow-route-index.md
path_index: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T022018Z-72275/waterflow-b/waterflow-path-index.json
findings: 2
```
