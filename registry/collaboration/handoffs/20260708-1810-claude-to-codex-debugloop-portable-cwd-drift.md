# Handoff: debug-loop `package-portable` probe fails (cwd drift after package relocation)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-08 18:10 (+0800)
- Kind: defect report + reproduction (review-only; no source logic changed)

## Task

Independent brain/deploy verification of the customer-support agent after your
2026-07-08 release + login-fallback + UI work. Ran the full gateway test suite
and the backend debug loop.

## What is green (evidence)

- Gateway node test suite: **253 pass / 2 fail** out of 255. All brain logic
  green: orchestrator, intents, knowledge (CJK tokenizer fine, no AC-1),
  modelGateway, identityScope, eventStore, runStore.
- `runtime-security` probe 69/69, `answer-quality` probe 72/72, `context-eval`,
  `runtime-contract`, `backend-http-contract` — all pass.
- Login fallback independently reproduced: `POST /prod-api/auth/login` → HTTP 200
  + header `x-clink-local-demo-login-fallback: true` + `local_demo_*` token when
  backend 403s. 8790/8788 both live, health 200. Real token still proxies.
- I fixed `deployConfig.test.mjs`: the two stale tmux assertions
  (`GATEWAY_SESSION="${SESSION_PREFIX}-gateway"` / `BFF_SESSION=...`) now assert
  the pid-file launcher shape (`GATEWAY_LAUNCHER`/`BFF_LAUNCHER`/`*_PID_FILE`/
  `nohup bash`). You then merged fast-start assertions on top at 18:02 — file is
  green now (`node --test test/deployConfig.test.mjs` exit 0).

## Request

Fix the `package-portable` probe cwd drift in `scripts/debug-loop.mjs` so the
backend debug loop returns to green, and commit it on the Codex lane. Detail below.

## Expected Artifacts

- `scripts/debug-loop.mjs` (probe `cwd`/workspace-root resolution fix)
- `services/gateway/test/debugLoop.test.mjs` back to green
- optional: `check-portable.sh` relocation/symlink if you choose fix option 2

## Verification

- `node --test "services/gateway/test/*.test.mjs"` → 255/255
- `runDebugLoop({profile:'backend'})` → status=pass, findings=[]

## The one real defect (Codex to fix)

`test/debugLoop.test.mjs` → `debug loop backend profile default probe list stays
backend-only` fails because the `package-portable` probe exits **127**:

```
bash: scripts/check-portable.sh: No such file or directory
```

Root cause = **cwd drift after the package was relocated under
`external/merchant-portal-refactor-main-agent/`**:

- In `scripts/debug-loop.mjs` the `package-portable` probe is defined with
  `cwd: workspaceRoot` and `command: ['bash', 'scripts/check-portable.sh']`.
- `workspaceRoot` is computed as `packageRoot/../..`. Before relocation that
  landed on `workspaces/agent-dev-workspace/` (where `scripts/check-portable.sh`
  really lives, mtime 07-01). After relocation `packageRoot` is
  `.../external/merchant-portal-refactor-main-agent/agents/customer-support`, so
  `packageRoot/../..` now resolves to `.../external/` — which has no
  `scripts/check-portable.sh`. Hence exit 127.
- Proof it is NOT a portability regression: running the real script directly
  (`bash workspaces/agent-dev-workspace/scripts/check-portable.sh`) prints
  "Portable check passed." exit 0.

## Suggested fix (your call on exact shape)

Pick one; do not weaken the secret/path boundary the probe enforces:

1. Resolve the probe `cwd` to the actual workspace that owns
   `scripts/check-portable.sh` (walk up until the script is found, or make the
   path configurable via the debug-loop contract), OR
2. Point the probe at the package-local portability check if that is the
   intended post-relocation home, and move/symlink `check-portable.sh`
   accordingly, OR
3. If `external/` is meant to be a git-root boundary, make `workspaceRoot`
   detection anchor on a marker file rather than a fixed `../..` depth.

After the fix: `node --test "services/gateway/test/*.test.mjs"` should be 255/255
and `runDebugLoop({profile:'backend'})` should return status=pass findings=[].

## Boundary

Review-only on your source logic. I edited only `deployConfig.test.mjs` (stale
assertion catch-up). No commit, no push, no GitLab, no live deploy, no secrets
read. Codex owns the debug-loop cwd fix + any commit.
