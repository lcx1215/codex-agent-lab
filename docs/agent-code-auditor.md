# Agent Code Auditor

`scripts/audit-agent-code` audits the *code inside* an agent package for quality
and security anti-patterns. It complements the structure gates:

| Gate | Looks at | Answer |
| --- | --- | --- |
| `check-rule-ladder` | rule-chain declarations | is the package *wired* into the rule hierarchy? |
| `check-agent-packages` | registry + manifest integrity | is the package *registered* coherently? |
| `audit-agent-code` | the runtime source code | is the code *itself* free of known anti-patterns? |

## What It Detects

| Code | Severity | Anti-pattern |
| --- | --- | --- |
| `FAIL_OPEN_AUTH` | fail | a verifier/auth fn returns `ok: true` when the secret/token is missing (fail-open — same family as the rg-fail-open gate bug) |
| `EMPTY_SECRET` | fail | a verifier is called with an empty/placeholder secret literal, disabling the check |
| `INJECTION_SINK` | warn | `eval`, `child_process`/`exec`, or `subprocess(..., shell=True)` — confirm inputs aren't attacker-controlled |
| `UNBOUNDED_BODY` | warn | request body read without an obvious size cap (DoS surface) |
| `NO_TESTS` | warn | runtime `src/` files exist but the package has no test/spec files |

Severity ladder: only `fail` findings make the gate exit non-zero, so it can gate
CI without blocking on advisory warnings. It is heuristic and scoped to one
package's runtime code; warnings are prompts to confirm, not automatic defects.

## Usage

```bash
scripts/audit-agent-code workspaces/<ws>/agents/<package>      # human-readable
scripts/audit-agent-code <package> --json                      # machine-readable
scripts/audit-agent-code <package> --write                     # JSON+MD under outputs/shared/agent-code-audit/
```

## Proof It Works

Run against the first real agent package (`agents/customer-support`) it caught a
genuine vulnerability: the support-inbox webhook verifier fails open when no
secret is configured (`security/signature.mjs`) and the server calls it with
`secret: ''` (`server.mjs`), so the signature check was effectively disabled —
anyone could POST forged inbox messages. Run against the clean neutral kernel
(`lab_agents/agent_kernel`) it reports `pass` with zero findings (no false
positives). Both behaviors are locked by `tests/test_audit_agent_code.py`.

## Boundary

The auditor is read-only: it never edits the audited package. When it runs
against another lane's package, findings are reported through a collaboration
handoff, not by editing that lane's files.
