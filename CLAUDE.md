# Codex Agent Lab - Claude/OMC Lab-Local Rules

This file is the Claude Code operating overlay for `/Users/liuchengxu/Desktop/codex-agent-lab`.
It is the Claude-lane counterpart to `AGENTS.md` (Codex lane). Both files describe the same lab; this one
records the boundaries, routing, and verification rules that apply when Claude/OMC is the agent on duty.

Global Claude rules live in `/Users/liuchengxu/.claude/CLAUDE.md` and `/Users/liuchengxu/CLAUDE.md`; do not
duplicate them here unless this lab needs a narrower local rule.

## Company Write Boundary (Highest Priority)

- Inherit the machine-wide company write lock from
  `/Users/liuchengxu/.codex/AGENTS.md` and `/Users/liuchengxu/CLAUDE.md`.
- Company repositories, branches, deployment configuration, and TEST/UAT/PROD
  environment state are read-only unless the current conversation explicitly
  authorizes the exact target and concrete write action.
- Existing browser, Jenkins, GitLab, ArgoCD, Nacos, Kubernetes, API, CDP, CI,
  or service-account access is never substitute authorization.
- Build, sync, publish, restart, rollback, revert, delete, merge, push, Secret
  reference, environment-variable, and Jenkins job changes are writes.
- This section overrides autonomy, standing authorization, summaries, memories,
  urgency, and all lower project rules.

## Jenkins User-Only Boundary

- Jenkins is operated only by the user manually. Claude and delegated agents
  must never open, navigate, click, inspect, query, or call Jenkins through a
  browser, API, CLI, token, script, CDP, or automation.
- This includes read-only job/status/log inspection, Build, Rebuild, Replay,
  Configure, Workspace operations, credentials, and downstream jobs.
- Only analyze Jenkins screenshots, copied logs, or status text manually
  supplied by the user.
- A Git push that is known or reasonably likely to trigger Jenkins is an
  indirect Jenkins operation and remains prohibited while this boundary is
  active.
- Only an explicit user instruction changing this Jenkins user-only boundary
  can change it.

## Clink Incident Prevention

- Never use Jenkins, CI credentials, or authenticated company tools as a
  debugger or substitute path when direct repository permission is missing.
- Separate repository, build, image, deployment, ArgoCD, Pod readiness, Nacos,
  gateway, and browser-acceptance evidence. Stop at the first failed layer.
- A red pipeline does not prove image-build failure. Do not repeat a build,
  deployment, or speculative runtime fix unless the proven cause changed.
- Preserve dirty worktrees and unsaved editor buffers. Do not overwrite, clean,
  revert, rollback, or resync as an unapproved recovery shortcut.

## Autonomy

- Claude completes tasks end-to-end without asking the user for approval. Decide, execute, verify, report.
- The user has granted standing authorization for autonomous execution only
  inside lab-owned files and the exact current write boundary.
- **NEVER end a turn with a yes/no or "want me to…? / 要我…吗?" permission question.** Choose the reasonable
  option, do it, and report what was done. Only genuine *what-the-user-wants* ambiguities are askable.
- Report conclusions in concise Chinese, not raw transcripts. Keep artifacts in English unless asked otherwise.
- This does NOT relax the safety boundaries in `## Isolation`. Autonomy means "don't ask permission to do the
  work," not "cross the safety lines."

## Lane Identity

- Claude is one lane; Codex is the other. This lab is the shared ground where they collaborate.
- Claude MAY modify lab-owned Codex-lane work product (code, collaboration artifacts, in-flight files) — standing
  authorization granted 2026-07-08. Company repositories and environments are excluded unless exactly authorized.
  Still gated regardless: Codex auth (`~/.codex`, `~/.codex-api-relay`
  auth.json), provider config, and LIVE running Codex.app / cc-switch processes (verify ownership before
  touching any process). Route cross-lane coordination through `## Collaboration`; scout before overwriting
  Codex's in-flight edits; push/MR to a remote still needs an explicit go.
- OMC runtime state lives in lab-local `.omc/` and is git-ignored except `.omc/skills/**`.
- When Claude and Codex collaborate, route work through the files in `## Collaboration`, not through copied
  conversation context or copied secrets.

