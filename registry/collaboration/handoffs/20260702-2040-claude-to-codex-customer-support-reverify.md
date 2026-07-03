# Handoff: Claude -> Codex, customer-support re-verify after fixes

## Task
Re-verify the customer-support agent after Codex's fix round responding to the
collab-0019 review (findings handoff 20260702-1710). Read-only. Confirm which of
F1-F8 are actually fixed, by test + live probe, not by self-report.

## From / To
- From: claude (independent reviewer)
- To: codex (customer-support package owner)
- Follows: 20260702-1710-claude-to-codex-customer-support-review-findings.md

## Request
Codex: F5/F6/F8 remain open (all Minor). Pick them up or explicitly defer with a
reason. Optionally leave a codex->claude receipt so the collab record shows your
side; this round was answered by code only, no handoff.

## Expected Artifacts
- This re-verify handoff (delivered).
- assignments.json collab-0019 note updated with re-verify result.
- app-inbox 0003 / INDEX updated to mark F1-F4/F7 fixed.

## Verification
Test suite: 115 pass / 0 fail (was 100). Two new test files added: server.mjs
HTTP-layer integration test and frontendFallback.

Finding-by-finding (verified, not self-reported):

- F1 [Important] event write-path trusts client identity — **FIXED**.
  eventStore.mjs normalizeEvent now uses `hasRequestIdentityScope ?
  requestIdentityScope : <client fallback>`, so a scoped request overrides
  per-event client scope. Live probe: POST events with per-event
  identity_scope.tenant_id='tnt_victim' under a tnt_clinkpay token -> stored scope
  is tnt_clinkpay. Test: eventStore.test.mjs 'request identity overrides spoofed
  per-event identity scope on write'.

- F2 [Important] billing isolates tenant-only vs contract's three levels —
  **FIXED**. payments.mjs now imports and uses canReadIdentityScopedRecord for a
  full tenant+merchant+person check (payments.mjs:143); fixtures carry
  merchant_id/person_id. Test: tenantIsolation.test.mjs 'same-tenant token cannot
  read another person billing context'. Billing now shares the same enforcement
  as events/runs (the unification the review asked for, not a second local copy).

- F3 [Important] the token-beats-body gate had zero tests — **FIXED**. New
  server.test.mjs 'gateway token identity overrides spoofed request body identity
  at HTTP boundary' drives the real HTTP layer: body sends tnt_spoof/mch_spoof/
  person_spoof, asserts downstream input + metadata are tnt_clinkpay and no spoof
  id survives.

- F4 [Important] canReadRun route isolation untested — **FIXED**. server.test.mjs
  'tracked run route enforces tenant merchant person read isolation': same-person
  200, other-person 403, unscoped 403 against /v1/assistant/runs/:id.

- F7 [Minor] error responses echo raw Node SyntaxError — **FIXED**. server.test.mjs
  'malformed JSON returns stable public error code'.

Remaining (all Minor, not blocking):
- F5 operator forced-execution fail-closed path still untested
  (clinkOperator.mjs:205-228: enabled+executionEnabled+dry_run:false ->
  execution_adapter_not_wired).
- F6 idempotency cross-identity reuse still tested only on person dimension; no
  tenant-A-key vs tenant-B-key and no scoped-vs-unscoped same-key case.
- F8 global in-memory event buffer evicts across tenants; document as demo-scope
  boundary in README/contract.

Assessment: Codex fixed all four Important findings + F7, and fixed them at the
root (added the whole HTTP integration-test layer for F3/F4; unified billing on
the canonical predicate for F2) rather than as local patches. This is a direct,
correct response to the micro-trap meta-finding.

## Constraints honored
Read-only. No source files modified. Live probe ran on a scratch port (8801),
stopped after; did not touch the running instance on 8787. Did not touch ~/.codex,
~/.codex-api-relay, ~/.claude, auth, provider config, LaunchAgents, plugin config.
No secrets/preview tokens printed. Did not clean dirty tree.

## Verdict
Ready. All Important findings verified fixed with tests. Three Minor items remain,
none blocking demo or the isolation model.
