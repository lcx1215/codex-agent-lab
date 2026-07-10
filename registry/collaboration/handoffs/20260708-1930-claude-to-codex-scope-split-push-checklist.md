# Handoff: customer-support scope split + push checklist (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-08 19:30 (+0800)
- Kind: decision record + pre-push checklist (no push performed; user has NOT
  yet approved any GitLab push)

## Task

The user concluded the customer-support package "做得太大了" — it grew into a
full-stack monolith (frontend + BFF + backend + business logic + DB + devops all
in one package). This handoff records the agreed scope boundary and the checklist
Codex must run before anything is pushed.

## Request

Before pushing anything to GitLab, split the package by ownership and only push
each part to its correct repo. Do NOT push the whole package into the frontend
repo. Run the checklist below and report results. Wait for explicit user
go-ahead on every remote push (push/MR is an outward action, still gated).

## Ownership split (agreed with user)

The package currently mixes four different owners. Route each part home:

1. **Frontend integration (6 files) → `merchant-portal-refactor` (frontend repo).**
   These are Vue components, depend only on frontend libs (`vue`, `vue-router`,
   `ant-design-vue`, `@vben/preferences`, `#/api/request`, `#/locales`), and are
   absent from `origin/main` today. They belong in the Vben frontend repo.
   - `apps/web-antd/src/api/assistant-support.ts`
   - `apps/web-antd/src/components/assistant-support/index.ts`
   - `apps/web-antd/src/components/assistant-support/src/context.ts`
   - `apps/web-antd/src/components/assistant-support/src/assistant-support.vue`
   - `apps/web-antd/src/locales/langs/zh-CN/assistantSupport.json`
   - `apps/web-antd/src/locales/langs/en-US/assistantSupport.json`
2. **Agent brain (`services/gateway/` = agent/ + runtime/ + security/, plus
   knowledge/, prompts/, skills/) → stays on fly / its own repo. NOT the frontend
   repo.** This is the backend service; it already runs at
   `clinkbill-support.fly.dev`.
3. **B-end identity/BFF layer (the Java patch) → `clink-gateway` (backend repo),
   branch `codex/agent-api-bff`.** Derives tenant/merchant/person from Sa-Token
   session, signs `X-Agent-BFF-*`. NOT the frontend repo.
4. **Deploy/devops (`deploy/`, `scripts/` ~33 files, nginx / Spring Cloud Gateway
   templates) → deliverables handed to ops/B-end, not maintained inside the agent
   package as "core".**

## Expected Artifacts

- A frontend-only change set (the 6 files above) prepared for
  `merchant-portal-refactor`, secret-clean and CI-green locally.
- A new `.env.example` (names only, no values).
- A collab ledger entry for the scope split (e.g.
  `collab-0023-scope-split-frontend-push`).
- Confirmation of the ownership routing for brain / Java BFF / devops parts
  (which repo each goes to), with none of them in the frontend push.

## Checklist for Codex before any push

- [ ] **Confirm the frontend push contains ONLY the 6 files above.** No
      `services/gateway/`, no `deploy/`, no `scripts/`, no `browser*/`, no
      `exports/`, no `.run/`, no `node_modules/`. If the diff includes backend or
      devops files, stop — the split is wrong.
- [ ] **Secret scan the exact push set.** No real `LLM_API_KEY`, `TURSO_*`,
      HMAC secrets, gateway tokens, fly tokens, preview tokens, cookies. Run
      `scripts/check-secrets`. Secrets must never enter git history (irreversible).
- [ ] **Add a `.env.example`** (variable NAMES + purpose only, empty values) so
      other engineers know what to configure to reach the remote model + Turso.
      Currently missing. Do not put real values in it.
- [ ] **Rebase before push.** `main` is ahead of
      `codex/assistant-support-integration` by 2 commits — rebase to avoid
      conflicts.
- [ ] **Pass repo CI locally first.** The frontend repo has typecheck + cspell
      gates; run them on the 6-file change so the MR does not go red.
- [ ] **Confirm the FE component's agent base URL is config-driven** (it uses
      the repo's `requestClient` / `#/api/request`, so the endpoint is set by the
      frontend repo's env, not hardcoded) — document which var the FE team sets.
- [ ] **Open a collab ledger entry** for the scope-split + push (e.g.
      `collab-0023-scope-split-frontend-push`); Claude will do the reviewer pass.
- [ ] **Get explicit user go-ahead** before the actual `git push` / MR. Push is
      an outward action; approval in one context does not extend to the next.

## Open question for the user (do not assume)

Does the user have push rights to `merchant-portal-refactor`? If not, the 6
files must be handed to a frontend engineer / Codex to raise the MR — the user
cannot push them directly. Confirm before choosing the push path.

## Verification

- Gateway suite 259/259; backend debug-loop pass, findings=0.
- Release archive sha256 matches claimed (`cf4c8ad4...`).
- P1 (caller-scoped idempotency + shared libSQL run store + fail-closed) and P2
  (deploy-handoff refresh) verified — see `docs/VALIDATION.md` 18:45 section.
- The 6 frontend files confirmed absent from `origin/main` and from the Codex
  integration branch (they live only in the local `-main-agent` assembly area).

## Boundary

No push, no MR, no stage, no commit, no live deploy, no secret values read by
Claude. Claude edited only `deployConfig.test.mjs` (stale-assertion catch-up)
and validation/handoff docs this session. Codex owns the split, the commits,
and any push (with user approval).
