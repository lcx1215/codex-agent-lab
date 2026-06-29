# Security Policy

## Secrets

Never commit API keys, GitHub tokens, auth files, cookies, `.env` files, private keys, or session state.

GitHub credentials should stay in GitHub CLI, the OS keychain, or GitHub Actions runtime context. They should not be copied into repository files, README examples, logs, generated fixtures, or validation evidence.

Before committing, run:

```bash
./scripts/check-secrets
```

The repository also runs the same check in GitHub Actions.

## If A Secret Is Exposed

Revoke and rotate the key first. Then remove it from the repository and history. Do not rely on deleting the visible line alone.
