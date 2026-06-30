# Local Workspaces

This directory is for local scenario workspaces, proof runs, and long-horizon
agent experiments.

Workspace contents are intentionally not committed by default. Keep durable
project code in the lab root, `scripts/`, `docs/`, `tests/`, `waterflow/`,
`lab_agents/`, `.agents/skills/`, or `.codex/agents/`.

Each folder here is a medium environment under `docs/environment-layering.md`.
Each serious workspace should also follow `docs/rule-inheritance.md` so Codex
and Claude keep the root lab rules, the workspace rules, and any package rules
active at the same time.
Concrete agents should live one level lower inside the workspace, usually under
`agents/<package>/`, with package-local skills, tools, protocols, interfaces,
fixtures, and tests. These folders are workspaces/projects inside the wider
sandboxed lab, not separate sandboxes.

## Active Local Workspaces

- `support-agent-workspace/`: independent support-agent project repo. It is a
  scenario workspace managed from this lab, not a second agent-lab environment.
  Keep its product code, git history, exports, and runtime files inside that
  nested repo.

If a workspace becomes a real reusable project, promote it into its own clean
repository or add a narrow tracked path deliberately.
