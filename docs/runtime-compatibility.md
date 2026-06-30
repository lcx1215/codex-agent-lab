# Runtime Compatibility Contract

## Purpose

The lab should fail early on environment drift instead of letting Codex, Claude, OMX, or local harnesses discover basic setup problems halfway through a large agent build.

`scripts/check-runtime-compatibility` is the lightweight preflight for that layer. It checks local command availability, Python runtime support, script hygiene, runtime ignore rules, clean-home auth boundaries, and documentation wiring.

## Required Checks

- Required shell commands are on `PATH`: `bash`, `python3`, `git`, `rg`, `find`, `sed`, `stat`, `awk`, `grep`, `sort`, `tr`, and `wc`.
- Python is new enough for the lab scripts and can import required standard-library modules.
- Core lab directories exist.
- Scripts under `scripts/` have shebangs, executable bits, and LF line endings.
- `scripts/check-lab` aggregates the lightweight health gates that should protect normal development.
- Clean-home auth remains absent.

## Warning Checks

Optional runtime tools such as `codex`, `omx`, and `tmux` produce warnings instead of failures. They are needed for live runtime proofs, but ordinary static checks and documentation work should still be able to run without them.

If `CODEX_HOME` is set outside the expected lab or API-relay homes, the preflight warns instead of failing so the operator can confirm the lane before launching long work.

## Runtime State Rules

Runtime state belongs outside committable source:

- `.omx/` runtime state is ignored.
- `.omc/` runtime state is ignored.
- `.omc/skills/**` remains committable for future project-scoped OMC skills.

This prevents runtime noise from hiding real source changes while still allowing intentional project skills to enter the repo.

## Workspace Test Isolation

`scripts/new-workspace` defaults to `workspaces/` for real work. Tests and concurrent harnesses may set `WORKSPACE_ROOT` to a lab-internal temporary directory such as `.tmp/tests/...`.

The override is accepted only when it resolves inside the lab root. Paths outside the lab are rejected before directories are created.

## Error-Reduction Rules

- Prefer failing before model-backed work starts when required local tools are missing.
- Keep optional CLI proofs separate from default edit-loop health.
- Write compatibility artifacts under `outputs/shared/compatibility/` so dashboard and handoffs can distinguish environment drift from implementation bugs.
- Do not inspect or print secrets as part of compatibility checks.

## Health Gate

Run:

```bash
./scripts/check-runtime-compatibility
```

The command returns non-zero only for failed required checks. Warnings are visible but do not block normal work.
