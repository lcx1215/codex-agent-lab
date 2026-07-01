# Platform Coherence Mega Audit - 2026-07-01

Generated: 2026-07-01 16:54 +0800  
Auditor lane: Codex / OMX App-safe spine  
Handoff: `registry/collaboration/handoffs/20260701-1545-claude-to-codex-mega-audit.md`

## Executive Verdict

**Commit-readiness verdict: READY TO COMMIT after the fixes listed below.**

- Remaining blocker findings: **0**.
- Outright breakage fixed during this audit: **5**.
- Remaining findings are **should-fix documentation or future gate-automation recommendations**, not blockers for committing the lifecycle-gates work.
- Customer-support package was **not touched**.
- Fresh verification evidence is listed at the end of this report.

## Outright Breakage Fixed During Audit

These were repaired because they were concrete fail-open/crash/test-honesty defects, not design preferences.

1. **Gate crash path fixed - unregistered agent package.**
   - Current fix: `scripts/check-agent-packages:179-187` reports `AGENT_PACKAGE_UNREGISTERED` using `catalog_dir / package_id` instead of crashing.
   - Regression: `tests/test_agent_package_integrity.py:130-146` asserts non-zero exit, no `NameError`, and the expected issue code.
   - Justification: a hard metadata gate must fail closed on an unregistered package, not crash or hide the actionable issue.

2. **Cross-module invalid transition fixed - task verification promotion.**
   - Current fix: `lab_agents/task_verify.py:42-68` allows only `review -> verified` and appends the matching history entry.
   - Regression: `tests/test_task_verify.py:102-106` validates a promoted task against `lab_agents.task_state.validate_task_registry`.
   - Justification: `lab_agents/task_state.py:20-29` defines `running -> review -> verified`; emitting `running -> verified` would corrupt the shared state machine.

3. **Lifecycle gate schema fail-closed fixed.**
   - Current fix: `scripts/check-gates:62-66` now runs `validate_task_registry` before Gate 1 / Gate 3 checks.
   - Regression: `tests/test_task_verify.py:154-168` creates malformed `tasks.json` with non-list `tasks` and asserts `check-gates` returns `1`.
   - Justification: `check-gates` must not treat malformed task registry content as an empty OK registry.

4. **Agent-code audit source collection fixed for lab-local async TMPDIR.**
   - Current fix: `scripts/audit-agent-code:67-82` evaluates skipped directories relative to the package root, not absolute path ancestors; `scripts/audit-agent-code:93-101` also recognizes relative `src/` and `test/` paths.
   - Regression: `tests/test_audit_agent_code.py:49-66` places a package under `.tmp/tests/...` and proves a fail-open verifier is still scanned and flagged.
   - Justification: `scripts/check-async-execution` sets per-task `TMPDIR` under `.tmp`; absolute ancestor matching skipped all source files and made security tests falsely pass.

5. **Run-record test assumption fixed for async TMPDIR under the repo.**
   - Current fix: `tests/test_run_record.py:106-126` initializes an empty nested git repo before asserting missing HEAD values are null.
   - Justification: a temp directory under the lab repo is still inside the parent git checkout; the old test assertion depended on environment placement rather than run-record behavior.

---

## Dimension 1 - Gate Enforcement Reality (`scripts/check-*`)

### Blocker

- **None remaining.** The concrete gate breakages found during this audit were fixed above.

### Should-fix

1. **`check-collaboration` validates proof shape, but not artifact existence.**
   - Evidence: `scripts/check-collaboration:86-89` requires proven entries to have at least one artifact, but does not check that paths exist.
   - Current reality: manual audit found all current `proven` artifacts exist; see Dimension 4.
   - Recommendation: add a future fail-closed artifact-existence pass for `status == proven`, while preserving support for intentional directory artifacts.
   - Status: design recommendation, not a blocker for this commit.

### Nit

- **Expected fail-closed stderr appears during unit tests.**
  - Evidence: `tests/test_task_verify.py:154-168` intentionally invokes `check-gates.main()` on malformed data; the full unittest run prints `FAIL: invalid registry/tasks/tasks.json: tasks must be a list` while still passing.
  - Recommendation: capture stderr in that regression later for cleaner logs.
  - Status: cosmetic only.

### Systematic gate reality table

