# Workspace Safety Contract

## Purpose

Workspaces are where large agents, proofs, scenario experiments, and long-horizon tasks happen. They must be flexible enough for Codex or Claude to create files while working, but strict enough to catch dangerous drift before it reaches the rest of the lab.

`scripts/check-workspace-safety` is the workspace-level boundary gate. It distinguishes active in-progress gaps from hard safety failures, and it runs explicitly after workspace changes, before promotion, or when a workspace must be treated as stable. It is not part of the root default fast path.

## Hard Failures

The gate fails when a workspace contains risks that can damage isolation or leak credentials:

- secret-like committable file paths such as `auth.json`, `.env`, private keys, token files, or secret files;
- symlinks that resolve outside the lab root;
- workspace runtime state that is not ignored by git;
- workspace-local `.codex-home/auth.json`;
- workspace paths that resolve outside the lab root.

## Warnings

The gate warns, but does not block, when a workspace appears in-progress:

- missing `AGENTS.md`, `brief.md`, or `progress.md`;
- missing local `.gitignore`;
- no validation surface yet (`validation.md`, `VALIDATION.md`, `registry/VALIDATION.md`, or `tests/`);
- missing explicit parent rule-chain declaration in a workspace `AGENTS.md`;
- missing explicit parent rule-chain declaration in an agent package README, `AGENTS.md`, `CLAUDE.md`, or manifest;
- machine-local `/Users/...` paths inside workspace source files;
- intentional workspace-local `.codex-home` runtime without `auth.json`.

Warnings are visible in the report so Codex or Claude can repair them before promotion, but they do not stop another agent that is actively creating a workspace.

## Runtime State

Workspace runtime state should not become source truth. Root `.gitignore` should ignore `.omx/`, `.omc/` runtime state, temporary files, logs, and secret-like paths. Project-scoped OMC skills remain the exception when placed under `.omc/skills/**`.

## New Workspace Template

`scripts/new-workspace` creates:

- `AGENTS.md`
- `CLAUDE.md`
- `brief.md`
- `progress.md`
- `agents/README.md`
- `.gitignore`

Tests and harnesses may set `WORKSPACE_ROOT` to a lab-internal temporary directory. The script rejects outside-lab workspace roots before creating directories.

## Health Gate

Run:

```bash
./scripts/check-workspace-safety
```

The command returns non-zero only for hard failures. Warnings are expected while Codex or Claude is actively building a new workspace.
