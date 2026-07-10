# Failure Patterns Library

The compounding asset behind [[PLATFORM_VISION]] pillar 1+3+4: every real trap
we hit becomes a structured, reusable pattern here, so the same class of bug is
caught (and taught) forever.

## Why this exists

A CS person's edge is years of pattern recognition — "I've seen this bug before."
A vibecoder's weakness is per-session amnesia. This library is the external,
never-forgetting version of that pattern recognition. It does not just record
what broke; it names the **class**, the **root cause**, and the **gate that
should exist** so the class can't recur silently.

## One file per pattern

Each `FP-NNN-slug.md` follows this contract:

- **Symptom** — what it looked like (usually "looks correct / looks like it runs").
- **Root cause** — the actual class of mistake.
- **Why a CS person catches it / a vibecoder doesn't** — the discipline gap.
- **The gate** — the mechanical check that should stop the whole class. Points at
  a real `scripts/check-*` where one exists, or marks it as a gate still to build.
- **Learning note** — the WHY, written for the user to internalize (pillar 4).
  A pattern with no learning note is incomplete: the goal is fewer repeats, not
  more automation.

## Rules

- A pattern is only "gated" when a real runnable check enforces it — an installed
  capability is not proof (mirrors the lab's `check-lab` honesty rule).
- The gate itself must be adversarially verified (dual-lane), because a gate can
  silently fail — see FP-002, where the safety gate itself had false-negatives.
- Seeded 2026-07-06 from three real incidents this session. Add to it whenever a
  new trap is hit; that is the compounding.

## Index

- [FP-001-fail-open-authorization](FP-001-fail-open-authorization.md) — a predicate
  returns "allow" on the untagged/unknown case (SEC-1 tenant isolation).
- [FP-002-safety-gate-silent-false-negative](FP-002-safety-gate-silent-false-negative.md)
  — a checker passes dangerous input because its own patterns are wrong.
- [FP-003-side-effect-without-dry-run-gate](FP-003-side-effect-without-dry-run-gate.md)
  — a script's pass path fires a live mutation with no apply/confirm gate.
