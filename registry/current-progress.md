# Current Lab Progress

Last updated: 2026-06-30 16:10 +0800

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
- Eleven custom agents are defined under `.codex/agents`.
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
- Sandbox Skill Pack 1 is installed under `.agents/skills`: `secret-boundary-auditor`, `async-race-detector`, `tmux-omx-runtime-doctor`, and `sandbox-artifact-hygiene`. `scripts/check-sandbox-skills` validates the pack and is invoked by `scripts/check-lab`.
- Waterflow speed contract is promoted as a default health gate: `docs/waterflow-speed-contract.md` defines non-blocking supervision, fast/boundary/stress paths, blocking rules, and performance budgets; `scripts/check-speed-contract` validates that default gates stay lightweight.
- IDE-loop benchmark and dashboard are installed: `scripts/benchmark-ide-loop` records repeatable RED/GREEN, health-gate, Waterflow, async, and optional OMX-smoke timings under `outputs/shared/benchmarks/ide-loop/`; `scripts/lab-dashboard` renders the latest benchmark, Waterflow, async, and git state into `outputs/shared/dashboard/`.
- A local-only scenario workspace exists for private agent experimentation and is intentionally excluded from Git/GitHub.
- Root lab positioning has been corrected: the sandbox is scenario-neutral and can host arbitrarily large agent families. UCP and other domain-specific agents are future scenario workspaces only. The lab's job is to amplify Codex and Claude with durable state, harnesses, Waterflow, benchmarks, skills, and verification gates, not replace their reasoning or coding ability.
- Codex/OMX and Claude/OMC now share the same environment placement model: `codex-agent-lab` is the maximum environment, `workspaces/<scenario>/` are medium workspaces/projects, and `agents/<package>/` folders are small agent packages. All three levels are sandboxed work surfaces, so the support scenario is named `workspaces/support-agent-workspace/`; `sandbox` is reserved for the safety property of the whole layered environment.
- Nested rule inheritance is installed: `docs/rule-inheritance.md` defines the effective rule chain from root lab to workspace to small agent package. `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/environment-layering.md`, `docs/scenario-workspace-contract.md`, `docs/project-rule-template.md`, and `workspaces/README.md` now point to it. New workspaces generated by `scripts/new-workspace` include local `AGENTS.md`, a Claude entry `CLAUDE.md`, and `agents/README.md` so Codex or Claude can start inside a medium workspace or small package without dropping parent rules.
- Scenario workspace contract is installed: `docs/scenario-workspace-contract.md` defines how arbitrary future agent families stay local while amplifying Codex/Claude capability. `scripts/new-workspace` now generates `Scenario Boundary` and `Codex Claude Amplification` sections, and `tests/test_workspace_contract.py` locks that scaffold behavior.
- Foundation amplifier agent is installed under `.codex/agents/foundation-amplifier.toml` to help Codex and Claude route large lab work, choose the right verification chain, and backtest whether new capabilities actually improve the environment. Backtest artifact: `outputs/shared/foundation-amplifier/backtest-20260630T0330Z.md`.
- Real model-backed validation is now allowed as normal evidence when it proves the capability being changed. A live API-relay OMX invocation used `gpt-5.5` with `xhigh` reasoning and wrote `outputs/shared/foundation-amplifier/live-model-backed-20260630T034423Z.md`.
- Former frugality guidance has been removed from lab rules and mirrored skill surfaces. Security credential protections remain in force: secrets, auth files, API keys, cookies, OTPs, provider config, and plugin state are still protected.
- Development Experience Auditor is installed under `.codex/agents/development-experience-auditor.toml` with docs in `docs/development-experience-auditor-agent.md`, a deterministic harness in `lab_agents/development_experience.py`, and CLI entrypoint `scripts/development-experience-audit`.
- Latest development comfort report is `outputs/shared/development-experience-auditor/latest.md`: score 92, status `usable_with_friction`, with runtime as the only mixed dimension because the latest OMX model smoke took 84.959s.
- Third-Party Large Agent Readiness Auditor is installed under `.codex/agents/third-party-large-agent-auditor.toml` with docs in `docs/third-party-large-agent-auditor.md`, a deterministic harness in `lab_agents/large_agent_readiness.py`, and CLI entrypoint `scripts/large-agent-readiness-audit`.
- Latest third-party large-agent readiness report is `outputs/shared/large-agent-readiness-auditor/latest.md`: score 92, status `ready_with_known_constraints`, with delegation and performance as mixed dimensions and no failed or missing dimensions.
- Runtime compatibility gate is installed: `scripts/check-runtime-compatibility` verifies required local commands, Python support, script hygiene, runtime ignore rules, clean-home auth absence, and documentation wiring. It writes `outputs/shared/compatibility/runtime-compatibility.json` and `.md`, and `scripts/lab-dashboard` now shows compatibility status.
- `scripts/new-workspace` now supports a guarded `WORKSPACE_ROOT` override for tests and harnesses. Overrides must resolve inside the lab root before directories are created, reducing async test collisions and preventing accidental outside-lab workspace writes.
- Workspace safety gate is installed: `scripts/check-workspace-safety` checks all `workspaces/*` for hard safety failures while allowing active in-progress scaffolding gaps as warnings. It writes `outputs/shared/workspace-safety/workspace-safety.json` and `.md`, is referenced by root contracts, remains available in `scripts/check-async-execution` and `scripts/lab-dashboard`, and now runs explicitly at workspace-change, stability, or promotion boundaries instead of inside the root default fast path.
- New workspace scaffolds now include a local `.gitignore` for temp files, runtime state, logs, node_modules, and secret-like paths.
- No secrets are copied into the lab.
- Capability Layer 6 (Codex-Claude Collaboration) is installed: `CLAUDE.md` is the Claude/OMC lane-local contract (counterpart to `AGENTS.md`), `docs/codex-claude-collaboration-protocol.md` defines leader/worker/reviewer roles, lane boundaries, handoff format, assignments-ledger shape, and a proof bar, `registry/collaboration/assignments.json` is the durable ledger (schema `codex-claude-collaboration-assignments/v1`), `registry/collaboration/handoffs/` holds dated English handoffs, and `scripts/check-collaboration` is the lane-portable health gate wired into `scripts/check-lab`.
- Collaboration honest status: commands are installed (`omc ask`, `omc team`, `omc interop`, Codex `omx-api`). Real OMC-to-OMX interop is now proven by assignment `collab-0003-interop-proof`; official OMC team bootstrap remains blocked in `collab-0001` with `worker_start_submit_unverified`.
- Cross-lane script portability root cause documented: lab scripts call `rg`, which is the Codex.app-bundled ripgrep at `/Applications/Codex.app/Contents/Resources/rg`, not a system binary; the Claude bash lane has no `rg`, so `scripts/check-collaboration` falls back to `grep -E` and runs in both lanes.