| Gate | Current audit result | Fail-closed evidence |
| --- | --- | --- |
| `scripts/check-agent-packages` | Pass after fix | `scripts/check-agent-packages:179-187`, `:310`, `:386`; regression `tests/test_agent_package_integrity.py:130-146`. |
| `scripts/check-async-execution` | Pass | Task fan-out includes key gates/tests at `scripts/check-async-execution:23-46`; timeout/non-zero/unexpected stderr fail at `:83-89`; exit follows failed count at `:152-177`. Fresh run: 9 passed, 0 failed. |
| `scripts/check-collaboration` | Pass with artifact-existence recommendation | Required protocol sections at `scripts/check-collaboration:31-38`; ledger schema/status checks at `:43-91`; handoff naming/sections at `:94-106`. |
| `scripts/check-gates` | Pass after fix | Schema fail-closed at `scripts/check-gates:62-66`; Gate 1 / Gate 3 checks at `:74-83`; non-zero on violations at `:85-89`. |
| `scripts/check-lab` | Pass | Required scripts/config at `scripts/check-lab:39-63`; root fast-path gates run at `:92-106`. |
| `scripts/check-merge-queue` | Pass | Report status returns non-zero on fail at `scripts/check-merge-queue:24-38`; missing state fails in `tests/test_worktree_merge_queue.py:111-123`. |
| `scripts/check-project-rules` | Pass | Missing files/patterns exit via `fail` at `scripts/check-project-rules:7-22`; required surfaces checked at `:24-130`. |
| `scripts/check-rule-ladder` | Pass | Missing/undeclared surfaces recorded at `scripts/check-rule-ladder:64-80` and `:170-200`; report fails when issues exist at `:228-245`; exit at `:310`. |
| `scripts/check-run-records` | Pass | Missing runs/latest/no records fail at `scripts/check-run-records:14-39`; schema, lane coverage, latest-newest checks fail at `:41-79`. |
| `scripts/check-runtime-compatibility` | Pass | Required commands include `rg` at `scripts/check-runtime-compatibility:19-32`; failed checks determine status at `:327-340`; exit at `:401`. |
| `scripts/check-sandbox` | Pass | Missing `rg` fails closed at `scripts/check-sandbox:24-40`; config errors exit at `:47-87`; forbidden files and symlink escapes fail at `:94-130`. |
| `scripts/check-sandbox-skills` | Pass | Missing files/patterns/TODOs fail at `scripts/check-sandbox-skills:13-23`, `:32-58`. |
| `scripts/check-secrets` | Pass | Missing `rg` fails closed at `scripts/check-secrets:15-31`; scanner status `0` means finding, `1` means clean, any other code fails at `:39-50` and `:60-81`; token output redacted at `:72-76`. |
| `scripts/check-speed-contract` | Pass | Required docs and default-gate budget checks at `scripts/check-speed-contract:29-61`; heavy default-gate scans fail at `:63-76`. |
| `scripts/check-task-state` | Pass | Unreadable registry returns status fail at `scripts/check-task-state:28-48`; exit fails on report status `fail` at `:67-71`; state/history validation lives in `lab_agents/task_state.py:47-132`. |
| `scripts/check-workflow-modes` | Pass | Missing docs/script/mode fields/list mismatch fail at `scripts/check-workflow-modes:15-38`. |
| `scripts/check-workspace-safety` | Pass as explicit boundary gate | Outside-lab and secret-like paths fail at `scripts/check-workspace-safety:73-87`, `:137-150`; warnings remain non-blocking by design; exit fails only on status fail at `:254-265`, `:350-358`. |

---

## Dimension 2 - Doc vs Code Drift

### Blocker

- **None.** Drift is real, but it does not invalidate the current lifecycle-gates commit after the code fixes above.

### Should-fix

1. **Collaboration Layer 6 status is stale.**
   - Drift: `registry/CAPABILITY_LAYERS.md:170-192` says runtime proof is pending and real interop is not proven yet.
   - Reality: `registry/current-progress.md:74` says real OMC-to-OMX interop is proven by `collab-0003`; `registry/collaboration/assignments.json:166-184` records that proof and its artifacts.
   - Recommendation: update Layer 6 to distinguish proven OMC-to-OMX interop from still-blocked OMC team bootstrap.

2. **Health-gate layer omits newly wired gates.**
   - Drift: `registry/CAPABILITY_LAYERS.md:146-163` lists many health gates but omits `scripts/check-run-records`, `scripts/check-merge-queue`, and `scripts/check-gates`.
   - Reality: `scripts/check-lab:20-24` declares those gates and `scripts/check-lab:102-106` runs them.
   - Recommendation: refresh Layer 5 implementation bullets.

3. **Orchestration state doc overstates merge queue as not done.**
   - Drift: `registry/ORCHESTRATION_LAYER_STATE.md:83-85` lists live runtime as not done and includes per-agent worktree isolation + merge queue in that not-done bundle.
   - Reality: the full live scheduler is not done, but the worktree merge-queue kernel is installed and proven: `registry/current-progress.md:80` and `registry/collaboration/assignments.json:314-332`.
   - Recommendation: split this into: worktree/merge-queue kernel done; live scheduler/retry/resume not done.

