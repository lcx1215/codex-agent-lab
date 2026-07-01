# Agent Registry

## Custom Agents

All 11 TOML definitions remain available because definitions are cheap and
historical checks reference them. The roster posture below controls default
resident delegation. See `.codex/agents/ROSTER.md` for the rationale and exact
invocation rule.

| Agent | Purpose | Default posture | Roster posture |
| --- | --- | --- | --- |
| `context-architect` | Context packs and task briefs | workspace-write, high | resident core |
| `handoff-summarizer` | Restart and compaction notes | workspace-write, medium | resident core |
| `third-party-large-agent-auditor` | External-review large-agent readiness scoring across lifecycle, scale, safety, handoff, and model-proof signals | workspace-write, high | resident core |
| `development-experience-auditor` | Codex/Claude development comfort scoring across context, runtime, verification, handoff, and safety | workspace-write, high | resident core |
| `waterflow-auditor` | Workflow graph audit and repair briefs | workspace-write, xhigh | resident core |
| `foundation-amplifier` | Lab foundation strengthening, Codex/Claude amplification routing, and backtests | workspace-write, high | resident core |
| `long-horizon-orchestrator` | Phase planning, delegation, durable progress | workspace-write, xhigh | on-demand only |
| `research-scout` | Source-backed research | read-only, high | on-demand only |
| `implementation-worker` | Scoped implementation | workspace-write, high | on-demand only |
| `verification-auditor` | Tests and evidence | workspace-write, high | on-demand only |
| `risk-reviewer` | Correctness and security review | read-only, xhigh | on-demand only |

## Runtime Lanes

| Lane | Command | Notes |
| --- | --- | --- |
| Clean home | `scripts/start-clean-home` | Uses `.codex-home`; no secrets copied. |
| API relay | `scripts/start-api-relay` | Uses `/Users/liuchengxu/.codex-api-relay` for auth/config but keeps cwd in this lab. |

## Skill Source

Long-horizon skills are copied from `/Users/liuchengxu/.codex/skills` according to `/Users/liuchengxu/.codex-long-horizon-agent/registry/installed-20260629_154856.txt`.

Lab-specific skills live under `.agents/skills`; `waterflow-auditor` is local to this lab.
