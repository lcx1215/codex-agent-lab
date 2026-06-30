# Rule Inheritance Contract

## Purpose

Codex and Claude must be able to start work from the lab root, a scenario
workspace, or a small agent package without losing the higher-level rules that
make the environment safe and coherent.

Local rules are additive and narrowing. A child directory may add scope,
commands, fixtures, package details, or stricter checks, but it must not weaken
parent rules for secrets, auth, provider config, plugin state, lane isolation,
sandbox boundaries, collaboration, or promotion.

## Effective Rule Chain

When working from any directory, the effective rule chain is:

1. Machine/global rules in the active Codex or Claude home.
2. Maximum-environment rules at the lab root:
   - `AGENTS.md` for Codex.
   - `CLAUDE.md` for Claude.
   - `docs/environment-layering.md`.
   - `docs/codex-claude-collaboration-protocol.md`.
   - this file.
3. Medium-environment rules in `workspaces/<scenario>/`:
   - local `AGENTS.md`.
   - local `CLAUDE.md` when present, usually as a pointer to the same local
     rules plus the root Claude contract.
   - local `README.md`, `brief.md`, `progress.md`, or validation notes.
4. Small-agent-package rules in `agents/<package>/`:
   - package `AGENTS.md`, `CLAUDE.md`, `README.md`, manifest, skills, tools,
     fixtures, and tests.

If a lower layer conflicts with a higher layer, the higher layer wins unless
the user explicitly changes the higher-layer contract.

## Medium Workspaces

Every serious workspace should make the parent rule chain visible near the top
of its local operating surface. The minimum declaration is:

- it inherits the root lab rules;
- it follows `docs/environment-layering.md`;
- it follows `docs/codex-claude-collaboration-protocol.md` for cross-lane work;
- local rules can only narrow or add detail;
- workspace changes use `scripts/check-workspace-safety` before promotion or
  before claiming the workspace is stable.

## Small Agent Packages

Every concrete agent package should declare its parent workspace and the root
lab inheritance chain in either `AGENTS.md`, `CLAUDE.md`, or a package README.

Small packages may define agent-specific tools, manifests, knowledge, evals, and
skills. They must not define lab-wide policy, global provider/auth/plugin state,
or cross-scenario protocols.

## Verification

Use:

```bash
./scripts/check-project-rules
```

to verify the root templates and rule-chain references.

Use:

```bash
./scripts/check-workspace-safety
```

when a workspace or package has changed and must be treated as stable.
