# Handoff: customer-support doc trim + scratch cleanup (Claude → Codex, informational)

- From: Claude (OMC lane)
- To: Codex (OMX lane) — customer-support package co-owner
- Date: 2026-07-07 17:00 (+0800)
- Kind: informational — package-local doc trim + gitignored scratch cleanup. No code, no runtime
  state, no git-tracked file, no commit, no push. `.run/` (runtime tokens) untouched.

## Task

Both docs were long, untracked, local-only history logs (2797 + 1918 lines). Trimmed to
current-state summaries; full history archived losslessly first.

- `agents/customer-support/docs/VALIDATION.md`: 2797 → 87 lines. Now current runtime state,
  latest gates (233/233), BFF artifacts, stable boundaries, open boundary only.
- `workspaces/agent-dev-workspace/progress.md`: 1918 → 88 lines. Now current focus, pause
  checkpoint, runtime surface, boundaries, next-owner work, debug entry only.
- Full originals archived, byte-identical (SHA-verified before trim):
  - `agents/customer-support/docs/archive/VALIDATION-full-through-20260707.md`
    (sha1 `402dd4a135f19e7e8428ef5017c1f45de48d043e`)
  - `agents/customer-support/docs/archive/progress-full-through-20260707.md`
    (sha1 `6105c451354374ebc08097a945ab64fc3bf3611a`)
  - Both trimmed files carry a top pointer to their archive copy.
- `agents/customer-support/.tmp/`: cleared 1.7M / 248 debug-loop scratch files (gitignored,
  regenerable). `.run/` NOT touched.

## Why

The two logs had grown to ~4700 lines of dated RED/GREEN checkpoints, most historical. Current
live state was hard to find. No content was lost — it moved to `docs/archive/`.

## Request

Informational only — no action required. For Codex:

- Nothing to fix or verify. If you expected the full history in the old location, it is intact
  under `docs/archive/`. New checkpoints append to the trimmed files as before.
- Gates re-run clean after the trim: `check-secrets` OK, workspace `check-portable.sh` passed,
  `check-agent-packages` `agents=3 failed_links=0`.
- If you prefer the archive indexed by theme (SEC / Fly / knowledge / BFF) instead of one flat
  dump, say so and I'll restructure it; current form is one lossless flat copy.

## Expected Artifacts

- Trimmed: `agents/customer-support/docs/VALIDATION.md` (87 lines),
  `workspaces/agent-dev-workspace/progress.md` (88 lines).
- Archived (byte-identical originals):
  `agents/customer-support/docs/archive/VALIDATION-full-through-20260707.md`,
  `agents/customer-support/docs/archive/progress-full-through-20260707.md`.
- This handoff note.
- No git-tracked file changed; no commit, no push; `.run/` untouched.

## Verification

- SHA-1 of each archive matches the pre-trim original: VALIDATION
  `402dd4a135f19e7e8428ef5017c1f45de48d043e`, progress
  `6105c451354374ebc08097a945ab64fc3bf3611a`.
- Both trimmed files contain a working pointer to their archive copy.
- Lab-root `./scripts/check-secrets` -> OK.
- Workspace `./scripts/check-portable.sh` -> passed.
- Lab-root `./scripts/check-agent-packages` -> `agents=3 failed_links=0`.
- Lab-root `./scripts/check-collaboration` -> re-run after adding this note.
