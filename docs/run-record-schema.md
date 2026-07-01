# Per-Run Record Schema

Last updated: 2026-07-01 11:10 +0800
Owner lane: claude (root-layer orchestration surface)
Status: v1 active — validated by `scripts/check-run-records`, now wired into
`scripts/check-lab`.
Related: `registry/ORCHESTRATION_LAYER_STATE.md` (this is the "structured
per-run logging" seam), `docs/codex-claude-collaboration-protocol.md`.

## Why

Today the lab's execution evidence lives as prose in `registry/VALIDATION.md`
and as gate stdout. That is durable but not structured, so it cannot be
queried, diffed, or later rendered by a Run Recorder / GUI. This schema is the
headless bridge: every meaningful agent run is captured as one JSON record with
enough state to answer "what ran, what changed, and how to revert it" — without
any desktop UI.

This is an orchestration-layer surface (about the *environment*, not about any
one agent's internal behavior).

## Storage

- One record per run: `registry/runs/<run_id>/record.json`.
- `run_id` = `<UTC-compact-timestamp>-<lane>-<short-slug>`, e.g.
  `20260701T023500Z-claude-self-audit`.
- A convenience pointer `registry/runs/latest.json` mirrors the newest record.
- Records are durable evidence and may be committed. High-volume rotation is a
  later concern (mirror the existing `outputs/**/runs/` rotation pattern).

## Record shape (schema_version 1)

```json
{
  "schema_version": 1,
  "run_id": "20260701T023500Z-claude-self-audit",
  "lane": "claude",
  "agent": "large-agent-readiness hardening",
  "task": "make verification run the gate, not stat it",
  "repo_root": "/abs/path/to/codex-agent-lab",
  "started_at": "2026-07-01T02:35:00+00:00",
  "ended_at": "2026-07-01T02:41:12+00:00",
  "git": { "head_before": "ce38ef4...", "head_after": "ce38ef4..." },
  "steps": [ { "index": 0, "kind": "prompt|command|note|result", "...": "..." } ],
  "files_changed": [
    { "path": "lab_agents/x.py", "change_type": "modified",
      "before_sha": "<blob-sha-or-null>", "after_sha": "<blob-sha-or-null>" }
  ],
  "outcome": "success|failure|aborted",
  "summary": "one-line human result"
}
```

<!--CONTINUE-->

## Field contract

- `schema_version` (int, required): currently `1`.
- `run_id` (str, required): unique, sortable, matches the directory name.
- `lane` (str, required): `claude` | `codex` | other declared lane.
- `agent` (str, required): which agent/surface produced the run.
- `task` (str, required): one line of intent.
- `repo_root` (str, required): absolute repo path the run acted on.
- `started_at` / `ended_at` (ISO-8601 str, required): `ended_at` may equal
  `started_at` for instantaneous records.
- `git.head_before` / `git.head_after` (str|null): commit SHAs bracketing the
  run. `head_after` == `head_before` means the run made no commit; working-tree
  edits are still captured in `files_changed`. These SHAs are the revert basis.
- `steps` (list, required, may be empty): ordered execution trace. Each step has
  `index` (int), `kind` (`prompt`|`command`|`note`|`result`), and kind-specific
  fields — `command`/`exit_code`/`stdout`/`stderr` for commands, `text` for
  prompts/notes/results. `stdout`/`stderr` are truncated to a byte cap.
- `files_changed` (list, required, may be empty): each entry has `path`
  (repo-relative), `change_type` (`added`|`modified`|`deleted`), and
  `before_sha`/`after_sha` (git blob SHA or null). Placeholder strings such as
  `pending` are invalid; unknown values must be recorded as null.
- `outcome` (str, required): `success` | `failure` | `aborted`.
- `summary` (str, required): one-line human-readable result.

## Boundaries (inherited from lab rules)

- No secrets: `stdout`/`stderr`/`text` must never carry `auth.json`, tokens,
  API keys, cookies, or `.env` values. The writer scrubs a denylist of markers
  plus common secret value patterns, and callers must not feed secret material
  in.
- Lane ownership: root-layer runs may be written by Claude; package-specific
  runs should be emitted by the lane that owns the package being changed
  (Codex's recommendation on `collab-0012`).
- This schema is a gate: `scripts/check-run-records` validates every
  `registry/runs/*/record.json` plus `registry/runs/latest.json`, requires both
  `claude` and `codex` lane records, verifies `latest.json` points to the newest
  run, and `scripts/check-lab` runs that validator.

## Writer

`lab_agents/run_record.py` provides `RunRecord` (a builder) and
`write_run_record(...)`. Callers build a record incrementally
(`add_prompt` / `add_command` / `add_note` / `record_file_change`), then
`finalize(outcome, summary)` and write it. `capture_command(...)` runs a
subprocess and appends a `command` step with a byte-capped, secret-scrubbed
stdout/stderr in one call. Git SHAs are captured via `git rev-parse HEAD`
(null when not a repo or git is unavailable).
