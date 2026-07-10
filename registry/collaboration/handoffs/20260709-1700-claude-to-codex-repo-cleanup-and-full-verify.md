# Handoff: repo cleanup required + full verification evidence (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-09 17:00 (+0800)
- Kind: review — one blocking cleanup + full verification record

## Task

Deep pre-push review of `workspaces/customer-support-production-repo`. User goal:
production-grade, minimize backend/ops confusion. I verified everything I can verify
locally and found ONE thing that must be fixed before push: repo hygiene (internal
files + dead links leak into the company-facing repo).

## Request

Please fix the repo hygiene issues below in your lane (these files are yours; I did
not delete them). All are delete/rename — no functional code touched.

### A. Remove internal / experimental files that should NOT ship to company GitLab
(all currently git-tracked, would be pushed):
- `CLAUDE.md`, `AGENTS.md`, `SHARE.md` — internal AI-collaboration rules; backend
  readers won't know what these are.
- `browser/`, `browser-extension/`, `evals/`, `skills/`, `prompts/` — dev/experiment.
- `docs/superpowers/` (plans), `docs/VALIDATION.md` (16K, full of dead links to files
  not in this repo), `docs/development-fast-start.md`.
- Top-level stray `billing-resolution.agent.json`, `support-triage.agent.json`,
  `clinkbill-assistant.agent.json` — decide if these belong or move under a clear dir.

### B. Fix dead links / name drift in SHIPPING docs (these confuse ops directly)
- `README.md` and `PRODUCTION_RELEASE_zh.md` reference `clink-gateway-path-mapping.yml`
  but the actual file is `deploy/templates/nacos-clink-gateway-path-mapping.agent-api.yml`.
  Ops will look for the referenced name and not find it. Fix the reference or rename.
- `integrations/.../OPS_DEPLOY_CHECKLIST_zh.md` same `clink-gateway-path-mapping.yml`
  dead reference.
- Several `/openapi.json` and cross-doc links in `docs/contracts/*` are dead — either
  ship the target or drop the link.

## Expected Artifacts

- Internal/experimental files removed from the repo.
- Shipping-doc references point at real files (no dead links in README /
  PRODUCTION_RELEASE / ops checklists).
- Re-run `npm run verify:upload` after cleanup.

## Verification

Everything below I re-ran myself (not trusted from report):
- Node gateway: `261 pass / 1 skip / 0 fail` (after `npm install`).
- `npm run verify:upload`: PASS (release + secret scan + transient scan).
- Java (real `clink-gateway`, BFF already merged into src/main): `mvn -o compile` =
  BUILD SUCCESS, 8 BFF classes emitted; `mvn -o test` for the 3 BFF suites =
  **13 run / 0 fail / 0 error**. Identity resolver uses REAL company APIs and they
  compile: `LoginHelper.getTenantId()`, `MerchantHelper.getDynamicMerchant()`,
  `LoginHelper.getUserId()`, `StpUtil.checkLogin()` (from `clink-common-satoken` 2.2.2).
- Secrets clean; knowledge base public-only; no transient artifacts tracked.
- Multi-replica: nonce/idempotency memory Maps HAVE shared-store fallback
  (`AGENT_API_BFF_REPLAY_STORE_MODULE`, `RUN_STORE_LIBSQL_URL`) and DEPLOY.md §Multi-
  Replica documents it + fail-closed if unset. Not a bug.
- `docker-compose.yml` is complete (49 lines) — README `docker compose up` is valid.
- `integrations/dashboard/frontend-source` is a 6-file PATCH into the company web-antd
  repo (not a buildable frontend); build happens in the company FE repo. Correct by design.

## Residual (NOT code — cross-team confirmation, cannot be closed by us)

- Identity field SEMANTICS: methods compile, but 鹏哥 must confirm
  `getDynamicMerchant()`/`getUserId()` map to the intended merchant/person. One-sentence
  confirm, not a code change.
- Company Nacos actual schema for the `/agent-api/**` route (ops confirm).
- Real end-to-end (real login + TEST DB) never run — needs a real environment.

## Boundary

No push, no MR, no commit by Claude. Installed deps + compiled/tested locally (all
gitignored; 0 tracked changes). Did not delete Codex's files — cleanup is your call.
No secret values read. Push stays user-gated.
