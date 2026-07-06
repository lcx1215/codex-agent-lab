# Handoff: Claude -> Codex, SEC-1 fail-closed re-verification PASS

## Task
Independently re-verify Codex's SEC-1 fail-closed implementation (app-inbox
`0009`, deployed to Fly) before SEC-1 is marked closed in the collaboration
ledger. Requested by `registry/collaboration/handoffs/20260706-1445-codex-to-claude-sec1-fail-closed.md`.

## Request
Confirm the four SEC-1 acceptance points and that no public-knowledge (AC-1)
regression was introduced.

## Expected Artifacts
- This handoff (Claude reviewer receipt).
- `registry/VALIDATION.md` SEC-1 completed-check entry.
- Ledger entry `collab-0020-sec1-fail-closed-reverify` (status proven).

## Verification
Independent, Claude-run this session (real `rg` on PATH; customer-support source
NOT edited — review-only, package is Codex-owned).

- Codex's targeted suite re-run by Claude:
  `node --test test/identityScope.test.mjs test/tenantIsolation.test.mjs test/knowledge.test.mjs`
  -> `tests 34 / pass 34 / fail 0`.
- Claude-authored predicate assertions (not Codex's tests), directly against
  `src/security/identityScope.mjs`, 7/7 pass (exit 0):
  - `canReadSensitiveScopedRecord`: unscoped record + scoped requester -> DENY;
    unscoped requester -> DENY; cross-tenant -> DENY; own tenant -> ALLOW.
  - `canReadIdentityScopedRecord` (public KB): unscoped doc + scoped requester
    -> ALLOW (Chinese/public knowledge preserved, the AC-1 trap avoided);
    cross-tenant scoped doc -> DENY.
  - `canReadRuntimeScopedRecord` (runs/events): unscoped run -> DENY
    (fail-closed unchanged).
- Code reading confirms the design: `identityScope.mjs:46` public records with
  no scope return true (fail-open, intended); `identityScope.mjs:59-60` the
  sensitive predicate denies when requester OR record is unscoped (fail-closed,
  the SEC-1 fix).

## Verdict
SEC-1 PASS. Sensitive records are code-enforced fail-closed for legacy/untagged
records; public knowledge (incl. Chinese QA) preserved; runs/events unchanged.
Deploy/live evidence in the 1445 handoff accepted as-is (Claude did not re-drive
live Fly). SEC-1 may be marked closed.

## Note (cross-lane awareness)
See `registry/VALIDATION.md` "Incident + Rollback" — during an unrelated cutover-
script re-verify earlier today, a guard-passing fake-key input triggered a real
live cutover; rolled back to `anthropic-compatible` (version 9, health 200,
`ANTHROPIC_*` intact). Follow-up app-inbox `0010` proposes a dry-run gate on the
cutover script. No secret values were read or written by Claude.

## Constraints Honored
No secrets, tokens, auth files, or provider config read/written. customer-support
source untouched. No push (awaiting user).
