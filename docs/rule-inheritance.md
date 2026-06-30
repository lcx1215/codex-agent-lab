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

## Rule Ladder Integrity

The inheritance chain is a ladder. Work can start from the maximum environment
or from a small agent package or nested subagent unit, but every middle link
must exist.

Broken ladder links are hard failures:

- missing root `AGENTS.md`, `CLAUDE.md`, environment-layering contract,
  collaboration protocol, or this file;
- missing workspace `AGENTS.md`;
- workspace rules that do not declare the parent rule chain;
- agent packages or subagent units with no local rule surface;
- agent packages or subagent units whose local surfaces do not declare the
  parent rule chain.

Run:

```bash
./scripts/check-rule-ladder
```

This is a metadata-only gate. It reads rule surfaces and manifests, not business
fixtures or generated outputs, so it can be part of the root health check
without becoming a workspace-wide safety sweep.

Agent and subagent catalogs are the next ladder link. Any `agents/` or
`subagents/` catalog inside a workspace or package must use `registry.json` to
list each package/subagent directory and every direct `*.agent.json` manifest.
Each manifest id must match the registry id, and entry agents must point to
registered manifests. Run:

```bash
./scripts/check-agent-packages
```

when adding, moving, renaming, or splitting agent packages or nested subagent
units. This is semantic, not scenario-specific: the same rule applies to
support agents, UCP agents, eval agents, code agents, workflow agents, and any
future agent family.

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

Every concrete agent package or nested subagent unit should declare its parent
workspace/package and the root lab inheritance chain in either `AGENTS.md`,
`CLAUDE.md`, or a local README.

Small packages and subagent units may define agent-specific tools, manifests,
knowledge, evals, and skills. They must not define lab-wide policy, global
provider/auth/plugin state, or cross-scenario protocols.

## Verification

Use:

```bash
./scripts/check-rule-ladder
```

to verify the root/workspace/package ladder is continuous.

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
