# Handoff: merchant-console "人工" button shows false success on rejected handoff (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex lane
- Date: 2026-07-10 12:30 (+0800)
- Kind: ClinkBot re-review finding on 47c1bb0. NON-blocking, demo-surface frontend bug.
  NOT a security or backend defect. Claude verified; Codex owns the fix.

## Task

ClinkBot (gpt-5.5) re-reviewed import-customer-support-agent @ 47c1bb0. Confirmed the
BFF single-secret key-id fix landed. New finding: the "人工" (request-human) button in the
demo console reports success even when the real handoff request is rejected.

## The finding (Claude VERIFIED against real code)

- apps/merchant-console/index.html:7037 calls POST /v1/assistant/handoff directly from the
  browser (cookie/same-origin), reading session id only inside `if (response.ok)` (:7052).
- server.mjs:393 + :987 correctly return 403 `backend_header_auth_required` for browser
  cookie auth on /assistant/handoff — this is the INTENDED hardening (browsers must not call
  internal endpoints). So the request is rejected as designed.
- Bug: the frontend does NOT handle non-2xx. A 403 is not an fetch reject, so `catch` never
  fires; sessionId stays at the default sentinel 'CB-1031'; then it unconditionally fires
  trackAssistantEvent('handoff.submitted') and shows "已为你提交人工客服" + "人工客服已接入".
- Net: user sees "human agent connected" while the backend accepted nothing.

## Scope / severity

- Surface is apps/merchant-console (local/demo verification UI), NOT the real B-end dashboard
  frontend (integrations/dashboard/frontend-source). So blast radius = demo/console, not the
  production merchant path. Severity: low-to-medium, NON-blocking for dashboard go-live.
- Root cause is using the wrong endpoint for browser context: browser should go through the
  browser-allowed path, not the internal /handoff.

## Request

(Codex to implement.)

- Preferred: route the demo "人工" action through the browser-allowed
  POST /v1/assistant/query with `request_human: true` (backend still owns handoff decision),
  OR add a signed/BFF-safe handoff path if a dedicated endpoint is required.
- Minimum: on non-2xx, reset handoffSubmitted state and show a failure message instead of the
  success animation. Do not emit handoff.submitted on a rejected request.
- Add/adjust a test so a rejected handoff does not render success.

## Verification

(Claude.)

- Traced call site (index.html:7037-7059) + backend rejection (server.mjs:393,987,
  backendHeaderAuthError / isBrowserCookieAuth). Confirmed 403-on-browser is intended and the
  frontend swallows it. gateway suite 266 pass / 0 fail / 2 skip on 47c1bb0 (unrelated to this
  demo-page bug, which has no gateway test coverage yet).
- Claude did NOT edit the delivery repo (Codex is actively working it; avoid concurrent clobber).

## Expected Artifacts

- merchant-console request-human path uses a browser-allowed endpoint and/or handles non-2xx.
- Failure no longer renders as success; no handoff.submitted on rejection.
