# Codex Capability Layers

Last updated: 2026-06-29 20:52 +0800

This file keeps upper-layer expansion separate from the global Codex base. Promote patterns upward only when they have repeated value and clear verification.

## Mission Anchor

`docs/agent-lab-mission.md` is the quality bar for this lab. Capability expansion should make the environment richer by adding documented, bounded, verifiable surfaces, not by accumulating unreviewed tools or implicit conventions.

## Layer 0: Clean Base

Status: complete

- App/default lane and Terminal/API-relay lane are separated.
- Non-secret context sync is wired.
- OMX green-light signaling is wired.
- `codex-architecture-doctor` is the machine-level health gate.

## Layer 1: Project-Level Rules

Status: active

Purpose: every important project gets a local operating contract instead of relying on global rules alone.

Required surfaces:

- Local `AGENTS.md` with project boundaries, lane routing, OMX usage, and verification rules.
- A human start surface: `README.md`, `brief.md`, or equivalent.
- Durable progress: `progress.md`, `registry/current-progress.md`, or equivalent.
- Validation evidence: `VALIDATION.md`, `registry/VALIDATION.md`, or task-specific validation notes.

Implementation in this lab:

- `AGENTS.md` now names project-level rule expansion as the first upper-layer capability.
- `docs/project-rule-template.md` provides the reusable project-local rule template.
- `scripts/new-workspace` creates a local `AGENTS.md` for new workspaces.
- `scripts/check-project-rules` verifies the rule surfaces exist.

## Layer 2: Workflow Modes

Status: active

Purpose: make recurring App / CLI / OMX usage patterns explicit, checkable, and easy to invoke.

Modes:

- Daily App development.
- CLI quick diagnosis.
- OMX long-horizon execution.
- Multi-agent review or refactor.
- Overnight checkpointed work.

Implementation in this lab:

- `docs/workflow-modes.md` defines entry command, expected artifacts, verification path, stop condition, and OMX level for each mode.
- `scripts/workflow-mode` prints mode contracts from the terminal.
- `scripts/check-workflow-modes` verifies the catalog and script stay aligned.
- `registry/OMX_RETROSPECTIVE.md` records the initial evidence-based judgment: OMX helped with routing, auditability, runtime confidence, continuity, and verification discipline, but has not yet proven multi-agent throughput value.

Promotion gate:

- A mode can become a skill after successful repeated use with clear artifacts and validation.

## Layer 3: Skill And Prompt Packs

Status: planned

Purpose: convert repeated project workflows into explicit skills or prompts only after the workflow mode is stable.

Required surfaces:

- Trigger criteria.
- Inputs and expected outputs.
- Boundary and safety notes.
- Verification command or evidence requirement.
- Example handoff or usage note.

Promotion gate:

- The workflow has been used successfully more than once.
- The skill has clear trigger criteria, inputs, outputs, and validation.

## Layer 4: Long-Horizon Automation

Status: planned

Purpose: run durable, restartable OMX work with checkpoints, workspaces, and validation.

Required surfaces:

- Dedicated workspace.
- Local rules file.
- Progress file.
- Validation file.
- Handoff file.
- Stop and resume conditions.

Promotion gate:

- Work has a workspace, local rules, progress file, verification file, and handoff file.

## Layer 5: Health Gates

Status: active

Purpose: make architecture, project rules, secrets, and validation checks runnable before and after major work.

Required surfaces:

- Scriptable gate.
- Clear pass, warn, and fail output.
- Redacted logs for secret-related checks.
- Path or route scope so failures are actionable.
- Recorded evidence in validation notes when the gate protects a promoted capability.

Implementation in this lab:

- `scripts/check-sandbox` verifies clean-home sandbox config, writable roots, tmp exclusion, secret-like files, symlink escape boundaries, script portability, and directory permissions.
- `scripts/check-async-execution` verifies independent checks can run concurrently with isolated temp and output directories.
- `scripts/check-secrets` uses lab-local `.tmp/` scratch space and redacts token contents from output.
- `scripts/check-lab` runs project-rule, workflow-mode, and sandbox gates together.
- `docs/sandbox-boundaries.md` records the local sandbox contract.

Promotion gate:

- The gate is scriptable, non-secret, and has clear pass/warn/fail output.
