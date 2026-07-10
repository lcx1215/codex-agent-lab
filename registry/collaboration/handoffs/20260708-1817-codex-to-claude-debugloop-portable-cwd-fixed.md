# Handoff: debug-loop portable cwd drift fixed (Codex → Claude)

- From: Codex (OMX lane)
- To: Claude (OMC lane)
- Date: 2026-07-08 18:17 (+0800)
- Kind: implementation complete / independent reviewer requested

## Task

Fix the customer-support `debug-loop` backend profile failure caused by the
`package-portable` probe running from the relocated product assembly root.

## From / To

- From: codex
- To: claude

## Context

Claude reported the defect in:

`registry/collaboration/handoffs/20260708-1810-claude-to-codex-debugloop-portable-cwd-drift.md`

The active package is still:

`workspaces/agent-dev-workspace/external/merchant-portal-refactor-main-agent/agents/customer-support/`

Root cause confirmed by Codex: `scripts/debug-loop.mjs` computed
`workspaceRoot` as `packageRoot/../..`, which is now the product assembly root.
That root does not contain `scripts/check-portable.sh`; the owning workspace
does, at `workspaces/agent-dev-workspace/scripts/check-portable.sh`.

## Request

Please independently re-verify this Codex fix and update
`collab-0022-debugloop-portable-cwd` with your reviewer verdict.

## Constraints

- Review only; no GitLab push or live deploy is needed.
- Do not read or print secrets, `.env` values, cookies, tokens, or auth files.
- Keep the production dashboard claim separate from this local correctness fix.
- Do not treat the fast LAN demo as production deployment evidence.

## Expected Artifacts

Changed implementation:

- `workspaces/agent-dev-workspace/external/merchant-portal-refactor-main-agent/agents/customer-support/scripts/debug-loop.mjs`

Collaboration tracking:

- `registry/collaboration/assignments.json`
- `registry/collaboration/handoffs/20260708-1817-codex-to-claude-debugloop-portable-cwd-fixed.md`

## Verification

Codex ran:

- `node --check agents/customer-support/scripts/debug-loop.mjs` — pass.
- `node agents/customer-support/scripts/debug-loop.mjs --profile backend --rounds 1` — pass, `findings=0`.
- `node --test agents/customer-support/services/gateway/test/debugLoop.test.mjs` — pass, 12/12.
- `npm test --prefix agents/customer-support/services/gateway` — pass, 255/255.

Suggested reviewer commands:

```sh
cd /Users/liuchengxu/Desktop/codex-agent-lab/workspaces/agent-dev-workspace/external/merchant-portal-refactor-main-agent
node agents/customer-support/scripts/debug-loop.mjs --profile backend --rounds 1
npm test --prefix agents/customer-support/services/gateway
cd /Users/liuchengxu/Desktop/codex-agent-lab
scripts/check-collaboration
```
