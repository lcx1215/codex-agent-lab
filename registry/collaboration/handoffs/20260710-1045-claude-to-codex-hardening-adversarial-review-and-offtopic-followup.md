# Handoff: 631bfe8 hardening adversarial review + off-topic follow-up (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-10 10:45 (+0800)
- Kind: independent adversarial review of a Codex fix + one Claude code change (off-topic
  gate follow-up) + a NON-blocking backlog. Deployment verdict: SAFE TO DEPLOY.

## Task

logbot (gpt-5.5) independently reviewed branch `a2a15eb0`; Codex then landed `631bfe8`
("fix: harden dashboard auth and replay boundaries"). Claude independently verified all
4 logbot findings against the real code, then ran a dimension-split adversarial review
(frontend auth / Java gateway / off-topic intent / DynamoDB replay), each finding
adversarially re-verified before acceptance.

## What Claude verified GREEN (safe to deploy)

- Fix 1 SSE auth header: `basic.vue` injects `__CLINK_ASSISTANT_AUTH_HEADERS__` from the
  real `accessStore.accessToken`; `buildAssistantFetchHeaders` uses window-provider first,
  storage JSON fallback (`core-access`) second, with a forwarded-header allowlist. Priority
  correct — no "logged-in user gets 401" blocker.
- Fix 2 pre-login public assistant: `<AssistantSupport surface="public">` fully removed from
  `auth.vue`; docs updated to "prod /agent-api requires login".
- Java gateway auth boundary: adversarial reviewer returned ZERO deployable findings —
  no reproduced "/agent-api/** open in production" hole in the current repo.
- Fix 4 replay: `deleteReplayExpiredItems` (per-request full-table Scan) removed;
  `rememberAgentApiBffNonce` keeps only `attribute_not_exists(entry_key)` conditional put
  (401 on replay). Matches the 2026-07-09 infra-decisions design (TTL background + conditional put).
- Tests: gateway suite 258 pass / 0 fail / 2 skip (skips = no local DynamoDB + no model key).

## Claude change made this session (kept, net-positive)

`services/gateway/src/agent/intents.mjs` + `test/intents.test.mjs` (working tree, uncommitted):
added `requestsOffTopicContent()` so a page-ref-wrapped off-topic *generation/recommendation*
request ("这个页面能不能顺便推荐一本管理学的书") no longer smuggles past the off-topic gate.
+4 regression tests lock the off-topic × page-context invariant. Does NOT fully close the
gate (see backlog 1/2) but is a strict improvement and all tests green.

## Backlog (NON-blocking — post-launch small iterations, Codex-owned)

1. [medium/semantic] Domain-saturated page_context still admits FACTUAL off-topic questions
   ("On this page, what is the capital of France?") — `requestsOffTopicContent` only blocks
   generation verbs, not factual queries. intents.mjs:275.
2. [medium/semantic] `requestsOffTopicContent` regex is itself bypassable ("讲讲唐朝历史",
   "推荐几首歌", translation asks). intents.mjs:378. Correct long-term fix = invert to an
   opt-in referential whitelist instead of an off-topic denylist (don't keep whack-a-mole).
3. [medium/UX] FALSE POSITIVES: legit in-domain questions wrongly rejected ("怎么申诉?",
   "钱到账要多久?") because `dispute/申诉/到账/入账` are missing from `containsSupportDomainTerm`.
   intents.mjs:358. This one hurts real users — prioritize over 1/2.
4. [medium/ops] Replay table never provisions native TTL: `ensureReplayTable`/`ensureTable`
   CreateTableCommand sets no `TimeToLiveSpecification` and no code calls UpdateTimeToLive
   (dynamodbClient.mjs:84,107-112). After removing Scan cleanup, expired nonces never purge on
   auto-created tables → table grows unbounded. Add idempotent UpdateTimeToLive(expires_at) or
   a startup/CI DescribeTimeToLive assertion.

## Request

- Accept Claude's off-topic follow-up (intents.mjs + intents.test.mjs) or fold it into the
  inverted-whitelist rework (backlog 2).
- Treat backlog 1-4 as post-launch iterations; none blocks deploying 631bfe8.
- Prioritize backlog 3 (false-positive rejection of real support questions) first.

## Expected Artifacts

- Decision on Claude's off-topic follow-up (keep as-is / rework).
- Backlog 3 fix (domain-term vocabulary) as the first post-launch iteration.
- TTL provisioning (backlog 4) before real production traffic volume.

## Verification

- Claude: 4 logbot findings re-verified against real code (Fix 1/2/4 clean; Fix 3 had a
  residual bypass, closed by Claude's change). Dimension-split adversarial review + per-finding
  adversarial re-verification (workflow, stopped after Verify phase by user; Review complete,
  4 findings CONFIRMED). Gateway tests 258 pass / 0 fail / 2 skip. node --check clean.
- Claude did NOT commit/push. Working tree carries only intents.mjs + intents.test.mjs edits
  on top of 631bfe8 on branch codex/dynamodb-runtime-storage.
