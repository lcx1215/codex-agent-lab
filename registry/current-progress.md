# Current Lab Progress

Last updated: 2026-07-21 00:00 +0800

## Current Objective

Keep `codex-agent-lab` as a thin, scenario-neutral governance and collaboration
layer for Codex and Claude agent work.

Root layer contains:

- hard safety boundaries;
- placement and rule-inheritance contracts;
- fast health gates;
- compact harness/loop discipline;
- pointers to scenario workspaces and evidence stores.

Root layer does not carry project history, company deployment detail, retired
runtime experiments, or release logs. Those belong in workspaces, docs, outputs,
validation records, or archives.

## Active Operating Shape

- Default work surface: Codex App.
- Terminal surface: `codex-api` through `scripts/start-api-relay` when useful.
- Default proof loop: smallest relevant file read, minimal action, targeted
  check, then continue/stop/escalate.
- Heavy harnesses are boundary tools, not per-edit tools.
- `scripts/check-lab` is the root fast health gate.

## Scenario Pointers

- Clink company context:
  `workspaces/clink-internal-dev-context/README.md`.
- Current Clink Agent pointer exists for explicit Clink tasks only:
  `.current-agent` and `scripts/check-current-agent`.
- Internal in-development Agent repositories are not default Lab context.

## Current Verification Baseline

Latest slim-runtime cleanup verification is recorded in `registry/VALIDATION.md`
under `Lightweight Runtime, Harness, And Loop Cleanup`.

Known current outcomes:

- `python3 -m unittest discover -s tests` passed with 162 tests.
- `./scripts/check-lab` passed.
- `./scripts/check-secrets` passed.
- `./scripts/check-runtime-compatibility` passed.
- `./scripts/check-rule-ladder` passed.
- `./scripts/check-agent-packages` passed.
- `./scripts/check-workspace-safety` reported warnings only, failed 0.

## History

Detailed historical progress before the root-layer slimming is archived at:

`registry/archive/current-progress-20260721-pre-slim.md`
