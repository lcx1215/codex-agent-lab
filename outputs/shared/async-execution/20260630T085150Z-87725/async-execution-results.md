# Async Execution Check

- Generated: `2026-06-30T08:51:54.880504+00:00`
- Run id: `20260630T085150Z-87725`
- Checks: `9`
- Passed: `9`
- Failed: `0`
- Timed out: `0`
- Duration seconds: `4.541`

## 1. runtime-compatibility: pass

command: `./scripts/check-runtime-compatibility`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `1.29`
tmpdir: `.tmp/async-execution/20260630T085150Z-87725/runtime-compatibility`

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

## 2. workspace-safety: pass

command: `./scripts/check-workspace-safety`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `1.217`
tmpdir: `.tmp/async-execution/20260630T085150Z-87725/workspace-safety`

stdout:

```text
status: warn
workspaces: 6
warnings: 24
failed: 0
json: /Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/workspace-safety/workspace-safety.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/workspace-safety/workspace-safety.md
```

## 3. sandbox: pass

command: `./scripts/check-sandbox`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `1.513`
tmpdir: `.tmp/async-execution/20260630T085150Z-87725/sandbox`

stdout:

```text
OK: sandbox boundaries are valid
```

## 4. secrets: pass

command: `./scripts/check-secrets`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.774`
tmpdir: `.tmp/async-execution/20260630T085150Z-87725/secrets`

stdout:

```text
OK: no committable secrets or README-local user paths detected
```

## 5. project-rules: pass

command: `./scripts/check-project-rules`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `1.506`
tmpdir: `.tmp/async-execution/20260630T085150Z-87725/project-rules`

stdout:

```text
OK: project rule surfaces are valid
```

## 6. workflow-modes: pass

command: `./scripts/check-workflow-modes`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.356`
tmpdir: `.tmp/async-execution/20260630T085150Z-87725/workflow-modes`

stdout:

```text
OK: workflow modes are valid
```

## 7. unit-tests: pass

command: `python3 -m unittest discover -s tests`
exit_code: `0`
timed_out: `false`
stderr_allowed: `true`
duration_seconds: `4.522`
tmpdir: `.tmp/async-execution/20260630T085150Z-87725/unit-tests`

stderr:

```text
..............................
----------------------------------------------------------------------
Ran 30 tests in 4.296s

OK
```

## 8. waterflow-scan-a: pass

command: `python3 -m waterflow.auditor --root . --output-dir /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-a --compare-last`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.205`
tmpdir: `.tmp/async-execution/20260630T085150Z-87725/waterflow-scan-a`

stdout:

```text
json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-a/waterflow-report.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-a/waterflow-report.md
repair_briefs: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-a/waterflow-repair-briefs.md
validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-a/waterflow-validation-plan.json
validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-a/waterflow-validation-plan.md
changed_validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-a/waterflow-validation-plan-changed.json
changed_validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-a/waterflow-validation-plan-changed.md
route_index_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-a/waterflow-route-index.json
route_index_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-a/waterflow-route-index.md
path_index: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-a/waterflow-path-index.json
findings: 1
```

## 9. waterflow-scan-b: pass

command: `python3 -m waterflow.auditor --root . --output-dir /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-b`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.196`
tmpdir: `.tmp/async-execution/20260630T085150Z-87725/waterflow-scan-b`

stdout:

```text
json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-b/waterflow-report.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-b/waterflow-report.md
repair_briefs: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-b/waterflow-repair-briefs.md
validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-b/waterflow-validation-plan.json
validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-b/waterflow-validation-plan.md
changed_validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-b/waterflow-validation-plan-changed.json
changed_validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-b/waterflow-validation-plan-changed.md
route_index_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-b/waterflow-route-index.json
route_index_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-b/waterflow-route-index.md
path_index: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085150Z-87725/waterflow-b/waterflow-path-index.json
findings: 1
```
