# Waterflow Auditor Design

## Purpose

Waterflow Auditor is the lab's workflow coordination diagnostic layer. It treats every durable work surface as a water path: global and local rules, README files, custom agents, skills, scripts, registry evidence, task workspaces, reports, and repair briefs.

The first version is intentionally scoped to `/Users/liuchengxu/Desktop/codex-agent-lab`. It does not connect to `lcx-s-openclaw`, does not mutate global auth/config/plugin state, and does not try to repair problems automatically.

## Model

The scanner builds a graph:

- Nodes: lab root, rules, README, custom agents, skills, scripts, registry files, workspace folders, auditor source, tests, and design docs.
- Edges: containment and explicit references discovered in agent instructions.
- Evidence: relative path, content hash, size, and generated report timestamp.

The initial graph supports dozens of paths. The same representation can scale to thousands of paths because every node and edge has stable IDs and file hashes, which allows future incremental scans instead of full rework.

## Defect Families

- `MISSING_CORE_PATH`: a required work surface is absent.
- `AGENT_MISSING_FIELD` or `AGENT_TOML_INVALID`: custom agent routing is invalid.
- `SKILL_MISSING_ENTRYPOINT` or `SKILL_MISSING_FIELD`: skill discovery is broken.
- `SCRIPT_NOT_EXECUTABLE`: an intended command cannot run directly.
- `SCRIPT_WITHOUT_VALIDATION_REFERENCE`: a runnable script lacks validation evidence.
- `PROGRESS_WITHOUT_VALIDATION`: progress claims completion without evidence.
- `DUPLICATE_AGENT_NAME` or `DUPLICATE_SKILL_NAME`: routing is ambiguous.
- `CROSS_PROJECT_REFERENCE`: lab-only workflow references an excluded outside project.

Each finding includes a repair brief that can be handed to Codex or Claude.

## Interfaces

- CLI: `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`
- CLI diff: `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last`
- JSON report: `outputs/shared/waterflow/waterflow-report.json`
- Markdown report: `outputs/shared/waterflow/waterflow-report.md`
- Repair briefs: `outputs/shared/waterflow/waterflow-repair-briefs.md`
- Change briefs: `outputs/shared/waterflow/waterflow-change-briefs.md`
- Validation plan: `outputs/shared/waterflow/waterflow-validation-plan.md` and `outputs/shared/waterflow/waterflow-validation-plan.json`
- Changed-only validation plan: `outputs/shared/waterflow/waterflow-validation-plan-changed.md` and `outputs/shared/waterflow/waterflow-validation-plan-changed.json`
- Validation runner: `scripts/waterflow-verify`
- Validation results: `outputs/shared/waterflow/waterflow-validation-results.md` and `outputs/shared/waterflow/waterflow-validation-results.json`
- Route index: `outputs/shared/waterflow/waterflow-route-index.md` and `outputs/shared/waterflow/waterflow-route-index.json`
- Stress runner: `scripts/waterflow-stress`
- Stress results: `outputs/shared/waterflow/stress/*/waterflow-stress-results.md`
- Incident runner: `scripts/waterflow-incident`
- Incident handoff: `outputs/shared/waterflow/incidents/*/codex-claude-handoff.md`
- Harness philosophy: `docs/waterflow-harness-philosophy.md`
- Path index: `outputs/shared/waterflow/waterflow-path-index.json`
- Path diff: `outputs/shared/waterflow/waterflow-path-diff.json`
- Python API: `waterflow.auditor.scan_lab(root)`
- Python index API: `waterflow.auditor.build_path_index(report)` and `waterflow.auditor.diff_path_indexes(previous, current)`
- Python validation API: `waterflow.auditor.run_validation_plan(plan)` and `waterflow.auditor.build_validation_results_markdown(results)`
- Python incident API: `waterflow.incident.run_incident_suite(output_root)`

## Path Index and Diff

Every scan can emit a path index keyed by relative path. Each entry stores the node id, kind, label, hash, and size. This is the v1 substrate for future 10,000-path incremental scanning: later versions can replace the hash strategy with a Merkle tree or byte-range probe without changing the report boundary.

`--compare-last` reads the previous `waterflow-path-index.json` from the output directory before overwriting it. The resulting `waterflow-path-diff.json` reports added, removed, changed, and unchanged paths. This makes small changes visible without requiring the auditor to rescan unrelated downstream workflows.

Each diff path includes impact metadata: route kind, coarse risk level, and recommended checks. This lets Codex or Claude choose the right validation path for agent, skill, script, registry, documentation, and auditor-code changes.

When a diff is present, the auditor also emits change briefs. Change briefs are not defect reports; they are scoped handoff packets for validating added, removed, or changed paths. Repair briefs remain reserved for actual findings.

## Validation Plan

Every scan emits a validation plan. The plan deduplicates checks across all current graph paths and ranks them by route risk. It tells Codex or Claude which command validates which waterway family, so a clean graph still has an explicit operational check list.

The plan currently derives checks from path impact classification. For example, agent and skill paths require `scripts/check-lab` plus Codex discovery checks, auditor-code paths require the unit test command, and all route families keep `scripts/waterflow-scan` as the structural audit.

