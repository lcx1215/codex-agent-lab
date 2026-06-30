# Async Execution Check

- Generated: `2026-06-30T03:51:14.142505+00:00`
- Run id: `20260630T035111Z-64295`
- Checks: `7`
- Passed: `7`
- Failed: `0`
- Timed out: `0`
- Duration seconds: `3.088`

## 1. sandbox: pass

command: `./scripts/check-sandbox`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `2.314`
tmpdir: `.tmp/async-execution/20260630T035111Z-64295/sandbox`

stdout:

```text
OK: sandbox boundaries are valid
```

## 2. secrets: pass

command: `./scripts/check-secrets`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.823`
tmpdir: `.tmp/async-execution/20260630T035111Z-64295/secrets`

stdout:

```text
OK: no committable secrets or README-local user paths detected
```

## 3. project-rules: pass

command: `./scripts/check-project-rules`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.363`
tmpdir: `.tmp/async-execution/20260630T035111Z-64295/project-rules`

stdout:

```text
OK: project rule surfaces are valid
```

## 4. workflow-modes: pass

command: `./scripts/check-workflow-modes`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.573`
tmpdir: `.tmp/async-execution/20260630T035111Z-64295/workflow-modes`

stdout:

```text
OK: workflow modes are valid
```

## 5. unit-tests: pass

command: `python3 -m unittest discover -s tests`
exit_code: `0`
timed_out: `false`
stderr_allowed: `true`
duration_seconds: `3.076`
tmpdir: `.tmp/async-execution/20260630T035111Z-64295/unit-tests`

stderr:

```text
................
----------------------------------------------------------------------
Ran 16 tests in 2.881s

OK
```

## 6. waterflow-scan-a: pass

command: `python3 -m waterflow.auditor --root . --output-dir /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-a --compare-last`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.304`
tmpdir: `.tmp/async-execution/20260630T035111Z-64295/waterflow-scan-a`

stdout:

```text
json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-a/waterflow-report.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-a/waterflow-report.md
repair_briefs: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-a/waterflow-repair-briefs.md
validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-a/waterflow-validation-plan.json
validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-a/waterflow-validation-plan.md
changed_validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-a/waterflow-validation-plan-changed.json
changed_validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-a/waterflow-validation-plan-changed.md
route_index_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-a/waterflow-route-index.json
route_index_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-a/waterflow-route-index.md
path_index: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-a/waterflow-path-index.json
findings: 0
```

## 7. waterflow-scan-b: pass

command: `python3 -m waterflow.auditor --root . --output-dir /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-b`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.3`
tmpdir: `.tmp/async-execution/20260630T035111Z-64295/waterflow-scan-b`

stdout:

```text
json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-b/waterflow-report.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-b/waterflow-report.md
repair_briefs: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-b/waterflow-repair-briefs.md
validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-b/waterflow-validation-plan.json
validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-b/waterflow-validation-plan.md
changed_validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-b/waterflow-validation-plan-changed.json
changed_validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-b/waterflow-validation-plan-changed.md
route_index_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-b/waterflow-route-index.json
route_index_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-b/waterflow-route-index.md
path_index: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T035111Z-64295/waterflow-b/waterflow-path-index.json
findings: 0
```
