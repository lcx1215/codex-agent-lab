---
name: external-review-acceptance-gate
description: Use when external code review reports security, auth, storage, deployment, or semantic-gating issues and a branch must be accepted, fixed, classified, committed, or pushed after independent verification
---

# External Review Acceptance Gate

## Overview

External review findings are test cases to verify, not orders to obey. The job is to turn each finding into code evidence, a narrow fix or rejection, fresh validation, and a deploy/no-deploy verdict.

## When To Use

Use this when:
- A reviewer, bot, or another agent reports multi-item findings.
- The findings touch auth, security, storage, request routing, deployment docs, or model/intent gates.
- You must decide whether a branch is safe to push or ship.

Do not use this for trivial style nits or single-line typo fixes.

## Acceptance Ledger

For every finding, build a ledger before pushing:

| Field | Required evidence |
|---|---|
| Original claim | Reviewer text and affected path/function |
| Local reality | Current branch, HEAD, remote HEAD, relevant code path |
| Impact | Blocking, non-blocking backlog, or false positive |
| Fix | Commit or diff that addresses exactly this issue |
| Regression proof | Test name, command, pass/fail count |
| Residual risk | What still remains and why it is not blocking |

## Gate Sequence

1. Anchor the branch: `git status --short --branch`, `git log --oneline -5`, and `git fetch` the target remote branch before push.
2. Verify the report against source. Trace the real path end to end for auth, request headers, identity, storage keys, replay, and public/private endpoint boundaries.
3. Classify severity:
   - Blocking: auth bypass, production 401, data loss, cross-tenant leakage, request-path table scan, broken startup, dead deploy path, failing tests.
   - Non-blocking backlog: semantic edge cases, future scale concerns, operational TTL setup, known false positives with safe fallback.
   - Reject: reviewer assumed a path, profile, or runtime that the current repo does not use.
4. Fix narrowly. Do not rewrite surrounding docs, paths, or architecture unless the finding requires it.
5. Add regression tests that prove both sides of the boundary.
6. Run fresh validation after the final commit, not before it only.
7. Push only the intended branch. Prefer fast-forward push; do not force-push unless the user explicitly asked for history rewriting.

## Boundary Test Patterns

Auth/header fixes:
- Prove the real product token source is used, not only a storage guess.
- Prove production routes stay behind the product auth filter.
- Prove local/dev bypasses are profile-scoped.

Storage fixes:
- Prove identity keys include tenant, merchant, and person where required.
- Prove replay/idempotency writes use atomic conditional puts.
- Prove paginated reads do not truncate detail views.
- Prove request paths do not perform unbounded table scans.

Semantic gates:
- Test bypass examples, not only happy paths.
- Include a realistic page context saturated with domain terms.
- Test legitimate in-domain examples to avoid harming real users.
- Record remaining semantic gaps as backlog when they are not deploy blockers.

Deployment/docs:
- Check that documented filenames exist.
- Remove obsolete hosted-provider references when the architecture retired them.
- Keep local paths and internal lab artifacts out of company-facing docs.

## Output Shape

Report in this order:
1. Branch and remote HEAD.
2. Findings ledger summary.
3. Commits made.
4. Verification commands and exact pass/fail/skip counts.
5. Push target and resulting remote HEAD.
6. Non-blocking backlog.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Trusting reviewer context blindly | Reproduce or trace the current code path first |
| Fixing only the reported symptom | Add a regression for the boundary that failed |
| Calling a semantic edge case a blocker | Block only when it can break safety, auth, data, deployment, or core UX |
| Pushing the local helper branch name | Push `HEAD:<intended-remote-branch>` |
| Saying tests passed from a previous run | Re-run after the final commit |
| Mixing skill/lab files into product delivery | Commit product repo and lab skill repo separately |

## Stop Condition

The branch is ready only when every blocking finding is fixed or disproven, fresh validation passes, the remote branch is advanced intentionally, and remaining risks are listed as non-blocking backlog.
