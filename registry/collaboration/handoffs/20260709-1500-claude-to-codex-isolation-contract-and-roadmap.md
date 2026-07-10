# Handoff: data-isolation contract + new roadmap from product sync (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-09 15:00 (+0800)
- Kind: decision record + review finding (no code edits by Claude this pass)

## Task

User synced with 新元哥 (product) and 鹏哥/Patrick (backend) this morning. New
roadmap locks scope and raises a hard question — "客服 agent 有数据隔离吗?" — that
must be answerable with code evidence, and answered so ops/backend does NOT come
back saying "you still need to rewrite code".

## New roadmap (agreed with 新元哥 — this narrows scope, please align to it)

1. **Freeze customer-support features.** No more feature iteration; the agent does
   NOT execute action/operational tasks. Connect to the **B-end TEST database** and
   bind each support conversation to the real logged-in user.
2. **Adapt to the existing backend framework**; the customer-support service must be
   **discoverable by Nacos** (register as a service instance).
3. **Align the existing interface with 鹏哥/Patrick.**

## Isolation finding (verified in code — this is the answer to Patrick's question)

Isolation mechanism is REAL and already implemented. Evidence:

- `services/gateway/src/security/identityScope.mjs`:
  - 3-level scope `tenant_id → merchant_id → person_id`, checked level-by-level
    (`canReadIdentityScopedRecord`); any mismatch → deny.
  - **Fail-closed for sensitive records** (`canReadSensitiveScopedRecord`): no valid
    requester scope (unscoped / no tenant) → DENY. This closes the old SEC-1
    fail-OPEN hole.
  - Public knowledge (FAQ) stays readable to all; private data uses the fail-closed
    path — two separate paths, no leak from opening FAQ.
- `services/gateway/src/agent/runStore.mjs` `scopedIdempotencyKey` (L186): each run's
  idempotency key embeds `caller + scoped + tenant + merchant + person` → conversations
  are isolated per real user. This is exactly roadmap #1's "bind each conversation to
  the real user" — the mechanism already exists.
- `services/gateway/src/security/gatewayAuth.mjs`: identity arrives via signed
  `x-agent-bff-*` headers; `verifyAgentApiBffAuth` rejects with 503
  `agent_api_bff_identity_not_configured` if no server-side scope.

**Header contract is already aligned both sides (verified, byte-for-byte):**
Node gateway reads `x-agent-bff-{key-id,timestamp,nonce,signature,tenant-id,
merchant-id,person-id,roles,scopes}`; Java `AgentApiBffSigner.java` emits the exact
same 9 `X-Agent-BFF-*` headers. No mismatch.

## The point for ops/backend (please confirm + close)

We do NOT touch or need to understand the B-end user store. Our isolation only
CONSUMES the identity triple (tenant/merchant/person) the backend derives. So:

- Isolation logic: DONE, do not rewrite.
- Identity derive + sign + emit headers: already coded in Java
  `AgentApiBffIdentityResolver`.
- **The ONE thing backend may need to touch:** confirm how their Sa-Token session
  maps to `tenant_id / merchant_id / person_id` in `AgentApiBffIdentityResolver`. If
  Codex's field names differ from the real session fields, that's a **single mapping
  function** edit — NOT a rewrite of isolation.
- Everything else is config: Nacos `/agent-api/**` route + HMAC secret/upstream.

## Request

1. Confirm the Sa-Token → tenant/merchant/person mapping in
   `AgentApiBffIdentityResolver` uses field names 鹏哥's backend actually provides
   (or flag which fields need confirming from him).
2. For roadmap #2 (Nacos-discoverable service): the Node customer-support gateway
   currently is NOT a Nacos-registered instance. Advise how you plan to make it
   discoverable — native Nacos client in the Node service, or register via the Java
   `clink-gateway` fronting it. This is a design decision I want your call on before
   anyone writes code.
3. For roadmap #1 (B-end TEST DB + per-user conversation binding): the scope key
   already supports it; confirm what still needs wiring to point at the test DB and
   feed the real user identity end-to-end.

## Expected Artifacts

- Codex confirmation (or fix) of the identity field mapping vs 鹏哥's real session.
- A short design note on how customer-support becomes Nacos-discoverable (#2).
- List of what remains to connect B-end TEST DB + per-user binding (#1).

## Verification

- Isolation code paths read and cited above (identityScope / runStore / gatewayAuth).
- Header contract cross-checked Node reader vs Java signer: identical 9 headers.
- No code edited by Claude this pass; this is a contract/roadmap handoff only.

## Boundary

No push, no MR, no commit, no secret values read (HMAC secret seen only as env NAME).
Claude did not touch the customer-support package files Codex is actively assembling;
this handoff is review + contract only. Scout-before-overwrite respected.
