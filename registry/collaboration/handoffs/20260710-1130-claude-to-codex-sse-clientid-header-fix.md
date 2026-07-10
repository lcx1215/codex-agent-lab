# Handoff: SSE ClientID header missing — fix spec (Claude → Codex)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-10 11:30 (+0800)
- Kind: NEW severe finding from ClinkBot re-review of f09cec3 + verified fix spec.
  Claude STOOD DOWN (both lanes were editing the delivery repo concurrently) and
  reverted its own edits so Codex owns the landing. This is the spec, not a patch.

## Task

ClinkBot (gpt-5.5) re-reviewed `import-customer-support-agent @ f09cec3` and confirmed
the prior 3 fixes (pre-login mount, off-topic page-context, replay Scan) are resolved,
but found ONE remaining SEVERE issue: the SSE assistant fetch still lacks the ClientID
header, so production Sa-Token gateway rejects it.

## The finding (Claude independently VERIFIED against real code)

- `basic.vue` header provider returns ONLY `Authorization`, no `ClientID`
  (integrations/dashboard/frontend-source/apps/web-antd/src/layouts/basic.vue, the
  `assistantHeaderProvider` closure).
- The Java gateway `AuthFilter.java` checks header ClientID matches the token's bound
  client and throws NotLoginException on mismatch/missing — so a request with
  Authorization but no ClientID is rejected in production.
- Real clientId source (cross-repo fact, verified in the B-end main repo copy at
  workspaces/agent-dev-workspace/external/merchant-portal-refactor):
  - `packages/effects/hooks/src/use-app-config.ts:20,31`: `clientId: VITE_GLOB_APP_CLIENT_ID`
    (the RAW env key is `VITE_GLOB_APP_CLIENT_ID`; useAppConfig maps it to `clientId`).
  - `apps/web-antd/src/api/request.ts:32,108`: `const { clientId } = useAppConfig(import.meta.env, import.meta.env.PROD)`
    then `config.headers.ClientID = clientId`.
- The assistant's window/storage fallback previously probed `_VBEN_ADMIN_PRO_APP_CONF_.clientId`
  but NOT the raw key `VITE_GLOB_APP_CLIENT_ID`, so even the fallback likely missed it.

## Fix spec (what Claude implemented, verified green, then reverted for you to own)

1. `basic.vue`: import `useAppConfig` from `@vben/hooks` (already imports useWatermark from
   there), resolve `const { clientId: appClientId } = useAppConfig(import.meta.env, import.meta.env.PROD)`
   — SAME source as request.ts — and have `assistantHeaderProvider` also set
   `headers.ClientID = String(appClientId||'').trim()` when non-empty (keep the existing
   Authorization branch). Return an object built up from both headers.
2. `assistant-support.ts`: add the raw env key `VITE_GLOB_APP_CLIENT_ID` to the client-id
   fallback discovery (CLIENT_ID_STORAGE_KEYS, the storage-JSON paths, and
   CLIENT_ID_WINDOW_JSON_PATHS) so storage/window fallback also finds it.
   (NOTE: a linter already applied a broader version of this in the working tree before
   revert — Codex may re-derive or reuse it.)
3. `deployConfig.test.mjs`: replace the string-presence assert (`assert.match(api,/ClientID/)`)
   with a STRUCTURAL assertion that the provider derives ClientID from useAppConfig().clientId
   and assigns it to the returned headers, plus a guard against regressing to an
   Authorization-only provider. ClinkBot specifically asked for real-header-construction
   tests over string matching — the string test passed even when ClientID was never returned,
   which is exactly why this bug slipped through.

## Verification (Claude, before revert)

- gateway suite 259 pass / 0 fail / 2 skip (was 258; +1 the new structural test).
- node --check on all touched files clean; verify:upload release+eval passed.
  (`rg: command not found` in the secret-scan step is the known Claude-zsh PATH gotcha,
  not a real failure — run with /Applications/Codex.app/Contents/Resources on PATH.)

## Request

- Land the ClientID fix (spec above) as a Codex commit on import-customer-support-agent.
- Keep the structural test (not string-match) so this cannot silently regress.
- After landing, re-send the branch link to ClinkBot for the next pass.

## Expected Artifacts

- basic.vue provider returns both Authorization and ClientID from useAppConfig().clientId.
- assistant-support.ts fallback probes VITE_GLOB_APP_CLIENT_ID.
- deployConfig.test.mjs structural provider test.
