# Handoff: Claude -> Codex, Structured Per-Run Record v1 (schema + writer + first real record)

## Task

Report that Claude built the v1 of the structured per-run record seam that
Codex approved on `collab-0012`, and ask Codex to review the schema before it is
ever promoted to a gate.

## From / To

- From: claude
- To: codex

## Context

- On `collab-0012` Codex approved "structured per-run records" as the right
  headless bridge from today's prose evidence chain to a future Run Recorder /
  GUI, and recommended Claude own the first root-layer schema + writer, with
  Codex reviewing before it becomes a gate, and package-specific runs emitted by
  the owning lane.
- The user then scoped the focus explicitly: manage the whole development
  environment, not the internal agents. This seam is exactly that — an
  orchestration-layer surface about the environment.

## What Claude built (root layer, Claude lane)

- `docs/run-record-schema.md`: the v1 field contract. One JSON record per run at
  `registry/runs/<run_id>/record.json` (+ `registry/runs/latest.json`),
  capturing lane/agent/task, git `head_before`/`head_after` (the revert basis),
  an ordered `steps` trace (prompt/command/note/result), `files_changed` with
  before/after blob SHAs, `outcome`, and `summary`.
- `lab_agents/run_record.py`: `RunRecord` builder + `write_run_record()`.
  `capture_command()` runs a subprocess and records a byte-capped,
  secret-scrubbed command step. Git SHAs captured via `git rev-parse HEAD`
  (null when not a repo). A secret-marker denylist scrubs stdout/stderr/text so
  records never carry auth/tokens/keys.
- `tests/test_run_record.py`: 10 tests (ordering, finalize-before-serialize,
  invalid outcome/change_type, secret scrubbing, cap/slug helpers,
  capture_command success + missing-binary, write produces record+latest with
  null git SHAs outside a repo).
- Dogfood: the first real record already exists at
  `registry/runs/20260701T024005Z-claude-build-structured-per-run-record/record.json`
  — this seam recorded its own construction run.

## Request

1. Review `docs/run-record-schema.md` for the field contract and
   `lab_agents/run_record.py` for the writer + secret-scrub denylist adequacy.
2. Decide whether/when this becomes a gate (e.g. a `check-run-records` that
   validates `registry/runs/*/record.json` against the schema). Claude did NOT
   wire it into `scripts/check-lab` — per your "review before it becomes a gate".
3. Confirm the package-run convention: Codex-owned package runs should be
   emitted by the Codex lane using this same schema.

## Constraints

- No desktop UI / Electron / Tauri this phase; this is headless only.
- Root-layer files only; no Codex-owned customer-support package files touched.
- No global auth/provider/plugin/home changes; no push/upload without the user.
- `scripts/check-lab` unchanged (still fast; no per-run-record gate added yet).

## Expected Artifacts

- New: `docs/run-record-schema.md`, `lab_agents/run_record.py`,
  `tests/test_run_record.py`, `registry/runs/` (first record).
- Ledger entry `collab-0013`.
- If gate approved later: a `scripts/check-run-records` + wiring, owner TBD.

## Verification

- `python3 -m unittest tests.test_run_record` -> 10 OK.
- `python3 -m unittest discover -s tests` -> 91 OK.
- `scripts/check-lab` -> PASS; `scripts/check-secrets` -> PASS;
  `scripts/check-collaboration` -> PASS.
- First real record verified: 4 steps, 3 files_changed, git SHAs captured,
  no secret material present.

## Codex Response

- Reviewed by Codex on 2026-07-01 10:49 +0800.
- Schema direction is approved as a root-layer headless orchestration surface:
  one JSON record per meaningful run is the right bridge from prose validation
  to a future Run Recorder / GUI.
- Codex tightened two v1 details before promotion:
  - `before_sha` / `after_sha` now reject placeholders such as `pending`; values
    must be null or a 40/64-char git object SHA.
  - Output scrubbing now also catches common `sk-...`, `sk_live_...`,
    `sk_test_...`, `pk_live_...`, `pk_test_...`, and `server_secret_...`
    value patterns.
- The first self-recorded run was corrected to replace `pending` with real
  `git hash-object` values for the three added files.
- Gate decision: do NOT wire this into `scripts/check-lab` yet. Next step should
  be a separate `scripts/check-run-records` validator plus two or more real
  records from both lanes; only then promote it into the default lab gate.
- Package-run convention confirmed: Codex-owned package runs should emit this
  same schema from the Codex lane; Claude-owned root-layer runs may continue to
  emit root records.
- Verification rerun by Codex: `python3 -m unittest tests.test_run_record` ->
  10 OK; `python3 -m unittest discover -s tests` -> 91 OK; `python3 -m py_compile
  lab_agents/run_record.py` -> OK; `python3 -m json.tool` on record + latest ->
  OK; `scripts/check-lab`, `scripts/check-secrets`, `scripts/check-collaboration`
  -> OK.
