# Live Model-Backed Foundation Amplifier Validation

## Summary

This artifact is a bounded live model-backed validation of the lab-local `foundation-amplifier` operating surface.
It was produced by the active model in `/Users/liuchengxu/Desktop/codex-agent-lab`, not by a stored template or broad test run.
Verdict: the foundation-amplifier contract is usable for concise routing/backtest judgment, with the boundary that this proves model interpretation and artifact production, not full agent-runtime/team execution.

## Evidence Read

- `.codex/agents/foundation-amplifier.toml`: role purpose, safety limits, routing choices, amplification plan, and verification-backtest expectations.
- `docs/foundation-amplifier-agent.md`: purpose, when-to-use criteria, output contract, and backtest meaning.
- `registry/current-progress.md`: current lab state, scenario-neutral positioning, existing foundation-amplifier backtest artifact, OMX/team caveat, and next optional model-backed validation note.
- `registry/VALIDATION.md`: foundation-amplifier implementation evidence, discovery proof, prior checks, benchmark result, and prior backtest verdict.

## Amplification Check

- Target outcome: prove a real model can use the lab-local foundation-amplifier contract to produce a durable validation artifact.
- Scenario boundary: root lab foundation validation only; no customer-service, UCP, or other scenario assumptions were promoted into root policy.
- Durable state/artifact: this file under `outputs/shared/foundation-amplifier/`.
- Lightest adequate surface: API-relay OMX CLI runtime with direct local file reads and a bounded artifact write; no OMX team, no Waterflow, no tests.
- Codex/Claude amplification result: improved evidence handoff and routing clarity, because a future agent can inspect this artifact to see what the live model read, concluded, and did not prove.
- Non-replacement check: scripts/dashboards remain evidence surfaces only; model agents still own interpretation, integration, and repair.

## Problems Found

- No secret, auth, provider, plugin, token, cookie, or live customer-data files were read or changed.
- No tests or broad scans were run, by request; therefore this artifact should not be cited as a fresh health-gate pass.
- The live proof is narrow: it validates model-backed contract use and artifact production, not native subagent dispatch, OMX team reliability, or long-running autonomy.
- Existing progress notes still record OMX team/tmux as mixed: direct `omx-api exec` workers worked, while official `omx-api team` had not proven reliable.

## Recommended Next Step

If this validation is promoted into the normal lab evidence chain, add a short registry entry that cites this artifact and clearly labels it as a model-backed invocation proof rather than a health-gate run. Only run `scripts/check-lab`, Waterflow, or OMX proofs later when a concrete capability change needs that stronger evidence.
