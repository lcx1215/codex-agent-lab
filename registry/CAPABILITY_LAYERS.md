# Codex Capability Layers

Last updated: 2026-06-30 20:30 +0800

This file keeps upper-layer expansion separate from the global Codex base. Promote patterns upward only when they have repeated value and clear verification.

## Mission Anchor

`docs/agent-lab-mission.md` is the quality bar for this lab. Capability expansion should make the environment richer by adding documented, bounded, verifiable surfaces, not by accumulating unreviewed tools or implicit conventions.

The lab is scenario-neutral. UCP, support-oriented, research, code-maintenance, workflow, evaluation, and future agent families should enter as workspaces first. Shared capabilities should be promoted only when they amplify Codex/Claude work across more than one scenario.

Equivalent-effect simplicity is part of the quality bar. Before adding or promoting a capability, check whether the same outcome can be achieved by an existing rule, script, skill, workspace note, or on-demand check. Prefer the smaller surface unless the larger one proves better safety, speed, isolation, or verification.

`docs/environment-layering.md` is the placement contract for scale. Root lab
surfaces are maximum-environment assets; scenario folders under `workspaces/`
are medium environments; concrete agent packages inside them are small
environments. Skills, plugins, protocols, interfaces, and Waterflow surfaces must
live at the narrowest level that matches their reuse scope.

`docs/rule-inheritance.md` is the rule-chain contract for nested work. Local
workspace and package rules can add detail or narrow scope, but they cannot
weaken parent safety, lane, sandbox, collaboration, or promotion rules.

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
- Scenario boundary and Codex/Claude amplification declarations for scenario workspaces.

Implementation in this lab:

- `AGENTS.md` now names project-level rule expansion as the first upper-layer capability.
- `docs/project-rule-template.md` provides the reusable project-local rule template.
- `docs/scenario-workspace-contract.md` defines how arbitrary future agent scenarios stay local while amplifying Codex/Claude capability.
- `docs/rule-inheritance.md` defines the effective rule chain from root lab to workspace to small agent package.
- `scripts/new-workspace` creates a local `AGENTS.md`, `CLAUDE.md`, and `agents/README.md` for new workspaces.
- `scripts/check-rule-ladder` is the metadata-only hard gate for missing root/workspace/package/subagent rule links.
- `scripts/check-agent-packages` is the metadata-only hard gate for `agents/` and `subagents/` catalog registry, concrete manifest, entrypoint, and id/path continuity.
- `scripts/audit-agent-code` is the code-content auditor for an agent package: where rule-ladder/agent-packages prove a package is wired and registered, this reads the runtime source for anti-patterns (fail-open auth, empty-secret verifier calls, injection sinks, unbounded body reads, missing tests). Fail-level findings exit non-zero; see `docs/agent-code-auditor.md`. Read-only across lanes — findings on another lane's package are reported via handoff, not edits.
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

Status: active

Purpose: convert repeated project workflows into explicit skills or prompts only after the workflow mode is stable.

Required surfaces:

- Trigger criteria.
- Inputs and expected outputs.
- Boundary and safety notes.
- Verification command or evidence requirement.
- Example handoff or usage note.
- Leanness check showing why an existing skill, prompt, or script is insufficient.

Implementation in this lab:

- `secret-boundary-auditor` protects secret, auth, token, and local path boundaries.
- `async-race-detector` protects concurrent checks, temp paths, hidden stderr, timeouts, and cleanup.
- `tmux-omx-runtime-doctor` captures staged diagnosis for OMX team/tmux worker failures.
- `sandbox-artifact-hygiene` classifies generated outputs, logs, workspaces, and proof artifacts before commit.
- `scripts/check-sandbox-skills` validates the sandbox skill pack and is invoked by `scripts/check-lab`.

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
- `scripts/check-runtime-compatibility` verifies required local commands, Python capabilities, script hygiene, runtime ignore rules, clean-home auth absence, and compatibility documentation wiring.
- `scripts/check-workspace-safety` verifies workspace-level hard safety boundaries while reporting active in-progress scaffolding gaps as warnings instead of blocking another agent mid-creation. It is an explicit workspace/promotion boundary gate, not a root default fast-path sweep.
- `scripts/check-async-execution` verifies independent checks can run concurrently with isolated temp and output directories.
- `scripts/check-secrets` uses lab-local `.tmp/` scratch space and redacts token contents from output.
- `scripts/check-speed-contract` verifies Waterflow supervision stays non-blocking by default and that default lab gates do not invoke heavy Waterflow, stress, incident, broad unit, or async fan-out checks.
- `scripts/benchmark-ide-loop` records repeatable RED/GREEN, health-gate, Waterflow, and optional OMX model-smoke timings under `outputs/shared/benchmarks/ide-loop/`.
- `scripts/lab-dashboard` renders the latest benchmark, Waterflow, async, and git state into one compact Markdown and JSON dashboard.
- `scripts/check-lab` runs root fast-path gates together while avoiding workspace-wide sweeps that can slow or disturb active Codex/Claude workspace work.
- `docs/sandbox-boundaries.md` records the local sandbox contract.
- `docs/runtime-compatibility.md` records the required checks, warning checks, runtime state rules, and error-reduction contract for environment drift.
- `docs/workspace-safety-contract.md` records hard workspace failures, warning-only in-progress states, runtime-state policy, and the new workspace template contract.
- `docs/waterflow-speed-contract.md` records the fast path, boundary path, stress path, and blocking rules that protect Codex and Claude worker speed.

