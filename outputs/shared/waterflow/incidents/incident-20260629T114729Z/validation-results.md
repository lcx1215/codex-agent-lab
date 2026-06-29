# Waterflow Validation Results

- Generated: `2026-06-29T11:47:30.587207+00:00`
- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z`
- Checks: `3`
- Passed: `1`
- Failed: `2`
- Timed out: `1`
- Max exit code: `124`
- Duration seconds: `1.057`

## Check 1: pass

command: `python3 -c 'print("incident-pass: baseline evidence readable")'`
risk: `P2`
exit_code: `0`
timed_out: `false`
duration_seconds: `0.027`

route_kinds:
- `incident`

covered_paths:
- `validation/pass`

stdout:

```text
incident-pass: baseline evidence readable
```

## Check 2: fail

command: `python3 -c 'import sys; print("incident-fail: broken handoff reproduced"); sys.exit(9)'`
risk: `P1`
exit_code: `9`
timed_out: `false`
duration_seconds: `0.027`

route_kinds:
- `incident`

covered_paths:
- `validation/fail`

stdout:

```text
incident-fail: broken handoff reproduced
```

## Check 3: fail

command: `python3 -c 'import time; print("incident-timeout: stuck repair loop"); time.sleep(5)'`
risk: `P1`
exit_code: `124`
timed_out: `true`
duration_seconds: `1.003`

route_kinds:
- `incident`

covered_paths:
- `validation/timeout`

stderr:

```text
Timed out after 1 seconds.
```