## Verification

- `scripts/check-lab` passed.
- TOML parsing passed for the clean-home config and all agent files.
- `codex debug prompt-input` with `CODEX_HOME=.codex-home` confirmed lab sandbox, AGENTS.md, and project skills are discovered.
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
- Sandbox Skill Pack 1 checks passed: `scripts/check-sandbox-skills`, Bash syntax checks for the updated gates, `scripts/check-project-rules`, and `scripts/check-lab` with 46 lab-local skills detected.
- Waterflow speed-contract checks added: `scripts/check-speed-contract` is the lightweight gate for non-blocking supervision and is wired into `scripts/check-lab` and `scripts/check-project-rules`.
- Waterflow speed-contract verification passed: Bash syntax checks, `scripts/check-speed-contract`, `scripts/check-project-rules`, `scripts/check-lab`, `scripts/check-sandbox-skills`, `scripts/check-secrets`, unit tests, `scripts/waterflow-verify`, and final `scripts/waterflow-scan --root . --compare-last` all passed. Final Waterflow summary reported 99 paths, 0 findings, and 0 added/removed/changed paths.
- IDE-loop benchmark verification passed: `scripts/benchmark-ide-loop` recorded `status=pass`, `total_seconds=22.005`, `local_seconds=0.570`, `gate_seconds=13.088`, and `waterflow_seconds=8.347` in `outputs/shared/benchmarks/ide-loop/runs/20260630T022007Z/`.
- Dashboard verification passed: `scripts/lab-dashboard` reported `health=ok`, Waterflow 102 paths with 0 findings and 0 changed paths, async 7/7 passed, latest benchmark pass, and current dirty worktree counts.
- Commercial Agent Foundation verification passed for the expanded limitation harness: workspace tests reported `Ran 16 tests in 0.002s` and `OK`; compile check passed; root `scripts/check-project-rules`, `scripts/check-lab`, `scripts/check-secrets`, and root unit tests passed; Waterflow compare reported 103 paths, 0 findings, and 0 changed paths; `scripts/waterflow-verify` passed 5/5; dashboard reported `health=ok`.
- Live foundation-amplifier model invocation passed: `/Users/liuchengxu/.local/bin/omx-api exec -C /Users/liuchengxu/Desktop/codex-agent-lab -` reported provider `custom`, model `gpt-5.5`, reasoning effort `xhigh`, wrote `outputs/shared/foundation-amplifier/live-model-backed-20260630T034423Z.md`, verified 34 lines and all 5 required sections, and reported `tokens used 96,651`.
- Final validation for this update passed: targeted benchmark/foundation tests reported `Ran 3 tests in 0.019s` and `OK`; root tests reported `Ran 16 tests in 2.944s` and `OK`; `scripts/check-speed-contract`, `scripts/check-sandbox-skills`, `scripts/check-secrets`, `scripts/check-project-rules`, and `scripts/check-lab` passed.
- Real IDE-loop benchmark passed with model smoke enabled: run `20260630T035103Z` reported `with_omx=true`, `status=pass`, `total_seconds=103.590`, `local_seconds=0.356`, `gate_seconds=9.969`, `waterflow_seconds=8.306`, `omx_seconds=84.959`, and `failed_checks=none`.
- Final Waterflow and dashboard checks passed: compare-last reported `findings: 0`; `scripts/waterflow-verify` reported 5 passed and 0 failed; final dashboard reported `Health: ok`, Waterflow 109 paths, 0 findings, 0 added/changed/removed diff, and async 7 passed / 0 failed / 0 timed out.
- Development Experience Auditor verification passed: TDD RED failed on missing `lab_agents`, then missing `collect_lab_comfort_signals`, then missing benchmark parser; GREEN passed with `python3 -m unittest tests.test_development_experience_auditor` reporting 5 tests OK and root tests reporting 21 tests OK.
- `scripts/development-experience-audit` generated `outputs/shared/development-experience-auditor/runs/20260630T040747Z/report.md` and `outputs/shared/development-experience-auditor/latest.md`; final project gates passed: `scripts/check-project-rules`, `scripts/check-secrets`, `scripts/check-lab`, `scripts/check-speed-contract`, `scripts/waterflow-scan --root . --compare-last`, `scripts/waterflow-verify`, and `scripts/lab-dashboard`.
- Live model-backed Development Experience Auditor review passed: `/Users/liuchengxu/.local/bin/omx-api exec -C /Users/liuchengxu/Desktop/codex-agent-lab -` wrote `outputs/shared/development-experience-auditor/live-model-review-20260630T041305Z.md`, verified 33 lines, reported `tokens used 45,468`, and concluded the lab is `usable_with_friction` with score 92.
- Latest dashboard after this agent build reported `Health: ok`, Waterflow 113 paths, 0 findings, 0 added/changed/removed diff, and async 7 passed / 0 failed / 0 timed out.
- Third-Party Large Agent Readiness Auditor TDD passed: initial RED was `ModuleNotFoundError: No module named 'lab_agents.large_agent_readiness'`; GREEN reported `Ran 4 tests in 0.011s` and `OK`.
- `scripts/large-agent-readiness-audit` generated `outputs/shared/large-agent-readiness-auditor/runs/20260630T053031Z/report.md` and `outputs/shared/large-agent-readiness-auditor/latest.md`; report score was 92 with status `ready_with_known_constraints`.
- Current third-party finding: the lab can support large-agent development under explicit governance. The remaining mixed dimensions are official team-mode delegation proof and slow real-model smoke performance.
- Third-party auditor validation passed: py_compile and Bash syntax checks, root unit tests 25/25, `scripts/check-project-rules`, `scripts/check-secrets`, `scripts/check-speed-contract`, `scripts/check-lab`, `scripts/check-sandbox-skills`, `scripts/waterflow-scan --root . --compare-last`, `scripts/waterflow-verify`, and `scripts/lab-dashboard`.
- Waterflow correctly caught the newly added CLI before validation was recorded: `SCRIPT_WITHOUT_VALIDATION_REFERENCE` for `scripts/large-agent-readiness-audit`. Recording validation evidence closed the finding and the follow-up scan reported 0 findings.
- Waterflow validation then exposed a separate workspace metadata defect: `workspaces/20260630_133236-multiagent-parallel-proof` existed without `brief.md`. The workspace now has `brief.md`, `progress.md`, and `AGENTS.md`; `scripts/check-lab` and `scripts/waterflow-verify` passed afterward.
- Live model-backed third-party review passed: `/Users/liuchengxu/.local/bin/omx-api exec -C /Users/liuchengxu/Desktop/codex-agent-lab -` wrote `outputs/shared/large-agent-readiness-auditor/live-third-party-review-20260630T053456Z.md`, verified 48 lines, reported `tokens used 47,433`, and concluded the lab is conditionally ready for controlled large-agent pilots, not unconstrained production-scale multi-agent operation.
- Runtime compatibility verification passed: `scripts/check-runtime-compatibility` reported 40 checks, 40 passed, 0 warnings, and 0 failures.
- Async hardening found and fixed real workspace-test collision risks: `scripts/check-async-execution` initially failed because `tests/test_workspace_contract.py` wrote to shared `workspaces/`; after adding guarded `WORKSPACE_ROOT` support and moving the test to lab-local `.tmp/tests`, async execution passed. A second concurrent proof showed the test also needed a unique temp root per process; after switching to `tempfile.mkdtemp`, simultaneous root unit tests and async unit tests passed. Latest async run reports 9/9 checks passed with 0 failures and 0 timeouts.
- Rule inheritance verification passed: `bash -n scripts/new-workspace scripts/check-project-rules scripts/check-workspace-safety scripts/check-lab`; `python3 -m unittest tests.test_workspace_contract tests.test_workspace_safety tests.test_runtime_compatibility` reported `Ran 6 tests` and `OK`; `scripts/check-project-rules`, `scripts/check-speed-contract`, `scripts/check-lab`, `scripts/check-runtime-compatibility`, and `scripts/check-collaboration` passed. `scripts/check-workspace-safety` reported `warnings: 10` and `failed: 0`; the remaining warnings are old proof/workspace scaffold issues, not rule-inheritance gaps.

## Next Optional Check

- Add a generic JSONL batch eval runner template for local-only scenario workspaces.
- Run a stricter OMX team/tmux or longer-running proof only when there is a real task that benefits from parallelism or checkpointed runtime state.
- Add sampled rotation checks for unchanged low-risk route families.
- Add a small registry index for live model-backed invocation artifacts if more than one such proof is created.
- Use `development-experience-auditor` after the next medium/large agent build to compare whether comfort improves beyond 92 and whether the runtime friction is reduced or intentionally accepted as a boundary-only cost.
- Use `third-party-large-agent-auditor` before the first truly large long-horizon workspace pilot and after any delegation/runtime promotion.
