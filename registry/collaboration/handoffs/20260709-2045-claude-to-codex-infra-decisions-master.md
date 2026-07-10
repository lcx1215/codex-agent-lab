# Handoff: infrastructure decisions master (storage + Fly exit + model + RAG) — Claude → Codex

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-09 20:45 (+0800)
- Kind: architecture master brief — aligns the in-flight work you already started (69
  uncommitted changes: dynamodb adapters + fly script edits) to the decisions the user
  and I reached over several rounds. Read before committing that work.

## Task

User is reshaping the customer-support agent's infrastructure. Over several rounds we
settled a set of decisions about storage, model↔DB relationship, Fly exit, and RAG
scope. You are already mid-change (dynamodbClient.mjs, dynamodbRuntimeStore.mjs,
dynamodbAgentApiBffReplayStore.mjs, runtimeDynamoDbStore.test.mjs uncommitted; fly.toml
+ fly scripts modified). This brief records the agreed decisions so your commit matches
them and nothing regresses.

## Decisions (authoritative)

### 1. Storage layering
```
DynamoDB (AWS, shared, persistent, compliant):
  - realtime session/conversation state
  - agent execution/run state
  - replay nonce (TTL, atomic conditional write)
  - [RESERVED, do NOT build] user long-term memory
Local JSON (ships in image, read-only): knowledge base原文 (4 knowledge/*.json), keep as-is
Turso/libSQL: RETIRE — run + replay move to DynamoDB; knowledge stays local JSON.
Future RAG (NOT now, separate project): embedding vectors (Qdrant/pgvector), chunk
  metadata, S3/OSS原文. Today's knowledge is full-text keyword scoring, not vector RAG.
```
Keep SQL stores selectable (do not delete) — DynamoDB is one more selectable adapter.

### 2. Model ↔ DB relationship — NO CHANGE NEEDED
Verified: model provider layer (`modelProviders/`) touches ZERO database. The model
only receives a backend-assembled, trimmed context pack (messages / page context /
retrieved knowledge / intent), never a DB handle. So switching storage to DynamoDB has
zero impact on the model layer — do not add DB access into model providers.

### 3. User long-term memory — RESERVE, do NOT implement
Does not exist today (all `memory` matches are in-memory stores). When built it goes in
DynamoDB (partition = backend-derived stable user identity, never browser-supplied).
Leave an inert, documented extension point only. Reason it is blocked (all 3 unmet):
- identity not confirmed (Sa-Token → getUserId() pending 鹏哥),
- compliance not approved (per-user behavioral data in payments = data-level approval),
- product undefined (what to store / how used).
See prior handoff 20260709-2015 for detail.

### 4. Fly exit → company AWS / container platform
Verified: agent gateway code has ZERO Fly dependency — it is a standard node:22-alpine
container. Fly only provides: public HTTPS endpoint + keep-alive + health check + demo
UI. All `fly.dev` occurrences are examples/defaults/starter, not hard deps.

Fly exit needs 4 things (ops must be able to take over without Fly confusion):
- a) Deploy the SAME Dockerfile to company platform (ECS/EKS/K8s) — ops standard work.
- b) Set Java BFF `upstreamBaseUrl` = company agent gateway address (config).
- c) **Java hardcoded default is a trap**: `AgentApiBffProperties.java:20`
  `DEFAULT_UPSTREAM_BASE_URL = "https://clinkbill-support.fly.dev"`. If ops forgets to
  set upstreamBaseUrl AFTER Fly is down, the BFF silently falls back to a dead Fly URL
  with no clear error. Change this default to empty / fail-closed so a missing config
  raises an explicit "upstream not configured" error instead of hitting a dead link.
- d) There is NO non-Fly deployment guide today (DEPLOY.md is Fly-centric). Replacement
  pieces exist (Dockerfile, docker-compose, nginx template, company-production.env,
  nacos template) but need a "deploy this container to a company platform" guide that
  covers what Fly used to give for free: HTTPS/TLS, public/VPC ingress, keep-alive,
  health check. Note: agent needs no public internet — it sits behind the Java gateway
  and only takes signed backend requests, so a VPC-internal placement is simpler + safer.

## Request

1. When committing the in-flight DynamoDB work: ensure prior review fixes are preserved
   (replay atomicity via `attribute_not_exists`, `scopedIdempotencyKey` idempotency),
   SQL stores stay selectable, tests run against local DynamoDB (http://localhost:8000).
2. Apply decision (4c): make `DEFAULT_UPSTREAM_BASE_URL` fail-closed (empty → explicit
   config error), so Fly-exit does not leave a silent dead-link fallback.
3. Add a non-Fly company deployment guide (decision 4d); demote Fly to optional starter
   in DEPLOY.md; keep/label or remove Fly-only scripts (`smoke-fly-*`, `cutover-fly-*`)
   as starter-only.
4. Reserve (not build) the userMemory extension point (decision 3).
5. Do NOT add DB access to model providers (decision 2).
6. Flag to the user before implementing anything requiring the 3 unmet prereqs
   (identity / compliance / product) — user memory especially.

## Expected Artifacts

- DynamoDB adapters committed + green against localhost:8000; verify:upload passing;
  the 257 gateway tests still pass.
- Fail-closed Java upstream default.
- Company (non-Fly) container deployment guide; DEPLOY.md de-Fly-centralized.
- Inert documented userMemory slot; CONFIG_KEYS note (Turso retirement + DynamoDB prod
  + user memory reserved).

## Verification

- Repo state at brief time: HEAD 89f0924 (pushed), 69 uncommitted + 4 untracked =
  your in-flight DynamoDB + fly-script work. Dynamo adapters present as untracked files.
- Verified in code: model providers touch zero DB; agent gateway zero Fly dependency;
  no user-memory feature exists; Java default upstream hardcodes the Fly URL
  (AgentApiBffProperties.java:20). Local DynamoDB v1.25.1 up at localhost:8000.

## Boundary

Infra reshape is a NEW line — keep it on a NEW branch, do NOT mix into the pending
import-customer-support-agent merge (which is the reviewed, 257-test app). No push/MR by
Claude. Local DynamoDB/local run are dev/test only; production uses real AWS DynamoDB +
company container platform via company config, no secrets committed. User memory:
reserve only, no data collection until identity + compliance + product are ready.
