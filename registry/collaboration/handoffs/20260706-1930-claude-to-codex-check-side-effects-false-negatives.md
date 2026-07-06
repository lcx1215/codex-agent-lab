# Handoff: check-side-effects false-negatives (Claude review-only → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane) — owner of the uncommitted `check-side-effects` work
- Date: 2026-07-06 19:30 (+0800)
- Kind: independent review of in-flight, uncommitted Codex work (lab-root shared scripts)
- Lane note: `scripts/check-side-effects` is a lab-root shared script (NOT the gitignored
  customer-support package), so Claude may review it read-only. Claude did NOT edit the
  script, did NOT commit, did NOT push. Findings only; fix ownership stays with Codex.

## Task

Independently verify the new, uncommitted side-effects guard before it is committed:
- `scripts/check-side-effects` (new Python gate)
- `scripts/check-lab` (wires the gate into the default lab check)
- `scripts/sync-long-horizon-skills` (adds `# side-effects: gated` annotation)
- `.tmp/se-test/*.sh` (8 adversarial sample scripts left by Codex)

The gate exists to catch the class of the 2026-07-06 cutover incident: a script whose
*pass* path fires a live mutation. A report-only gate is only worth its exit code if it
actually `fail`s on ungated dangerous scripts.

## Request

Verdict: **NOT READY — the gate is silent on textbook-dangerous input.** Run against the
8 samples Codex itself left, the gate reports `fail=0`, `exit=0`. Three independent,
reproducible defects:

**D1 — `APPLY_GATE` matches the sink's own verb, laundering fail→warn.**
`APPLY_GATE` (check-side-effects.py:59-62) is `re.IGNORECASE` and scanned over the whole
script text. The command verbs ARE the tokens:
- `kubectl apply` → `apply` matches `\bAPPLY\b`
- `terraform apply` → same
- `git push --force` → the dangerous flag `--force` matches the `--force\b` gate token
So three ungated dangerous scripts are misclassified as "author wired a dry-run gate" and
demoted `SINK_UNGATED (fail)` → `SINK_GATED (warn)`. The dangerous action's own name
whitelists it. The gate should decide "gated" per-sink-line / by real flag *definition*
(e.g. `getopts`/`case` handling of `--apply`), not by any token appearing anywhere,
and `apply`/`--force`/`--execute` must not be gate tokens when they are the sink verb.

**D2 — SINKS list has large blind spots (silent, not even warn):**
- `flyctl secrets set` — SINK only matches `\bfly\s+secrets` (not `flyctl`). MISS.
- `fly apps destroy`, `fly volumes destroy` — SINK only matches `fly machines? …`. MISS.
- `aws s3 rm --recursive`, `gh repo delete --yes`, `docker push`, `npm publish` — not in
  SINKS at all. `f_gh_aws.sh` (4 dangerous commands) scans **`pass fail=0 warn=0`**.

**D3 — `rm` sink regex misses common variants.**
`\brm\s+-rf?\b` (check-side-effects.py:54) hard-codes `rf` order, case-sensitive, `?`
only makes the 2nd `f` optional. `rm -Rf` (capital R) and `rm -fr` (flags reversed) both
escape. `g_rm_variants.sh` → both lines missed.

**Scope defect (design, worth a line):** the gate defaults to scanning lab-root
`scripts/` only, but the actual incident culprit `cutover-fly-stable-model.sh` lives under
`workspaces/agent-dev-workspace/agents/customer-support/scripts/` (gitignored). The
default run never sees the very script this gate was born to catch — it must be pointed at
the package dir explicitly. Consider documenting/adding the package scan to the loop that
already reviews that package, or the gate gives false assurance.

## Expected Artifacts

- `scripts/check-side-effects` — D1/D2/D3 fixed; per-sink gating; `flyctl`, `fly apps|volumes
  destroy`, `aws s3 rm --recursive`, `gh repo delete`, `docker push`, `npm publish` added;
  `rm` regex made order/case tolerant (`-[a-zA-Z]*[rf]` style with both flags present).
- A test file (`tests/test_check_side_effects.py`) asserting the 8 `.tmp/se-test` cases —
  the ungated dangerous ones must be `fail`, exit non-zero. Right now `.tmp/se-test` is
  scratch with no test locking the behavior.
- Re-run: gate against `.tmp/se-test` must exit non-zero with the ungated samples as `fail`.

## Verification

What Claude ran (read-only):

- `python3 scripts/check-side-effects .tmp/se-test` → `status: warn fail=0 warn=3 EXIT=0`
  (expected: multiple fails, non-zero).
- Per-case regex replication confirmed D1 (apply/--force self-match), D2 (empty sink set
  for flyctl/aws/gh/fly-destroy), D3 (`rm -Rf`/`rm -fr` no match).
- `scripts/check-side-effects .tmp/se-test/f_gh_aws.sh` → `pass fail=0 warn=0`.
- `scripts/check-side-effects .tmp/se-test/h_flydestroy.sh` → `pass fail=0 warn=0`.
- Confirmed `cutover-fly-*.sh` live only under gitignored `workspaces/.../customer-support/scripts/`.
- Full `scripts/check-lab` (with gate wired in, `rg` on PATH) → `OK` — but note check-lab
  runs the gate against lab-root `scripts/` which is currently all-clean, so check-lab
  passing does NOT exercise any of these defects.

Not done by Claude: no edit to the gate, no ledger write, no commit/push. Ledger entry
(suggest `collab-0021-check-side-effects-gate`) is Codex's to open when the fix lands, per
the both-lanes-quiet + owner-commits convention.
