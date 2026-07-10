# Handoff: real-merchant live-test findings — intent routing + model fallback (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-09 22:30 (+0800)
- Kind: post-merge findings — NON-blocking, post-launch optimization items from a real
  B-end merchant live test (with real Claude model via modextm relay + DynamoDB).

## Task

I ran the full agent as a real B-end merchant against the DynamoDB architecture, first
with local-rule, then with a real Claude model (anthropic-compatible). Deployment/usability
is FINE — the finding is about answer quality (internal intent understanding), not a deploy
failure. Recording so these don't get lost as post-launch optimizations.

## What works (verified live, not claimed)

- Service boots, health 200; query / query-stream(SSE) / context-cards all respond.
- Data lands in DynamoDB (biz-runtime CONV records confirmed via Scan); knowledge
  retrieved from local JSON (payments-support / clink_payment_skills / clink_integ_skills).
- Real model connects & answers (log: provider=anthropic-compatible model=claude-sonnet-5
  status=ok fallback=false).
- Safety holds: refund request → needs_handoff=true (refused execution); onboarding →
  no promise + handoff; low-confidence/chitchat → handoff. Every answer carries ~5 evidence.

**Conclusion: it runs, it's usable, it answers. Not a "deployed but won't work" problem.**

## Finding 1 (real, latency-independent) — intent routing not robust to phrasing

Same question, different phrasing, fresh sessions, model succeeded both times
(fallback=false), but results diverged:
- "webhook回调收不到怎么办" → route integration_validation → excellent answer (3-step
  callback-address/firewall/delivery-log troubleshooting).
- "我配了webhook但一直收不到支付成功的回调怎么排查" → route support_triage → answered
  "第一笔支付3信号" (wrong topic).

Root cause: intent detection / triage keys on keywords and is brittle to long, colloquial
phrasing. The miss happens BEFORE the model call — the model then gets a wrong intent +
wrong retrieved knowledge, so a faster/smarter model can't fix it. Real merchants use
long colloquial phrasing, so this WILL happen in production. Severity: medium — not a
crash, not a safety issue (refund still handed off), but degrades answer relevance.

Fix options: (a) expand intent synonyms/colloquial phrasings for webhook/回调/收不到 etc.;
(b) better: let the model participate in intent classification (model understands NL far
better than keyword rules), keeping backend as the authority on assignment/handoff.

## Finding 2 (config/observability) — silent fallback to local-rule on model timeout

modextm relay latency was 8–20s; anthropic timeout default is 20s, so calls frequently
timed out and silently fell back to local-rule (log: status=error latency_ms=20028
fallback=true reason=timeout), which then produced fixed template text. In production, if
the company model gateway is slow, the agent silently degrades to rule answers and neither
user nor ops knows. Fix: (a) surface degradation (e.g. response flag model_degraded=true
or a warning metric/log) so a degraded answer is observable; (b) make timeout configurable
per environment and document expected model latency budget.

## Finding 3 (docs) — README under-documents model wiring & rule↔model mechanics

Config keys exist in ops/CONFIG_KEYS_zh.md (LLM_/ANTHROPIC_*), but README has no direct
"to connect a real model, set these envs" block, and does not systematically explain:
rule↔model division (backend assembles trimmed safe context pack; model writes draft only),
fallback-to-local-rule behavior, timeout values, grounding rules, gateway queue/concurrency.
User specifically flagged this gap. Add a README "模型接入" section covering these.

## Request

Record these as POST-LAUNCH optimizations (none blocks the current merge). Prioritize:
1. Finding 2 observability (silent degradation is a production risk) — make fallback visible.
2. Finding 1 intent robustness — expand phrasings and/or model-assisted intent.
3. Finding 3 README model section.

## Expected Artifacts

- Fallback/degradation made observable (response flag or metric/log when model falls back
  to local-rule); configurable + documented model timeout.
- Intent routing more robust to colloquial phrasing (expanded synonyms and/or
  model-assisted intent classification), backend still owning assignment/handoff.
- README "模型接入" section: direct env list to connect a real model + rule↔model
  mechanics (context pack, fallback, timeout, grounding, queue).

## Verification

- Live-tested on branch import-customer-support-agent @ bcb001a with real Claude model +
  local DynamoDB (localhost:8000). Isolated latency by raising timeout to 90s: intent
  routing bug persisted with model fallback=false, proving it is agent-side, not relay
  latency. Deploy/usability/data/safety all verified working.

## Boundary

Non-blocking post-launch items — do NOT hold the merge for these. No push/MR by Claude.
Test API key appeared in chat in plaintext — user advised to rotate it; not stored by Claude.
Local test agents cleaned up; local DynamoDB left running.
