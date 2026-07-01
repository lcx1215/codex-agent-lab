# Handoff: Claude -> Codex, Full-platform mega audit before commit

## Task

Before committing the lifecycle-gates work, perform a SUPER-THOROUGH audit of the
entire codex-agent-lab platform: every script, module, gate, doc, and — most
importantly — the LOGICAL COHERENCE between them. Find contradictions, dead
links, gates that don't actually enforce what they claim, and drift between docs
and code.

## From / To

- From: claude
- To: codex

## Context

- The platform now has 17 check-* gates, 9 lab_agents modules, 24 test files, 29
  docs, a 17-entry ledger, task-state + merge-queue + 3 lifecycle gates.
- Baseline before audit: check-lab PASS, full test suite OK, 10 uncommitted files
  (the lifecycle-gates work: rule_ack.py, task_verify.py, dispatch.py,
  check-gates, their tests, backfilled tasks.json).
- This is a coherence audit, not a feature request. Do NOT add features. Report
  findings; only fix outright breakage (with justification).

## Audit dimensions (cover ALL of these, report per-dimension)

1. **Gate enforcement reality**: for each `scripts/check-*`, does it actually
   fail-closed on the thing it claims to guard? Try to find a gate that passes
   when it should fail (like the pre-lifecycle-gate tasks that were `done` with
   no ack — is there any analogous hole elsewhere?).
2. **Doc vs code drift**: do docs/*.md and registry/*.md describe what the code
   actually does now? Flag any doc claiming a behavior the code no longer has (or
   vice versa). Especially ORCHESTRATION_LAYER_STATE.md, CAPABILITY_LAYERS.md,
   the protocol, and the new proposal-subagent-gates.md.
3. **Rule-ladder coherence**: from the bottom package up to root, is every
   parent-rule link real and reciprocal? Does check-rule-ladder actually catch a
   broken link (test by reasoning, don't break real files)?
4. **Ledger vs reality**: does every assignments.json entry marked `proven`
   actually have its artifacts present? Any `blocked`/`in_progress` that's stale?
5. **Cross-module logic**: task_state + rule_ack + task_verify + dispatch +
   merge_queue — do their state models agree? (e.g. do the states in dispatch
   match VALID_STATES? does check-gates enforce the same states the state machine
   allows?) Find any inconsistency in the combined logic.
6. **Test honesty**: do the 24 test files actually assert behavior, or are any
   vacuous/always-pass? Spot-check the critical ones (gates, merge conflict).

<!--MORE-->

## Request

Go through ALL six dimensions. For each finding, record: dimension, severity
(blocker / should-fix / nit), the exact file+line or logic path, and whether it's
a real defect or acceptable. Produce a single audit report at
`registry/PLATFORM_AUDIT_20260701.md` structured by dimension. Only fix outright
breakage (broken link, gate that crashes, test that errors) and note each fix;
leave design-level findings as recommendations for Claude/user to decide.

End with an explicit verdict: is the platform coherent enough to commit the
lifecycle-gates work now, or are there blockers that must be fixed first?

## Constraints

- Coherence audit only; add no features; do not touch the customer-support
  package (user develops that separately in the Codex App).
- No secrets/auth/provider/home changes.
- Follow the collaboration protocol; reply in Codex Response with a summary +
  the report path; add a ledger entry; keep check-lab + check-collaboration green
  (or, if the audit finds check-lab SHOULD fail, say so loudly instead).

## Expected Artifacts

- `registry/PLATFORM_AUDIT_20260701.md` — findings by dimension, severity-ranked.
- Any outright-breakage fixes, each justified.
- Ledger entry for this audit.
- Codex Response with the commit-readiness verdict.

## Verification

- The report covers all six dimensions with concrete file/line references.
- check-lab + check-collaboration PASS (or a loud, justified explanation if not).

## Codex Response

Verdict: **READY TO COMMIT** after the audit fixes in `registry/PLATFORM_AUDIT_20260701.md`.

Report path: `registry/PLATFORM_AUDIT_20260701.md`.

Summary:

- Covered all six requested dimensions: gate enforcement reality, doc/code drift, rule-ladder coherence, ledger/artifact reality, cross-module state logic, and test honesty.
- Remaining blockers: **0**.
- Fixed outright breakage only:
  1. `scripts/check-agent-packages` unregistered-package crash path now reports `AGENT_PACKAGE_UNREGISTERED`.
  2. `lab_agents/task_verify.py` now promotes only `review -> verified`, matching `task_state`.
  3. `scripts/check-gates` now fails closed on invalid task-registry schema before lifecycle checks.
  4. `scripts/audit-agent-code` no longer skips package sources merely because the package is under lab `.tmp`.
  5. `tests/test_run_record.py` no longer assumes temp dirs are outside the parent git checkout.
- Design/doc findings are left as recommendations, chiefly stale Layer 6 interop wording, missing Layer 5 references for new gates, and proposal-vs-implementation lifecycle naming drift.
- Customer-support package was not touched.

Verification evidence:

- `python3 -m unittest discover -s tests` -> 144 tests OK.
- `scripts/check-async-execution` -> 9 passed, 0 failed, 0 timed out.
- `scripts/check-rule-ladder --json` -> pass, 7 workspaces, 1 agent unit, 0 failed links.
- `scripts/check-agent-packages --json` -> pass, 1 registry, 1 package, 3 agents, 0 failed links.
- `scripts/check-task-state --json` -> pass, 3 tasks, 3 done, 0 stale running.
- `scripts/check-merge-queue --json` -> pass, empty valid queue.
- `scripts/check-gates` -> OK: 3 tasks satisfy lifecycle gates.
- Final post-response/post-ledger gates: `scripts/check-collaboration` -> assignments OK: 18 entries, collaboration surfaces valid; `scripts/check-lab` -> lab structure valid.


