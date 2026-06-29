# OMX Execution Proof Report

## Scope

Workspace: `workspaces/20260629_204008-omx-execution-proof`

This bounded proof inspected the lab workflow-mode system and recorded fresh verification evidence without modifying parent lab source. The active host surface for this run was Codex App outside tmux, so the work used the App-safe OMX spine and does not claim that an attached tmux CLI OMX runtime independently completed the task.

## Inspected Local Evidence

- Workspace contract: `AGENTS.md` keeps edits inside this workspace, sets default workflow mode to `omx-long-horizon`, and names the required output files.
- Task brief: `brief.md` requires `omx-execution-report.md`, `validation.md`, `benefit-matrix.json`, and an updated `progress.md`.
- Workflow contract: `docs/workflow-modes.md` defines `omx-long-horizon` as Terminal/API-relay with CLI runtime, entry `omx-api` or `./scripts/start-api-relay`, expected artifacts including workspace brief/progress/validation/handoff notes, and stop condition of completed checkpoints plus recorded evidence.
- Mode script: `scripts/workflow-mode omx-long-horizon` emits the same machine-checkable contract.
- Lab health script: `scripts/check-lab` verifies lab structure and invokes project-rule and workflow-mode checks.

## Checks Run

Fresh command evidence is recorded in `validation.md`.

| Command | Status | Key evidence |
| --- | --- | --- |
| `scripts/check-workflow-modes` | PASS | `OK: workflow modes are valid`, exit 0 |
| `scripts/check-lab` | PASS | `Agents: 8`, `Skills: 42`, `OK: lab structure is valid`, exit 0 |
| `scripts/workflow-mode omx-long-horizon` | PASS | `surface: Terminal/API-relay`, `omx_level: CLI runtime`, `entry: omx-api or ./scripts/start-api-relay`, exit 0 |

## Findings

1. **Routing contract exists and is checkable.** The workflow-mode docs and script agree on the `omx-long-horizon` contract, and `scripts/check-workflow-modes` validates all expected modes.
2. **Auditability is the clearest value.** The workspace brief, progress file, validation file, and structured benefit matrix make the result reviewable without trusting the chat transcript.
3. **Lab structure currently passes its health gate.** `scripts/check-lab` reports a valid lab with 8 agents and 42 skills, and it invokes project-rule and workflow-mode checks internally.
4. **Runtime-execution proof is partial.** This run validated the CLI-runtime contract and produced the required artifacts, but the main execution surface was App-safe outside tmux. A shell quoting error briefly invoked `omx-api`, which failed due missing stdin prompt / non-TTY before doing task work; that failed invocation is not counted as a successful CLI runtime proof.
5. **No parent lab source change was needed.** Any future improvement to make this proof stronger should be recorded as a recommendation rather than editing parent lab source from this workspace.

## Boundary Notes

- No secrets, auth files, provider config, plugins, LaunchAgents, or parent lab source files were intentionally modified.
- During artifact writing, an unquoted here-doc accidentally evaluated backticks and invoked `omx-api`; stdout showed green-light lines and then failures (`No prompt provided via stdin`, `TERM is set to "dumb"`). This was a boundary incident and is recorded in `validation.md`.
- A temporary `/tmp/benefit-matrix-check.txt` was created during a JSON pretty-print check; no secret data was included. The authoritative validation artifact is `validation.md`.

## Verdict On Execution-Layer Value

`omx-long-horizon` adds **moderate positive value** for this task through explicit routing, artifact discipline, validation gates, and handoff quality. For this bounded read-only proof, the marginal value over a disciplined App-side run is mostly auditability and restartability rather than parallelism or heavy runtime execution.

Because the active run did not complete inside an attached CLI OMX runtime, the runtime-execution claim remains a validation gap. A stronger follow-up proof should launch from `omx-api` or `./scripts/start-api-relay` only when the task boundary explicitly allows its green-light/lane-guard side effects, and should have that runtime generate the same four artifacts.

## Handoff

Artifacts to audit:

- `workspaces/20260629_204008-omx-execution-proof/omx-execution-report.md`
- `workspaces/20260629_204008-omx-execution-proof/validation.md`
- `workspaces/20260629_204008-omx-execution-proof/benefit-matrix.json`
- `workspaces/20260629_204008-omx-execution-proof/progress.md`