Promotion gate:

- The gate is scriptable, non-secret, and has clear pass/warn/fail output.

## Layer 6: Codex-Claude Collaboration

Status: active (capabilities available, runtime proof pending)

Purpose: give the Claude/OMC lane and the Codex/OMX lane a durable, auditable way to collaborate inside one lab without crossing isolation boundaries or copying secrets between lanes.

Required surfaces:

- A lane-local operating contract for each lane (`AGENTS.md` for Codex, `CLAUDE.md` for Claude).
- A shared protocol that defines roles, lane boundaries, handoff format, and a proof bar.
- A durable assignments ledger and a dated handoffs directory.
- A scriptable health gate.

Implementation in this lab:

- `CLAUDE.md` records the Claude/OMC lane-local boundaries, lane identity, and collaboration routing.
- `docs/codex-claude-collaboration-protocol.md` defines leader/worker/reviewer roles, lane boundaries, the handoff file format, the assignments ledger shape, and the proof bar.
- `registry/collaboration/assignments.json` is the durable assignments ledger (schema `codex-claude-collaboration-assignments/v1`).
- `registry/collaboration/handoffs/` holds dated English handoff notes between lanes.
- `scripts/check-collaboration` validates the protocol doc, ledger JSON shape, handoff naming and sections, and the `CLAUDE.md` collaboration surfaces. It is portable across lanes (uses ripgrep when present, else `grep -E`).

Honest status:

- Collaboration commands are installed (`omc ask`, `omc team`, `omc interop`; Codex `omx-api exec`/`team`).
- Real interop is not proven yet: the earlier OMC team run is `blocked` (`worker_start_submit_unverified`), `.omc/state/interop` does not exist, and a real tmux proof must be run from a terminal.

Promotion gate:

- A collaboration capability is promoted to `proven` only when a real runtime artifact exists under `outputs/shared/` and the assignment entry records it. Installed-but-unproven capabilities stay `pending`/`blocked` with the failure reason.

## Layer 7: Domain-Neutral Agent Kernel

Status: active

Purpose: give every large-agent family a shared, scenario-neutral behavior core so the lab can develop *any* large agent, not re-implement safety guards per domain. This is the promoted form of the agent-behavior primitives that first lived inside a single scenario contract.

Required surfaces:

- A neutral type layer with no product-domain vocabulary.
- A library of composable, configurable decision/safety policies.
- An ordered decision engine with an auditable trace and a fallback.
- A neutral eval harness that runs against any family.
- Cross-domain proof that more than one unrelated family composes the same primitives.

Implementation in this lab:

- `lab_agents/agent_kernel/core.py` defines neutral `Principal`, `ContextItem`, `Tool`, `ToolCall`, `Turn`, `Decision`, `PolicyContext`, and the shared risk ladder.
- `lab_agents/agent_kernel/policies.py` provides the primitive factories (input-size limit, sensitive-data refusal, forbidden action, cross-scope signal, foreign-subject reference, value threshold, permissioned tool call, untrusted-instruction signal, grounded answer, insufficient-evidence fallback).
- `lab_agents/agent_kernel/engine.py` runs the ordered policy chain (first terminating policy wins; advisory annotations fold into the audit trail; `decide_with_trace` exposes evaluation order).
- `lab_agents/agent_kernel/eval_harness.py` is the neutral JSONL batch eval runner + disposition matrix for any `decide(turn) -> Decision` callable.
- `tests/test_kernel_neutrality.py` builds two unrelated agent chains (infra-ops, research) inline on the kernel to prove it is not a single-domain engine; the lab keeps the kernel, not resident example products.
- `docs/agent-behavior-kernel.md` documents the kernel, primitives, family-build pattern, neutrality proof, and boundary.
- Tests: `tests/test_agent_kernel.py` (core + engine + eval harness), `tests/test_kernel_policies.py` (each primitive), `tests/test_kernel_neutrality.py` (two inline domains) — all pure Python, no external-binary dependency.

Leanness:

- A real agent builds its chain inside its own `workspaces/` scenario; the lab does not keep demo families or a family-scaffold script. Neutrality is proven by a test, not by resident example products.

Promotion gate:

- A new primitive enters the kernel only after it shows value in more than one scenario/family, has a neutral signature (no domain vocabulary), and ships with a test. Domain-specific logic stays in a scenario workspace until it meets that bar.
