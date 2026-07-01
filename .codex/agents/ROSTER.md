# Codex Agent Roster Policy

Last updated: 2026-07-01 15:05 +0800
Owner lane: Codex

This directory keeps all 11 TOML definitions because definitions are cheap and
some checks/history expect the files to remain. The trimmed roster below controls
which agents are treated as resident default delegation candidates. Every agent
call still burns model quota, so use the main lane unless a separate seat earns
its cost.

## Resident core

| Agent | Decision | Rationale | Invoke when |
| --- | --- | --- | --- |
| `context-architect` | keep resident | Read-a-lot-then-compress work saves main-lane context. | A context map or brief will unblock implementation/review. |
| `handoff-summarizer` | keep resident | Durable restart and cross-lane summaries are real output, not duplicate review. | A compact handoff/checkpoint saves context or prevents restart loss. |
| `third-party-large-agent-auditor` | keep resident | External-review posture reduces self-review bias for large-agent readiness. | A boundary/promotion decision needs independent readiness judgment. |
| `development-experience-auditor` | keep resident | Has deterministic harness/output history for Codex/Claude comfort audits. | Lab ergonomics or comfort score needs evidence-backed assessment. |
| `waterflow-auditor` | keep resident | Has workflow-graph identity and Waterflow artifact path. | Coordination defects or route health need Waterflow-specific audit. |
| `foundation-amplifier` | keep resident | Helps route large lab work and backtest whether capabilities amplify Codex/Claude. | Root-lab capability placement or large-agent task routing needs judgment. |

Note: the handoff mentioned `large-agent-readiness-auditor`; in this roster the
resident file is `third-party-large-agent-auditor.toml`, with outputs under
`outputs/shared/large-agent-readiness-auditor/`.

## On-demand definitions

| Agent | Decision | Rationale | Invoke only when |
| --- | --- | --- | --- |
| `long-horizon-orchestrator` | demote to on-demand | Active Codex/OMX lane already owns normal orchestration; this xhigh controller is expensive. | A genuinely multi-phase controller seat is needed. |
| `implementation-worker` | demote to on-demand | Ordinary implementation is the main lane's job. | A written, isolated implementation slice benefits from a separate builder. |
| `research-scout` | demote to on-demand | Small current-doc lookups belong in the main lane or researcher role. | A bounded external research packet with citations is needed. |
| `risk-reviewer` | demote to on-demand | Routine review is not worth a separate xhigh reviewer call. | High-risk, security-sensitive, or adversarial review needs independence. |
| `verification-auditor` | demote to on-demand | Main lane must run verification before completion anyway. | Independent verification materially improves trust. |

Operational rule: do not invoke on-demand agents as part of a default team or
appearance roster. Name them explicitly in the task plan only when the invocation
rule above is satisfied.
