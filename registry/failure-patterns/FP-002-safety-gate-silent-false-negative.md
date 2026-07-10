# FP-002 — Safety gate with silent false-negatives

## Symptom

A checker meant to catch dangerous things reports "pass" on obviously dangerous
input. It runs, exits 0, looks like protection — but protects nothing. (The
`check-side-effects` gate: 8 textbook-dangerous scripts, `fail=0`, exit 0. Three
causes: its allow-token regex matched the sink's own verb (`kubectl apply`,
`git push --force` self-whitelisted); its sink list missed `flyctl`/`aws s3 rm`/
`fly destroy`/etc; its `rm -rf` regex missed `rm -Rf` / `rm -fr`.)

## Root cause

The check's own logic is wrong, and nothing tests the check against known-bad
input. A green checkmark from a broken checker is worse than no checker — it
manufactures false confidence.

## Why a CS person catches it / a vibecoder doesn't

A CS person writes the test that feeds the checker a bad input and asserts it
FAILS ("who watches the watchmen"). A vibecoder writes the checker, runs it once
on clean code, sees pass, trusts it. The checker is never adversarially probed.

## The gate

- Every gate must have a test that feeds it known-dangerous input and asserts a
  non-zero / FAIL result (the `.tmp/se-test` samples must become a locked test).
- Dual-lane: the gate is reviewed by the other lane, not self-approved — this is
  how the false-negatives were found (handoff `20260706-1930`).
- Meta-rule: a "pass" from any gate is only trustworthy if that gate has a
  red-team test proving it can say "fail."

## Learning note (the WHY, for you)

A test that only checks "good input passes" tests nothing about a safety tool —
its entire job is to reject bad input, so **the test that matters is "bad input
must fail."** Whenever you build a check, filter, validator, or guard, your first
test should be an attack that it must catch. If you can't write an input that
makes your guard fail, you don't yet know if your guard works.

Related: [[PLATFORM_VISION]] (pillar 2 adversarial dual-lane).
