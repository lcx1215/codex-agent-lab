# Handoff: storage layering + reserve (not implement) user long-term memory (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-09 20:15 (+0800)
- Kind: design direction — finalize storage layering; reserve user-memory slot without building it yet

## Task

User is finalizing the storage architecture as DynamoDB adapters land. Decisions to
encode: (1) Turso/libSQL retires; (2) confirm the pragmatic storage layering; (3) user
long-term memory is a FUTURE feature — reserve the architectural slot NOW (so it can be
done right in one shot later) but DO NOT implement it yet, because three prerequisites
are unmet. This handoff records why and what to pre-wire.

## Current state (verified in code)

- No "user long-term memory" feature exists today. All `memory` matches in the gateway
  are in-memory stores, not a per-user long-term memory. Today's stores are only
  `conversations` / `events` / `runs` (+ replay nonce).
- Codex is mid-writing DynamoDB adapters (uncommitted): `dynamodbClient.mjs`,
  `dynamodbRuntimeStore.mjs`, `dynamodbAgentApiBffReplayStore.mjs`. Good — replay uses
  `ConditionExpression: attribute_not_exists(entry_key)` (atomic), runtime keeps
  `scopedIdempotencyKey`. Prior review fixes are preserved.
- Turso currently backs: run store, replay store, optional knowledge — all now have a
  new home (see layering).

## Target storage layering (user-confirmed)

```
DynamoDB (AWS, shared, persistent, compliant):
  - realtime session/conversation state
  - agent execution/run state
  - replay nonce (TTL)
  - [RESERVED] user long-term memory  ← future, see below
Local JSON (ships with image, read-only):
  - knowledge base原文 (the 4 knowledge/*.json — current, keep)
  - optional prompt templates (static)
Turso/libSQL: RETIRE — run+replay move to DynamoDB, knowledge stays local JSON.
Future RAG (NOT now): embedding vectors (Qdrant/pgvector), chunk metadata, S3/OSS原文 —
  separate project, needs embedding pipeline; today's knowledge is full-text keyword
  scoring, not vector RAG.
```

## Request

1. Finish the 3 DynamoDB structured-store adapters (run / runtime / replay) behind the
   existing port/adapter slots; keep SQL stores selectable (do not delete). Ensure prior
   review fixes (idempotency scoping, replay atomicity) hold — test against local
   DynamoDB at http://localhost:8000.
2. RESERVE user long-term memory as an architectural slot, but DO NOT implement:
   - Leave a clear extension point (a `userMemory` port descriptor / documented table
     shape: partition key = backend-derived stable user identity scope, NOT
     browser-supplied). Comment it as reserved-pending-prereqs.
   - No table creation logic, no read/write paths, no data collection yet.
3. Document in ops/CONFIG_KEYS_zh.md: Turso retirement path + DynamoDB as prod store +
   "user memory reserved, not active".

## Why user memory is NOT implemented now (3 unmet prerequisites)

- **Identity not confirmed**: memory keys on a stable user id, but the Sa-Token →
  tenant/merchant/person derivation (`LoginHelper.getUserId()` etc.) is still pending
  鹏哥's confirmation. Building memory before the key is confirmed risks attaching
  memories to the wrong identity (data-correctness bug, worse than not having it).
- **Compliance not approved**: persistent per-user behavioral memory in a payments
  context is compliance-sensitive (retention, consent, data level) — must be approved
  by company like Turso data-level approval was.
- **Product not defined**: "user memory" is undefined (summary? full history? preference
  tags? used for what?). Implementing on a guess = rework.

Doing it now = building on unmet prerequisites → wrong key / non-compliant data / wrong
product shape → rework costs more than reserving the slot. "Do it best" = reserve the
slot correctly now, implement in one shot once the 3 prereqs are ready.

## Expected Artifacts

- 3 DynamoDB adapters complete + green against localhost:8000; verify:upload passing.
- A documented, INERT userMemory extension point (port descriptor or doc), no runtime.
- CONFIG_KEYS note on Turso retirement + reserved user memory.

## Verification

- Storage survey read from code: no long-term memory feature exists; stores are
  conversations/events/runs/replay. DynamoDB adapters exist as uncommitted files with
  replay atomicity + idempotency scoping preserved.
- Local DynamoDB v1.25.1 running at http://localhost:8000 for adapter tests.

## Boundary

Develop DynamoDB work on a NEW branch, not the pending import-customer-support-agent
merge. No push/MR by Claude. User memory: reserve only, no data collection until
identity + compliance + product prereqs are met. Local DynamoDB is dev/test only;
prod uses real AWS DynamoDB via company config.
