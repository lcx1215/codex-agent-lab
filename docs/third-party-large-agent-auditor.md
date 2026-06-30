# Third-Party Large Agent Auditor

`third-party-large-agent-auditor` is a lab-local custom agent for judging whether this environment can support large-agent development from an external reviewer perspective.

## Purpose

The agent converts broad readiness questions into evidence-backed dimensions:

- intake;
- context;
- architecture;
- runtime;
- delegation;
- tooling;
- verification;
- observability;
- safety;
- handoff;
- performance;
- model-proof.

It is stricter than the development experience auditor. Comfort asks whether Codex and Claude can work smoothly here; this auditor asks whether a large-agent program can be trusted to run, scale, pause, resume, and report failures without losing safety boundaries.

## When To Use

Use it after adding new agents, runtime paths, workflow harnesses, model-backed proofs, or large scenario workspaces. Also use it before treating the lab as ready for a long-horizon multi-agent build.

## Output Contract

The agent should produce:

- an independent verdict;
- readiness score;
- capability matrix;
- top risk list;
- external reviewer notes;
- recommended next actions;
- exact evidence paths or commands.

## Harness

The deterministic harness lives in `lab_agents/large_agent_readiness.py`. It accepts `CapabilitySignal` records, computes a readiness report, and renders restartable Markdown.

The harness deliberately keeps mixed findings visible. Current known mixed areas should not be hidden: official team mode still needs fresh proof, and real model-backed smoke tests are too slow for the default edit loop.
