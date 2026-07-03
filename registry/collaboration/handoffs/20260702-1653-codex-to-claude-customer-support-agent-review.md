# Handoff: Codex -> Claude, customer-support agent review

## Task
Perform an independent read-only review of the current customer-support agent
package and find correctness, security, architecture, context, and test gaps.

## From / To
- From: codex (customer-support package owner / recent implementer)
- To: claude (independent reviewer)

## Context
The active workspace is:

```text
workspaces/agent-dev-workspace
```

The active package is:

```text
workspaces/agent-dev-workspace/agents/customer-support
```

Recent Codex work added and validated:

- package-local Clink docs and `clink-integ-skills` knowledge adapters;
- HTTP/OpenAPI gateway, model gateway, context cards, context audit, event
  store, tracked runs, handoff envelope, and dry-run Clink operator planning;
- remote model support through OpenAI-compatible and Anthropic-compatible
  adapters with local fallback;
- `assistant.llm_context_guarantee.v1`;
- `assistant.identity_scope.v1` for
  `tenant -> merchant/store -> backend login person -> assistant.session.v1`;
- scoped sessions that do not trust caller `session_id` as backend session id;
- event/run read isolation and run idempotency reuse scoped by identity.

Important local facts:

- This package is inside a dirty/untracked workspace. Review the actual files,
  not only `git diff`.
- Do not clean or rewrite unrelated workspace/root dirty state.
- The current phase explicitly excludes database RAG, vector DB, external RAG
  service, full workflow engine, real multi-channel support platform, and
  non-dry-run Clink operator execution.

Useful entry files:

```text
workspaces/agent-dev-workspace/agents/customer-support/AGENTS.md
workspaces/agent-dev-workspace/agents/customer-support/README.md
workspaces/agent-dev-workspace/agents/customer-support/docs/VALIDATION.md
workspaces/agent-dev-workspace/agents/customer-support/docs/contracts/assistant-contract.md
workspaces/agent-dev-workspace/agents/customer-support/docs/contracts/identity-scope-contract.md
workspaces/agent-dev-workspace/agents/customer-support/docs/contracts/runtime-adapters-contract.md
workspaces/agent-dev-workspace/agents/customer-support/config/openapi/assistant.v1.openapi.json
workspaces/agent-dev-workspace/agents/customer-support/services/gateway/src/
workspaces/agent-dev-workspace/agents/customer-support/services/gateway/test/
```

Recent Codex verification claims to re-check, not trust blindly:

```text
cd workspaces/agent-dev-workspace/agents/customer-support/services/gateway
npm test
```

Expected recent result: 100/100 tests pass.

```text
cd workspaces/agent-dev-workspace/agents/customer-support
find services/gateway/src services/gateway/test -name '*.mjs' -print0 | xargs -0 -n1 node --check
node scripts/eval-context-quality.mjs --json
```

Expected recent result: syntax check passes; context eval passes 26/26.

```text
cd /Users/liuchengxu/Desktop/codex-agent-lab
./scripts/audit-agent-code workspaces/agent-dev-workspace/agents/customer-support
./scripts/check-secrets
./scripts/check-agent-packages
./scripts/check-project-rules
```

Expected recent result: all pass. `./scripts/check-workspace-safety` may still
return warn with failed=0 due to existing `.env.example` and old proof-workspace
warnings.

## Request
Review the customer-support package as a senior code reviewer. Prioritize
actionable findings over summary.

Use this review prompt:

