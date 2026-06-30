# OMX Smoke

## Summary
This workspace defines a small Codex edit-test-verify benchmark for a Waterflow-style route summarizer. The implementation parses route records, groups summaries, ranks risk, selects validation modes, and handles a 10000-record synthetic case.

## Evidence
- `README.md` documents the intended unit-test loop: `python3 -m unittest discover -s tests`.
- `progress.md` says the RED fixture was added and risk ordering / sampled mode behavior were fixed.
- `lane_router.py` implements parsing, grouping, risk ranking, owner sorting, and `fast` / `boundary` / `sampled` mode selection.
- `tests/test_lane_router.py` covers changed-route boundary mode, low-risk fast mode, large unchanged sampled mode under 1s, and malformed-line rejection.

## Gaps
- `validation.md` is still a placeholder; no timing or pass/fail result is recorded there yet.
- The local unit-test loop appears verifiable from the files because README provides the command and tests target the implementation directly, but I did not run the test suite for this smoke note.
