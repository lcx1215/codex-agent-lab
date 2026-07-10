# Handoff: nginx template SSE gaps + doc consistency (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-09 13:30 (+0800)
- Kind: review finding (no edits to Codex files; verify + fix in your lane)

## Task

User is about to hand the deploy package to their company ops/backend and is worried
"运维配好了发现出错". I did a pre-ship end-to-end + template audit of the current
`/agent-api` production path. Java gateway itself is verified good; the nginx edge
template has real gaps that would break `query-stream` in production.

## Request

Please verify and, in your lane, fix the nginx template + reconcile the docs. These
are your delivery artifacts; I did not edit them.

## Findings (verified against your files)

1. **nginx template missing SSE settings — `query-stream` WILL break in prod.**
   `scripts/deploy/templates/nginx-dashboard-assistant/dashboard-assistant.conf`
   (and the identical backend-handoff copy) `location ^~ /agent-api/` has NO
   `proxy_buffering off;`. nginx default buffering will coalesce the SSE stream →
   ChatGPT-style streaming becomes "hang then dump". Also missing
   `proxy_read_timeout` (default 60s cuts long answers) and
   `proxy_request_buffering off`. The Java gateway correctly sends
   `X-Accel-Buffering: no`, but that alone is not reliable across all nginx configs;
   the edge must set buffering off explicitly for the `/agent-api/` location.

   Suggested additions inside `location ^~ /agent-api/`:
   ```nginx
   proxy_buffering off;
   proxy_request_buffering off;
   proxy_cache off;
   proxy_read_timeout 300s;
   proxy_send_timeout 300s;
   ```

2. **README upstream story contradicts SERVICE.MD.** The nginx README says the
   upstream is "the included Node assistant BFF"
   (`assistant_bff_upstream -> assistant-agent-bff internal service`), but
   `clink-gateway/SERVICE.MD` states the production BFF is the Java `clink-gateway`
   (Sa-Token session → identity → HMAC). Ops will be confused about which service
   `/agent-api` should target. Please pick one production story and make the README
   name/point at the Java gateway (or clarify the Node BFF is demo-only).

3. **What is verified GOOD (no action):** Java gateway on local 8793 — targeted
   tests 13/13; live smoke `context-cards`/`query` 200 JSON, `query-stream` 200 SSE
   with real `start/delta/done`, headers `text/event-stream` + chunked +
   `no-store` + `X-Accel-Buffering: no`. Route order `^~ /agent-api/` before SPA
   fallback: correct. path not rewritten (`proxy_pass` without trailing path):
   correct. Self-forward-loop warning present in SERVICE.MD:81: good.

## Expected Artifacts

- Updated nginx template with SSE buffering/timeout for `/agent-api/`.
- README reconciled with SERVICE.MD on which service is the production BFF.
- Optional: a note in BEND_DEPLOY_NOW.md that streaming requires edge buffering off.

## Verification

- Java gateway 8793 smoke: `context-cards` 200 JSON; `query` 200 JSON;
  `query-stream` 200 `text/event-stream` chunked, emitted `event: start` + data.
- Two-layer mistake noted: chaining the Node `assistant-agent-bff.mjs` in FRONT of
  the Java gateway returns `identity_not_configured`/`not_found` — expected, because
  prod is nginx-static + Java-gateway-as-sole-BFF, NOT two stacked BFFs. The Node
  shell is local-demo only. Confirms the topology.
- No push / MR / commit; Codex delivery files untouched by Claude.

## Boundary

No push, no MR, no commit, no secret values read. HMAC secret seen only as env NAME.
