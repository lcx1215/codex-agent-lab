# Reasoning Speed Playbook

This lab defaults important CLI work to `gpt-5.5` with `xhigh` reasoning. That improves hard-case reasoning, but it is not the fastest path for every step. The goal is to keep correctness while reducing avoidable wall-clock latency.

## Rule

Do not make the hard model think about easy work.

Use `gpt-5.5` + `xhigh` for architectural decisions, adversarial review, security-sensitive changes, cross-module reasoning, final integration, and high-risk debugging. Use faster or lower-effort paths for file discovery, command execution, simple edits, formatting, evidence collection, and routine validation.

Waterflow supervision follows the stricter contract in `docs/waterflow-speed-contract.md`: default supervision is non-blocking, changed-only, and route-index first; heavy validation is reserved for boundary checks.

## Practical Speed Levers

- Shrink context before the xhigh call: load only relevant files, current errors, and the exact acceptance checks.
- Use existing indexes and artifacts first: `registry/current-progress.md`, `registry/VALIDATION.md`, route indexes, changed-only validation plans, and workspace handoffs.
- Parallelize non-model work: run independent shell checks, file reads, scans, and tests concurrently when they do not write the same artifact.
- Use bounded specialists for lookup: explore/research passes should return compact facts, not full transcripts.
- Keep prompts outcome-shaped: objective, constraints, files, expected output, and stop condition.
- Avoid repeated xhigh re-planning: write the plan once, then execute small verified slices.
- Prefer changed-only checks first; run broader checks only when the changed surface justifies it.
- Keep generated artifacts concise enough for restart; do not paste large logs back into the model unless the failure requires them.
- For long-running work, checkpoint in files so a restart can resume from state instead of re-deriving context.
- Keep Waterflow out of the active Codex/Claude critical path unless a blocking rule in `docs/waterflow-speed-contract.md` applies.

## Async Safety

Parallelism speeds wall-clock time only when tasks are independent. Async tasks must not write the same output files, mutate global auth/provider/plugin state, or rely on shared system tmp paths.

Use this gate after changing async behavior, temp-file handling, sandbox boundaries, validation runners, or long-horizon execution scripts:

```bash
./scripts/check-async-execution
```

The gate runs independent checks concurrently with per-task `TMPDIR` and isolated Waterflow output directories.
Unexpected `stderr` is treated as a failure for quiet health checks, so race
warnings are not hidden behind an exit code of zero. Unit tests are explicitly
allowed to write progress output to `stderr`.

## When Not To Optimize

- Do not lower reasoning for security, auth, irreversible, or unclear architecture decisions.
- Do not parallelize tasks that write the same generated artifact unless the writer has locking or unique output directories.
- Do not trade verification for speed. If a faster lane cannot prove the result, keep the slower verification.
