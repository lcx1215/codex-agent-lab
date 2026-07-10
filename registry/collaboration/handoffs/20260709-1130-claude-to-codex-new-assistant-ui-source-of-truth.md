# Handoff: which assistant UI is the source of truth + how to run it against real data (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-09 11:30 (+0800)
- Kind: question / alignment request (NO push, NO commit, NO overwrite performed)

## Task

User wants to log in with their real company account, reach the REAL backend data
on `https://dashboard.clinkbill.dev`, and see the LATEST assistant AI UI (the one
Codex most recently built) — NOT the old demo UI. User reports "登进去还是老的 ai ui
界面" and asked me to stop and align with Codex before touching anything.

## What I found (facts, read-only)

1. The old UI the user saw came from `real-agent-demo-server.mjs` (pid 7551, port
   8791) which serves a hard-coded `demoHtml()`, plus my own stray
   `assistant-agent-bff.mjs` old shell. Both are stopped now (user confirmed 7551
   was theirs). 8791 is free.
2. The real assistant UI lives in these files, and they DIFFER between the
   assembly area and the real repo:

   | file | assembly `-main-agent` | real repo `merchant-portal-refactor` |
   |---|---|---|
   | `apps/web-antd/src/api/assistant-support.ts` | differs (139 lines) | mtime newer |
   | `.../assistant-support/src/assistant-support.vue` | 2026-07-08 21:49 | **2026-07-09 11:10 (NEWER)** |
   | `.../src/context.ts` | differs (33) | |
   | zh-CN/en-US `assistantSupport.json` | differs (25 each) | |
   | `layouts/basic.vue`, `layouts/auth.vue` | differs (4 / 1) | |

   **The real repo's .vue is NEWER than the assembly area's** (07-09 11:10 vs
   07-08 21:49). So my earlier assumption "assembly = latest" was WRONG. Someone
   updated the real repo component this morning.
3. Real backend is reachable and live: `GET /prod-api/system/user/getInfo` →
   `{"code":401,"msg":"未能读取到有效 token"}` (real backend, not demo). Login is
   POST `/prod-api/auth/login`, `altcha` human-verification is ON
   (`altchaEnabled:true`) — so login MUST happen in a real browser by the user,
   not via curl. Passthrough works: local BFF real-mode returns the identical
   real-backend 401 (no `x-clink-local-demo-auth` header).
4. New UI calls (from `assistant-support.ts`): `/agent-api/v1/assistant/query`
   (sync), `/agent-api/v1/assistant/query-stream` (SSE — you shipped streaming!),
   `/agent-api/v1/assistant/context-cards`. Same-origin, base = `window.location.origin`.

## What I did NOT do

- Did NOT push / commit / MR / stage anything. GitLab untouched.
- I briefly overlaid the assembly-area files onto a temp branch
  `claude/new-assistant-ui-alignment`, then user said align first — I fully
  reverted (git checkout -- the 7 files), deleted the temp branch, restored real
  repo to clean `assistant-support-integration` (only the pre-existing 2 unrelated
  `.mjs` changes remain, untouched by me).

## Request

(Please answer before I build/run anything.)

1. **Which assistant UI is the source of truth right now?** The real repo's .vue
   is newer (07-09 11:10) than the assembly area's (07-08 21:49). Is the real repo
   `assistant-support-integration` branch ALREADY the latest UI you built? Or is
   the assembly `-main-agent` version the intended one and the real repo got an
   unrelated tweak? I do not want to overwrite the newer with the older.
2. **User has push rights to `merchant-portal-refactor` and wants to run it
   locally against real data first (no push).** What's your intended way to run
   the real frontend locally so `/agent-api` is served and `/prod-api` proxies to
   `dashboard.clinkbill.dev` with real login? Is there a ready dev/preview command
   + dist, or should I build from the real repo?
3. **Ownership / who commits:** per your 07-08 scope-split checklist the FE files
   go to `merchant-portal-refactor` and you own the commits. User can push. Do you
   want me to prepare the change set for user to push, or will you commit it?

## Expected Artifacts

- Codex answer on #1: which assistant UI is source-of-truth (real repo
  `assistant-support-integration` @ 07-09 11:10 vs assembly `-main-agent` @ 07-08
  21:49), so the newer version is not clobbered by the older.
- Codex answer on #2: the intended local run recipe (dev/preview command + dist)
  to serve the real frontend with `/agent-api` + `/prod-api` → real backend.
- Codex answer on #3: who commits the FE change set (Claude prepares vs Codex
  commits), consistent with the 07-08 scope-split checklist.

## Verification

- Real backend reachability confirmed read-only: `/prod-api/system/user/getInfo`
  → real-backend `401`; local BFF real-mode returns identical `401` with no
  `x-clink-local-demo-auth` header (true passthrough).
- Real repo restored clean: on `assistant-support-integration`, the 7 UI files
  reverted (git checkout), temp branch `claude/new-assistant-ui-alignment`
  deleted; only the pre-existing 2 unrelated `.mjs` changes remain (not mine).
- No push / MR / commit / stage performed; `scripts/check-collaboration` re-run
  after this handoff.

## Boundary

No push, no MR, no commit, no secret values read. Login stays in the user's
browser (altcha). I only need your answer on #1 to avoid clobbering the newer UI.
