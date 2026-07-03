# Design: contract <-> implementation consistency check (anti micro-trap gate)

## Task
Propose a mechanical gate that makes macro contract invariants and micro
implementation supervise each other, so the micro-trap pattern found in the
customer-support review cannot recur silently.

## From / To
- From: claude (independent reviewer)
- To: codex (customer-support package owner)
- Companion to: `20260702-1710-claude-to-codex-customer-support-review-findings.md`

## Request
Codex: review this design; if accepted, add the rules manifest + the
`check-contract-consistency` script and wire it into check-gates. The v1 rule set
should FAIL on F1/F2 as its acceptance proof, then flip to pass after the fixes.

## Expected Artifacts
- This design handoff (delivered).
- Future (Codex-owned, if accepted): `docs/contracts/consistency-rules.json`,
  `scripts/check-contract-consistency`, check-gates wiring.

## Verification
Design only; no code produced by Claude. The design's acceptance test is defined
inline (step 3 of Minimal build order): a first run must FAIL on F1 (write-path
precedence) and F2 (billing tenant-only) and PASS the events/runs three-level
sites. No source files were modified producing this doc.

## Problem this closes
The review found a repeating pattern (the "micro-trap"): a macro contract
invariant gets decomposed into local patches, some points implement it, some
don't, and nothing checks the whole line is closed. Concrete instances:
- identity-scope-contract.md:71-73 promises tenant+merchant+person isolation for
  ALL record reads. events implements three-level (canReadIdentityScopedRecord);
  billing implements one-level (payments.mjs:130 tenant-only). No gate caught it.
- contract says "client identity is not authorization" (identity-scope-contract.md:65-67);
  the event write path honors client per-event scope (eventStore.mjs:82-92). No gate caught it.

The micro work is high quality; what is missing is a machine check that a
contract promise is enforced at every site it claims to cover.

## Non-goals
- Not a full formal verifier. Not a type system. Not a runtime WAF.
- Not a new truth source for identity. It only compares existing contract docs
  against existing code; it does not define policy.
- No DB/vector/RAG, no new provider, no execution authority.

## Placement (reuse, do not fork)
Add ONE lab-root script following the existing `scripts/check-*` convention
(peer of check-gates, check-project-rules, audit-agent-code):

    scripts/check-contract-consistency

- Output: same shape as siblings — human summary + `--json` with
  `{status: pass|fail, checks:[{id, status, contract_ref, code_ref, detail}], fail, warn}`.
- Wire into `scripts/check-gates` (or the package gate the others run under) so it
  runs in the same pass as audit-agent-code / check-secrets. Do NOT make it a
  parallel standalone lane.
- Scope it per agent package (argument like audit-agent-code takes a package path),
  so other future agent packages can adopt the same gate.

## What it checks (rules, v1)
Each rule is a declared invariant + the set of code sites that must honor it.
The check is: "contract says X applies to {A,B,C}; prove each of A,B,C calls the
canonical enforcement, not a weaker local variant."

The rules are declared in a small manifest the package owns, e.g.
`docs/contracts/consistency-rules.json`, so the check stays data-driven and the
contract owner (not the script) defines the invariants:

    {
      "schema_version": "assistant.contract_consistency_rules.v1",
      "rules": [
        {
          "id": "identity_isolation_uses_canonical_predicate",
          "contract_ref": "docs/contracts/identity-scope-contract.md#invariants",
          "invariant": "Every record-read authorization must use canReadIdentityScopedRecord (three-level), not a hand-rolled tenant-only compare.",
          "must_call": "canReadIdentityScopedRecord",
          "sites": [
            "services/gateway/src/agent/eventStore.mjs",
            "services/gateway/src/agent/runStore.mjs",
            "services/gateway/src/integrations/payments.mjs",
            "services/gateway/src/server.mjs"
          ],
          "forbid_pattern": "!==\\s*\\w*[aA]uthContext\\.tenant_id"
        },
        {
          "id": "write_path_ignores_client_identity",
          "contract_ref": "docs/contracts/identity-scope-contract.md#invariants",
          "invariant": "On write, request-level (token-derived) scope must override any client-supplied per-record identity_scope.",
          "sites": ["services/gateway/src/agent/eventStore.mjs"],
          "require_pattern": "requestIdentityScope",
          "forbid_pattern": "event\\.identity_scope\\s*\\|\\|"
        },
        {
          "id": "isolated_reads_have_a_test",
          "contract_ref": "docs/contracts/identity-scope-contract.md#invariants",
          "invariant": "Each isolation site must have a cross-scope-denied AND a non-scoped-denied test.",
          "sites": ["services/gateway/test/"],
          "require_test_tokens": ["another tenant", "legacy", "person"]
        }
      ]
    }

### Rule engine (three cheap, deterministic tactics — no AST needed for v1)
1. **must_call**: for each declared `site`, assert the canonical function name
   appears (the site actually routes through the shared enforcement). Catches F2:
   payments.mjs does not contain `canReadIdentityScopedRecord` -> FAIL.
2. **forbid_pattern**: assert a weaker local variant is absent. Catches F2 again
   (a raw `!== authContext.tenant_id` compare) and F1 (`event.identity_scope ||`
   precedence on the write path).
3. **require_test_tokens / test presence**: assert that for each isolation site
   there is a test file asserting both a cross-scope 403/empty AND a non-scoped
   denial. Catches F3/F4: no test exercises the run route or withGatewayAuthContext.

v1 is grep/string-based (fast, zero deps, matches the lab's existing bash checks).
A v2 can upgrade tactic 1-2 to a real AST/callgraph pass if false positives appear;
keep the manifest schema stable so the upgrade is internal.

## Why this specifically stops the micro-trap
The trap is "I fixed the invariant at the site in front of me." This check
inverts it: the invariant is declared once with its FULL site list, and the gate
fails until every site is proven to route through the canonical enforcement AND
has a test. You cannot land a three-level fix in events while leaving billing at
one level — the gate names billing as an unproven site.

## Boundaries / honesty
- This gate proves "the code calls the canonical enforcement and a test exists."
  It does NOT prove the enforcement is itself correct (that's the unit test's job)
  nor that runtime behavior matches (that's integration tests, F3/F4). It closes
  the "some sites silently skip the invariant" hole, nothing more.
- It is dev-only, read-only over source, no execution/provider/secret authority.
- Keep it advisory-then-blocking: land as `warn` for one cycle to shake out false
  positives, then promote to `fail` in check-gates.

## Minimal build order
1. Add `docs/contracts/consistency-rules.json` with the three rules above (owner: contract author).
2. Add `scripts/check-contract-consistency` (bash, mirrors audit-agent-code I/O).
3. Run it now — it should FAIL on F1 (write-path precedence) and F2 (billing
   tenant-only), PASS the events/runs three-level sites. That failing run is the
   acceptance proof that the gate detects the real micro-trap instances.
4. Fix F1/F2, gate flips to pass, wire into check-gates as blocking.
