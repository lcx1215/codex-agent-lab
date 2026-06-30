# Handoff: Claude -> Codex, Domain-Neutral Agent Kernel

## From / To

- From: claude
- To: codex

## Task

Generalize the lab from "can develop a support-scenario agent" to "can develop
any large agent". The only runnable agent-behavior asset was a single
support-scenario contract; its safety guards are needed by every large agent but
were locked to one domain and one file.

## What Changed (branch `claude/neutral-agent-kernel`, not yet merged)

- New domain-neutral kernel `lab_agents/agent_kernel/`:
  - `core.py` neutral types (`Principal`, `ContextItem`, `Tool`, `Turn`,
    `Decision`, `PolicyContext`, risk ladder) - no product vocabulary.
  - `policies.py` 10 composable primitive factories (the generalized form of the
    support-scenario guards: input-size, sensitive-data, forbidden-action,
    cross-scope, foreign-subject, value-threshold, permissioned-tool, untrusted
    -instruction, grounded-answer, insufficient-evidence fallback).
  - `engine.py` ordered `DecisionEngine` with audit trace + annotation folding.
  - `eval_harness.py` neutral JSONL batch eval runner + disposition matrix.
- Neutrality is proven by `tests/test_kernel_neutrality.py`: two unrelated agent
  chains (infra-ops + research) are built inline on the kernel and behave
  correctly. Kept lean on purpose - no resident demo-family package, no scaffold
  script. A real agent builds its chain in its own `workspaces/` scenario.
- `docs/agent-behavior-kernel.md` + Layer 7 in `registry/CAPABILITY_LAYERS.md`
  + README wiring.

## Boundary Respected

- Did NOT touch the git-excluded support scenario contract
  (Codex owns that file). The kernel is a separate, additive,
  root-level capability; the support workspace can adopt it later as a
  composition, but that migration is left to its owner.
- No secrets, no auth, no Codex/provider state touched. Stayed in the lab root.

## Request

Review the kernel API and the inline neutrality proof for correctness and for any
domain leakage you can spot. If you agree it is neutral and useful, consider
adopting it in the support workspace by expressing its evaluator as a
`DecisionEngine` composition. Its 9 guards map 1:1 onto the kernel primitives;
that would retire the bespoke chain and make the workspace a true kernel
consumer.

## Expected Artifacts

- `lab_agents/agent_kernel/{core,policies,engine,eval_harness}.py`
- `docs/agent-behavior-kernel.md`
- `tests/test_agent_kernel.py`, `tests/test_kernel_policies.py`,
  `tests/test_kernel_neutrality.py`

## Verification

- `python3 -m pytest tests/test_agent_kernel.py tests/test_kernel_policies.py
  tests/test_kernel_neutrality.py -q` -> 29 passed, pure Python, no `rg` dependency.
- Full suite `python3 -m pytest -q` passes with `rg` on PATH (export
  `PATH=/Applications/Codex.app/Contents/Resources:$PATH`).
- `./scripts/check-secrets` -> OK. `./scripts/check-lab` -> OK.
  `./scripts/check-collaboration` -> OK.
- Pre-existing unrelated fragility: `tests/test_runtime_compatibility.py` fails
  in a subprocess that lacks `rg` on PATH, because `check-runtime-compatibility`
  lists `rg` as a *required* command though it is not a system binary on this
  Mac. Known rg-portability gap, not caused by this change; overlaps assignment
  `collab-0005` (rg-absent gate hardening) - left for that lane.
