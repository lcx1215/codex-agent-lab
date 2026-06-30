# Benchmark Validation

## Local Edit-Test Loop

- Workspace creation: pass, generated `workspaces/20260630_095508-codex-self-ide-benchmark`.
- RED test: pass as expected failure.
  - Command: `/usr/bin/time -p python3 -m unittest discover -s tests`
  - Result: failed with 1 assertion showing `max_risk` was `P3` instead of expected `P1`.
  - Timing: `real 0.32`, unittest body `Ran 4 tests in 0.033s`.
- GREEN test: pass.
  - Command: `/usr/bin/time -p python3 -m unittest discover -s tests`
  - Result: `Ran 4 tests in 0.038s`, `OK`.
  - Timing: `real 0.44`.
- Compile check: pass.
  - Command: `/usr/bin/time -p python3 -m py_compile lane_router.py`
  - Timing: `real 0.24`.

## Lab Gates

- Speed contract: pass.
  - Command: `/usr/bin/time -p ./scripts/check-speed-contract`
  - Result: `OK: Waterflow speed contract is valid`.
  - Timing: `real 0.41`.
- Project rules: pass.
  - Command: `/usr/bin/time -p ./scripts/check-project-rules`
  - Result: `OK: project rule surfaces are valid`.
  - Timing: `real 0.25`.
- Secret guard: pass.
  - Command: `/usr/bin/time -p ./scripts/check-secrets`
  - Result: `OK: no committable secrets or README-local user paths detected`.
  - Timing: `real 0.71`.
- Integrated lab check: pass.
  - Command: `/usr/bin/time -p ./scripts/check-lab`
  - Result: 8 agents, 46 skills, Codex CLI found, `OK: lab structure is valid`.
  - Timing: `real 4.17`.
- Lab unit tests: pass.
  - Command: `/usr/bin/time -p python3 -m unittest discover -s tests`
  - Result: `Ran 12 tests in 2.800s`, `OK`.
  - Timing: `real 3.10`.
- Async execution safety: pass.
  - Command: `/usr/bin/time -p ./scripts/check-async-execution`
  - Result: 7 checks, 7 passed, 0 failed, 0 timed out.
  - Timing: `real 3.31`.

## Waterflow

- Changed-path scan: pass.
  - Command: `/usr/bin/time -p ./scripts/waterflow-scan --root . --compare-last`
  - Result: `findings: 0`.
  - Timing: `real 0.32`.
  - Summary: 100 paths, 0 findings, 1 added path: this benchmark workspace.
  - Changed-only plan: 1 check, max risk `P3`.
- Boundary verification: pass.
  - Command: `/usr/bin/time -p ./scripts/waterflow-verify`
  - Result: 5 checks, 5 passed, 0 failed.
  - Timing: `real 5.69`.

## Model-Backed OMX Smoke

- Command shape: `OMX_GREEN_LIGHT_NOTIFY=0 /usr/bin/time -p /Users/liuchengxu/.local/bin/omx-api exec -C <benchmark-workspace> - < omx-smoke-prompt.md`
- Result: pass.
- Timing: `real 81.66`.
- Tokens: `40,106`.
- Runtime: model `gpt-5.5`, provider `custom`, reasoning effort `xhigh`.
- Output: wrote `omx-smoke.md` in this workspace and verified required sections.
- Noted runtime noise:
  - Linear, Cloudflare, and Notion MCP workers emitted missing or invalid OAuth token errors.
  - Skills context budget warning removed skill descriptions and omitted 98 skills.
  - The API-relay exec runtime reported `sandbox: danger-full-access`; the prompt constrained edits to this workspace, but the runtime itself was broader than the lab's ideal workspace-write posture.
