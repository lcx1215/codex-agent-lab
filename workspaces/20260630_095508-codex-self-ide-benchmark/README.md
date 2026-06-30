# Codex Self IDE Benchmark

This workspace measures whether the lab can support a realistic Codex edit-test-verify loop without relying on global state.

## Scenario

Build and verify a small Waterflow-style route summarizer:

- parse route records;
- group by route family;
- keep the highest workflow risk;
- select fast, boundary, or sampled validation mode;
- handle a 10000-record synthetic graph quickly.

## Commands

```bash
python3 -m unittest discover -s tests
```

Record timing and results in `validation.md`.
