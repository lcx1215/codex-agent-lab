# Waterflow Auditor Report

- Generated: `2026-06-29T08:51:36.530886+00:00`
- Lab root: `/Users/liuchengxu/Desktop/codex-agent-lab`
- Nodes: `63`
- Edges: `62`
- Findings: `5`

## Findings

### P3 SCRIPT_WITHOUT_VALIDATION_REFERENCE

Script has no explicit validation reference: new-workspace

Evidence:
- `scripts/new-workspace`
- `registry/VALIDATION.md`

Repair brief:

Add the command or validation evidence for `scripts/new-workspace` to `registry/VALIDATION.md`.

### P3 SCRIPT_WITHOUT_VALIDATION_REFERENCE

Script has no explicit validation reference: start-api-relay

Evidence:
- `scripts/start-api-relay`
- `registry/VALIDATION.md`

Repair brief:

Add the command or validation evidence for `scripts/start-api-relay` to `registry/VALIDATION.md`.

### P3 SCRIPT_WITHOUT_VALIDATION_REFERENCE

Script has no explicit validation reference: start-clean-home

Evidence:
- `scripts/start-clean-home`
- `registry/VALIDATION.md`

Repair brief:

Add the command or validation evidence for `scripts/start-clean-home` to `registry/VALIDATION.md`.

### P3 SCRIPT_WITHOUT_VALIDATION_REFERENCE

Script has no explicit validation reference: sync-long-horizon-skills

Evidence:
- `scripts/sync-long-horizon-skills`
- `registry/VALIDATION.md`

Repair brief:

Add the command or validation evidence for `scripts/sync-long-horizon-skills` to `registry/VALIDATION.md`.

### P3 SCRIPT_WITHOUT_VALIDATION_REFERENCE

Script has no explicit validation reference: waterflow-scan

Evidence:
- `scripts/waterflow-scan`
- `registry/VALIDATION.md`

Repair brief:

Add the command or validation evidence for `scripts/waterflow-scan` to `registry/VALIDATION.md`.

## Graph Summary

| Kind | Count |
| --- | ---: |
| `agent` | 8 |
| `readme` | 1 |
| `registry` | 3 |
| `root` | 1 |
| `rules` | 1 |
| `script` | 6 |
| `skill` | 42 |
| `workspace-root` | 1 |
