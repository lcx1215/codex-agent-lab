# Handoff: dashboard assistant final delivery package refreshed (Codex → Claude)

- From: Codex (OMX lane)
- To: Claude (OMC lane)
- Date: 2026-07-08 15:12 (+0800)
- Kind: delivery closeout / mechanism-backed release handoff

## Task

Finalize the handoff surface for the Clink dashboard assistant hybrid
architecture without touching GitLab remotes or the live dashboard. The goal was
to make the current package maximally handoffable while preserving the true
remaining production blocker.

## Request

Future review should treat this as the current delivery package:

```text
workspaces/agent-dev-workspace/external/merchant-portal-refactor-main-agent/exports/dashboard-assistant-release-current/
```

Current release:

```text
release id: dashboard-assistant-20260708-070618Z
dist archive: dashboard-assistant-dist-20260708-070618Z.tar.gz
sha256: 3ad3ad8d1611fea3fff607abbcc33920d4acb89f57b53ac1b8c2ce31ad2b684c
backend handoff files: 18
```

Do not claim production completion until the real `https://dashboard.clinkbill.dev/`
deployment serves this bundle and both same-origin `/agent-api` POST routes
return JSON before SPA fallback.

## Expected Artifacts

Added or refreshed:

- `docs/dashboard-assistant-final-delivery-checklist.md`
- `exports/dashboard-assistant-release-current/BEND_DEPLOY_NOW.md`
- `exports/dashboard-assistant-release-current/README.md`
- `exports/dashboard-assistant-release-current/dashboard-assistant-release-manifest.json`
- `exports/dashboard-assistant-release-current/dashboard-assistant-dist-20260708-070618Z.tar.gz`
- `exports/dashboard-assistant-release-current/backend-handoff/docs/dashboard-assistant-final-delivery-checklist.md`
- `registry/scratch-durability/snapshots/clink-dashboard-assistant-main-agent/dashboard-assistant-20260708-070618Z/`

Generator/verifier updates:

- `scripts/deploy/prepare-dashboard-assistant-release.mjs`
- `scripts/deploy/verify-dashboard-assistant-backend-handoff.mjs`
- `scripts/deploy/verify-dashboard-assistant-release-package.mjs`
- `scripts/deploy/verify-dashboard-assistant-release-package.test.mjs`

Operational prompt cleanup:

- `agents/customer-support/prompts/subagents/preview-runtime-verifier.md`
- `agents/customer-support/prompts/subagents/debug-loop-auditor.md`
- `agents/customer-support/prompts/subagents/doc-evidence-scanner.md`

Source-of-truth boundary:

- Active package remains
  `workspaces/agent-dev-workspace/external/merchant-portal-refactor-main-agent/agents/customer-support/`.
- Do not use or recreate the historical outer workspace package
  `workspaces/agent-dev-workspace/agents/customer-support/` as a deployment
  source. Old references in archived validation/provenance notes are historical
  evidence only.

## Verification

- `pnpm run verify:dashboard-assistant-backend` — pass, no failures.
- `pnpm run release:dashboard-assistant` — pass, generated timestamped release
  and refreshed `exports/dashboard-assistant-release-current`; local release
  verifier OK, live not run.
- `pnpm run verify:dashboard-assistant-release-package` — pass, 18 backend
  handoff files, 688 dist checksum entries, 688 extracted dist files, 21
  release text files secret-scanned.
- `pnpm test:assistant-bff` — pass, 5 files / 38 tests.
- `pnpm run smoke:dashboard-assistant-release-local` — pass, archive sha, BFF
  health, root HTML, both `/agent-api` routes, and gateway signature checks OK.
- `scripts/check-agent-packages` — pass, 2 registries, 2 packages, 6 agents,
  0 failed links.
- `scripts/check-collaboration` — pass, protocol OK, 21 assignments, 29
  handoffs.
- `scripts/check-secrets` — pass, no committable secrets or README-local user
  paths detected.
- `python3 -m unittest tests.test_scratch_durability` — pass, 4 tests.
- `scripts/check-scratch-durability` — warn only:
  `SCRATCH_OWNER_REPO_PENDING` for the future dedicated agent-runtime/B-end owner
  repo decision.

Skipped/aborted: `scripts/check-lab` was started twice but became too slow in
the current shell. Both instances were interrupted; this handoff relies on the
targeted gates above.

Boundary: no GitLab push/merge/stage/reset/clean; no live dashboard deploy; no
secrets or `.run/` capture. The production blocker remains external deployment
authority for the original dashboard domain plus production B-end route/session
configuration.
