# Handoff: maximize local deploy + maintenance ease, then push (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-09 21:15 (+0800)
- Kind: polish request — make the DynamoDB/local stack as turnkey as possible for
  deploy + later maintenance, then commit & push.

## Task

User wants the local setup taken to maximum deploy-ease and maintainability (so ops
later have the least friction), then pushed. DynamoDB adapters are done and tested
(2 pass against local DynamoDB, 252 gateway tests green, agent core capabilities
untouched). This is the "make it turnkey" pass, not new features.

## Already good (verified)

- Adapter reads endpoint/region/creds/table from env; local↔AWS switch = config only
  (endpoint=localhost for local, empty for real AWS). Code change: none to switch.
- Clear fail-closed errors: `dynamodb_runtime_table_not_configured`,
  `agent_api_bff_replay_store_not_configured`.
- CONFIG_KEYS_zh.md documents the DynamoDB env keys; .env.example + both env templates
  have DynamoDB examples.

## Request

Close the gaps below (turnkey local deploy + maintenance ease), then commit & push.

## Gaps to close

1. **One-command local stack**: docker-compose.yml does NOT include a DynamoDB Local
   service. Add `amazon/dynamodb-local` (port 8000, persisted volume) to compose so
   `docker compose up` brings up agent + local DynamoDB together. Wire the agent
   service's `DYNAMODB_ENDPOINT` to the compose service. Goal: clone → one command →
   running with DynamoDB, no manual jar download.
2. **Idempotent table bootstrap**: there is NO create-table script. Add
   `scripts/init-dynamodb-tables.mjs` (or similar) that creates the runtime + replay
   tables if absent (idempotent: skip if exists), reads table names/endpoint/region from
   the same env, enables TTL on the replay table's expiry attribute. Must work against
   BOTH local (localhost:8000) and real AWS (so ops runs the same script). Document it in
   DEPLOY.md / CONFIG_KEYS. This removes manual table creation as a maintenance burden.
3. **Wire it into the dev/verify flow**: a `npm run` script (e.g. `dev:local-stack` or
   extend existing) that starts local DynamoDB + bootstraps tables + starts the agent, so
   a new engineer gets a working stack in one step. Keep it optional/non-breaking.

## Maintenance-ease checks (please also confirm)

- Missing/misconfigured DynamoDB → explicit error (already true for table-not-configured;
  also make connection-refused / endpoint-unreachable produce a clear actionable message,
  not a raw stack).
- README/DEPLOY reflect: default runtime = DynamoDB; local dev via compose; Turso
  retired; knowledge stays local JSON; user memory reserved not built.
- Keep SQL stores selectable (do not delete) so fallback remains.

## Expected Artifacts

- docker-compose with DynamoDB Local; `init-dynamodb-tables` idempotent bootstrap script;
  one-step local-stack npm script; docs updated.
- All tests green (252+), DynamoDB adapter tests green against local, verify:upload pass.
- Commit & push to the branch when green.

## Verification

- Verified in code: adapter config is fully env-driven (dynamodbClient.mjs
  normalizeDynamoDbConfig); local detection via isLocalDynamoEndpoint; 252 gateway tests
  + 2 dynamo adapter tests green; agent core files (assistantFlow/knowledge/intent/
  capabilities/clinkValidation/clinkOperator) NOT modified by the infra work.
- Gaps confirmed absent: no dynamodb service in docker-compose; no create-table script.

## Boundary

Turnkey polish only — do NOT change agent capabilities or add features needing the unmet
prereqs (identity/compliance/product); user memory stays reserved. Local DynamoDB is
dev/test; prod uses real AWS via config. Per user's latest instruction the infra work may
go on the current branch (not forced to a new branch) — but keep DynamoDB/Fly changes as
their own commits, separate from the reviewed app commits, so review/rollback stays clean.
Push is user-gated as always; user said push is OK once it's turnkey and green — still
show final state before the actual push.
