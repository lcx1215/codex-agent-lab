---
name: secret-boundary-auditor
description: Use when sandbox work may expose API keys, auth files, tokens, cookies, OTPs, local user paths, provider config, logs, outputs, or GitHub-public artifacts.
---

# Secret Boundary Auditor

## Overview

Audit sandbox changes before they leave the lab. Treat secret safety as a routing
boundary: the goal is to prove that artifacts can be shared without exposing
credentials, account state, or machine-local details.

## Workflow

1. Identify the exact scope: changed files, untracked files, generated outputs,
   workspace artifacts, and docs that may be committed or shared.
2. Run the repository gate first:

   ```bash
   ./scripts/check-secrets
   ```

3. For generated artifacts that the gate intentionally skips, run a filename-only
   or redacted scan. Report only paths and line numbers, never secret values.
4. Check reader-facing docs for machine-local paths unless the file is explicitly
   local operational state.
5. Check `.gitignore` before staging: runtime repos, transient logs, `.env`,
   `auth.json`, token files, private keys, and session state must not be
   committable.
6. If a potential secret is found, stop and redact or remove it before any commit,
   push, PR, handoff, or paste.

## Redacted Scan Pattern

Use this shape for extra artifact scopes:

```bash
for pattern in \
  'gh[opsu]_[A-Za-z0-9_]{30,}' \
  'github_pat_[A-Za-z0-9_]{20,}' \
  'sk-[A-Za-z0-9_-]{20,}' \
  'AKIA[0-9A-Z]{16}' \
  '-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----'
do
  rg -I -n --no-heading --hidden -e "$pattern" <paths> |
    awk -F: '{ print $1 ":" $2 }' | sort -u
done
```

## Decisions

| Artifact | Default action |
| --- | --- |
| `auth.json`, `.env`, private keys, API tokens | never commit, never print |
| provider/model config without secrets | commit only when intended and documented |
| generated logs | inspect, redact or ignore unless they are proof artifacts |
| local absolute paths in README/public docs | replace with relative paths or placeholders |
| local absolute paths in operational registries | allowed when they are local-only handoff truth |

## Common Mistakes

- Treating `exit 0` as enough when stdout or stderr contains sensitive text.
- Letting generated workspaces carry nested `.git` directories into the parent repo.
- Redacting docs but forgetting validation outputs or worker logs.
- Printing the matching line content instead of path-only evidence.
