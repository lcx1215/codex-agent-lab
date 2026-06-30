# Agent Lab Mission

This repository is a strict, long-horizon agent development environment, not a throwaway sandbox and not a single-scenario product template.

## Mission

Build a rich, isolated, evidence-driven environment where Codex, Claude, and future agents can plan, execute, audit, verify, and hand off very large engineering tasks without leaking secrets, breaking lane isolation, or losing durable progress.

The lab is scenario-neutral. UCP agents, commercial customer-service agents, research agents, code-maintenance agents, workflow agents, evaluation agents, and future agent families should all fit here as workspaces, not as constraints on the environment.

The lab amplifies Codex and Claude. It gives them durable memory surfaces, harnesses, route indexes, health gates, benchmarks, isolated workspaces, and handoff contracts. It must not pretend to replace their reasoning, coding, review, or recovery ability with rigid automation.

## Quality Bar

- Isolation first: App, CLI, API-relay, OMX, clean-home, and project workspaces must have explicit boundaries.
- Secrets stay out: auth files, API keys, tokens, cookies, private keys, and session files are never copied into this lab or printed in logs.
- Durable state wins: important work writes progress, validation, and handoff artifacts before it depends on conversation memory.
- Evidence before claims: every completed capability needs a runnable check, captured result, or explicit validation gap.
- Richness means layered capability, not uncontrolled sprawl.
- Simplicity wins at equal effect: if two designs preserve the same safety, speed, isolation, and verification value, choose the one with fewer moving parts.
- Openness means new agent families can be added without rewriting the lab's identity.
- Amplification over replacement: scripts, skills, Waterflow, OMX, and dashboards should increase Codex/Claude leverage while leaving final reasoning, integration, and verification ownership explicit.
- Agents stay bounded: every delegated agent needs a named role, narrow task, expected output, and integration owner.
- Harnesses must test detection and reporting, not just happy-path success.
- Reader-facing docs should use relative paths and placeholders instead of machine-local paths.
- Promote repeated workflows into scripts, skills, prompts, or global rules only after they prove value locally.
- Keep heavyweight harnesses, broad scans, model-smoke checks, and multi-agent orchestration on demand unless they are needed to prove the current claim.

## Capability Targets

- Project-local rule surfaces for every serious workspace.
- Workflow modes for App, CLI, OMX, multi-agent review, and checkpointed long-horizon work.
- Agent catalog with bounded roles, handoff contracts, and verification expectations.
- Lab-local skills and prompt packs for repeated workflows.
- Waterflow-style path auditing, route indexes, changed-only validation, stress fixtures, and incident rehearsals.
- Health gates for structure, secrets, rules, workflow modes, validation evidence, and generated handoffs.
- Restartable workspaces that can survive app restart, context compaction, or lane handoff.
- Scenario workspaces that remain local examples unless their patterns prove broadly reusable.

## Expansion Rule

Every promoted capability should have:

- A written purpose and boundary.
- A clear entry command or invocation pattern.
- Expected artifacts.
- A verification command or check.
- A failure mode and recovery path.
- A promotion gate showing why it belongs in the lab, a skill, or global rules.
- A leanness check showing why an existing document, script, skill, or workspace-local note is not enough.

If a capability lacks these pieces, keep it experimental and local until the missing evidence exists.
