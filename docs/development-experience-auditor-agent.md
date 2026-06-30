# Development Experience Auditor Agent

`development-experience-auditor` is a lab-local custom agent for judging how comfortable and effective the Codex Agent Lab is for medium and large agent development.

## Purpose

The agent turns subjective "does this environment feel good to work in?" feedback into a structured evidence report. It scores:

- context loading;
- runtime ergonomics;
- verification loop quality;
- durable handoff quality;
- safety boundary clarity.

## When To Use

Use it after a medium or large agent build, after a new workflow mode is added, or when Codex/Claude work feels slower or more awkward than expected.

## Output Contract

The agent should produce:

- a comfort score;
- dimension breakdown;
- top friction list;
- exact evidence paths or commands;
- recommended next environment improvements;
- a boundary note explaining what was not proven.

## Harness

The deterministic harness lives in `lab_agents/development_experience.py`. It accepts `ComfortSignal` records, computes a comfort report, and renders restartable Markdown.

The harness is intentionally simple. It does not replace model judgment; it gives Codex or Claude a stable scoring surface for comparing future lab changes.
