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

- This boundary overrides speed, autonomy, end-to-end completion, inferred intent, and any internal task summary.
- Treat all company repositories, branches, deployment configuration, and TEST/UAT/PROD environment state as strictly read-only by default.
- A company write is allowed only when the user explicitly authorizes the exact repository or system, environment, file or resource, and concrete write action in the current conversation.
- General instructions such as `继续`, `做好`, `修复`, `修改吧`, `加速`, or `部署` are not company-write authorization.
- Access is not authorization. Existing browser sessions, Jenkins credentials, GitLab permissions, ArgoCD access, Nacos access, Kubernetes access, APIs, CDP, or another service account must never be used to route around a missing permission or missing explicit authorization.
- Indirect writes are still writes. This includes changing Jenkins jobs, triggering builds that edit configuration, pushing through CI, ArgoCD refresh/sync/rollback, Nacos publish, Kubernetes apply/restart, environment-variable or Secret references, Git push, merge, revert, delete, and rollback.
- If the user says to stop or says that company configuration must not be changed, perform read-only inspection only. Do not revert an earlier change because reverting is also a write.
- When authorization scope is missing or ambiguous, stop before the write and ask for the exact target and action. Never infer authorization from urgency or from a previous authorization for a different file or system.

## Absolute Jenkins User-Only Boundary

- Jenkins is operated only by the user manually. Codex and delegated agents must never open, navigate, click, inspect, query, or call Jenkins through browser automation, API, CLI, token, scripts, CDP, or any other tool.
- Prohibited Jenkins actions include read-only job/status/log inspection, Build, Rebuild, Replay, Configure, Workspace operations, credential use, and downstream-job operations.
- Codex may only analyze Jenkins screenshots, copied logs, or status text manually supplied by the user.
- Treat a Git push that is known or reasonably likely to trigger Jenkins as an indirect Jenkins operation. It remains prohibited while this boundary is active.
- Only an explicit user instruction changing this Jenkins user-only boundary can change it. Authorization for another repository, file, environment, or action does not override it.

## Clink Company Development Flow

