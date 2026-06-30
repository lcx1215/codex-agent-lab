# Codex Self IDE Benchmark Report

## Verdict

The lab is already strong for a file-based, evidence-driven agent environment. Local edit-test-verify work is fast, Waterflow supervision is lightweight, and API-relay/OMX can perform a bounded model-backed task inside a workspace.

It is not yet a best-in-class integrated development environment. The main gaps are runtime latency, noisy plugin startup, weak IDE-style feedback surfaces, and insufficiently automatic sandbox enforcement for model-backed CLI runs.

## Measured Results

| Capability | Command | Result | Wall time |
| --- | --- | --- | --- |
| RED unit test | `python3 -m unittest discover -s tests` | expected 1 failure | 0.32s |
| GREEN unit test | `python3 -m unittest discover -s tests` | 4 passed | 0.44s |
| Compile check | `python3 -m py_compile lane_router.py` | pass | 0.24s |
| Speed contract | `./scripts/check-speed-contract` | pass | 0.41s |
| Project rules | `./scripts/check-project-rules` | pass | 0.25s |
| Secret guard | `./scripts/check-secrets` | pass | 0.71s |
| Integrated lab check | `./scripts/check-lab` | pass | 4.17s |
| Lab unit tests | `python3 -m unittest discover -s tests` | 12 passed | 3.10s |
| Async execution | `./scripts/check-async-execution` | 7/7 passed | 3.31s |
| Waterflow scan | `./scripts/waterflow-scan --root . --compare-last` | 0 findings | 0.32s |
| Waterflow verify | `./scripts/waterflow-verify` | 5/5 passed | 5.69s |
| OMX model smoke | `omx-api exec` | wrote and verified `omx-smoke.md` | 81.66s |

## What Worked

- The workspace pattern is effective: local rules, progress, validation, code, tests, and model smoke output stayed inside one folder.
- RED/GREEN debugging was quick: a real risk-ranking defect was exposed and fixed in one tight loop.
- Fast gates are genuinely fast: speed, project-rule, and secret checks are subsecond.
- Waterflow supervision did not slow normal work: compare-last took 0.32s and derived a changed-only plan with one P3 check.
- Async execution is useful: seven independent checks completed successfully in 3.31s.
- API-relay/OMX can execute a bounded task and write a file in the target workspace.

## Bottlenecks

- Model-backed OMX smoke was slow for the task size: 81.66s and 40,106 tokens for a short read/write task.
- Plugin/MCP startup is noisy when credentials are missing; Linear, Cloudflare, and Notion emitted OAuth errors before useful work began.
- Skill loading is not selective enough; the run warned that skill descriptions were removed and 98 skills were omitted because of context budget.
- The API-relay exec runtime reported `danger-full-access`; the prompt behaved, but best IDE-grade safety needs runtime-enforced workspace boundaries.
- There is no single IDE dashboard tying together test status, Waterflow status, async status, model usage visibility, plugin auth state, and current workspace progress.

## Gap To Best IDE

Best-in-class would mean this environment can feel like one continuous development surface: editor diagnostics, tests, agent plans, cost, file diffs, Waterflow, and runtime state all visible and actionable without manual log reading.

The next improvements should be:

- a benchmark command that runs this exact test suite and stores historical timings;
- automatic fast-model routing for tiny smoke tasks instead of defaulting every model-backed run to `gpt-5.5` + `xhigh`;
- plugin auth health preflight that suppresses or isolates unusable MCP servers for tasks that do not need them;
- runtime sandbox hardening for `omx-api exec` so workspace-write is enforced, not only requested in prompts;
- a compact status dashboard over `registry/`, Waterflow outputs, async outputs, git status, and model-backed run cost;
- IDE-style diagnostics for generated workspaces: tests, validation freshness, changed-only Waterflow plan, and open handoff gaps.
