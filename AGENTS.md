# Codex Agent Lab Rules

This workspace is `/Users/liuchengxu/Desktop/codex-agent-lab`.

## Effective Operating Order

- Safety locks first: company writes, Jenkins, secrets, external environments,
  and user-owned dirty worktrees override speed, autonomy, loops, and harnesses.
- Current goal next: choose the fastest evidence-backed path for the user's
  current request; keep simple work simple.
- Proof surface: use the smallest useful current evidence, harness, fixture,
  eval, or check before claiming a result.
- Loop control: iterate in short cycles: goal, minimal action, evidence check,
  then continue, stop, or escalate.
- Scope ladder: root rules stay scenario-neutral; workspace and package rules
  may only narrow the parent boundary.

## Non-Negotiable Company Write Boundary

- Company repositories, branches, deployment configuration, and TEST/UAT/PROD
  environment state are read-only by default.
- A company write is allowed only when the current conversation names the exact
  repository or system, environment, file or resource, and concrete write action.
- `继续`, `做好`, `修复`, `修改吧`, `加速`, or `部署` are not company-write
  authorization.
- Access is not authorization. Do not use browser sessions, GitLab, Jenkins,
  ArgoCD, Nacos, Kubernetes, APIs, CDP, CI credentials, or service accounts to
  bypass missing authorization.
- Indirect writes are still writes: push, merge, revert, rollback, delete,
  build, sync, publish, restart, Kubernetes apply, Nacos publish, Secret/env
  changes, Jenkins changes, and CI/CD-triggering actions.
- Stop before a company write when scope is missing or ambiguous. Reverting an
  earlier company change is also a write.

## Absolute Jenkins User-Only Boundary

- Jenkins is operated only by the user manually.
- Codex and delegated agents must never open, navigate, click, inspect, query,
  or call Jenkins through browser automation, API, CLI, token, scripts, CDP, or
  any other tool.
- Codex may only analyze Jenkins screenshots, copied logs, or status text
  manually supplied by the user.
- A Git push that is known or reasonably likely to trigger Jenkins is an
  indirect Jenkins operation and remains prohibited while this boundary is
  active.

## Company Context Routing

- Keep root rules company-neutral. Clink-specific branch, TEST, deployment,
  Nacos, route, and incident details live in
  `workspaces/clink-internal-dev-context/`.
- For Clink company deployment or internal environment questions, read
  `workspaces/clink-internal-dev-context/README.md` first.
- Use `.current-agent` and `scripts/check-current-agent` only when the user
  explicitly asks for current Clink Agent context. Do not enter or modify
  internal in-development Agent repos by default.
- Run `scripts/check-clink-safe-path` only when the task explicitly allows
  Clink context inspection; it may inspect company checkout metadata.

## Mission And Quality Bar

- Highest local principle: treat rules as guardrails, not a fixed workflow; choose the fastest evidence-backed path that fits the user's current goal.
- Harness and loop mastery: use harnesses as compact proof surfaces and bounded
  loops as short execution cycles. Keep context small by loading only the current
  goal, relevant files, recent evidence, and the next verification command.
  Default to the fastest useful check; escalate to heavier harnesses only for
  complex, risky, shared, or hard-to-prove work. Stop loops on proof, blockage,
  or approval boundaries, and never let harness or loop results bypass
  company-write, Jenkins, secret, or ownership boundaries.
- Handle clear requests end to end. Ask only when ambiguity affects safety, ownership, or the actual target.
- Keep the Lab scenario-neutral, evidence-backed, and smaller when equivalent
  safety and capability can be preserved.

## Environment Scale Placement

- Stay inside this lab unless the user explicitly names an outside path.
- Do not read, print, copy, rewrite, or migrate secrets, auth files, tokens, cookies, OTPs, API keys, provider config, or account sessions.
- Do not touch `/Users/liuchengxu/.codex`, `/Users/liuchengxu/.codex-api-relay`, Codex app state, LaunchAgents, or plugins unless the user explicitly asks for that exact local Codex cleanup/config task.
- Preserve user changes. Check `git status` before edits and do not revert unrelated dirty files.
- Keep nested workspace rules compatible with `docs/rule-inheritance.md`.
- Medium environments live under `workspaces/`; agent and `subagents/`
  packages stay under their owning workspace.
- Keep workspaces under `workspaces/` by default. If the user names a specific repo/path, follow that target first.
- Use the closest workspace/repo `AGENTS.md` and `README.md` as local context, while keeping this file's safety boundaries.
- When developing agents, prefer current mainstream production agent architectures and implementation patterns, but adapt them to the user's need, the existing codebase, and deployment reality.
- Treat company repositories, deployment configs, and environment settings as read-only unless the user explicitly authorizes the exact file/code/config change.
- Add durable memory only from work that was actually done; use those memories as context, not rigid rules.

## Project-Level Rule Expansion

- Local rules may add detail or narrow scope, but they cannot weaken parent
  safety boundaries.
- Run `scripts/check-rule-ladder` and `scripts/check-agent-packages` after
  changing workspace or package structure.
- Run `scripts/check-workspace-safety` before treating a changed workspace as
  stable.
- Run `scripts/check-task-state` when changing long-running task state.
- Use `docs/waterflow-speed-contract.md` and `scripts/check-speed-contract` to
  keep default proof loops fast and reserve heavy harnesses for boundary cases.
- Prefer `rg`, `apply_patch`, and the smallest useful verification; use a better repo-supported tool when it is clearly more suitable.
- Run `scripts/check-runtime-compatibility` after changing lab runtime scripts or checks when that verification is relevant.
- Registered Lab support agents include `foundation-amplifier`,
  `development-experience-auditor`, and `third-party-large-agent-auditor`; use
  them only when their evidence would help the current task.
- Keep generated artifacts under `.tmp/` or `outputs/`; clean obvious `.DS_Store`, logs, caches, and temp build output when asked.
- User-facing status should be concise Chinese. Report conclusions, not raw logs.