4. **Lifecycle proposal remains draft/proposed while implementation exists with different names/boundaries.**
   - Drift: `docs/proposal-subagent-gates.md:3` says draft pending user approval; `:39-40`, `:47-48`, and `:52-55` name proposed scripts (`check-rule-acknowledgment`, `dispatch-next`, `verify-task`).
   - Reality: the implemented surfaces are `lab_agents/rule_ack.py`, `lab_agents/dispatch.py`, `lab_agents/task_verify.py`, and `scripts/check-gates`; see `lab_agents/dispatch.py:1-12` and `scripts/check-gates:1-10`.
   - Recommendation: either rename the doc to historical proposal, or add an implementation status section mapping proposal names to current modules. Do not expand automation in this audit.

### Nit

- `registry/CAPABILITY_LAYERS.md:3` still says last updated 2026-06-30 even though several 2026-07-01 root-layer capabilities are now wired. This is stale metadata only.

---

## Dimension 3 - Rule-Ladder Coherence

### Blocker

- **None.** Current rule ladder is coherent.

### Evidence

- Fresh structured run: `scripts/check-rule-ladder --json` returned `status=pass`, `workspace_count=7`, `agent_unit_count=1`, `failed_count=0`.
- Root/workspace/package checks are real:
  - Root required surfaces: `scripts/check-rule-ladder:74-80`.
  - Workspace rule marker enforcement: `scripts/check-rule-ladder:170-180`.
  - Package/subagent rule marker enforcement: `scripts/check-rule-ladder:182-200`.
- Tests prove broken links fail without touching real files:
  - Missing workspace surface fails: `tests/test_rule_ladder.py:78-89`.
  - Package missing parent marker fails: `tests/test_rule_ladder.py:91-103`.
  - Nested subagent missing marker fails: `tests/test_rule_ladder.py:117-127`.

### Should-fix

- **None for commit readiness.**

### Nit

- `scripts/check-rule-ladder:233-237` reports both `package_count` and `agent_unit_count` from the same value. This is harmless but semantically redundant.

---

## Dimension 4 - Ledger vs Reality

### Blocker

- **None.** All current proven ledger artifacts exist.

### Evidence

- Manual read/verify of `registry/collaboration/assignments.json` found:
  - total entries: 17
  - `proven`: 16
  - `blocked`: 1
  - missing artifacts for `proven`: `[]`
- The only non-proven entry remains clearly blocked:
  - `registry/collaboration/assignments.json:128-143` (`collab-0001-omc-team-bootstrap`, blocked because it requires a real tmux team proof from an allowed terminal session).
- Current proof examples with artifact paths:
  - Interop proof: `registry/collaboration/assignments.json:166-184`.
  - Merge queue kernel proof: `registry/collaboration/assignments.json:314-332`.
  - Integration probe proof: `registry/collaboration/assignments.json:335-349`.

### Should-fix

- Automate the manual artifact-existence check in `scripts/check-collaboration`; see Dimension 1 recommendation. Current ledger data itself is coherent.

### Nit

- Some ledger notes are long and duplicate historical status. This is readability debt, not proof failure.

---

## Dimension 5 - Cross-Module Logic (`task_state` / `rule_ack` / `task_verify` / `dispatch` / `merge_queue`)

### Blocker

- **None remaining.** The invalid `task_verify` transition and `check-gates` malformed-registry pass were fixed.

### Evidence of agreement

- Canonical task states/transitions: `lab_agents/task_state.py:18-29`.
- Registry schema/history validation: `lab_agents/task_state.py:47-132`.
- Gate 1 start rule: `lab_agents/rule_ack.py:50-63` permits start only for pending tasks with complete rule ack.
- Dispatch model: `lab_agents/dispatch.py:32-68` uses `runnable_tasks` (pending + dependencies done) and then blocks candidates that fail `rule_ack.can_start`.
- Gate 3 verification model: `lab_agents/task_verify.py:15-39` fails closed on missing/empty checks; `lab_agents/task_verify.py:42-68` promotes only `review -> verified`.
- Registry-level lifecycle gate: `scripts/check-gates:26-48` covers current state and history; `scripts/check-gates:62-83` validates schema, Gate 1, and Gate 3.
- Merge-queue state is separate and internally consistent: valid stream/queue statuses at `lab_agents/worktree_merge_queue.py:22-23`; validation at `:133-216`; pre-merge conflict refusal at `:334-370`.
- Current registry reality: `registry/tasks/tasks.json:1-181` has 3 tasks, all `done`, all with `rule_ack` and passing `verification` backfills.
- Current merge-queue reality: `registry/worktree-merge-queue/state.json:1-7` is empty/valid and `scripts/check-merge-queue --json` returned `status=pass`.

