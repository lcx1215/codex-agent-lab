# Handoff: verification of Codex's 2026-07-06 in-flight batch (Claude review-only → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane) — owner of the uncommitted 2026-07-06 evening batch
- Date: 2026-07-07 12:00 (+0800)
- Kind: independent read-only verification of in-flight, uncommitted Codex work (lab-root shared surfaces)
- Lane note: All targets below are lab-root shared scripts/docs (NOT the gitignored customer-support
  package). Claude reviewed read-only; did NOT edit, commit, or push any of them. Fix ownership stays
  with Codex. The one customer-support-package item (cutover script) is flagged for the Codex App lane.

## Task

Independently verify the untracked/dirty batch Codex left on 2026-07-06 evening (mtimes 16:24–21:59),
which has sat 14+ hours with no ledger entry and no return handoff:
- `scripts/check-side-effects` (+ its wiring into `scripts/check-lab`)
- `lab_agents/run_liveness.py`, `scripts/check-liveness`, `tests/test_run_liveness.py`
- `registry/failure-patterns/` (README + FP-001/002/003)
- `registry/PLATFORM_VISION.md`
- tracked diffs: `check-workspace-safety` (+`test_workspace_safety.py`), `lab-dashboard`,
  `sync-long-horizon-skills`, `VALIDATION.md`

Four parallel Claude subagents (2× verifier, code-reviewer, critic) plus direct runs by the lead.
`rg` was put on PATH from Codex.app Resources before every run.

## Request

Per-item verdict below. **One item is a still-live HIGH operational risk; the rest are safe to keep,
two need honesty/coverage fixes before commit.**

### 1. `check-side-effects` — NOT READY (unchanged since the 1930 review; all 3 defects still live)
Ground-truth run: `python3 scripts/check-side-effects .tmp/se-test` → `status: warn (fail=0 warn=3) EXIT=0`.
8 textbook-dangerous scripts, zero fails, exit 0. Independently reproduced with source line cites:
- **D1** `APPLY_GATE` (check-side-effects:59-62) self-whitelists the sink's own verb: `\bAPPLY\b` matches
  `kubectl apply` / `terraform apply`; `--force\b(?!-)` matches `git push --force`. a/b/c demoted fail→warn.
- **D2** `SINKS` (check-side-effects:46-55) blind to `flyctl`, `fly apps|volumes destroy`, `aws s3 rm`,
  `gh repo delete`, `docker push`, `npm publish` → d/e/f/h fully silent (not even warn).
- **D3** `\brm\s+-rf?\b` (check-side-effects:54) misses `rm -Rf` and `rm -fr` → g silent.
- **Wiring risk:** the gate is now called from `check-lab:106` but only over lab-root `scripts/` (all-clean),
  so `check-lab` reports OK while the gate waves through every dangerous sample → false green in CI.

### 2. cutover script — STILL-LIVE HIGH RISK (Codex App lane)
`workspaces/.../customer-support/scripts/cutover-fly-stable-model.sh` was modified post-incident and now
fires `fly secrets import -a "$APP"` on its **default path with no `--apply`/dry-run gate**. Worse: `import`
is a *different verb* than the `fly secrets set/unset` in `SINKS`, so even a fully-fixed check-side-effects
would not catch the very script that caused the 2026-07-06 live-cutover incident. This is app-inbox `0010`
(open). Until the gate exists, Claude will NOT run this script and only tests with guard-REJECTING input.

### 3. liveness tooling (`run_liveness.py` / `check-liveness` / test) — PARTIAL, honest, safe to keep
11/11 unit tests pass; `bash scripts/check-liveness` → `runs:10 finished:10 … status:pass` exit 0. No
skip/stub/placeholder. BUT it is a *post-hoc record auditor*, not the active timeout/kill scheduler the (c)
gap names: it only flags a `record.json` that sits unfinished past a deadline — a process that hangs before
writing a record (the actual omx-exec failure mode) is invisible. Not wired into check-lab or any scheduler.
Verdict: legitimate verified building block; do NOT mark the (c) liveness gap closed. (Minor: `check-liveness`
is bash — invoke via `bash`/`./`, not `python3`.)

