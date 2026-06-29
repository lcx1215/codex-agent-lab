# Agent Registry

## Custom Agents

| Agent | Purpose | Default posture |
| --- | --- | --- |
| `long-horizon-orchestrator` | Phase planning, delegation, durable progress | workspace-write, xhigh |
| `context-architect` | Context packs and task briefs | workspace-write, high |
| `research-scout` | Source-backed research | read-only, high |
| `implementation-worker` | Scoped implementation | workspace-write, high |
| `verification-auditor` | Tests and evidence | workspace-write, high |
| `risk-reviewer` | Correctness and security review | read-only, xhigh |
| `handoff-summarizer` | Restart and compaction notes | workspace-write, medium |
| `waterflow-auditor` | Workflow graph audit and repair briefs | workspace-write, xhigh |

## Runtime Lanes

| Lane | Command | Notes |
| --- | --- | --- |
| Clean home | `scripts/start-clean-home` | Uses `.codex-home`; no secrets copied. |
| API relay | `scripts/start-api-relay` | Uses `/Users/liuchengxu/.codex-api-relay` for auth/config but keeps cwd in this lab. |

## Skill Source

Long-horizon skills are copied from `/Users/liuchengxu/.codex/skills` according to `/Users/liuchengxu/.codex-long-horizon-agent/registry/installed-20260629_154856.txt`.

Lab-specific skills live under `.agents/skills`; `waterflow-auditor` is local to this lab.
