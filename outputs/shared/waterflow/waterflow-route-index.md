# Waterflow Route Index

- Generated: `2026-06-29T13:27:59.469522+00:00`
- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab`
- Routes: `6`
- Paths: `88`
- Changed paths: `0`
- Findings: `0`
- Max risk: `P2`

## Routes

| Route | Risk | Paths | Changed | Findings | Checks |
| --- | --- | ---: | ---: | --- | ---: |
| `agent` | `P2` | 8 | 0 | - | 3 |
| `auditor-code` | `P2` | 8 | 0 | - | 2 |
| `documentation` | `P3` | 9 | 0 | - | 1 |
| `registry` | `P3` | 5 | 0 | - | 1 |
| `script` | `P2` | 16 | 0 | - | 3 |
| `skill` | `P2` | 42 | 0 | - | 3 |

## Validation Commands

- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify agent discovery only."` covers 8 path(s), risk `P2`, routes `agent`.
- `CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input "Verify skill discovery only."` covers 42 path(s), risk `P2`, routes `skill`.
- `python3 -m unittest discover -s tests` covers 24 path(s), risk `P2`, routes `auditor-code`, `script`.
- `scripts/check-lab` covers 66 path(s), risk `P2`, routes `agent`, `script`, `skill`.
- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab` covers 88 path(s), risk `P2`, routes `agent`, `auditor-code`, `documentation`, `registry`, `script`, `skill`.
