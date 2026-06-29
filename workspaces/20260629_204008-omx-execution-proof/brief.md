# Task Brief

Created: 2026-06-29 20:40:08 +0800

## Objective

Run a bounded real `omx-long-horizon` proof task through the CLI OMX runtime and evaluate whether OMX adds execution-layer value beyond App-side orchestration.

The task is not to change lab source code. The task is to independently inspect the current lab workflow-mode system, run the relevant checks, and create evidence artifacts that another Codex App session can audit.

## Constraints

- Keep work inside this workspace unless explicitly assigned otherwise.
- Do not read or write secrets.
- Record verification evidence before completion.
- Do not modify files outside this workspace.
- Do not change Codex auth, provider config, plugins, LaunchAgents, global rules, or App state.
- Use only non-secret metadata and local repository files needed to evaluate workflow modes.

## Required OMX Outputs

- `omx-execution-report.md`: concise report covering what was inspected, checks run, findings, and a verdict on execution-layer value.
- `validation.md`: exact commands run, pass/fail status, and evidence snippets.
- `benefit-matrix.json`: structured comparison of App-only vs OMX-assisted execution for this task.
- Update `progress.md` with current status and final handoff.

## Acceptance Checks

- OMX CLI runtime produces all required files in this workspace.
- Report cites concrete evidence from local files or command outputs.
- Validation includes at least `scripts/check-workflow-modes`, `scripts/check-lab`, and one `scripts/workflow-mode ...` command.
- Benefit matrix includes at least `routing`, `auditability`, `runtime_execution`, `parallelism`, `handoff_quality`, and `net_value` fields.
- App-side audit can verify the artifacts without trusting the OMX answer blindly.
