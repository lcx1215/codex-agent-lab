# Handoff: add frontend-source landing note to README (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-09 17:45 (+0800)
- Kind: doc request (README owner is you; you are actively editing it, ahead 1 unpushed)

## Task

The uploaded repo `clink-merchant-assistant` (branch `import-customer-support-agent`)
ships `integrations/dashboard/frontend-source/` as a 6-file UI patch. User asked
whether to remove it or keep it. Decision: KEEP it (verified it is a pure reference
copy — no code/build/verify in the repo depends on it, and 10 docs reference it, so
removing it would create dead links). But README does not yet tell a frontend engineer
HOW to use it, which risks confusion / two-sided drift with the company `merchant-portal`
repo (the same files the user previously reverted out of merchant-portal).

## Request

You own README and are mid-edit (commit be4778e, ahead 1, unpushed). To avoid two lanes
editing README at once, please add a short frontend-landing note yourself. Suggested
placement: the existing `## 前端和 Feishu` section (around line 400). Suggested text:

> 前端 UI 落地说明:`integrations/dashboard/frontend-source/` 是前端接入的
> **权威源码副本(图纸)**,不在本仓构建。前端工程师需将这些文件合入公司前端仓
> `merchant-portal`(`apps/web-antd/...` 对应路径),走独立分支 + MR 合并部署。
> 请以本仓这份为准,避免与 `merchant-portal` 两边分叉;本仓副本仅作交付存档与
> 前后端接口契约参考(调用 `/agent-api/v1/assistant/{query,query-stream,context-cards}`)。

Rationale to capture:
- It is a reference/handoff copy, NOT built here.
- Frontend team copies it INTO merchant-portal (new branch + MR), does not make
  merchant-portal depend on this repo.
- Treat this repo's copy as the authoritative source to prevent drift (user reverted an
  earlier messy merge out of merchant-portal; next merge should be clean via MR).

## Expected Artifacts

- README updated with the frontend-landing note (your wording is fine; keep the three
  points: authoritative source / merge into merchant-portal via MR / no drift).
- Re-run `npm run verify:upload` after edit.

## Verification

- Confirmed no code/build/verify depends on `frontend-source` (grep of services/,
  config/, scripts/, package.json = no functional references).
- Confirmed 10 markdown docs reference the `frontend-source` path (removing it would
  break them) — hence keep, don't remove.
- Confirmed merchant-portal `origin/main` currently does NOT contain these UI files
  (they were reverted earlier), so this repo is now the sole source.

## Boundary

No push, no MR, no commit by Claude. I did not edit README (you are actively editing it
— scout-before-overwrite). No secret values read. Push stays user-gated.
