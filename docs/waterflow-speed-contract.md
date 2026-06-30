# Waterflow Speed Contract

Waterflow supervision must improve coordination without making Codex or Claude slower during ordinary work. The default path is advisory, incremental, and asynchronous. Heavy Waterflow checks run only at explicit boundaries.

## Operating Contract

- Default Waterflow supervision is advisory and non-blocking for active Codex and Claude work.
- The main worker path uses existing route indexes, changed-only validation plans, and compact handoff artifacts before running new scans.
- Full verification, stress fixtures, and incident fixtures are boundary tools, not per-edit tools.
- Supervision may block only for high-risk findings, secret or lane-boundary risk, destructive actions, release/PR gates, or an explicit user request.
- If Waterflow and a worker run at the same time, they must use isolated temp paths and unique output directories.

## Fast Path

Use this path for normal editing, exploration, and implementation loops.

- Read `registry/current-progress.md`, `registry/VALIDATION.md`, and the latest Waterflow route index before recomputing.
- Prefer `outputs/shared/waterflow/waterflow-route-index.md` to locate affected route families.
- Prefer `outputs/shared/waterflow/waterflow-validation-plan-changed.md` for changed waterways.
- Run cheap structural gates such as `scripts/check-speed-contract`, `scripts/check-project-rules`, and targeted syntax checks.
- Do not run stress, incident, full validation, or broad unit suites merely because a file changed.

## Boundary Path

Use this path before commit, push, PR, major handoff, or after a meaningful workflow change.

- Run a fresh Waterflow comparison when the graph changed enough that old route evidence may be stale.
- Run the smallest validation set that proves the changed route families.
- Run full Waterflow validation only when changed-only evidence is insufficient or a gate demands it.
- Record command evidence in `registry/VALIDATION.md` or a task-specific validation file.

## Stress Path

Use this path only for explicit resilience work, realistic problem injection, or scale rehearsal.

- Run stress and incident fixtures outside the active edit loop.
- Keep generated fixtures under `outputs/shared/waterflow/`.
- Treat stress pass as detector proof, not proof that the lab or product is healthy.
- Convert any real gap into a small repair, then return to the fast path.

## Blocking Rules

Waterflow can stop active Codex or Claude work only when at least one condition is true:

- P0 or P1 coordination, secret, lane, auth, or destructive-action risk.
- A planned action would modify global auth, provider, plugin, or app state.
- The user asks for a high-pressure Waterflow test or a full audit.
- The work is at a commit, push, PR, release, or external handoff boundary.
- Changed-only evidence contradicts the claimed state.

All other findings should become repair briefs or next-check recommendations while the main worker keeps moving.

## Performance Budgets

- Default health checks stay metadata-only or changed-only.
- No default gate may invoke stress fixtures, incident fixtures, full Waterflow verification, broad unit discovery, async fan-out, or workspace-wide safety sweeps.
- Async supervision must write per-run artifacts and per-task temp paths.
- Route-index lookup comes before manual path inspection at large scale.
- A scaling target such as 10000 paths is a pressure parameter, not permission to inspect every path inline.

## Verification

Run this lightweight gate after changing Waterflow supervision, speed routing, async execution, or default health gates:

```bash
./scripts/check-speed-contract
```

The gate checks the contract and routing metadata only. It must not run stress, incident, broad unit, or full Waterflow validation commands.
