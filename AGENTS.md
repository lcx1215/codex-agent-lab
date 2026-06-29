# Codex Agent Lab Rules

This file is the project-specific overlay for `/Users/liuchengxu/Desktop/codex-agent-lab`.
Global Codex rules remain in `/Users/liuchengxu/.codex/AGENTS.md`; do not duplicate them here unless this lab needs a narrower local rule.

## Mission And Quality Bar

- This lab is a strict, long-horizon agent development environment, not a throwaway sandbox.
- Use `docs/agent-lab-mission.md` as the durable mission and capability-quality bar.
- Build the environment richly, but only through layered, documented, verifiable capabilities.
- Every promoted capability should have a purpose, boundary, entrypoint, expected artifacts, verification path, failure mode, and promotion gate.
- Prefer durable files, health gates, harnesses, and handoffs over relying on conversation memory.

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
- Existing global plugins may be used normally when available, but plugin install/enable/disable state must not be changed from this lab unless explicitly requested.
- The lab config uses `workspace-write` with this lab as the writable root. Treat any request to weaken sandboxing or write elsewhere as a lane-affecting action.
- The lab config excludes system tmp directories; scripts and tests should use `.tmp/` for local temporary files.
- Run `scripts/check-async-execution` after changing async behavior, validation runners, temp-file handling, or long-horizon execution scripts.
- Keep `agents.max_depth = 1`; child agents should not recursively fan out.

## Long-Horizon Work Contract

- Start by creating or updating `registry/current-progress.md`.
- For a new project or task, create a dedicated folder under `workspaces/`.
- New workspace folders should include a local `AGENTS.md` derived from `docs/project-rule-template.md` when the work may span sessions, agents, or lanes.
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
- Track capability-layer decisions in `registry/CAPABILITY_LAYERS.md` before promoting a pattern into scripts, skills, or global rules.
- Run `scripts/check-project-rules` after adding or changing project-level rule surfaces.

## Workflow Modes

- Use `docs/workflow-modes.md` as the local catalog for App / CLI / OMX work modes.
- Use `scripts/workflow-mode list` to list modes and `scripts/workflow-mode <mode>` to print the entry command, artifacts, verification path, stop condition, and OMX level.
- Run `scripts/check-workflow-modes` after changing workflow mode docs or scripts.
- Keep modes as routing contracts, not rigid ceremonies. Simple work stays simple; OMX is activated only when the mode or task complexity warrants it.

## Reasoning Speed

- Use `docs/reasoning-speed-playbook.md` to reduce avoidable `gpt-5.5` + `xhigh` latency.
- Keep xhigh for high-risk architecture, security, root-cause debugging, and final integration decisions.
- Move file lookup, scans, shell checks, changed-only validation, and independent evidence collection onto faster or parallel lanes when safe.

## Agent Roles

- `long-horizon-orchestrator`: breaks work into phases, coordinates agents, maintains durable progress.
- `context-architect`: builds context maps and task briefs without implementing.
- `research-scout`: gathers current source-backed evidence and writes compact research packets.
- `implementation-worker`: performs scoped edits from a brief and reports tests.
- `verification-auditor`: verifies behavior, tests, and artifacts.
- `risk-reviewer`: reviews correctness, security, regressions, and missing tests.
- `handoff-summarizer`: writes compact restart and compaction handoffs.
- `waterflow-auditor`: scans lab workflow paths and emits repair briefs for coordination defects.

## Reporting

- Prefer concise Chinese user-facing status.
- Keep artifacts in English unless the user asks otherwise.
- When a result is inferred from old notes, say it may be stale.