### 4. `registry/failure-patterns/` — COMMENT, substantially accurate + honest, 4 MEDIUM fixes
FP-001/002/003 all cross-check accurately against their incidents (SEC-1 fail-closed at identityScope.mjs:55;
cutover incident in VALIDATION.md:38-62; check-side-effects defect reproduced live). Honesty rules in README
are strong. Fixes before commit:
- README:32-33 past tense ("had false-negatives") implies the gate is fixed — it is NOT. Make present tense
  + dated status.
- FP-002 never states `check-side-effects` is still installed-and-broken today — add a Status line.
- FP-003 says the incident used `fly secrets set`; the live script now uses `fly secrets import` and is still
  ungated — note both, and that `import` must be added to SINKS + samples.
- `.tmp/se-test` (the "must-become-locked-test" samples) is git-ignored — if failure-patterns/ is committed,
  the referenced proof doesn't travel. Move samples to a committed path (e.g. `scripts/tests/side-effects-fixtures/`).
- LOW: FP-001/FP-003 `[[...]]` links point at ~/.claude memory files that don't resolve in-repo; annotate as external.

### 5. `PLATFORM_VISION.md` — ACCEPT-WITH-RESERVATIONS
No (c) scope-creep, no production/open-source-engine drift, honesty guards strong; its proposed first step
(the failure-patterns library) was actually built. Reservations: (a) terminology drift — it rebrands the
private workbench as "the platform," softly collapsing the workbench-vs-product two-layer separation the
purpose doc insists on; reframe as a discipline/verification layer, not a platform the lab *is*. (b) header
says "Owner lane: claude (draft; Codex reviews)" but the file was authored by the Codex lane at 21:57 —
fix attribution. (c) untracked and unlinked from the resume path; link from assignments.json/NEXT-SESSION or
it dies in one session (the exact fate it warns about).

### 6. tracked diffs — GREEN
`test_workspace_safety.py` 4/4 pass (covers the new `SKIP_RECURSE_DIRS`/`iter_paths` in check-workspace-safety).
`sync-long-horizon-skills` gained an honest `# side-effects: gated` annotation. `lab-dashboard`, `VALIDATION.md`
changes read consistent with the incident record.

## Expected Artifacts

- `scripts/check-side-effects` — D1/D2/D3 fixed (per-sink gating; add `flyctl`, `fly apps|volumes destroy`,
  `aws s3 rm`, `gh repo delete`, `docker push`, `npm publish`, **`fly secrets import`**; order/case-tolerant
  `rm -[rRfF]+`), plus a committed test (`tests/test_check_side_effects.py`) locking the 8 samples as `fail`+exit≠0.
- `cutover-fly-stable-model.sh` — `--apply`/dry-run gate (app-inbox 0010) before it is ever run again.
- failure-patterns/ — 4 MEDIUM fixes above; then safe to commit.
- PLATFORM_VISION.md — terminology trim + attribution fix + resume-path link; then safe to commit.
- Ledger: open `collab-0021-check-side-effects-gate` (and optionally `collab-0022` for the liveness building
  block) when the fixes land — Claude did not open it, per owner-commits convention.

## Verification

What Claude ran (read-only, nothing changed):
- `python3 scripts/check-side-effects .tmp/se-test` → `warn fail=0 warn=3 exit=0` (all 8 dangerous samples pass/warn).
- `python3 -m pytest tests/test_run_liveness.py -q` → 11 passed, exit 0.
- `bash scripts/check-liveness` → `runs:10 finished:10 unfinished:0 stale:0 ill_formed:0 status:pass` exit 0.
- `python3 -m pytest tests/test_workspace_safety.py -q` → 4 passed, exit 0.
- FP cross-checks vs `identityScope.mjs:55`, `VALIDATION.md:38-74`, live cutover script content.
- `git diff --stat` + per-file diff of the 7 tracked-modified files.

Not done by Claude: no edit to any gate/script/doc, no ledger write, no commit/push. Both lanes were checked
quiet at review time (only mtime under `.omx/state/` in the last 30 min; the live Codex kernel pid was idle,
not writing source). Ledger `collab-0021` remains Codex's to open when the fix lands.
