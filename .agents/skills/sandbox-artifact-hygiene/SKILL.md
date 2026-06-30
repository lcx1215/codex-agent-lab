---
name: sandbox-artifact-hygiene
description: Use when deciding which sandbox outputs, logs, waterflow reports, async results, workspaces, tmux artifacts, or generated files should be committed, ignored, redacted, archived, or regenerated.
---

# Sandbox Artifact Hygiene

## Overview

Keep the lab useful without turning it into an unbounded artifact dump. Every
generated file needs a classification: source, durable proof, handoff,
transient scratch, or forbidden material.

## Workflow

1. Start with `git status --short --branch` and separate tracked changes from
   untracked artifacts.
2. Classify each artifact before staging:

   | Class | Commit? | Examples |
   | --- | --- | --- |
   | source | yes | scripts, skills, docs, tests |
   | durable proof | yes, if it supports a recorded claim | validation results, worker reports |
   | handoff | yes, when future agents need it | progress, summaries, repair briefs |
   | transient scratch | no | debug logs, nested runtime repos, `.tmp` |
   | forbidden | no | secrets, auth, session state, private keys |

3. Run `./scripts/check-secrets` before and after staging.
4. Ignore recurring transient files in `.gitignore`; do not delete user or
   proof files just to make status clean.
5. If generated waterflow files are updated, finish with:

   ```bash
   ./scripts/waterflow-scan --root . --compare-last
   ```

   Run it twice when the first compare only records the registry update and the
   desired final handoff state is `changed_count: 0`.
6. Keep large proof workspaces concise: commit summaries and intentional logs,
   ignore nested runtime repos and raw debug traces unless they are the only
   evidence.

## Commit Decision Checklist

- Does this file support a current claim in `registry/VALIDATION.md` or a
  workspace `validation.md`?
- Would a future agent need this artifact to resume or audit the work?
- Is it free of secrets and unnecessary local personal paths?
- Is it deterministic enough to review, or is it transient noise?
- Is there a better summary artifact that should be committed instead?

## Common Mistakes

- Committing all of `outputs/` without checking whether the files are current.
- Ignoring proof logs before extracting the failure reason into a durable
  validation note.
- Treating untracked files as disposable when they may be the only record of a
  failed long-horizon run.
- Letting nested `.git` directories or runtime state become parent repo content.
