# Waterflow Validation Plan

- Generated: `2026-06-29T13:27:59.469522+00:00`
- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab`
- Scope: `all`
- Changed paths: `0`
- Checks: `5`
- Max risk: `P2`

## Check 1: P2

Command: `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify agent discovery only."`

Route kinds:
- `agent`

Covered paths:
- `.codex/agents/context-architect.toml`
- `.codex/agents/handoff-summarizer.toml`
- `.codex/agents/implementation-worker.toml`
- `.codex/agents/long-horizon-orchestrator.toml`
- `.codex/agents/research-scout.toml`
- `.codex/agents/risk-reviewer.toml`
- `.codex/agents/verification-auditor.toml`
- `.codex/agents/waterflow-auditor.toml`

## Check 2: P2

Command: `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify skill discovery only."`

Route kinds:
- `skill`

Covered paths:
- `.agents/skills/api-and-interface-design/SKILL.md`
- `.agents/skills/brainstorming/SKILL.md`
- `.agents/skills/browser-testing-with-devtools/SKILL.md`
- `.agents/skills/ci-cd-and-automation/SKILL.md`
- `.agents/skills/cli-creator/SKILL.md`
- `.agents/skills/code-review-and-quality/SKILL.md`
- `.agents/skills/code-simplification/SKILL.md`
- `.agents/skills/context-engineering/SKILL.md`
- `.agents/skills/debugging-and-error-recovery/SKILL.md`
- `.agents/skills/define-goal/SKILL.md`
- `.agents/skills/deprecation-and-migration/SKILL.md`
- `.agents/skills/dispatching-parallel-agents/SKILL.md`
- `.agents/skills/documentation-and-adrs/SKILL.md`
- `.agents/skills/doubt-driven-development/SKILL.md`
- `.agents/skills/executing-plans/SKILL.md`
- `.agents/skills/finishing-a-development-branch/SKILL.md`
- `.agents/skills/frontend-ui-engineering/SKILL.md`
- `.agents/skills/git-workflow-and-versioning/SKILL.md`
- `.agents/skills/idea-refine/SKILL.md`
- `.agents/skills/incremental-implementation/SKILL.md`

...and 22 more paths.

## Check 3: P2

Command: `python3 -m unittest discover -s tests`

Route kinds:
- `auditor-code`
- `script`

Covered paths:
- `scripts/check-async-execution`
- `scripts/check-lab`
- `scripts/check-project-rules`
- `scripts/check-sandbox`
- `scripts/check-secrets`
- `scripts/check-workflow-modes`
- `scripts/new-workspace`
- `scripts/start-api-relay`
- `scripts/start-api-relay-plain`
- `scripts/start-clean-home`
- `scripts/sync-long-horizon-skills`
- `scripts/waterflow-incident`
- `scripts/waterflow-scan`
- `scripts/waterflow-stress`
- `scripts/waterflow-verify`
- `scripts/workflow-mode`
- `tests/test_waterflow_auditor.py`
- `tests/test_waterflow_incident.py`
- `tests/test_waterflow_stress.py`
- `waterflow/__init__.py`

...and 4 more paths.

## Check 4: P2

Command: `scripts/check-lab`

Route kinds:
- `agent`
- `script`
- `skill`

Covered paths:
- `.agents/skills/api-and-interface-design/SKILL.md`
- `.agents/skills/brainstorming/SKILL.md`
- `.agents/skills/browser-testing-with-devtools/SKILL.md`
- `.agents/skills/ci-cd-and-automation/SKILL.md`
- `.agents/skills/cli-creator/SKILL.md`
- `.agents/skills/code-review-and-quality/SKILL.md`
- `.agents/skills/code-simplification/SKILL.md`
- `.agents/skills/context-engineering/SKILL.md`
- `.agents/skills/debugging-and-error-recovery/SKILL.md`
- `.agents/skills/define-goal/SKILL.md`
- `.agents/skills/deprecation-and-migration/SKILL.md`
- `.agents/skills/dispatching-parallel-agents/SKILL.md`
- `.agents/skills/documentation-and-adrs/SKILL.md`
- `.agents/skills/doubt-driven-development/SKILL.md`
- `.agents/skills/executing-plans/SKILL.md`
- `.agents/skills/finishing-a-development-branch/SKILL.md`
- `.agents/skills/frontend-ui-engineering/SKILL.md`
- `.agents/skills/git-workflow-and-versioning/SKILL.md`
- `.agents/skills/idea-refine/SKILL.md`
- `.agents/skills/incremental-implementation/SKILL.md`

...and 46 more paths.

## Check 5: P2

Command: `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`

Route kinds:
- `agent`
- `auditor-code`
- `documentation`
- `registry`
- `script`
- `skill`

Covered paths:
- `.agents/skills/api-and-interface-design/SKILL.md`
- `.agents/skills/brainstorming/SKILL.md`
- `.agents/skills/browser-testing-with-devtools/SKILL.md`
- `.agents/skills/ci-cd-and-automation/SKILL.md`
- `.agents/skills/cli-creator/SKILL.md`
- `.agents/skills/code-review-and-quality/SKILL.md`
- `.agents/skills/code-simplification/SKILL.md`
- `.agents/skills/context-engineering/SKILL.md`
- `.agents/skills/debugging-and-error-recovery/SKILL.md`
- `.agents/skills/define-goal/SKILL.md`
- `.agents/skills/deprecation-and-migration/SKILL.md`
- `.agents/skills/dispatching-parallel-agents/SKILL.md`
- `.agents/skills/documentation-and-adrs/SKILL.md`
- `.agents/skills/doubt-driven-development/SKILL.md`
- `.agents/skills/executing-plans/SKILL.md`
- `.agents/skills/finishing-a-development-branch/SKILL.md`
- `.agents/skills/frontend-ui-engineering/SKILL.md`
- `.agents/skills/git-workflow-and-versioning/SKILL.md`
- `.agents/skills/idea-refine/SKILL.md`
- `.agents/skills/incremental-implementation/SKILL.md`

...and 68 more paths.