### Should-fix

1. **Proposal doc claims stronger Gate 1 path reachability than code implements.**
   - Drift: `docs/proposal-subagent-gates.md:39-40` says Gate 1 checks required rule layers and that declared file paths are reachable.
   - Reality: `lab_agents/rule_ack.py:32-47` checks declared layer keys only; it does not read path declarations or call rule-ladder path resolution.
   - Recommendation: either update the proposal doc to describe current v1 honestly, or add a future Gate 1 path-check feature outside this audit.

2. **Dispatch is a pure plan, not an automatic worktree-backed launcher.**
   - Drift: `docs/proposal-subagent-gates.md:47-50` describes automatic `omx-api exec` dispatch and per-task worktrees.
   - Reality: `lab_agents/dispatch.py:10-11` explicitly does not run subprocesses or call `omx-api`.
   - Recommendation: keep current pure planner for this commit; document automation as future work.

### Nit

- The lifecycle state registry has only 3 root-layer tasks today (`scripts/check-task-state --json`: `task_count=3`). That is sufficient for this feature but not a broad historical import.

---

## Dimension 6 - Test Honesty

### Blocker

- **None remaining.** Two test-honesty defects were fixed (`audit-agent-code` skipped `.tmp` sources; `test_run_record` assumed temp dirs were outside git).

### Evidence

- Test inventory: 24 `tests/test_*.py` files, all with non-zero assertion counts.
- Full suite run: `python3 -m unittest discover -s tests` -> `Ran 144 tests in 9.033s`, `OK`.
- Critical fail-closed tests are behavioral, not vacuous:
  - Secret/sandbox `rg` scanner errors fail closed: `tests/test_gate_fail_closed.py:35-49`, `:83-97`.
  - Rule ladder broken links fail: `tests/test_rule_ladder.py:78-103`, `:117-127`.
  - Agent package unregistered directories fail without crash: `tests/test_agent_package_integrity.py:130-146`.
  - Dispatch blocks unacknowledged tasks and honors caps/dependencies: `tests/test_dispatch.py:26-75`.
  - Rule ack missing layer and missing ack fail: `tests/test_rule_ack.py:37-59`, `:77-81`.
  - Task verification fails closed and promotion validates against the state machine: `tests/test_task_verify.py:51-57`, `:102-106`.
  - Merge queue refuses conflicts before merge and leaves no conflict markers: `tests/test_worktree_merge_queue.py:77-93`.
  - Agent-code auditor now covers `.tmp` package placement: `tests/test_audit_agent_code.py:49-66`.

### Should-fix

- None for commit readiness.

### Nit

- Consider capturing expected stderr in `tests/test_task_verify.py:154-168` to keep full-suite output visually clean.

---

## Verification Evidence

Fresh commands run during this audit:

1. `python3 -m unittest tests.test_audit_agent_code tests.test_run_record tests.test_agent_package_integrity tests.test_task_verify`
   - Result: `Ran 41 tests in 0.429s`, `OK`.
2. `scripts/check-async-execution`
   - First post-fix result: `checks=9`, `passed=9`, `failed=0`, `timed_out=0`.
3. `python3 -m unittest tests.test_task_verify tests.test_task_state tests.test_dispatch tests.test_rule_ack tests.test_audit_agent_code tests.test_run_record`
   - Result: `Ran 57 tests in 0.138s`, `OK`.
4. `scripts/check-rule-ladder --json`
   - Result: `status=pass`, `workspace_count=7`, `agent_unit_count=1`, `failed_count=0`.
5. `scripts/check-agent-packages --json`
   - Result: `status=pass`, `registry_count=1`, `package_count=1`, `agent_count=3`, `failed_count=0`.
6. `scripts/check-task-state --json`
   - Result: `status=pass`, `task_count=3`, `done_count=3`, `stale_running_count=0`.
7. `scripts/check-merge-queue --json`
   - Result: `status=pass`, empty queue/streams, no issues.
8. `scripts/check-gates`
   - Result: `OK: 3 task(s) satisfy lifecycle gates`.
9. `python3 -m unittest discover -s tests`
   - Result: `Ran 144 tests in 9.033s`, `OK`.
10. `scripts/check-async-execution`
    - Final pre-report result: `checks=9`, `passed=9`, `failed=0`, `timed_out=0`.
11. `scripts/check-collaboration`
    - Pre-ledger-update result: `assignments OK: 17 entries`; protocol/handoffs valid.

12. `scripts/check-collaboration` (post-report, post-handoff, post-ledger)
    - Result: `assignments OK: 18 entries`; `OK: collaboration surfaces are valid`.
13. `scripts/check-lab` (post-report, post-handoff, post-ledger)
    - Result: `OK: lab structure is valid`.
