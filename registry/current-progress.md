# Current Lab Progress

Last updated: 2026-06-29 20:22 +0800

## Objective

Create a clean, isolated Desktop Codex agent lab for long-horizon work.

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
- `scripts/check-secrets` passed with no tracked secrets or README-local user paths detected.
- README local-path cleanup and secret guard regression checks passed: unit tests 12/12, `scripts/check-lab`, `scripts/waterflow-scan --root . --compare-last`, and `scripts/waterflow-verify`.

## Next Optional Check

- Add sampled rotation checks for unchanged low-risk route families.
- Run a short API-backed session that explicitly invokes `long-horizon-orchestrator` only when token spend is acceptable.
