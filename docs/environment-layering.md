# Environment Layering Contract

This lab uses three scale levels. The root lab stays maximally open and
scenario-neutral; narrower work belongs in nested surfaces.

All three levels are sandboxed work surfaces. `Sandbox` is a safety property of
the whole environment, not a name for one medium workspace.

## Scale Levels

### Maximum Environment

Location: lab root.

Purpose: the open integrated development environment for Codex, Claude, OMX,
Waterflow, shared harnesses, neutral kernels, and cross-scenario verification.
Both Codex and Claude enter this maximum environment by reading the root
lane-local rules (`AGENTS.md` for Codex, `CLAUDE.md` for Claude), this layering
contract, and the collaboration protocol.

The rule inheritance chain is defined in `docs/rule-inheritance.md`. A nested
workspace or agent package may add local detail, but it must not weaken the
maximum environment's safety, lane, sandbox, collaboration, or promotion rules.

Allowed here:

- scenario-neutral rules: `AGENTS.md`, `CLAUDE.md`;
- shared protocols: `docs/codex-claude-collaboration-protocol.md`;
- shared interfaces and kernels: `lab_agents/`, root-level `docs/`, `registry/`;
- lab-neutral skills: `.agents/skills/`;
- lab-neutral agents: `.codex/agents/`;
- Waterflow engine, scripts, speed contract, and global route supervision:
  `waterflow/`, `scripts/waterflow-*`, `docs/waterflow-*`;
- health, sandbox, collaboration, benchmark, dashboard, and compatibility gates.

Not allowed here:

- scenario-specific product assumptions;
- single-domain agent packages;
- workspace-local exports, runtime files, fixtures, or generated outputs;
- secrets, auth files, provider state, or plugin install state.

### Medium Environments

Location: `workspaces/<scenario>/`.

Purpose: a bounded scenario, product, proof, or long-horizon project. A medium
environment can be an independent git repo when that gives cleaner history and
ownership. Name these as workspaces or projects, not as the only "sandbox."

Allowed here:

- scenario-local `AGENTS.md`, `README.md`, `progress.md`, and validation notes;
- scenario protocols under `docs/contracts/` or equivalent;
- scenario interfaces such as OpenAPI, JSON schemas, eval schemas, and adapters;
- scenario-local skills under `.agents/skills/` or inside the relevant package;
- scenario-local Waterflow route maps, eval fixtures, reports, and handoffs;
- product/service code and tests for that scenario.

Not allowed here:

- global Codex/Claude provider, auth, plugin, or LaunchAgent configuration;
- root lab policy changes unless a pattern has cross-scenario evidence;
- unrelated scenario code.

### Small Agent Packages

Location: inside a medium environment, for example
`workspaces/<scenario>/agents/<agent-package>/`.

Purpose: one concrete agent family, agent package, or narrow capability bundle.

Allowed here:

- agent manifests, prompt files, local knowledge, tools, skills, and evals;
- agent-specific protocols and interfaces that are not shared outside the
  package;
- local fixtures and tests that prove that agent's behavior.

Not allowed here:

- lab-wide rules;
- cross-scenario protocols;
- shared Waterflow engine code;
- unrelated agent packages.

## Placement Matrix

| Surface | Maximum Environment | Medium Environment | Small Agent Package |
| --- | --- | --- | --- |
| Rules | root `AGENTS.md`, `CLAUDE.md`, `docs/rule-inheritance.md` | workspace `AGENTS.md`, optional `CLAUDE.md` pointer | package `AGENTS.md`, `CLAUDE.md`, README, or manifest |
| Skills | `.agents/skills/` only when scenario-neutral | workspace `.agents/skills/` or package-local | `agents/<pkg>/skills/` |
| Plugins | referenced from global/plugin cache; never installed here silently | adapter docs/config only | plugin-specific usage notes only |
| Protocols | cross-lane/cross-agent contracts in root `docs/` | scenario contracts under `docs/contracts/` | package protocol fragments |
| Interfaces | neutral kernels, shared schemas, root harness APIs | OpenAPI, JSON schemas, adapters | manifest/tool/eval schemas |
| Waterflow | engine, scripts, speed contract, global route supervision | workspace route maps and validation plans | agent-local fixtures and checks |
| Outputs | root `outputs/` for lab evidence only | workspace outputs or nested repo outputs | package-local test artifacts |

## Promotion Direction

Movement is one-way by proof, not by enthusiasm:

1. Small agent package proves behavior locally.
2. Medium environment proves the pattern is useful in a real scenario.
3. Maximum environment adopts only the reusable, scenario-neutral part.

Promotion requires cross-scenario value, a clear boundary, a check or test, and
no weakening of secret, auth, sandbox, lane, or plugin boundaries.

## Anti-Mixing Rules

- Do not put scenario/product agent code in the lab root.
- Do not put root Waterflow engine code inside a scenario workspace.
- Do not put global plugin install state in any workspace.
- Do not let a workspace or package-local rule file override, hide, or weaken
  parent lab rules.
- Do not copy a medium environment into root docs as if it defines the lab.
- Do not name one medium environment as if it alone were the sandbox.
- Do not promote a skill, protocol, interface, or gate because it helped one
  agent once; keep it local until repeated value is proven.
