# Handoff: Codex -> Claude, SEC-1 fail-closed implementation

## Task
Codex implemented app-inbox `0009-sec1-fail-closed-fix.md` for the
customer-support gateway and deployed it to Fly.io. Claude should independently
re-verify before marking SEC-1 closed in the collaboration ledger.

## From / To
- From: codex (customer-support package owner)
- To: claude (independent reviewer)
- Follows: `outputs/shared/app-inbox/0009-sec1-fail-closed-fix.md`

## Request
Claude independently re-runs the SEC-1 acceptance checks (see Reviewer Request
below) and, if they pass, marks SEC-1 closed in the collaboration ledger.

## Expected Artifacts
- Claude reviewer receipt handoff (Claude -> Codex).
- `registry/VALIDATION.md` SEC-1 completed-check entry.
- Ledger entry recording the SEC-1 re-verification (status proven).

## What Changed
- Added `canReadSensitiveScopedRecord` in
  `workspaces/agent-dev-workspace/agents/customer-support/services/gateway/src/security/identityScope.mjs`.
- Kept `canReadIdentityScopedRecord` fail-open for public knowledge records.
- Switched billing fixture authorization in
  `workspaces/agent-dev-workspace/agents/customer-support/services/gateway/src/integrations/payments.mjs`
  to the sensitive fail-closed predicate.
- Added an inline guard comment in
  `workspaces/agent-dev-workspace/agents/customer-support/services/gateway/src/agent/knowledge.mjs`
  so future edits do not replace public-knowledge semantics with the sensitive
  predicate.
- Added a legacy unscoped billing fixture and tests proving it is denied to a
  scoped requester.
- Added a public-knowledge regression proving unscoped public Chinese QA remains
  readable for scoped requesters.

## Verification
- Initial targeted run was red:
  `canReadSensitiveScopedRecord` export was missing, and the scoped-token
  billing test for `legacy-unscoped@example.com` did not reject.
- After implementation:
  - `node --test agents/customer-support/services/gateway/test/identityScope.test.mjs agents/customer-support/services/gateway/test/tenantIsolation.test.mjs agents/customer-support/services/gateway/test/knowledge.test.mjs`
    -> `34/34` pass.
  - `npm test --prefix agents/customer-support/services/gateway` -> `198/198`
    pass.
  - `node agents/customer-support/scripts/eval-context-quality.mjs --json` ->
    `29/29` pass.
  - `./scripts/audit-agent-code workspaces/agent-dev-workspace/agents/customer-support`
    -> `pass (fail=0 warn=0)`.
  - root `./scripts/check-secrets` -> pass.
  - root `./scripts/check-agent-packages` -> pass.
  - workspace `./scripts/check-portable.sh` -> pass.

## Deploy Evidence
- Deployed with:
  `fly deploy -c agents/customer-support/deploy/fly.toml --remote-only`
- New image:
  `clinkbill-support:deployment-01KWV2A867HJGXYEWSKBMWNMD0`
- `fly status -a clinkbill-support`:
  version `5`, region `sin`, state `started`, checks `1 total, 1 passing`.

## Live Smoke Evidence
Without printing preview or gateway tokens, live Fly smoke returned:
- `/health=200`
- tokenized page `200`
- served HTML did not expose the gateway token
- normal protected query `200`
- `source=runtime:model:anthropic-compatible`
- `llm.anthropicCompatible model=claude-opus-4-8 fallback=false`
- legacy unscoped billing query returned `403 tenant_scope_mismatch`
- event write `202`
- event read `200`
- `event_count=1`

## Reviewer Request
Please re-run the SEC-1 acceptance checks from app-inbox `0009`:
- unscoped sensitive billing record denied to scoped requester;
- matching scoped billing record still readable;
- unscoped public knowledge, including Chinese QA, remains retrievable;
- runs/events remain fail-closed;
- live Fly continues to use Claude through `anthropic-compatible` with
  `fallback=false`.

## Constraints Honored
No secrets, preview tokens, relay keys, API keys, auth files, or cookies were
printed or written outside `.run/fly`. Existing `.run/` state was preserved.
