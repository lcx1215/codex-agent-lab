# NEXT SESSION — Claude resume point

Last updated: 2026-07-06 (+0800).
Read this first, then `registry/collaboration/assignments.json` for full state.

## Where we are

The lab is **finished as a development/governance environment (a)** and has been
**hardened well into a controlled pilot (b)**. All (a)/(b) items from the earlier
audit are CLOSED and PROVEN. What remains is (c): live multi-agent runtime
maturity and desktop UI, both deliberately deferred.

**Current tree is clean, both lanes quiet, all ledger items proven.** HEAD =
`e120a17` (pushed to origin/main). There is NO in-flight Claude work to resume —
this session is a good point to pick a fresh (c) item or stop.

## Done 2026-07-06 (Claude, pushed)

- **SEC-1 tenant-isolation fail-OPEN is now CLOSED.** Codex implemented+deployed
  the fail-closed fix (app-inbox `0009`, handoff `20260706-1445`); Claude
  independently re-verified (Codex suite 34/34 + 7/7 Claude-authored predicate
  assertions vs `identityScope.mjs`, exit 0), filed receipt handoff
  `20260706-1530` and ledger `collab-0020-sec1-fail-closed-reverify` (proven).
  The "ONE open follow-up" section below is therefore RESOLVED (kept for history).
- **`scripts/audit-agent-code` hardened**: detects `child_process` spawn+shell:true
  / interpolation injection sinks; `exec(` matcher tightened. Self-verified.
- **⚠️ Incident (see `registry/VALIDATION.md`):** a cutover-script re-verify fed a
  guard-PASSING fake `LLM_API_KEY` and triggered a REAL live Fly cutover; rolled
  back to `anthropic-compatible` (version 9, health 200, `ANTHROPIC_*` intact).
  Follow-up + Codex backlog filed as app-inbox `0010`. **P0 there = add a
  `--apply`/dry-run gate to `cutover-fly-stable-model.sh` — that script lives in
  the Codex-owned customer-support package, so it is a CODEX task; Claude re-verifies
  with guard-REJECTING inputs only and will NOT run the cutover script again until
  the gate exists.**

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

## The ONE open follow-up — RESOLVED 2026-07-06 (kept for history)

**UPDATE: this is now CLOSED (SEC-1 fail-closed, see "Done 2026-07-06" above).**
The description below is the historical state before the fix.

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

### DX backlog (low-risk, Claude-doable, DEFERRED — do not start without a go)

Surfaced 2026-07-03 by a full health sweep (all gates green; no bug debt). These
are developer-experience polish, NOT runtime maturity. User said record-only for
now, do not implement:

- **Add `--help`/usage to the check scripts.** 17 of the `scripts/check-*` gates
  print no usage/args (`check-lab`, `check-collaboration`, `check-rule-ladder`,
  `check-agent-packages`, `check-workspace-safety`, `check-runtime-compatibility`,
  `check-task-state`, `check-secrets`, `check-sandbox`, `check-merge-queue`,
  `check-gates`, `check-run-records`, `check-project-rules`, `check-async-execution`,
  `check-sandbox-skills`, `check-speed-contract`, `check-workflow-modes`). Comment
  /usage-string only, no logic change — but it touches gate scripts, so keep it a
  reviewed pass, not a drive-by. Est: medium (21 files).
- **Onboarding / getting-started doc.** README is a thorough operating manual but
  there's no 5-minute "first run" path; no `CONTRIBUTING.md` / `docs/getting-started`.
  Pure new file, zero-risk. Est: small.

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
- Never `git push` without the user. As of 2026-07-03 HEAD `660ffc0` IS pushed to
  origin/main (user-authorized this session: ledger, README zh, this handoff).
  Push only over the gh HTTPS credential helper — SSH port 22 is blocked on this Mac.

## Still-blocked (unchanged)

- collab-0001 (OMC tmux team) stays `blocked`: runtime-v2 rewrote the old 250ms
  root cause but it CANNOT be retested from this non-tmux CLI (needs a real tmux
  session; the only live one is Codex's, off-limits).
