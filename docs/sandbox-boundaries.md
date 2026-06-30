# Sandbox Boundaries

This lab uses a project-scoped clean Codex home and a workspace-write sandbox. It is isolated for long-horizon agent development, but it is not an air-gapped environment.

## Protected Assets

- Codex auth files and account sessions.
- API keys, GitHub tokens, cookies, OTPs, private keys, and `.env` files.
- App/Plus lane state and API-relay lane provider config.
- Global plugin install/enable state.
- Durable progress and validation records.

## Writable Boundary

The clean-home config must keep:

- `sandbox_mode = "workspace-write"`
- `writable_roots` limited to this repository checkout.
- `exclude_tmpdir_env_var = true`
- `exclude_slash_tmp = true`
- `disable_response_storage = true`
- agent fan-out capped with `agents.max_depth = 1`.

Lab-local temporary files belong under `.tmp/`, which is ignored by git.
Static recursive sandbox scans prune `.tmp/` because async checks may create
and remove per-task scratch directories while the scan is running. The sandbox
gate still checks the top-level `.tmp/` directory permissions.

## Allowed Symlinks

Only these symlinks may leave their containing directory intentionally:

- `.codex-home/AGENTS.md` -> the active global Codex rules file.
- `.codex-home/agents` -> lab-local `.codex/agents`.
- `.codex-home/skills` -> lab-local `.agents/skills`.

Any other symlink that resolves outside this repository is a sandbox failure.

## Sandbox Skills

Sandbox-specific skills live under `.agents/skills/` and must stay lab-local
unless the user explicitly asks to promote them globally.

Current sandbox skill pack:

- `secret-boundary-auditor`: use before committing, pushing, sharing, or
  publishing sandbox artifacts that may expose secrets or machine-local details.
- `async-race-detector`: use when checks, scans, workers, or validation runners
  run concurrently or leave hidden stderr, timeouts, or residual processes.
- `tmux-omx-runtime-doctor`: use for OMX team, tmux pane, worker startup,
  green-light, or `omx-api exec` runtime failures.
- `sandbox-artifact-hygiene`: use when deciding whether generated outputs,
  logs, workspaces, and Waterflow artifacts should be committed, ignored,
  redacted, archived, or regenerated.

Run this gate after adding or editing sandbox-specific skills:

```bash
./scripts/check-sandbox-skills
```

## Network Boundary

Network access is explicit in the config because agent development may need current documentation, package indexes, GitHub, or provider APIs. Network access does not permit copying secrets into prompts, files, logs, or remote systems.

## Health Gate

Run this before relying on the clean-home lane:

```bash
./scripts/check-sandbox
```

`./scripts/check-lab` also invokes the sandbox gate.
`./scripts/check-lab` also invokes the sandbox skill gate.
