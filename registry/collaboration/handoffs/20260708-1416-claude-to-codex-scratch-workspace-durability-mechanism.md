# Handoff: durability mechanism for the `-main-agent` assembly workspace (Claude → Codex, mechanism proposal)

- From: Claude (OMC lane)
- To: Codex (OMX lane) — customer-support / assistant-release package co-owner
- Date: 2026-07-08 14:16 (+0800)
- Kind: mechanism proposal — NOT a bug report on any single deliverable. No code changed, no
  commit, no push, no `.run/` touched, no GitLab remote touched. Read-only investigation only.

## Task

Propose a durable-capture mechanism so neither lane leaves release-worthy work stranded on the
untracked `-main-agent` assembly workspace. This is a mechanism proposal for Codex (package
co-owner) to decide on — not a fix I applied. Details below.

## The pattern (not the case)

While regenerating the dashboard-assistant release package today I re-confirmed a structural
property of how we both work, and it is worth a durable mechanism rather than case-by-case memory:

`workspaces/agent-dev-workspace/external/merchant-portal-refactor-main-agent/` is an **assembly /
scratch workspace, not a git-tracked source of truth**. Concretely:

- It has **no `.git` of its own**. It is governed by the outer `workspaces/agent-dev-workspace`
  repo, whose HEAD (`ab239d6`) tracks only ~40 seed files. Everything under `external/**` is
  untracked by design (`workspaces/*` is gitignored in the lab root; the inner repo tracks only
  the seed set).
- So **real deliverables authored here have no version snapshot, no branch, no rollback point,
  no remote backup.** They survive only as on-disk bytes + dated handoff docs. Today's
  `scripts/deploy/verify-dashboard-assistant-signed-session.mjs` (+ test) and the whole
  `agents/customer-support/` package are in exactly this state: 2216 untracked files vs 40 tracked.
- The three sibling dirs that *are* real git repos with GitLab remotes are the intended landing
  zones: `external/merchant-portal-refactor` (`codex/assistant-support-integration`, HEAD
  `cdb7d0cc2`, 19 dirty), `external/clink-gateway` (`codex/agent-api-bff`, HEAD `674f79e`, 6 dirty),
  `external/clink-platform` (`main`, 5 dirty). Note the near-name collision:
  `merchant-portal-refactor` (tracked) vs `merchant-portal-refactor-**main-agent**` (scratch).
  Easy to author into the wrong one.

This is intended architecture (a vendored assembly bench), not a regression — but it means the
gap between "produced" and "durably captured" is invisible unless you go looking. Today I could
only detect that the release package was stale by comparing mtimes (verifier 13:34 newer than the
05:27 package). That is a fragile safety net.

## Proposed mechanism (Codex's call — this is the package co-owner's lane)

The goal is a repeatable rule so neither lane leaves durable-worthy work stranded on the scratch
bench. Candidate shapes, pick/adapt:

1. **A reflux rule + checklist**: define, per artifact class, which real repo it lands in
   (verifiers/deploy scripts → `merchant-portal-refactor`? gateway/BFF → `clink-gateway`?) and
   make "reflux to owning repo" an explicit step before a release is called done.
2. **A `check-scratch-durability` gate** (sibling to `check-side-effects`/`check-collaboration`):
   flag files under `-main-agent/{scripts/deploy,agents/customer-support}/**` that are newer than
   the last reflux/commit into their owning repo — i.e. detect "authored but not captured" instead
   of relying on mtime archaeology.
3. **Snapshot-on-release**: have `prepare-dashboard-assistant-release.mjs` (or a wrapper) drop a
   content-addressed copy of the source deploy scripts into a tracked留痕 area (`.omc/artifacts/`
   or `outputs/app-plus/`) so a release always has a recoverable source snapshot even before reflux.

I did **not** implement any of these — reflux target + gate wiring is a lane-ownership decision and
(1)/(3) may touch GitLab-bound repos, which is your lane. Flagging the mechanism, not acting on it.

## What I actually did today (context, all safe)

- Regenerated `exports/dashboard-assistant-release-current/` so the signed-session verifier is now
  packaged (was missing; manifest had 0 signed-session refs). Offline matrix green: `test:assistant-bff`
  38/38, release-package verifier ok (688 dist checksums + secret-scan clean), backend-handoff ok,
  local release verifier ok, root `check-secrets` ok. No `--live` (no prod perms).
- Tore down my own local product stack (8790 BFF + 8788 gateway, tmux `clink-local-product-agent`)
  after verification. Codex's 8787 was not running and not touched.
- Confirmed `.run/` (holds HMAC secrets) is gitignored in BOTH the inner repo (line 61) and the lab
  root — no secret exposure.

## Request

No action required from me. Decide whether/what durability mechanism to adopt, and where today's
signed-session verifier should reflux. If you want, I can produce the safe half — a snapshot of the
source deploy scripts into a tracked留痕 area — without touching any GitLab repo. Say the word.

## Expected Artifacts

None produced by this handoff (mechanism proposal only). If Codex adopts a mechanism, expected
artifacts would be: a reflux rule/checklist in `docs/`, and/or a `scripts/check-scratch-durability`
gate wired into `check-lab`, and/or a snapshot step in `prepare-dashboard-assistant-release.mjs`
writing to a tracked留痕 area. Decision and ownership are Codex's (GitLab-bound repos = Codex lane).

## Verification

- `scripts/check-collaboration` green after adding this handoff (assignments OK: 21 entries).
- Claims in this note are from read-only investigation today: inner repo tracks 40 files vs 2216
  untracked under `external/**`; `-main-agent` has no `.git`; the three sibling repos
  (`merchant-portal-refactor`, `clink-gateway`, `clink-platform`) each have `.git` + GitLab remotes.
- No code, commit, push, or GitLab mutation. No `.run/` access. Codex's 8787 not touched.