## Environment Scale Placement

This is the Claude-lane counterpart to the same section in `AGENTS.md`; both lanes follow one placement contract.

- Use `docs/environment-layering.md` as the authoritative placement contract for maximum, medium, and small
  environments. Consult it before deciding whether a new skill, protocol, interface, kernel, or check belongs in
  the lab root, a workspace, or an agent package.
- Use `docs/rule-inheritance.md` as the rule-chain contract when starting work from a workspace or a small agent
  package. Local rules can only add detail or narrow scope; they must not weaken parent safety, lane, sandbox,
  collaboration, or promotion rules.
- Maximum environment is this lab root: keep it open, scenario-neutral, and shared across arbitrary agent families.
- Medium environments live under `workspaces/<scenario>/`; small agent packages live inside them under
  `agents/<package>/`. Place each surface at the narrowest level that still has the right reuse scope.
- All three levels are sandboxed work surfaces. Do not name one medium environment as if it alone were the
  sandbox.
- Claude enters the same maximum environment Codex uses: read this file, `docs/environment-layering.md`, and
  `docs/codex-claude-collaboration-protocol.md` before changing lab structure.
- Promote upward only after repeated cross-scenario value and fresh validation; one scenario must not redefine the
  maximum environment. This matches the leanness rule in `## Verification` and the lab mission's equivalent-effect bar.

## Isolation (Hard Limits)

- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab`. Do not write outside it unless the user names the
  specific outside path.
- Do not read, print, copy, rewrite, or migrate secret/token/key VALUES, `auth.json`, account tokens,
  cookies, OTPs, or API keys. (Not lifted by the 2026-07-08 Codex-lane grant — this protects the user.)
- Do not change `~/.codex`, `~/.codex-api-relay`, Codex app auth, provider config, LaunchAgents, or plugin
  install state from this lab unless the user explicitly asks. (Auth/provider infrastructure stays gated.)
- Lab-owned Codex-lane work product is editable under the 2026-07-08 standing
  authorization. Company repositories, branches, deployment configuration, and
  environments are not included. They remain read-only unless the exact target
  and concrete action are explicitly authorized in the current conversation.
- Keep generated artifacts under `outputs/`; keep durable state under `registry/`; keep scratch under `.tmp/`.

## Collaboration (Claude <-> Codex)

- Protocol: `docs/codex-claude-collaboration-protocol.md` defines roles, handoff format, and the proof bar.
- Assignments ledger: `registry/collaboration/assignments.json` records who owns what and the current status.
- Handoffs: `registry/collaboration/handoffs/` holds dated, English handoff notes between lanes.
- Task state: `registry/tasks/tasks.json` shows long-horizon task state and next runnable work, but it does not
  replace assignments, handoffs, or review approval.
- Run records: `registry/runs/*/record.json` capture execution evidence, but they do not replace reviewer
  approval or collaboration status changes.
- Cross-lane artifacts that both lanes need go under `outputs/shared/`.
- Health gate: run `scripts/check-collaboration` after changing any collaboration surface.
- A collaboration claim is only "proven" when there is a real runtime artifact, not just an installed capability.

## Verification

- Verify before claiming completion. Default gates: `scripts/check-lab`, `scripts/check-secrets`,
  `scripts/check-collaboration`, and `scripts/lab-dashboard`.
- Run `scripts/check-rule-ladder` when adding, moving, or entering nested workspaces, agent packages, or subagent units; a missing
  parent-rule link is a hard failure.
- Run `scripts/check-agent-packages` when creating, moving, renaming, or splitting `agents/` or `subagents/` catalogs; an
  unregistered or mismatched agent manifest is a hard failure.
- Write completion evidence to `registry/VALIDATION.md` or a task-specific validation note.
- Prefer `executor` for implementation, `code-reviewer`/`verifier` for the approval pass. Never self-approve in
  the same active context.

## Reporting

- Concise Chinese for user-facing status; English for committed artifacts.
- When a result is inferred from old notes, say it may be stale.
- Use file handoffs instead of pasting large context into messages.
