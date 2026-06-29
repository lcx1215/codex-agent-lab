# Current Lab Progress

Last updated: 2026-06-29 21:35 +0800

## Objective

Create a clean, isolated Desktop Codex agent lab for strict, long-horizon agent development. The lab should become a rich, layered, evidence-driven environment for large Codex, Claude, OMX, and future-agent workflows while preserving lane isolation and secret safety.

## Isolation State

- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab`
- Clean home: `/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home`
- Project agents: `.codex/agents`
- Project skills: `.agents/skills`
- Existing App/Plus home and API-relay home are not modified by this lab setup.

## Current Status

- Directory skeleton created.
- Project rules, clean-home config, custom agents, and scripts are installed.
- Eight custom agents are defined under `.codex/agents`.
- Long-horizon skills were copied into `.agents/skills`.
- `.codex-home/agents` and `.codex-home/skills` point back to the lab-local project copies.
- `.codex-home/AGENTS.md` points to the global rules file at `/Users/liuchengxu/.codex/AGENTS.md`.
- Global `AGENTS.md` now includes a short Codex operating baseline.
- README now documents the intended framework locations without adding heavy future policy.
- `docs/agent-lab-mission.md` now records the long-term mission, quality bar, capability targets, and promotion rule for rich but controlled agent-environment growth.
- Waterflow Auditor v1 has design docs, a custom agent, a lab-local skill, a Python scanner, tests, and output artifacts.
- Waterflow Auditor now emits `waterflow-path-index.json` and can generate `waterflow-path-diff.json` with `--compare-last`.
- Waterflow Auditor scans its own `waterflow/`, `tests/`, and `docs/` paths while excluding generated `outputs/`.
- Path diffs include impact metadata: route kind, risk, and recommended checks.
- Waterflow Auditor emits `waterflow-change-briefs.md` when a previous path index is compared.
- Waterflow Auditor emits `waterflow-validation-plan.json` and `waterflow-validation-plan.md` on every scan.
- Waterflow Auditor emits `waterflow-route-index.json` and `waterflow-route-index.md` to collapse large graphs by route family, risk, changed paths, and checks.
- Waterflow Auditor emits `waterflow-validation-plan-changed.*` when a diff exists, so validation can focus on changed waterways.
- Waterflow Auditor clears stale path-diff/change-brief artifacts on non-comparison scans and rewrites changed-only validation as an empty scoped plan.
- Waterflow Auditor now has a real validation runner API and `scripts/waterflow-verify` for executing validation-plan commands.
- Waterflow Auditor now has `scripts/waterflow-stress` for generated problem fixtures, scale fixtures, needle fixtures, and expected validation failure capture.
- Harness philosophy is now explicit in `docs/waterflow-harness-philosophy.md`: stress `pass` means detector proof, not a claim that everything is healthy.
- Waterflow Auditor now has `scripts/waterflow-incident` for a realistic complex incident rehearsal that creates an isolated broken fixture, detects workflow defects, records failed and timed-out validation commands, and writes `codex-claude-handoff.md` for Codex or Claude repair.
- Repository now has `scripts/check-secrets` plus `.github/workflows/security.yml` to block common API-key/token/private-key leaks and README machine-local `/Users/` paths.
- README uses reader-friendly relative paths instead of machine-local `/Users/...` prefixes.
- Capability Layer 1 is installed for project-level rules: `registry/CAPABILITY_LAYERS.md` tracks the upper-layer expansion plan, `docs/project-rule-template.md` defines reusable project-local `AGENTS.md` structure, `scripts/check-project-rules` validates the rule surfaces, and `scripts/new-workspace` now creates a local workspace `AGENTS.md`.
- Capability Layer 2 is installed for workflow modes: `docs/workflow-modes.md` defines daily App, CLI diagnosis, OMX long-horizon, multi-agent review, and overnight checkpoint modes; `scripts/workflow-mode` prints each mode contract; `scripts/check-workflow-modes` validates the catalog; `registry/OMX_RETROSPECTIVE.md` records the evidence-based OMX usefulness assessment.
- First bounded OMX execution proof completed in `workspaces/20260629_204008-omx-execution-proof`. `omx-api exec` produced required artifacts and App-side audit added `app-audit.md`. Verdict: mixed but useful; OMX proved bounded CLI artifact execution and auditability, but not team/tmux parallel throughput. A shell quoting incident accidentally invoked `omx-api` and is recorded as an execution risk. App-side audit removed the temporary `/tmp/benefit-matrix-check.txt`.
- Team/tmux proof workspace `workspaces/20260629_210146-omx-team-tmux-proof` now records a second OMX proof. Official `omx-api team` still failed before useful worker execution (`worker_notify_failed`, missing pane `%1`, missing startup script evidence), but two direct tmux-launched `omx-api exec` workers completed and wrote `tmux-worker-1.md` and `tmux-worker-2.md`.
- Sandbox boundaries are hardened: `docs/sandbox-boundaries.md` defines the local contract, `scripts/check-sandbox` verifies clean-home config, writable roots, tmp exclusion, symlink escapes, forbidden secret-like files, script portability, and directory permissions, and `scripts/check-lab` now invokes the sandbox gate.
- Clean-home config now excludes system tmp directories; scripts and tests use lab-local `.tmp/` scratch space.
- Async execution safety is covered by `scripts/check-async-execution`, which runs independent checks concurrently with per-task `TMPDIR` values and isolated Waterflow output directories. `docs/reasoning-speed-playbook.md` records how to reduce avoidable `gpt-5.5` + `xhigh` latency without lowering reasoning quality for hard decisions.
- Async execution safety is now stricter: `scripts/check-async-execution` treats unexpected stderr from quiet health checks as failure, while explicitly allowing unittest progress stderr. `scripts/check-sandbox` prunes volatile `.tmp/` scratch subtrees during recursive scans to avoid racing concurrently removed temp directories.
- No secrets are copied into the lab.

## Verification

- `scripts/check-lab` passed.
- TOML parsing passed for the clean-home config and all agent files.
- `codex debug prompt-input` with `CODEX_HOME=.codex-home` confirmed lab sandbox, AGENTS.md, and project skills are discovered without a model call.
- `codex debug prompt-input` confirmed global AGENTS rules are layered before the lab-specific project overlay.
- `python3 -m unittest discover -s tests` passed for Waterflow Auditor behavior.
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab` generated JSON, Markdown, and repair brief artifacts under `outputs/shared/waterflow/`.
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` generated a path diff artifact.
- Latest graph expansion reached 67 paths with impact metadata for auditor-code and documentation paths.
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` generated change briefs for changed auditor-code paths.
- Latest validation plan produced 5 deduplicated checks with max risk `P2`.
- `python3 -m unittest discover -s tests` passed with 8 tests after adding real validation runner coverage.
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` passed after the validation runner extension with 69 paths and 0 findings.
- `scripts/waterflow-verify` passed with 5 real checks, 5 passed, 0 failed, 0 timed out, and max exit code 0.
- `scripts/waterflow-stress --scale-paths 2400` passed after adding detector coverage enforcement: problem fixture found 13 issues with 0 missing expected codes, detector coverage reported 12/12 implemented detector codes covered, scale fixture scanned 2409 nodes with 0 findings, needle fixture scanned 2412 nodes and found 4 injected defects, and validation stress captured 2 expected failures plus 1 expected timeout.
- Harness philosophy directly improved functionality by exposing and closing the missing `EMPTY_REGISTRY_FILE` injection case.
- `python3 -m unittest tests.test_waterflow_incident` passed for the complex incident harness.
- `python3 -m unittest discover -s tests` passed with 12 tests after adding incident coverage.
- `scripts/waterflow-incident` passed and generated `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/codex-claude-handoff.md`.
- Latest incident run found 14 intentional fixture findings, detected all 12 expected defect families, produced added/removed/changed path diff evidence, captured 2 expected validation failures plus 1 timeout, and wrote a Codex/Claude repair order.
- Post-incident `scripts/check-lab` passed.
- Post-incident `scripts/waterflow-verify` passed with 5 checks, 5 passed, 0 failed, 0 timed out, and max exit code 0.
- Post-incident final `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` reported 77 paths, 0 findings, and 0 added/removed/changed paths.
- `scripts/check-secrets` passed with no committable secrets or README-local user paths detected.
- README local-path cleanup and secret guard regression checks passed: unit tests 12/12, `scripts/check-lab`, `scripts/waterflow-scan --root . --compare-last`, and `scripts/waterflow-verify`.
- Project-level rule expansion checks passed: `scripts/check-project-rules`, Bash syntax checks for `scripts/check-project-rules`, `scripts/check-lab`, and `scripts/new-workspace`, integrated `scripts/check-lab`, `scripts/check-secrets`, `python3 -m unittest discover -s tests`, `scripts/waterflow-scan --root . --compare-last` with 0 findings, and `scripts/waterflow-verify` with 5 passed and 0 failed.
- Workflow mode checks passed: `scripts/workflow-mode list`, `scripts/workflow-mode omx-long-horizon`, `scripts/check-workflow-modes`, Bash syntax checks for the workflow scripts, integrated `scripts/check-lab`, `scripts/check-secrets`, `python3 -m unittest discover -s tests`, `scripts/waterflow-scan --root . --compare-last` with 0 findings, and `scripts/waterflow-verify` with 5 passed and 0 failed.
- Mission and quality-bar expansion checks passed: `scripts/check-project-rules`, Bash syntax checks, `scripts/check-secrets`, `scripts/check-lab`, `scripts/check-workflow-modes`, `python3 -m unittest discover -s tests`, and `scripts/waterflow-scan --root . --compare-last` with 86 paths and 0 findings.
- Sandbox hardening checks passed: `scripts/check-sandbox`, `scripts/check-project-rules`, `scripts/check-secrets`, integrated `scripts/check-lab`, Bash syntax checks, `python3 -m unittest discover -s tests`, `scripts/waterflow-scan --root . --compare-last` with 89 paths and 0 findings, and `scripts/waterflow-verify` with 5 passed and 0 failed.
- Async execution and speed-playbook checks passed: `scripts/check-async-execution` ran 7 concurrent checks with 7 passed, 0 failed, and 0 timed out; `scripts/check-project-rules` and `scripts/check-secrets` also passed after wiring the new speed and async surfaces; final `scripts/waterflow-scan --root . --compare-last` reported 92 paths, 0 findings, and 0 changed paths.
- Bounded OMX execution proof checks passed with a mixed verdict: required workspace artifacts exist, `benefit-matrix.json` is valid with all required fields, App-side command checks passed, `scripts/check-sandbox`, `scripts/check-lab`, `scripts/check-secrets`, unit tests, `scripts/waterflow-scan --root . --compare-last` with 0 findings, and `scripts/waterflow-verify` with 5 passed and 0 failed.
- Team/tmux proof 2 recorded a mixed result: direct tmux `omx-api exec` workers produced two reports with `EXIT:0`, while official `omx-api team` still failed before useful worker execution. No lab tmux sessions or lab OMX processes remained running after cleanup.
- Async race hardening checks passed: `bash -n scripts/check-sandbox scripts/check-async-execution`, `scripts/check-sandbox`, `scripts/check-async-execution`, `scripts/check-project-rules`, `scripts/check-secrets`, `scripts/check-lab`, `python3 -m unittest discover -s tests`, `scripts/waterflow-verify`, and final `scripts/waterflow-scan --root . --compare-last`. Latest async run `20260629T132619Z-90643` passed 7/7 with 0 failed, 0 timed out, and no unexpected stderr; final Waterflow compare reported 92 paths, 0 findings, and 0 changed paths.

## Next Optional Check

- Run a stricter OMX team/tmux or longer-running proof only when there is a real task that benefits from parallelism or checkpointed runtime state.
- Add sampled rotation checks for unchanged low-risk route families.
- Run a short API-backed session that explicitly invokes `long-horizon-orchestrator` only when token spend is acceptable.