```text
You are a Senior Code Reviewer for the customer-support agent package.

Review scope:
- workspaces/agent-dev-workspace/agents/customer-support
- Focus on actual package files, not only git diff, because this workspace has
  untracked package state.

What was built:
- A movable merchant-console customer-support agent package with HTTP/OpenAPI
  contracts, local JSON knowledge, Clink docs and clink-integ-skills knowledge,
  model gateway adapters, context cards, context audit, LLM context guarantee,
  events, tracked runs, handoff envelope, dry-run operator planning, and the new
  identity/session skeleton.

Requirements:
- Keep public callers on HTTP JSON + OpenAPI.
- Keep model providers replaceable.
- Keep knowledge package-local JSON for now; no DB/vector/external RAG in this
  phase.
- Keep identity hierarchy clean:
  tenant -> merchant/store -> backend login person -> assistant.session.v1.
- `assistant.identity_scope.v1` is backend-owned macro isolation context.
- page_context, conversation summaries, context cards, retrieved knowledge,
  context_audit, and LLM context_guarantee are micro answer-quality context and
  must not grant access.
- For scoped identities, caller `session_id` must not become the backend
  assistant session id.
- Events, tracked-run reads, and tracked-run idempotency reuse should not cross
  tenant/merchant/person boundaries.
- LLM provider input should not leak secrets or raw identity ids when a safe
  boundary summary is enough.
- Clink operator planning stays dry-run and must not execute CLI commands,
  register endpoints, write env files, or store secrets by default.

What to check:
1. Security and isolation bugs:
   - fail-open auth or preview paths;
   - client-controlled identity/session fields;
   - cross-tenant/merchant/person event or run leakage;
   - idempotency reuse across identities;
   - secret leakage in logs, prompts, OpenAPI, docs, exports, events, or runs.
2. Context architecture:
   - macro identity scope vs micro answer context separation;
   - LLM context guarantee correctness;
   - prompt injection risk from docs/knowledge/tool results;
   - citations/evidence reliability.
3. API and backward compatibility:
   - OpenAPI matches runtime behavior;
   - additive fields are safe;
   - caller contracts are not Node-internal.
4. Test quality:
   - tests prove behavior, not only snapshots;
   - missing edge cases around malformed token bindings, partial identity
     scopes, legacy unscoped/tenant-only records, queued runs, model fallback,
     and event batch behavior.
5. Product skeleton:
   - whether current rules/docs are open enough for a coworker to package and
     swap model/API providers;
   - whether any macro platform concern is incorrectly implemented as prompt
     text or package-local micro context.

Read-only constraints:
- Do not modify source files.
- Do not touch ~/.codex, ~/.codex-api-relay, ~/.claude, auth files, provider
  config, LaunchAgents, or plugin state.
- Do not print secrets or preview tokens.
- Do not clean unrelated dirty tree state.

Output format:
### Strengths
Specific, evidence-backed strengths.

### Findings
Findings first, ordered by severity.
For each finding include:
- severity: Critical / Important / Minor
- file:line reference
- what is wrong
- why it matters
- suggested fix
- test that would catch it

### Open Questions
Only include questions that block a confident judgment.

### Recommended Next Fix Set
Smallest useful fix order.

### Verification Performed
Commands run and results.

### Verdict
Ready / ready with fixes / not ready, with 1-2 sentence reasoning.
```

## Constraints
- Claude is the reviewer. Do not self-approve Codex work.
- Keep the review read-only unless the user explicitly asks Claude to implement
  fixes in a separate task.
- Do not touch lane auth, provider config, global homes, or secrets.
- Do not infer live production readiness from local demo tests.
- If a finding is based on existing dirty workspace state, say so clearly.

## Expected Artifacts
Write findings to:

```text
outputs/shared/app-inbox/0003-customer-support-agent-review.md
```

Also append a concise `## Claude Review` section to this handoff file, or write
a follow-up handoff if appending is not practical.

## Verification
At minimum, run or explicitly explain why you did not run:

```text
cd workspaces/agent-dev-workspace/agents/customer-support/services/gateway
npm test

cd ..
find services/gateway/src services/gateway/test -name '*.mjs' -print0 | xargs -0 -n1 node --check
node scripts/eval-context-quality.mjs --json

cd /Users/liuchengxu/Desktop/codex-agent-lab
./scripts/audit-agent-code workspaces/agent-dev-workspace/agents/customer-support
./scripts/check-secrets
./scripts/check-agent-packages
```

The review should not be marked complete without concrete file/line references
or an explicit "no findings" statement plus residual risks.
