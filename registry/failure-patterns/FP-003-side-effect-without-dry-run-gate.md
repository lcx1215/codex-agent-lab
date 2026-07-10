# FP-003 — Side effect without a dry-run / confirm gate

## Symptom

Running a script "just to test it" performs a real, irreversible action on live
state. There is no default-safe mode. (The cutover incident: a guard-PASSING
fake `LLM_API_KEY` fed to `cutover-fly-stable-model.sh` immediately ran
`fly secrets set` + rolled the live machine — no dry-run, no confirm. Testing it
mutated production; rollback to `anthropic-compatible` was needed.)

## Root cause

A script that mutates live state has its mutation on the DEFAULT path. Any run —
including a test — fires it. Safety requires the default run to be a no-op
preview, with mutation gated behind an explicit `--apply` / confirm flag.

## Why a CS person catches it / a vibecoder doesn't

A CS person separates "compute the plan" from "execute the plan" and makes
execute opt-in (dry-run by default) — burned once by a destructive default, they
never trust one again. A vibecoder writes the script to do the thing, and "run
it to see if it works" IS the destructive action.

## The gate

- Side-effecting scripts must be default-dry-run; live mutation only behind
  `--apply`/`--confirm`. (The `check-side-effects` gate is meant to enforce this —
  but see FP-002: that gate currently has false-negatives and must be fixed +
  red-team-tested before it can be trusted here.)
- Rule for testing: only ever test a side-effecting script with a
  guard-REJECTING input; a guard-PASSING input is exactly what fires the sink.

## Learning note (the WHY, for you)

"Let me just run it and see" is safe for a pure function and catastrophic for a
script that touches the world. Before you run ANYTHING that deploys, deletes,
force-pushes, or writes to a live system, ask: **"if this runs fully right now,
what changes in the real world, and can I undo it?"** If the answer isn't "a
dry-run preview / nothing," don't run it — add the `--apply` gate first. The safe
default is a preview; the dangerous default is action.

Related: [[PLATFORM_VISION]], [[destructive-op-verify-ownership-first]].
