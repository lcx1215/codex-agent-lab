# NEXT SESSION — Claude resume point

Last updated: 2026-07-03 (+0800).
Read this first, then `registry/collaboration/assignments.json` for full state.

## Where we are

The lab is **finished as a development/governance environment (a)** and has been
**hardened well into a controlled pilot (b)**. All (a)/(b) items from the earlier
audit are CLOSED and PROVEN. What remains is (c): live multi-agent runtime
maturity and desktop UI, both deliberately deferred.

**Current tree is clean, both lanes quiet, all ledger items proven.** HEAD =
`9fdcb72` (pushed to origin/main). There is NO in-flight work to resume — this
session is a good point to pick a fresh (c) item or stop.

## Done this session (2026-07-03, Claude, all pushed)

- **collab-0019 ledger + handoffs committed** (`3eeda3b`): recorded the
  customer-support review governance trail.
- **Chinese README added** (`9fdcb72`): `README.zh-CN.md` + English TOC/lang-switch.
  Light polish only; honest positioning kept verbatim, no badges/marketing.
- **Full read-only code review of the customer-support package** filed to the
  neutral app-inbox as `outputs/shared/app-inbox/0005-customer-support-code-review.md`
  (+ layout review `0006`). 4-lane review of the in-flight migrated tree
  `workspaces/agent-dev-workspace/agents/customer-support/`. No Critical; 6 HIGH
  before real/multi-tenant use. **Codex-owned package — Claude review-only, no
  source touched.** These reviews live under `outputs/` (gitignored, not pushed).
- **Lab health re-verified**: check-lab + 6 granular gates all green; no TODO/skip
  debt; 24 python test files; README doc-links intact.

## Everything proven (ledger, as of 2026-07-01 evening)

- collab-0016 — worktree isolation + ordered fail-closed merge queue kernel
  (`lab_agents/worktree_merge_queue.py`, `scripts/worktree-merge-queue`,
  `scripts/check-merge-queue` wired into check-lab). Conflicts refused with
  `pre_merge_conflict`, target left clean. PROVEN.
- collab-0017 — end-to-end integration probe (task-state → worktree → merge-queue
  → run-record). Statuses `[merged, merged, refused]`, no conflict markers, probe
  cleaned, main reset to pre-probe HEAD. PROVEN.
- collab-0018 (mega-audit) — six-dimension coherence audit
  (`registry/PLATFORM_AUDIT_20260701.md`); fixed only outright breakage, 144
  unittest OK. PROVEN.
- collab-0018 (tenant-isolation) — token→tenant binding + 403
  `tenant_scope_mismatch` + real cross-tenant-denial test (3/3). Claude
  independently reviewed and PROVEN.

## The ONE open follow-up (not a Claude task)

Tenant-isolation fail-OPEN on untagged runs: `canReadRun` returns true when a run
has no `tenant_id`. **Line moved after the customer-support migration: no longer
`server.mjs:422` — the fail-open branch is now `identityScope.mjs:43`, reached via
`canReadRun` at `server.mjs:475-478`** (confirmed in 0005 SEC-1). Isolation only
binds already-tenant-tagged runs; legacy/untagged runs pass. Filed for the **Codex
App lane** as `outputs/shared/app-inbox/0002-tenant-isolation-failopen.md` (see
`outputs/shared/app-inbox/INDEX.md`). Acceptable as backward-compat now; tighten
to fail-closed before true multi-tenant production. This belongs to the
customer-support package (gitignored medium workspace, Codex-owned) — Claude does
not edit it; review-only.

## Remaining (c) gap list (deferred, pick from here if continuing)

- reliable scheduler with timeout/liveness (the omx-exec hang on the scorecard
  handoff is live evidence it has no liveness guard).
- durable long-horizon task state machine beyond flat markdown.
- agent-level observability (tokens/tools/failures/file-impact/rollback);
  `scripts/lab-dashboard` still only reports build timings.
- desktop UI + full live multi-agent runtime (deliberately last).

## Operating reminders (unchanged — see memory)

- `assignments.json` gets concurrent writes from Codex: python read-modify-write
  (load → check id absent → insert → dump → revalidate), NOT the Edit tool.
  Status enum = pending/in_progress/blocked/proven/abandoned; every entry needs
  `updated`. Handoffs need exact `## Task` / `## Request` / `## Expected Artifacts`
  / `## Verification` headers.
- `workspaces/*` is gitignored (except `workspaces/README.md`).
- Wait for both lanes quiet (`find -mmin`) before any commit/merge.
- `export PATH="/Applications/Codex.app/Contents/Resources:$PATH"` for a real
  `rg` before running check-lab/pytest by hand (macOS has no `timeout` either).
- Never `git push` without the user. HEAD `3f67c35` is local; last user-authorized
  push was earlier. Merges so far are LOCAL only.

## Still-blocked (unchanged)

- collab-0001 (OMC tmux team) stays `blocked`: runtime-v2 rewrote the old 250ms
  root cause but it CANNOT be retested from this non-tmux CLI (needs a real tmux
  session; the only live one is Codex's, off-limits).
