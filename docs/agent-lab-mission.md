# Agent Lab Mission

This repository is a strict, long-horizon agent development environment, not a throwaway sandbox.

## Mission

Build a rich, isolated, evidence-driven environment where Codex, Claude, and future agents can plan, execute, audit, verify, and hand off large engineering tasks without leaking secrets, breaking lane isolation, or losing durable progress.

## Quality Bar

- Isolation first: App, CLI, API-relay, OMX, clean-home, and project workspaces must have explicit boundaries.
- Secrets stay out: auth files, API keys, tokens, cookies, private keys, and session files are never copied into this lab or printed in logs.
- Durable state wins: important work writes progress, validation, and handoff artifacts before it depends on conversation memory.
- Evidence before claims: every completed capability needs a runnable check, captured result, or explicit validation gap.
- Richness means layered capability, not uncontrolled sprawl.
- Agents stay bounded: every delegated agent needs a named role, narrow task, expected output, and integration owner.
- Harnesses must test detection and reporting, not just happy-path success.
- Reader-facing docs should use relative paths and placeholders instead of machine-local paths.
- Promote repeated workflows into scripts, skills, prompts, or global rules only after they prove value locally.

## Capability Targets

- Project-local rule surfaces for every serious workspace.
- Workflow modes for App, CLI, OMX, multi-agent review, and checkpointed long-horizon work.
- Agent catalog with bounded roles, handoff contracts, and verification expectations.
- Lab-local skills and prompt packs for repeated workflows.
- Waterflow-style path auditing, route indexes, changed-only validation, stress fixtures, and incident rehearsals.
- Health gates for structure, secrets, rules, workflow modes, validation evidence, and generated handoffs.
- Restartable workspaces that can survive app restart, context compaction, or lane handoff.

## Expansion Rule

Every promoted capability should have:

- A written purpose and boundary.
- A clear entry command or invocation pattern.
- Expected artifacts.
- A verification command or check.
- A failure mode and recovery path.
- A promotion gate showing why it belongs in the lab, a skill, or global rules.

If a capability lacks these pieces, keep it experimental and local until the missing evidence exists.