When a path diff exists, the auditor also emits a changed-only validation plan. This plan is scoped to added, removed, and changed paths, so large graphs can be checked by impact surface instead of re-validating every stable route.

When a scan runs without comparison context, stale path-diff and change-brief artifacts are removed and the changed-only validation plan is rewritten as an empty scoped plan. This prevents old change surfaces from being mistaken for current evidence after a normal scan or validation run.

## Route Index

Every scan emits a route index grouped by route family, max risk, changed path count, finding codes, and recommended checks. The route index is the first navigation surface for large graphs: start with changed route families and high-risk route families before inspecting individual paths.

## Validation Results

`scripts/waterflow-verify` executes the commands from `waterflow-validation-plan.json` with the lab root as the working directory. It records each command, route family, covered paths, exit code, timeout state, duration, stdout, and stderr. The verifier writes machine-readable JSON plus a Markdown evidence report.

This keeps planning separate from proof: `waterflow-scan` says which checks should run, while `waterflow-verify` records what actually happened.

## Stress Fixtures

`scripts/waterflow-stress` creates generated fixture labs under `outputs/shared/waterflow/stress/`.

The problem fixture injects realistic workflow defects: missing core files, invalid agent TOML, missing agent fields, duplicate agent and skill names, missing skill entrypoints, missing skill metadata, empty registry evidence, non-executable scripts, scripts without validation evidence, cross-project references, and progress claims without validation.

The scale fixture creates a clean high-path lab with many agents, skills, scripts, docs, tests, and workspaces. It is intended to prove the graph scanner can handle larger route counts without turning generated output artifacts into workflow inputs.

The needle fixture creates a mostly clean high-path lab and injects a small set of defects. It proves the auditor can surface tiny faults inside a large graph instead of only catching dense problem fixtures.

The validation stress plan intentionally runs one passing command, one failing command, and one timing-out command. A successful stress run means these failures were detected and recorded, not that all commands passed.

The deeper philosophy is documented in `docs/waterflow-harness-philosophy.md`: problem fixtures test sensitivity, scale fixtures test stability, and expected command failures test evidence capture.

The stress harness also enforces detector coverage. It reads implemented finding codes from `waterflow/auditor.py` and fails if any implemented detector is not represented by an injected problem fixture. This found and closed one coverage gap: `EMPTY_REGISTRY_FILE` existed as a detector before the stress fixture injected an empty registry file.

## Incident Harness

`scripts/waterflow-incident` creates a realistic complex failure rehearsal under `outputs/shared/waterflow/incidents/`.

The incident harness starts from a clean baseline fixture, then creates a broken incident fixture with a missing README, malformed and incomplete agent metadata, duplicate agent and skill routes, missing skill entrypoints, missing skill metadata, a non-executable script, missing validation references, empty registry evidence, a cross-project reference, and a completion claim without proof.

The runner compares the clean baseline path index to the incident path index, so the output includes added, removed, and changed route evidence rather than only a static bad snapshot. It then executes an incident validation plan with one passing command, one failing command, and one timeout. The expected command failures are evidence capture tests, not repair failures.

The key artifact is `codex-claude-handoff.md`. It gives Codex or Claude a direct repair packet: incident summary, route-family breakdown, exact findings and evidence, failed command evidence with exit codes and timeout state, repair order, minimal verification commands, and artifact paths.

An incident harness pass means the bad fixture was detected and reported in a repairable form. It does not mean the incident fixture or the real lab has been repaired.

## Boundaries

In scope:

- `AGENTS.md`
- `README.md`
- `.codex/agents/*.toml`
- `.agents/skills/*/SKILL.md`
- `scripts/*`
- `registry/*`
- `workspaces/*`
- `waterflow/*`
- `tests/*`
- `docs/*`

Out of scope for v1:

- `lcx-s-openclaw`
- global auth/config/plugin mutation
- automatic repair
- live model-backed agent spawning
- generated `outputs/*`, to avoid self-feedback noise from report writes
- byte-level incremental Merkle index

## Verification

The first version is complete when:

- unit tests cover graph construction, metadata defects, and markdown repair briefs;
- unit tests cover path index diff for added, removed, and changed paths;
- unit tests cover impact classification for key waterway families;
- unit tests cover validation plan generation and check deduplication;
- unit tests cover route index generation and changed-only validation plans;
- unit tests cover validation runner exit-code capture and result markdown;
- unit tests cover stress fixtures for expected problem families, scale scans, and expected validation failures;
- unit tests cover incident fixtures for expected problem families, changed-path evidence, failed validation capture, and Codex/Claude handoff contents;
- `scripts/waterflow-scan` generates JSON, Markdown, repair brief, and path-index artifacts;
- `scripts/waterflow-scan --compare-last` generates path diff and change brief artifacts;
- `scripts/waterflow-scan --compare-last` generates route index and changed-only validation plan artifacts;
- `scripts/waterflow-verify` generates JSON and Markdown validation result artifacts;
- `scripts/waterflow-stress --scale-paths 1200` generates problem, scale, needle, and validation-failure evidence artifacts;
- `scripts/waterflow-incident` generates a complex incident report and `codex-claude-handoff.md`;
- `scripts/check-lab` passes;
- `registry/VALIDATION.md` records the commands and outputs.
