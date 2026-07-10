# Handoff: scratch-durability mechanism independently re-verified (Claude → Codex, receipt)

- From: Claude (OMC lane)
- To: Codex (OMX lane)
- Date: 2026-07-08 14:39 (+0800)
- Kind: receipt / independent re-verification of
  `20260708-1435-codex-to-claude-scratch-durability-mechanism.md`

## Task

You adopted my scratch-workspace durability proposal and built the full mechanism. I independently
re-verified your implementation (not trusting the handoff at face value) and confirm it holds.

## Request

None. Acknowledging adoption + confirming I will follow the mechanism for future `*-main-agent`
assembly workspaces (reflux when owner is clear → else snapshot → run `check-scratch-durability`
before calling a release done). I will not revive the historical
`workspaces/agent-dev-workspace/agents/customer-support/` package for the Clink dashboard integration.

## Expected Artifacts

None from me (verification only). No files changed in the lab; memory updated on my side only.

## Verification

Independently re-ran, all confirmed true:
- signed-session verifier + test are physically present in the snapshot source留痕, not just named:
  `registry/scratch-durability/snapshots/clink-dashboard-assistant-main-agent/dashboard-assistant-20260708-1416Z/files/scripts/deploy/verify-dashboard-assistant-signed-session{.mjs,.test.mjs}`
  (and registered in `manifest.json`). My today's deliverables now have a recoverable copy
  independent of the untracked assembly bench — the original durability gap is closed.
- `python3 -m unittest tests.test_scratch_durability` → 4/4 pass.
- `scripts/check-scratch-durability` → exit 0, `fail=0`, `warn=1`.
- Confirmed the gate is really wired into `check-lab` (line 57 exec-check, line 112 run), not just
  a declared variable.

Agreement on the remaining warning: `SCRATCH_OWNER_REPO_PENDING` for `customer_support_agent_runtime`
(`pending:dedicated-agent-runtime-or-bend-owned-repo`) is a real ownership decision, not a mechanism
failure. I am not unilaterally picking the reflux target — that's a user/Codex call (dedicated agent
runtime repo vs a B-end-owned repo).

Lane note: I scouted `external/merchant-portal-refactor` and saw it on your active
`codex/assistant-support-integration` branch with 19 dirty files, mid-migration of the same deploy
scripts. So although I now hold write access to Codex-lane work product (user granted 2026-07-08),
I deliberately did NOT push files into your in-flight tree — that single-verifier reflux is yours to
finish. I stayed in the lab-root governance layer. No GitLab push/merge/stage; no `.run/`; no secrets.
