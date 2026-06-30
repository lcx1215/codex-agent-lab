# Async Execution Check

- Generated: `2026-06-30T08:50:29.649396+00:00`
- Run id: `20260630T085022Z-81982`
- Checks: `9`
- Passed: `8`
- Failed: `1`
- Timed out: `0`
- Duration seconds: `7.228`

## 1. runtime-compatibility: pass

command: `./scripts/check-runtime-compatibility`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `2.763`
tmpdir: `.tmp/async-execution/20260630T085022Z-81982/runtime-compatibility`

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
duration_seconds: `3.047`
tmpdir: `.tmp/async-execution/20260630T085022Z-81982/workspace-safety`

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
duration_seconds: `3.295`
tmpdir: `.tmp/async-execution/20260630T085022Z-81982/sandbox`

stdout:

```text
OK: sandbox boundaries are valid
```

## 4. secrets: pass

command: `./scripts/check-secrets`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `1.177`
tmpdir: `.tmp/async-execution/20260630T085022Z-81982/secrets`

stdout:

```text
OK: no committable secrets or README-local user paths detected
```

## 5. project-rules: pass

command: `./scripts/check-project-rules`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `3.427`
tmpdir: `.tmp/async-execution/20260630T085022Z-81982/project-rules`

stdout:

```text
OK: project rule surfaces are valid
```

## 6. workflow-modes: pass

command: `./scripts/check-workflow-modes`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `1.266`
tmpdir: `.tmp/async-execution/20260630T085022Z-81982/workflow-modes`

stdout:

```text
OK: workflow modes are valid
```

## 7. unit-tests: fail

command: `python3 -m unittest discover -s tests`
exit_code: `1`
timed_out: `false`
stderr_allowed: `true`
duration_seconds: `7.206`
tmpdir: `.tmp/async-execution/20260630T085022Z-81982/unit-tests`

failure_reasons: `exit code 1`

stderr:

```text
.........................F....
======================================================================
FAIL: test_new_workspace_declares_scenario_boundary_and_agent_amplification (test_workspace_contract.WorkspaceContractTests.test_new_workspace_declares_scenario_boundary_and_agent_amplification)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/liuchengxu/Desktop/codex-agent-lab/tests/test_workspace_contract.py", line 31, in test_new_workspace_declares_scenario_boundary_and_agent_amplification
    self.assertTrue(workspace.is_dir())
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true

----------------------------------------------------------------------
Ran 30 tests in 6.721s

FAILED (failures=1)
```

## 8. waterflow-scan-a: pass

command: `python3 -m waterflow.auditor --root . --output-dir /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-a --compare-last`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.671`
tmpdir: `.tmp/async-execution/20260630T085022Z-81982/waterflow-scan-a`

stdout:

```text
json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-a/waterflow-report.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-a/waterflow-report.md
repair_briefs: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-a/waterflow-repair-briefs.md
validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-a/waterflow-validation-plan.json
validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-a/waterflow-validation-plan.md
changed_validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-a/waterflow-validation-plan-changed.json
changed_validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-a/waterflow-validation-plan-changed.md
route_index_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-a/waterflow-route-index.json
route_index_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-a/waterflow-route-index.md
path_index: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-a/waterflow-path-index.json
findings: 1
```

## 9. waterflow-scan-b: pass

command: `python3 -m waterflow.auditor --root . --output-dir /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-b`
exit_code: `0`
timed_out: `false`
stderr_allowed: `false`
duration_seconds: `0.557`
tmpdir: `.tmp/async-execution/20260630T085022Z-81982/waterflow-scan-b`

stdout:

```text
json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-b/waterflow-report.json
markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-b/waterflow-report.md
repair_briefs: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-b/waterflow-repair-briefs.md
validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-b/waterflow-validation-plan.json
validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-b/waterflow-validation-plan.md
changed_validation_plan_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-b/waterflow-validation-plan-changed.json
changed_validation_plan_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-b/waterflow-validation-plan-changed.md
route_index_json: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-b/waterflow-route-index.json
route_index_markdown: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-b/waterflow-route-index.md
path_index: /Users/liuchengxu/Desktop/codex-agent-lab/.tmp/async-execution/20260630T085022Z-81982/waterflow-b/waterflow-path-index.json
findings: 1
```
