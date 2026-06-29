# Waterflow Route Index

- Generated: `2026-06-29T11:47:29.529570+00:00`
- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab/outputs/shared/waterflow/incidents/incident-20260629T114729Z/incident-lab`
- Routes: `7`
- Paths: `16`
- Changed paths: `22`
- Findings: `14`
- Max risk: `P1`

## Routes

| Route | Risk | Paths | Changed | Findings | Checks |
| --- | --- | ---: | ---: | --- | ---: |
| `agent` | `P1` | 4 | 5 | `AGENT_MISSING_FIELD`, `AGENT_TOML_INVALID`, `DUPLICATE_AGENT_NAME` | 3 |
| `auditor-code` | `P2` | 2 | 3 | - | 2 |
| `documentation` | `P1` | 2 | 3 | `CROSS_PROJECT_REFERENCE`, `MISSING_CORE_PATH` | 1 |
| `registry` | `P2` | 3 | 3 | `EMPTY_REGISTRY_FILE`, `PROGRESS_WITHOUT_VALIDATION` | 1 |
| `script` | `P2` | 2 | 2 | `SCRIPT_NOT_EXECUTABLE`, `SCRIPT_WITHOUT_VALIDATION_REFERENCE` | 3 |
| `skill` | `P2` | 3 | 4 | `DUPLICATE_SKILL_NAME`, `SKILL_MISSING_FIELD` | 3 |
| `unknown` | `P1` | 0 | 2 | `SKILL_MISSING_ENTRYPOINT` | 0 |

## Validation Commands

- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify agent discovery only."` covers 4 path(s), risk `P2`, routes `agent`.
- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify skill discovery only."` covers 3 path(s), risk `P2`, routes `skill`.
- `python3 -m unittest discover -s tests` covers 4 path(s), risk `P2`, routes `auditor-code`, `script`.
- `scripts/check-lab` covers 9 path(s), risk `P2`, routes `agent`, `script`, `skill`.
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab` covers 16 path(s), risk `P2`, routes `agent`, `auditor-code`, `documentation`, `registry`, `script`, `skill`.