- Follow the company [Git branch management specification](https://clinkpay.feishu.cn/wiki/P9Fywqc5Ti4iuLkrRxIc29xOncd?chunked=false) for Clink repository work.
- Do not develop directly on `test`. Start each requirement or fix from the latest `main` and create a dedicated feature branch.
- Before treating `test` as a valid promotion target, verify that `origin/main` and `origin/test` have a common ancestor and that the feature work descends from the intended `main` baseline. If the branches have no merge base, stop and report a branch-lineage incident instead of continuing TEST deployment iterations.
- Develop and integrate locally or in the approved `137` environment. Make meaningful staged commits so the development history remains reviewable.
- To verify in TEST, first update the local `test` branch from `origin/test`, then merge the feature branch into `test` with a normal Git merge.
- A linear `test` history alone does not prove that the feature-branch flow was followed. Report missing or ambiguous merge provenance honestly; do not claim a compliant merge without evidence.
- Do not use cherry-pick for TEST promotion because it creates replacement commits and loses the feature-to-TEST merge relationship.
- Do not rebase the feature branch onto `test` because unrelated TEST changes would enter the feature branch and contaminate the later merge to `main`.
- Keep branch and environment contracts aligned: TEST uses `test` and `ENV_NAME=test`, UAT uses `uat`, and production uses `main` with the production environment. Reject deployment instructions, manifests, or startup arguments that cross these boundaries.
- A push to `test` automatically triggers company CI/CD and deploys the TEST environment. Treat that push as both a repository write and an environment-changing deployment action.
- A green CI result counts as a quality gate only when the required unit tests actually ran and the build runtime satisfies the repository's declared engine version. Skipped tests, `EBADENGINE`, or an incompatible Node version mean the gate did not pass even if the pipeline is green.
- Complete validation in the TEST environment before opening the GitLab merge request for `main`.
- After review is complete, notify the assigned owner; the authorized assignee performs the merge.
- Production may deploy only code from `main`.
- This workflow describes the required company process; it does not grant Codex permission to create branches, commit, merge, push, trigger CI/CD, or operate Jenkins. The company write lock and Jenkins user-only boundary still apply.

## Clink Test Configuration Boundary

- Treat the company TEST deployment configuration as an external, centrally managed platform contract. Agent repositories may declare required environment-variable names and service contracts, but must not carry, recreate, or guess the live Nacos configuration, database DDL, route publication, credentials, or environment state.
- The current TEST gateway route configuration belongs to the centrally managed Nacos DataId `clink-gateway.yml`. Do not invent or substitute another DataId such as `clink-gateway-path-mapping.yml` without current company evidence.
- Company deployment documents can contain passwords, signing keys, database addresses, private URLs, tokens, and other sensitive values. Never copy raw values from those documents into source code, repository documentation, test fixtures, logs, summaries, chat responses, memories, or Agent Lab rules. Record only redacted configuration names and behavioral contracts.
- Do not infer Nacos server addresses, namespace IDs, groups, credentials, Pod IPs, route filters, or security settings from naming conventions or older repositories. Require current environment evidence or an authorized operator handoff.
- Keep the service boundary explicit: the Agent may self-register its own runtime instance when that design is authorized, while the gateway route, platform Service, NetworkPolicy, Secrets, and centralized Nacos configuration remain owned by authorized operations systems.
- A local configuration example must use placeholders and must not be presented as proof of TEST configuration. Local tests, Docker builds, and static route checks do not prove that the current TEST Nacos record, gateway route, network policy, or credentials exist.

## Clink Incident Prevention

- Never use Jenkins, CI credentials, or authenticated company tools as a debugger or as a substitute channel when direct repository permission is missing.
- Track repository state, build, image publication, deployment, ArgoCD state, Pod readiness, Nacos registration, gateway routing, and browser acceptance as separate evidence layers. Stop at the first failed layer.
- Never report Pod readiness as proof that Nacos discovery or gateway routing works. Those layers require their own current evidence.
- A failed pipeline does not prove an image failed to build. Identify the exact failed stage before proposing any repeat operation.
- Do not rebuild, redeploy, or push another fix unless the proven failure cause changed. Local test success alone does not prove a TEST/UAT/PROD runtime root cause.
- A manual no-change rebuild or redeploy is not acceptance evidence and should not be proposed as a diagnostic step.
- Automatic deployment from an authorized `test` push is the expected company flow. Do not describe it as global Jenkins, ArgoCD, or cross-service pollution without direct evidence of those wider effects.
- Preserve dirty worktrees and unsaved editor buffers. Never overwrite, clean, revert, rollback, or resync as an unapproved recovery shortcut.

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
- For Clink company deployment or internal environment questions, use `workspaces/clink-internal-dev-context/README.md` as the fast context entry when it helps.
- Use `.current-agent` and `scripts/check-current-agent` as the fast default pointer for Agent work; if the user names a specific repo/path, follow that path first.
- Run `scripts/check-clink-safe-path` after changing Clink repository mappings, company-tool capabilities, or company-write rules.

## Project-Level Rule Expansion

- Local rules may add detail or narrow scope, but they cannot weaken parent
  safety boundaries.
- Run `scripts/check-rule-ladder` and `scripts/check-agent-packages` after
  changing workspace or package structure.
- Run `scripts/check-workspace-safety` before treating a changed workspace as
  stable.
- Run `scripts/check-task-state` when changing long-running task state.
- Prefer `rg`, `apply_patch`, and the smallest useful verification; use a better repo-supported tool when it is clearly more suitable.
- Run `scripts/check-runtime-compatibility` after changing lab runtime scripts or checks when that verification is relevant.
- Keep generated artifacts under `.tmp/` or `outputs/`; clean obvious `.DS_Store`, logs, caches, and temp build output when asked.
- User-facing status should be concise Chinese. Report conclusions, not raw logs.
