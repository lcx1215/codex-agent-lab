# Handoff: default LLM base URL is a 3rd-party relay — prod egress risk (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-09 15:40 (+0800)
- Kind: review finding / production hardening request (no code edits by Claude)

## Task

Compliance asked whether the customer-support agent (a) exposes sensitive-data or
shell tools, (b) is a 3rd-party agent, (c) sends user data off to third parties.
While answering with code evidence I found a real production egress risk in the
default config that should be fixed so no one deploys it by accident.

## Finding (verified in code)

`services/gateway/src/config.mjs`:
- L95: `baseUrl: env.LLM_BASE_URL || env.OPENAI_BASE_URL || 'https://api.modextm.com/v1'`
  → the **default LLM base URL is a third-party relay** (`api.modextm.com`, not an
  official vendor, not company-private). If prod runs without overriding
  `LLM_BASE_URL`, **user conversation content is sent to an external third party.**
- L99: default `model: 'gpt-5.5'`.
- Default provider is `local-rule` (L34), which is safe (no external call), BUT once
  someone sets provider to `openai-compatible`/`anthropic-compatible` without also
  setting the base URL, the relay default kicks in.

Compliance-relevant framing already documented in
`exports/customer-support-production-current/COMPLIANCE_NOTE_zh.md` (Claude wrote it,
no secret values, only config names + hosts):
- Tool allow-list has NO sensitive-data / shell / write tools; `assignment.mjs` has an
  explicit block-list. Agent orchestration is self-built (no LangChain/Dify/Coze).
- Data egress depends entirely on the configured model base URL.

## Request

1. **Change the default `LLM_BASE_URL` so it does NOT silently point at a third-party
   relay.** Options (your call): make it empty and fail-closed (refuse remote model
   unless explicitly configured), or point the doc/default at the company-private
   model gateway. The current `api.modextm.com` default is a footgun — a prod deploy
   that forgets to override it leaks user chats off-site.
2. Document in the deploy/handoff docs that production MUST set the model base URL to
   a **company-private / self-hosted model gateway**, and that using a public/relay
   API requires a compliance review (data egress).
3. Confirm what the intended production model endpoint is (private deploy vs vendor),
   so we can give compliance a definite answer instead of "depends on config".

## Expected Artifacts

- Config default changed (empty/fail-closed or private gateway), OR an explicit
  deploy-doc warning + startup guard that refuses the relay default in production.
- A one-line statement of the intended production model endpoint.

## Verification

- `config.mjs` L34/L82-102 read directly; default `LLM_BASE_URL=https://api.modextm.com/v1`
  and `LLM_MODEL=gpt-5.5` confirmed.
- Running local 8788 instance uses `ANTHROPIC_BASE_URL=http://127.0.0.1:...` (local
  relay, dev only) — confirms prod endpoint is env-driven and currently undecided.
- No secret values read (only config KEY names + hosts). No code edited by Claude.

## Boundary

No push, no MR, no commit. Did not touch customer-support package files Codex is
assembling; this is a review finding + hardening request. HMAC/API keys seen only as
env NAMES, never values.
