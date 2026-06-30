# Async Execution Check

- Generated: `2026-06-30T08:10:48.605992+00:00`
- Run id: `20260630T081043Z-70694`
- Checks: `8`
- Passed: `8`
- Failed: `0`
- Timed out: `0`
- Duration seconds: `4.937`

## 1. runtime-compatibility: pass

command: `./scripts/check-runtime-compatibility`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `2.429`
tmpdir: `.tmp/async-execution/20260630T081043Z-70694/runtime-compatibility`

stdout:

```text
status: pass
checks: 40
passed: 40
warnings: 0
failed: 0
json: /Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/compatibility/runtime-compatibility.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/compatibility/runtime-compatibility.md
```

## 2. sandbox: pass

command: `./scripts/check-sandbox`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `2.175`
tmpdir: `.tmp/async-execution/20260630T081043Z-70694/sandbox`

stdout:

```text
OK: sandbox boundaries are valid
```

## 3. secrets: pass

command: `./scripts/check-secrets`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.787`
tmpdir: `.tmp/async-execution/20260630T081043Z-70694/secrets`

stdout:

```text
OK: no committable secrets or README-local user paths detected
```

## 4. project-rules: pass

command: `./scripts/check-project-rules`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.609`
tmpdir: `.tmp/async-execution/20260630T081043Z-70694/project-rules`

stdout:

```text
OK: project rule surfaces are valid
```

## 5. workflow-modes: pass

command: `./scripts/check-workflow-modes`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.753`
tmpdir: `.tmp/async-execution/20260630T081043Z-70694/workflow-modes`

stdout:

```text
OK: workflow modes are valid
```

## 6. unit-tests: pass

command: `python3 -m unittest discover -s tests`
exit_code: `0`
timed_out: `false`
stderr_allowed: `true`
duration_seconds: `4.923`
tmpdir: `.tmp/async-execution/20260630T081043Z-70694/unit-tests`

stderr:

```text
..........................
----------------------------------------------------------------------
Ran 26 tests in 4.714s

OK
```

## 7. waterflow-scan-a: pass

command: `python3 -m waterflow.auditor --root . --output-dir /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-a --compare-last`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.482`
tmpdir: `.tmp/async-execution/20260630T081043Z-70694/waterflow-scan-a`

stdout:

```text
json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-a/waterflow-report.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-a/waterflow-report.md
repair_briefs: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-a/waterflow-repair-briefs.md
validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-a/waterflow-validation-plan.json
validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-a/waterflow-validation-plan.md
changed_validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-a/waterflow-validation-plan-changed.json
changed_validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-a/waterflow-validation-plan-changed.md
route_index_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-a/waterflow-route-index.json
route_index_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-a/waterflow-route-index.md
path_index: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-a/waterflow-path-index.json
findings: 0
```

## 8. waterflow-scan-b: pass

command: `python3 -m waterflow.auditor --root . --output-dir /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-b`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.439`
tmpdir: `.tmp/async-execution/20260630T081043Z-70694/waterflow-scan-b`

stdout:

```text
json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-b/waterflow-report.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-b/waterflow-report.md
repair_briefs: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-b/waterflow-repair-briefs.md
validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-b/waterflow-validation-plan.json
validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-b/waterflow-validation-plan.md
changed_validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-b/waterflow-validation-plan-changed.json
changed_validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-b/waterflow-validation-plan-changed.md
route_index_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-b/waterflow-route-index.json
route_index_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-b/waterflow-route-index.md
path_index: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T081043Z-70694/waterflow-b/waterflow-path-index.json
findings: 0
```
