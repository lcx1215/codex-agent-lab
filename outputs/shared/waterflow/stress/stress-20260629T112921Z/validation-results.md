# Waterflow Validation Results

- Generated: `2026-06-29T11:29:24.531209+00:00`
- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/stress/stress-20260629T112921Z`
- Checks: `3`
- Passed: `1`
- Failed: `2`
- Timed out: `1`
- Max exit code: `124`
- Duration seconds: `1.071`

## Check 1: pass

command: `python3 -c 'print("stress-ok")'`
risk: `P2`
exit_code: `0`
timed_out: `false`
duration_seconds: `0.038`

route_kinds:
- `stress`

covered_paths:
- `validation/pass`

stdout:

```text
stress-ok
```

## Check 2: fail

command: `python3 -c 'import sys; print("stress-fail"); sys.exit(7)'`
risk: `P2`
exit_code: `7`
timed_out: `false`
duration_seconds: `0.029`

route_kinds:
- `stress`

covered_paths:
- `validation/fail`

stdout:

```text
stress-fail
```

## Check 3: fail

command: `python3 -c 'import time; print("stress-timeout"); time.sleep(5)'`
risk: `P2`
exit_code: `124`
timed_out: `true`
duration_seconds: `1.004`

route_kinds:
- `stress`

covered_paths:
- `validation/timeout`

stderr:

```text
Timed out after 1 seconds.
```
