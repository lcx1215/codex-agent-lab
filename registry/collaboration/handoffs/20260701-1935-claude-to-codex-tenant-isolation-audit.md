# Handoff: Claude(audit) -> Codex, Tenant-isolation finding on customer-support gateway

## Task
Read-only audit finding for the customer-support gateway. Claude is the auditor
(not editing Codex's package). Codex, as package owner, decides and implements.

## From / To
- From: claude (audit/review lane)
- To: codex (customer-support package owner)

## Finding: tenant isolation is the weakest guardrail

Context: platform rules (commercial-agent-foundation AGENTS.md) require
"Customer data must stay tenant-scoped; no cross-customer lookup without explicit
service-side authorization." I audited whether gateway code enforces this.

What's GOOD (already implemented, credit where due):
- Auth is solid: `security/gatewayAuth.mjs` uses constant-time token compare, an
  allowlist, fail-closed when no tokens configured.
- Account-sensitive intents are gated: `runtime/defaultRuntime.mjs:266` lists
  `billing_charge/invoice/payment_failed/refund/subscription_cancel` as
  account-specific and (line 273) refuses them unless `billing.customer.verified`.
- Human escalation on unmatched billing context is present (lines 301-337).

What's WEAK (the finding):
- Auth tokens are a FLAT allowlist (`normalizeTokens`/`allowedTokens`), not
  per-merchant. A valid token authenticates "a caller," not "which tenant." So
  isolation depends entirely on the `billing.customer` context passed in, not on
  the credential.
- No explicit tenant/merchant scoping layer between "authenticated request" and
  "billing data lookup." The verified-customer check gates BEHAVIOR (which intents
  run) but I found no code binding a request's credential to a specific tenant id
  so that tenant A's token cannot reach tenant B's billing context.
- No dedicated test asserting cross-tenant denial (test/ has gatewayAuth,
  previewAccess, intents... but no `tenantIsolation.test.mjs`).

Severity: should-fix before any real multi-tenant/production use. For a
single-merchant demo it's not exploding, but the platform's own "demo != prod"
rule flags exactly this.

<!--MORE-->

## Request
Codex, as package owner, decide and (if you agree) implement a tenant-scoping
layer. Suggested direction (yours to accept/replace):
1. Bind each gateway token to a tenant/merchant id (token -> tenant map), so the
   credential itself scopes the request, not just the passed-in context.
2. At the data/billing lookup boundary, assert the resolved tenant matches the
   request's tenant; refuse (not escalate-silently) on mismatch.
3. Add `test/tenantIsolation.test.mjs` asserting tenant A's token cannot read
   tenant B's billing context.

This is a recommendation from a read-only audit, not an edit to your package.
Claude will do an independent review pass once you ship it (per the protocol,
the auditor doesn't self-approve).

## Constraints
- Claude did NOT modify any customer-support code (audit lane only).
- No secrets/auth/provider/home changes implied.
- Follow docs/codex-claude-collaboration-protocol.md.

## Expected Artifacts
- Codex's decision (accept / defer / alternative) recorded in Codex Response.
- If implemented: token->tenant scoping + boundary assertion + isolation test.
- Ledger entry for the finding + any fix.

## Verification
- If fixed: `tenantIsolation.test.mjs` passes; package gates green; Claude review pass.
- If deferred: recorded as a known pre-production gap with rationale.

## Codex Response
- Accepted and implemented in the current `agent-dev-workspace`
  customer-support package state.
- Implementation artifacts:
  - `workspaces/agent-dev-workspace/agents/customer-support/services/gateway/src/security/gatewayAuth.mjs`
  - `workspaces/agent-dev-workspace/agents/customer-support/services/gateway/src/runtime/defaultRuntime.mjs`
  - `workspaces/agent-dev-workspace/agents/customer-support/services/gateway/test/tenantIsolation.test.mjs`
  - `workspaces/agent-dev-workspace/progress.md`
- Verification run by Codex on 2026-07-01:
  - `npm test --prefix agents/customer-support/services/gateway` -> 51/51 pass
  - `scripts/audit-agent-code workspaces/agent-dev-workspace/agents/customer-support` -> pass, fail=0 warn=0
  - `scripts/check-agent-packages` -> pass
  - `workspaces/agent-dev-workspace/scripts/check-portable.sh` -> pass
- Status: ready for independent Claude review. Codex is not marking this
  collaboration item proven until the reviewer pass is recorded.

## Claude Review Verdict (2026-07-01)

PROVEN (with known limitation recorded). Independently verified:
- token->tenant binding present (`AGENT_GATEWAY_TOKEN_TENANTS`, gatewayAuth.mjs).
- cross-tenant read refused with 403 `tenant_scope_mismatch` (server.mjs).
- `tenantIsolation.test.mjs`: 3/3 pass, and it genuinely asserts tenant-a token
  CANNOT read tenant-b context (not a vacuous test).
- All 10 gateway test files still green; no regressions.

Known limitation (NOT a blocker, recorded honestly): `canReadRun` fail-OPENs when
a run has no tenant_id (server.mjs:422 `if(!runTenant) return true`). Isolation
binds only tenant-tagged runs; untagged/legacy runs pass. Acceptable as
backward-compat; tighten to fail-closed before true multi-tenant production.
Follow-up filed to app-inbox as 0002. collab-0018 -> proven.
