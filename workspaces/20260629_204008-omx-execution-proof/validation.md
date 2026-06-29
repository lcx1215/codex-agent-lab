# Validation Evidence

## Boundary

- Write boundary requested: only files inside `workspaces/20260629_204008-omx-execution-proof` should be modified.
- Parent lab docs/scripts were inspected read-only to evaluate workflow modes.
- Secrets, auth files, provider config, plugins, LaunchAgents, and Codex App state were not intentionally modified.
- Boundary incident: an unquoted here-doc during artifact writing evaluated backticks and accidentally invoked `omx-api`; it failed before doing task work. This is recorded below and not counted as a successful CLI runtime proof.

## Required Commands

### 1. `scripts/check-workflow-modes`

Command run after correcting a shell wrapper variable name:

```sh
scripts/check-workflow-modes
rc=$?
printf '
EXIT_STATUS=%s
' "$rc"
exit "$rc"
```

Status: PASS

Evidence snippet:

```text
OK: workflow modes are valid

EXIT_STATUS=0
```

Operator note: an earlier wrapper used `status=$?` under zsh and failed because `status` is a read-only shell variable. The script itself had already printed `OK: workflow modes are valid`; the command was rerun with `rc` and passed with exit 0.

### 2. `scripts/check-lab`

Command:

```sh
scripts/check-lab
rc=$?
printf '
EXIT_STATUS=%s
' "$rc"
exit "$rc"
```

Status: PASS

Evidence snippet:

```text
Lab root: /Users/liuchengxu/Desktop/codex-agent-lab
Agents: 8
Skills: 42
Codex CLI: /Users/liuchengxu/.nvm/versions/node/v24.18.0/bin/codex
OK: lab structure is valid

EXIT_STATUS=0
```

### 3. `scripts/workflow-mode omx-long-horizon`

Command:

```sh
scripts/workflow-mode omx-long-horizon
rc=$?
printf '
EXIT_STATUS=%s
' "$rc"
exit "$rc"
```

Status: PASS

Evidence snippet:

```text
mode: omx-long-horizon
surface: Terminal/API-relay
omx_level: CLI runtime
entry: omx-api or ./scripts/start-api-relay
artifacts: workspace brief, progress file, validation evidence, handoff notes
verification: scripts/check-lab; task tests; waterflow scan/verify when applicable
stop: checkpoints complete, evidence recorded, handoff ready

EXIT_STATUS=0
```

## Read-Only Inspection Evidence

Files inspected for local proof context:

- `workspaces/20260629_204008-omx-execution-proof/AGENTS.md`
- `workspaces/20260629_204008-omx-execution-proof/brief.md`
- `workspaces/20260629_204008-omx-execution-proof/progress.md`
- `docs/agent-lab-mission.md`
- `docs/workflow-modes.md`
- `scripts/check-workflow-modes`
- `scripts/workflow-mode`
- `scripts/check-lab`

Key local contract evidence:

- `docs/workflow-modes.md` defines `omx-long-horizon` as CLI runtime with entry `omx-api` or `./scripts/start-api-relay`.
- `scripts/workflow-mode omx-long-horizon` emits the same contract in a checkable format.
- `scripts/check-workflow-modes` validates the documented mode index, per-mode script output, and Layer 2 registry section.
- `scripts/check-lab` validates lab structure and invokes both project-rule and workflow-mode checks.

## Boundary / Operator Incidents

### zsh wrapper variable

A first attempt to append an exit code used `status=$?` under zsh. zsh treats `status` as read-only, so the wrapper failed after `scripts/check-workflow-modes` printed success. The check was rerun with `rc=$?` and passed.

Observed snippet:

```text
OK: workflow modes are valid
zsh:2: read-only variable: status
```

### accidental `omx-api` invocation from unquoted here-doc

A later artifact-writing command used an unquoted here-doc containing Markdown backticks. zsh evaluated the backtick content as command substitution. This accidentally invoked `omx-api` from text that mentioned `omx-api exec`, then failed because no prompt/TTY was available.

Observed snippet:

```text
● OMX ACTIVE cli-omx-runtime lane=api-relay cwd=/Users/liuchengxu/Desktop/codex-agent-lab args=exec
Reading prompt from stdin...
No prompt provided via stdin.
[omx] codex exited with code 1
ERROR: TERM is set to "dumb". Refusing to start the interactive TUI because no terminal is available for a confirmation prompt (stdin/stderr is not a TTY).
```

This incident demonstrates that the wrapper can emit the green-light signal, but it is not a successful CLI runtime proof and may have produced the wrapper's normal lane-guard side effect outside the workspace. No task artifact was delegated to that failed runtime.

## Validation Gap

The current host surface was Codex App outside tmux. This run produced the required artifacts under the App-safe OMX spine and validated the `omx-long-horizon` CLI-runtime contract, but it did not prove that an attached CLI OMX runtime independently generated the artifacts.

## Result

PASS for bounded artifact production and local workflow-mode/lab validation.

PARTIAL for the stricter brief objective of a real attached CLI OMX runtime proof.
