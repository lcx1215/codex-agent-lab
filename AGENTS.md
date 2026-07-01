# Codex Agent Lab Rules

This file is the project-specific overlay for `/Users/liuchengxu/Desktop/codex-agent-lab`.
Global Codex rules remain in `/Users/liuchengxu/.codex/AGENTS.md`; do not duplicate them here unless this lab needs a narrower local rule.

## Autonomy (Highest Priority)

- Claude (and the agent on duty) completes tasks end-to-end without asking the user for approval. Decide, execute, verify, and report the result; do not pause to request permission to proceed.
- The user has granted standing authorization for autonomous execution in this lab.
- **NEVER end a turn with a yes/no or "want me to…? / 要我…吗?" permission question.** If about to ask "should I / want me to / shall I" — just do it and report. Asking permission is itself a violation. Only genuine *what-the-user-wants* ambiguities are askable, and even then prefer choosing the reasonable option and noting it.
- Report conclusions, not raw transcripts. The user is in the CLI without a GUI — clear presentation is the agent's job; don't dump long logs and make the user assemble the state. Use `mas` for environment status, `duo` for side-by-side collaboration.
- This does NOT relax the safety boundaries below: the `## Isolation` rules (no secrets/auth, no touching `~/.codex` / `~/.codex-api-relay` / provider config / LaunchAgents, stay within the lab root) remain hard limits. Autonomy means "don't ask permission to do the work," not "cross the safety lines."
- When the user's intent is ambiguous, pick the most reasonable interpretation and note it in the result instead of blocking on a question.

## Mission And Quality Bar

- This lab is a strict, long-horizon agent development environment, not a throwaway sandbox.
- This lab is scenario-neutral. UCP, support-oriented, and other future agents belong in workspaces; none of them should redefine the lab's core identity.
- The lab should amplify Codex and Claude with durable state, harnesses, supervision, verification, and handoffs. It should not replace their reasoning, coding, review, or recovery responsibilities with rigid automation.
- Use `docs/agent-lab-mission.md` as the durable mission and capability-quality bar.
- Build the environment richly, but only through layered, documented, verifiable capabilities.
- Prefer the leanest design with equal effect: fewer files, fewer rules, fewer default checks, and fewer always-on processes when safety, speed, isolation, and verification stay equivalent.
- Every promoted capability should have a purpose, boundary, entrypoint, expected artifacts, verification path, failure mode, and promotion gate.
- Prefer durable files, health gates, harnesses, and handoffs over relying on conversation memory.

## Environment Scale Placement

- Use `docs/environment-layering.md` as the placement contract for maximum, medium, and small environments.
- Use `docs/rule-inheritance.md` as the rule-chain contract when starting work from a workspace or a small agent package.
- Maximum environment means this lab root: keep it highly open, scenario-neutral, and shared across arbitrary future agent families.
- Medium environments live under `workspaces/<scenario>/`: they may be independent repos, product workspaces, proofs, or long-horizon projects with narrower local rules.
- Small agent packages live inside a medium environment, usually under `agents/<package>/`, with their own manifests, skills, tools, fixtures, and interfaces.
- All three levels are sandboxed work surfaces. Do not name one medium environment as if it alone were the sandbox.
- Claude enters this same maximum environment through `CLAUDE.md`; Codex enters through this file. Both lanes must share the same placement model from `docs/environment-layering.md`.
- Cross-lane work follows `docs/codex-claude-collaboration-protocol.md` (roles, handoff format, ledger, proof bar); these four files — this one, `CLAUDE.md`, the layering doc, and the collaboration protocol — form the unified development-environment protocol.
- `registry/tasks/tasks.json` and `registry/runs/*/record.json` extend the workbench with task state and execution evidence, but they do not replace `registry/collaboration/assignments.json`, handoffs, reviewer duties, or proof-bar requirements.
- Place skills, plugins, protocols, interfaces, and Waterflow artifacts at the narrowest level that still has the right reuse scope.
- Local workspace or package rules can only add detail or narrow scope; they must not weaken the root lab's safety, lane, sandbox, collaboration, or promotion rules.
- Promote upward only after repeated cross-scenario value and fresh validation; do not let one scenario redefine the maximum environment.

## Isolation

- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab`.
- Do not write outside this lab unless the user explicitly asks for that specific outside path.
- Do not read, print, copy, rewrite, or migrate secrets, `auth.json`, account tokens, cookies, OTPs, or API keys.
- Do not change `/Users/liuchengxu/.codex`, `/Users/liuchengxu/.codex-api-relay`, Codex app auth, provider config, LaunchAgents, or plugins from this lab unless the user explicitly asks.
- Use `docs/sandbox-boundaries.md` as the local sandbox contract and run `scripts/check-sandbox` after changing clean-home config, symlinks, temp-file behavior, or workspace boundaries.
- Keep outputs under `outputs/`:
  - `outputs/clean-home/` for the lab's isolated `CODEX_HOME`.
  - `outputs/api-relay/` for runs launched through the API relay home.
  - `outputs/app-plus/` only when the App lane explicitly uses this lab.
  - `outputs/shared/` only for handoff artifacts needed by more than one lane.

## Runtime

- Clean isolated runtime: `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home`.
- The clean home's global rules file is a reference to `/Users/liuchengxu/.codex/AGENTS.md`.
- This lab is the long-horizon / multi-agent / automation workspace. Ordinary daily edits can remain in Codex App unless the user routes them here.
- This lab is the CLI/OMX execution area for the unified App / CLI / OMX workflow. App-side agents may hand off complex durable work here through lane-guard notes, while keeping App as the daily driver.
- API-relay editing runtime defaults to OMX through `scripts/start-api-relay`, which invokes `/Users/liuchengxu/.local/bin/omx-api`.
- Use `scripts/start-api-relay-plain` only for explicit non-OMX fallback, diagnostics, or when the user asks for plain Codex.
- Project agents live in `.codex/agents/`.
- Project skills live in `.agents/skills/`.
- Environment-specific skills should be placed in `.agents/skills/`; general reusable skills can remain in global Codex homes or plugin caches.
- Sandbox-specific skills currently include `secret-boundary-auditor`, `async-race-detector`, `tmux-omx-runtime-doctor`, and `sandbox-artifact-hygiene`.
- Existing global plugins may be used normally when available, but plugin install/enable/disable state must not be changed from this lab unless explicitly requested.
- The lab config uses `workspace-write` with this lab as the writable root. Treat any request to weaken sandboxing or write elsewhere as a lane-affecting action.
- The lab config excludes system tmp directories; scripts and tests should use `.tmp/` for local temporary files.
- Run `scripts/check-async-execution` after changing async behavior, validation runners, temp-file handling, or long-horizon execution scripts.
- Run `scripts/check-runtime-compatibility` after changing script requirements, PATH assumptions, runtime ignore rules, clean-home compatibility, dashboard health inputs, or cross-lane startup commands.
- Run `scripts/check-workspace-safety` after adding or changing workspaces, workspace templates, workspace runtime directories, workspace-local symlinks, or large-agent task scaffolds.
- Run `scripts/check-sandbox-skills` after adding or changing sandbox-specific skills.
- Keep `agents.max_depth = 1`; child agents should not recursively fan out.

## Long-Horizon Work Contract

- Start by creating or updating `registry/current-progress.md`.
- For a new project or task, create a dedicated folder under `workspaces/`.
- New workspace folders should include a local `AGENTS.md` derived from `docs/project-rule-template.md` when the work may span sessions, agents, or lanes.
- Treat scenario workspaces as examples until their patterns are proven reusable; do not promote UCP, commercial support, or any single domain into root lab policy without broad value evidence.
- Use `docs/scenario-workspace-contract.md` for scenario boundaries and Codex/Claude amplification declarations.
- Use `docs/workspace-safety-contract.md` to distinguish hard workspace safety failures from temporary in-progress scaffold warnings.
- Use file handoffs instead of pasting large context into messages.
- When dispatching agents, name the exact custom agent and give it a narrow task.
- Do not dispatch unbounded "all agents" work. Use a small set with clear owners.
- Verify before completion and write evidence to `registry/VALIDATION.md` or a task-specific validation file.

## Project-Level Rule Expansion

- Treat this lab as the template factory for upper-layer Codex capability, not as a place to keep expanding global rules.
- Important projects should carry their own local operating surface:
  - `AGENTS.md` for project-specific boundaries, routing, runtime, and verification.
  - `README.md` or `brief.md` for the human goal and start commands.
  - `progress.md` or `registry/current-progress.md` for durable state.
  - `VALIDATION.md` or task-specific validation notes for completion evidence.
- Use `docs/project-rule-template.md` as the starting point for project-local rules.
- Use `docs/environment-layering.md` before deciding whether a new skill, protocol, interface, or Waterflow surface belongs in the lab root, a workspace, or an agent package.
- Use `docs/rule-inheritance.md` to keep nested `AGENTS.md`, `CLAUDE.md`, package README files, and manifests aligned with parent rules.
- Track capability-layer decisions in `registry/CAPABILITY_LAYERS.md` before promoting a pattern into scripts, skills, or global rules.
- Do not promote a helper, skill, workflow, or gate when an existing surface can provide the same effect with clear documentation and validation.
- Run `scripts/check-project-rules` after adding or changing project-level rule surfaces.

## Workflow Modes

- Use `docs/workflow-modes.md` as the local catalog for App / CLI / OMX work modes.
- Use `scripts/workflow-mode list` to list modes and `scripts/workflow-mode <mode>` to print the entry command, artifacts, verification path, stop condition, and OMX level.
- Run `scripts/check-workflow-modes` after changing workflow mode docs or scripts.
- Keep modes as routing contracts, not rigid ceremonies. Simple work stays simple; OMX is activated only when the mode or task complexity warrants it.

## Reasoning Speed

- Use `docs/reasoning-speed-playbook.md` to reduce avoidable `gpt-5.5` + `xhigh` latency.
- Use `docs/waterflow-speed-contract.md` to keep Waterflow supervision advisory, incremental, and non-blocking during ordinary Codex and Claude work.
- Keep xhigh for high-risk architecture, security, root-cause debugging, and final integration decisions.
- Move file lookup, scans, shell checks, changed-only validation, and independent evidence collection onto faster or parallel lanes when safe.
- Do not put stress fixtures, incident fixtures, full Waterflow verification, broad unit discovery, or async fan-out into the default edit loop.
- Run `scripts/check-speed-contract` after changing Waterflow supervision, speed routing, async execution, or default health gates.
- Use `scripts/benchmark-ide-loop` for measured RED/GREEN, gate, Waterflow, and OMX model-smoke timing; use `scripts/lab-dashboard` to summarize current health from artifacts.
- Use `docs/runtime-compatibility.md` and `scripts/check-runtime-compatibility` to separate environment drift from agent implementation bugs before long work starts.
- Use `scripts/check-rule-ladder` when adding, moving, or entering nested workspaces, agent packages, or subagent units; a missing parent-rule link is a hard failure.
- Use `scripts/check-agent-packages` when creating, moving, renaming, or splitting `agents/` or `subagents/` catalogs; an unregistered or mismatched agent manifest is a hard failure.
- Use `docs/task-state-scheduler.md` and `scripts/check-task-state` for root-layer long-horizon task state, dependency validity, stale running leases, and next runnable task visibility.
- Use `scripts/check-workspace-safety` after workspace changes, before promoting any workspace output into root lab patterns, or before treating a large-agent workspace as stable. It is an explicit boundary gate, not a root default fast-path sweep.

## Agent Roles

- `long-horizon-orchestrator`: breaks work into phases, coordinates agents, maintains durable progress.
- `context-architect`: builds context maps and task briefs without implementing.
- `research-scout`: gathers current source-backed evidence and writes compact research packets.
- `implementation-worker`: performs scoped edits from a brief and reports tests.
- `verification-auditor`: verifies behavior, tests, and artifacts.
- `risk-reviewer`: reviews correctness, security, regressions, and missing tests.
- `handoff-summarizer`: writes compact restart and compaction handoffs.
- `waterflow-auditor`: scans lab workflow paths and emits repair briefs for coordination defects.
- `foundation-amplifier`: strengthens the lab foundation by routing large agent work, defining Codex/Claude amplification plans, and backtesting whether environment capabilities improved.
- `development-experience-auditor`: scores Codex/Claude lab comfort across context, runtime, verification, handoff, and safety signals.
- `third-party-large-agent-auditor`: audits large-agent readiness from an external-review posture across intake, context, architecture, runtime, delegation, tooling, verification, observability, safety, handoff, performance, and model-proof signals.
- `secret-boundary-auditor`: audits secret, auth, token, and local-path leakage in sandbox artifacts.
- `async-race-detector`: diagnoses concurrent check, worker, temp, stderr, timeout, and cleanup races.
- `tmux-omx-runtime-doctor`: diagnoses OMX team, tmux pane, startup script, and worker runtime failures.
- `sandbox-artifact-hygiene`: classifies generated outputs, logs, workspaces, and proof artifacts before commit.

## Reporting

- Prefer concise Chinese user-facing status.
- Keep artifacts in English unless the user asks otherwise.
- When a result is inferred from old notes, say it may be stale.
