---
name: waterflow-auditor
description: Use when auditing the Codex agent lab for workflow coordination defects, broken handoffs, missing validation, duplicate routes, cross-lane contamination, or repair briefs for Codex or Claude.
---

# Waterflow Auditor

Audit the lab as a graph of work paths. The first version is scoped to `/Users/liuchengxu/Desktop/codex-agent-lab` only.

## Workflow

1. Read the closest `AGENTS.md` and `README.md`.
2. Run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.
3. Run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` when change detection against the previous path index matters.
4. Read `outputs/shared/waterflow/waterflow-report.md`.
5. For each finding, use `outputs/shared/waterflow/waterflow-repair-briefs.md` as the repair packet.
6. For changed paths without findings, use `outputs/shared/waterflow/waterflow-change-briefs.md` as the validation handoff.
7. Use `outputs/shared/waterflow/waterflow-validation-plan.md` to choose the smallest check set that covers the changed waterway.
8. Use `outputs/shared/waterflow/waterflow-route-index.md` to collapse large path counts by route family and risk.
9. Use `outputs/shared/waterflow/waterflow-validation-plan-changed.md` when only changed waterways should be verified.
10. Run `scripts/waterflow-verify` when real command evidence is required.
11. Run `scripts/waterflow-stress --scale-paths 1200` when the user asks for high-pressure or realistic problem injection; increase or reduce `--scale-paths` as pressure, not as a fixed target.
12. Run `scripts/waterflow-incident` when the user asks whether Waterflow can handle a realistic complex failure and produce a repair handoff for Codex or Claude.
13. Re-run the scan after repairs and record evidence in `registry/VALIDATION.md`.

## Defect Families

- Missing core path or entrypoint.
- Agent or skill metadata is invalid.
- Script exists without validation evidence.
- Progress claims completion without validation.
- Duplicate agent or skill routing.
- Cross-project references that violate the lab-only boundary.
- Added, removed, or changed paths between scans.
- Auditor source, test, or design paths that changed without matching verification.
- Changed paths that need Codex/Claude validation handoff even when they are not defects.
- Clean graphs that still need an explicit validation plan.
- Validation commands that fail, time out, or produce evidence that contradicts the claimed status.
- Synthetic high-pressure fixtures that should produce expected findings without contaminating the real lab.
- Needle fixtures that prove small injected defects can be found inside a large otherwise-clean graph.
- Complex incident fixtures that combine metadata defects, cross-boundary references, changed paths, validation failures, and a Codex/Claude handoff.

## Guardrails

- Do not inspect or copy secrets.
- Do not modify global Codex auth, provider config, or plugin state.
- Do not connect this first version to `lcx-s-openclaw`.
- Do not treat a clean report as proof of product correctness; it only verifies workflow structure.
- Do not scan generated `outputs/` as source paths; report artifacts are evidence, not workflow inputs.
- Do not run validation plans from untrusted sources; the verifier executes plan commands as local shell commands.
- Stress fixtures must stay under `outputs/shared/waterflow/stress/` or another explicitly generated output path.
- Incident fixtures must stay under `outputs/shared/waterflow/incidents/` or another explicitly generated output path.
- Interpret stress `pass` as detector proof, not system health: expected bad paths must be detected and expected command failures must be recorded.
- Interpret incident `pass` as detection and handoff proof, not repair completion.
- Treat detector coverage as part of stress proof: every implemented finding code needs an injected problem case.
- Treat route index and changed-only plans as the first response to large scale; do not manually inspect every path unless the index points there.
