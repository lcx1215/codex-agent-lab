# FP-001 — Fail-open authorization

## Symptom

An access-control predicate returns "allow" for the case it didn't explicitly
handle. Code reads as correct; tests over tagged data pass. But an untagged /
legacy / unknown record is readable by anyone. (SEC-1: `canReadRun` returned
true when a run had no `tenant_id`; untagged runs bypassed tenant isolation.)

## Root cause

The default branch of an authorization decision is "yes." Authorization must
default to "no" and only say "yes" on an explicitly satisfied rule. Fail-open
means every case the author forgot becomes an open door.

## Why a CS person catches it / a vibecoder doesn't

A CS person instinctively asks "what does this return when the input is null /
empty / unrecognized?" — threat-model reflex. A vibecoder tests the happy path,
sees green, ships. The hole is in the case never tested, and "it works" hid it.

## The gate

- Fail-closed predicate for sensitive reads: `identityScope.mjs`
  `canReadSensitiveScopedRecord` (denies unscoped record AND unscoped requester).
- Non-vacuous isolation test that asserts tenant-A cannot read tenant-B
  (`tenantIsolation.test.mjs`) — not just that A can read A.
- Generalizable gate still to build: a linter that flags any auth predicate
  whose default/early-return path is `true`/allow.

## Learning note (the WHY, for you)

Every authorization function has an implicit "else." If you don't write the else,
the language writes it for you — and its default is usually "return whatever's
truthy," i.e. allow. **Write the deny first, then carve out the allows.** When
you see `if (!x) return true` in anything about access, that is almost always a
hole. This one habit closes a whole class of the scariest bugs.

Related: [[PLATFORM_VISION]], [[codex-agent-lab-resume-point]] (SEC-1 history).
