# Async Execution Check

- Generated: `2026-06-29T13:08:41.771342+00:00`
- Run id: `20260629T130836Z-26094`
- Checks: `7`
- Passed: `7`
- Failed: `0`
- Timed out: `0`
- Duration seconds: `4.948`

## 1. sandbox: pass

command: `./scripts/check-sandbox`
exit_code: `0`
timed_out: `false`
duration_seconds: `4.947`
tmpdir: `.tmp/async-execution/20260629T130836Z-26094/sandbox`

stdout:

```text
OK: sandbox boundaries are valid
```

## 2. secrets: pass

command: `./scripts/check-secrets`
exit_code: `0`
timed_out: `false`
duration_seconds: `1.298`
tmpdir: `.tmp/async-execution/20260629T130836Z-26094/secrets`

stdout:

```text
OK: no committable secrets or README-local user paths detected
```

## 3. project-rules: pass

command: `./scripts/check-project-rules`
exit_code: `0`
timed_out: `false`
duration_seconds: `0.362`
tmpdir: `.tmp/async-execution/20260629T130836Z-26094/project-rules`

stdout:

```text
OK: project rule surfaces are valid
```

## 4. workflow-modes: pass

command: `./scripts/check-workflow-modes`
exit_code: `0`
timed_out: `false`
duration_seconds: `0.782`
tmpdir: `.tmp/async-execution/20260629T130836Z-26094/workflow-modes`

stdout:

```text
OK: workflow modes are valid
```

## 5. unit-tests: pass

command: `python3 -m unittest discover -s tests`
exit_code: `0`
timed_out: `false`
duration_seconds: `3.687`
tmpdir: `.tmp/async-execution/20260629T130836Z-26094/unit-tests`

stderr:

```text
............
----------------------------------------------------------------------
Ran 12 tests in 3.038s

OK
```

## 6. waterflow-scan-a: pass

command: `python3 -m waterflow.auditor --root . --output-dir /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-a --compare-last`
exit_code: `0`
timed_out: `false`
duration_seconds: `0.578`
tmpdir: `.tmp/async-execution/20260629T130836Z-26094/waterflow-scan-a`

stdout:

```text
json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-a/waterflow-report.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-a/waterflow-report.md
repair_briefs: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-a/waterflow-repair-briefs.md
validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-a/waterflow-validation-plan.json
validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-a/waterflow-validation-plan.md
changed_validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-a/waterflow-validation-plan-changed.json
changed_validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-a/waterflow-validation-plan-changed.md
route_index_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-a/waterflow-route-index.json
route_index_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-a/waterflow-route-index.md
path_index: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-a/waterflow-path-index.json
findings: 0
```

## 7. waterflow-scan-b: pass

command: `python3 -m waterflow.auditor --root . --output-dir /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-b`
exit_code: `0`
timed_out: `false`
duration_seconds: `0.491`
tmpdir: `.tmp/async-execution/20260629T130836Z-26094/waterflow-scan-b`

stdout:

```text
json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-b/waterflow-report.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-b/waterflow-report.md
repair_briefs: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-b/waterflow-repair-briefs.md
validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-b/waterflow-validation-plan.json
validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-b/waterflow-validation-plan.md
changed_validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-b/waterflow-validation-plan-changed.json
changed_validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-b/waterflow-validation-plan-changed.md
route_index_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-b/waterflow-route-index.json
route_index_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-b/waterflow-route-index.md
path_index: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260629T130836Z-26094/waterflow-b/waterflow-path-index.json
findings: 0
```
