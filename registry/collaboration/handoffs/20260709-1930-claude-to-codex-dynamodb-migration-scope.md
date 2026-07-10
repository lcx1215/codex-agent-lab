# Handoff: DynamoDB migration — storage survey + scoped adapter plan (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-09 19:30 (+0800)
- Kind: design request (storage migration) + local test infra ready

## Task

Company wants to move storage to AWS DynamoDB. User clarified there are actually two
storage families: a Turso/libSQL side AND a local knowledge database. I surveyed the
current storage layout to scope which parts can/should move to DynamoDB and which must
NOT, so you can write adapters against the right boundary. A local DynamoDB is already
running for you to develop against (details below).

## Survey (verified in code, branch import-customer-support-agent @ eac37da)

Storage splits into TWO families:

### A. Structured records — GOOD fit for DynamoDB (key-value + TTL)
- run store `services/gateway/src/agent/runStore.mjs` (+ libsqlRunStore.mjs):
  currently JSONL / SQLite / libSQL(Turso). Access is by run_id + idempotency key.
- runtime store `services/gateway/src/runtime/sqliteRuntimeStore.mjs`: SQLite, key access.
- replay store (BFF nonce) `security/libsqlAgentApiBffReplayStore.mjs`: libSQL, nonce key
  + expiry — DynamoDB TTL is a natural fit here.
- These have 45 SQL statements total (20+18+7) that would be re-expressed as DynamoDB
  key-value ops. They all already sit behind the runtime PORT interface
  (`runtime/ports.mjs`) with an `adapter` slot + `*_MODULE` env hook
  (`config.mjs:131`, `defaultRuntime.mjs` adapter branches). So: NEW adapter modules,
  NO change to upper agent logic.

### B. Knowledge base — do NOT put in DynamoDB
- 4 JSON files in `knowledge/` (payments-support 44K, clink-official-docs 291K,
  clink-integ-skills 539K, clink-payment-skills 493K).
- Retrieval (`agent/knowledge.mjs:70-95`) is FULL-TEXT fuzzy scoring: builds a haystack
  from title/keywords/content and does `includes(term)` weighted scoring + intent
  boosts. DynamoDB cannot do relevance ranking / full-text scan efficiently (it is
  primary-key lookup only). Forcing this into DynamoDB = full-table Scan per query =
  slow + expensive + loses ranking.
- Knowledge currently: local JSON (optionally SQLite/Turso via KNOWLEDGE_SQLITE_PATH /
  KNOWLEDGE_TURSO_DATABASE_URL). Keep it on JSON/SQLite/Turso, or if a managed search is
  wanted later, use OpenSearch/vector DB — NOT DynamoDB.

## Local DynamoDB is ready (develop against this)

- Running: DynamoDB Local v1.25.1 at `http://localhost:8000` (JDK17, no docker needed).
- Install dir: `~/Desktop/codex-agent-lab/.toolchain/dynamodb-local/`
  (jar + DynamoDBLocal_lib), data persisted to `.../dynamodb-local/data`, `-sharedDb`.
- Verified working: CreateTable / PutItem / GetItem / ListTables all succeed (created a
  test `assistant_runs` table, wrote+read a row incl. CJK text).
- Log: `/tmp/dynamodb-local.log`. Restart:
  `<toolchain>/java/jdk-17.0.19+10/Contents/Home/bin/java -Djava.library.path=<dir>/DynamoDBLocal_lib -jar <dir>/DynamoDBLocal.jar -sharedDb -port 8000 -dbPath <dir>/data`

## Target architecture (user-confirmed direction)

```
AWS DynamoDB (shared, persistent, in AWS, compliant)
  → user info / session cache / run records / replay nonce (the 3 structured stores)
Local knowledge base (ships WITH the agent image, read-only, in-memory)
  → the 4 knowledge/*.json (ALREADY this shape today — Dockerfile `COPY knowledge`,
    loaded once via fs.readFile + Map cache, in-memory scoring, no network)
Turso/libSQL → retires once user/session move to DynamoDB (knowledge does NOT need it;
  keep Turso only as an optional dev/transition backend, not a permanent prod dependency)
```

Rationale: knowledge is static/read-only and rides the image (fastest, multi-replica
consistent, no third-party dependency). Structured shared state goes to DynamoDB so all
prod data stays in AWS and Turso (third-party SaaS) can be dropped. Trade-off to note:
knowledge-as-image means "update knowledge = redeploy" — acceptable now (docs/skills
change rarely); only revisit if runtime hot-editing of knowledge is later required.

## Request

1. Confirm migration SCOPE with this boundary: DynamoDB adapters for the 3 structured
   stores (run / runtime / replay) ONLY; knowledge base stays as the local image-bundled
   store (JSON/SQLite), NOT DynamoDB (flag to the user if anyone insists knowledge must
   go to DynamoDB — that needs a different design, e.g. OpenSearch/vector DB). Keep the
   knowledge retrieval path untouched.
2. Write DynamoDB adapters implementing the existing PORT contracts:
   - `dynamoRunStore.mjs` (partition run_id; keep idempotency-key semantics — design a
     GSI or a deterministic key so the existing idempotency guarantee holds).
   - `dynamoRuntimeStore.mjs`.
   - `dynamoReplayStore.mjs` (use DynamoDB TTL for nonce expiry).
   Wire them through the existing `adapter` / `*_MODULE` slot so upper logic is untouched.
   Add `@aws-sdk/client-dynamodb` (+ lib-dynamodb) as deps; endpoint/region/credentials
   from env (endpoint override = http://localhost:8000 for local/CI).
3. Add tests that run against the local DynamoDB (localhost:8000), mirroring the existing
   libsql/sqlite store tests. Keep the existing SQL stores as selectable backends
   (do not delete them — DynamoDB becomes one more selectable adapter).
4. Do NOT touch the knowledge retrieval path.

## Expected Artifacts

- 3 DynamoDB adapter modules behind the port/adapter slots + env config keys.
- Tests green against localhost:8000; `npm run verify:upload` still passing.
- A short note in ops/CONFIG_KEYS_zh.md documenting the new DynamoDB env keys and the
  "knowledge stays off DynamoDB" decision.

## Verification

- Storage layout read directly from code (branch import-customer-support-agent @ eac37da):
  knowledge = 4 JSON files + full-text fuzzy scoring (`agent/knowledge.mjs:70-95`);
  run/runtime/replay = SQL stores behind the runtime PORT interface with adapter slot.
- Local DynamoDB v1.25.1 confirmed working at localhost:8000: CreateTable/PutItem/
  GetItem/ListTables all succeeded against a test `assistant_runs` table (CJK round-trip
  intact). No repo code edited by Claude; survey was read-only.

## Boundary

New feature — develop on a NEW branch, do NOT mix into the pending
import-customer-support-agent merge. No push/MR by Claude. Local DynamoDB is dev/test
only; production uses real AWS DynamoDB (endpoint/creds via company config, not committed).
Claude ran read-only survey + started local DynamoDB; no repo code edited.
