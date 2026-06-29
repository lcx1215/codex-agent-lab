# App-Side Audit

Audited: 2026-06-29 20:50 +0800

## What Actually Ran

The proof task was launched from the App-side leader through:

```sh
OMX_GREEN_LIGHT_NOTIFY=0 /Users/liuchengxu/.local/bin/omx-api exec -C /Users/liuchengxu/Desktop/codex-agent-lab "<bounded proof prompt>"
```

Evidence:

- The terminal output showed `OpenAI Codex v0.142.4`, `provider: custom`, `workdir: /Users/liuchengxu/Desktop/codex-agent-lab`, and a CLI session id.
- The green-light log contains the 2026-06-29 20:41 +0800 `cli-omx-runtime` event for the bounded proof prompt.
- The workspace now contains the required OMX-generated artifacts.

Correction to the OMX-generated self-assessment: this was a real `omx-api exec` CLI run, but it was not an attached tmux/team runtime and did not use OMX team/swarm parallelism.

## Artifact Audit

Required files exist:

- `omx-execution-report.md`
- `validation.md`
- `benefit-matrix.json`
- `progress.md`

Additional App audit file:

- `app-audit.md`

`benefit-matrix.json` is valid JSON and contains all required fields:

- `routing`
- `auditability`
- `runtime_execution`
- `parallelism`
- `handoff_quality`
- `net_value`

## Verification Re-run By App Side

Commands re-run from the lab root:

```sh
scripts/check-workflow-modes
scripts/check-lab
scripts/workflow-mode omx-long-horizon
```

Observed result:

- `scripts/check-workflow-modes`: pass
- `scripts/check-lab`: pass
- `scripts/workflow-mode omx-long-horizon`: printed the CLI runtime contract

## Side Effects

Expected side effect:

- OMX green-light events were appended to `/Users/liuchengxu/.codex/lane-guard/outputs/shared/omx-green-light/events.tsv`.

Unexpected side effects:

- The OMX agent made a shell quoting mistake in a generated here-doc. Markdown backticks were evaluated by zsh and accidentally invoked `omx-api` several times.
- Those accidental invocations failed before doing useful task work. They did emit green-light log entries.
- The OMX agent created `/tmp/benefit-matrix-check.txt` while pretty-printing JSON. App-side audit removed that temp file after confirming it contained only proof JSON.

No evidence found that the OMX run intentionally modified parent lab source, auth files, provider config, plugins, LaunchAgents, or secrets.

## Execution-Layer Value Verdict

Result: **mixed but useful**.

What OMX proved:

- `omx-api exec` can run a bounded task under the API-relay lane.
- It can read local instructions, run checks, recover from a small command-wrapper error, and produce durable artifacts.
- The green-light mechanism made activation visible.
- The artifact set improved auditability and handoff quality.

What OMX did not prove:

- It did not demonstrate team/swarm or parallel multi-agent throughput.
- It did not outperform App-side editing for this small local task.
- It introduced a real shell quoting risk while writing artifacts.

Net judgment:

OMX added execution-layer value for durable CLI execution, artifact discipline, and restartable proof records. It has not yet justified automatic use for small App-sized edits, and it still needs a stricter team/tmux or long-running task proof before we claim parallel execution benefit.
