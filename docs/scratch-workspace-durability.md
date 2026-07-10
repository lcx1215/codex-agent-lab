# Scratch Workspace Durability

Some integration work happens in assembly directories that are useful for speed
but are not git-backed source-of-truth repos. The current Clink dashboard
assistant workspace is one of them:

`workspaces/agent-dev-workspace/external/merchant-portal-refactor-main-agent/`

The rule is simple: a release-worthy file authored in a scratch workspace must
be captured before anyone calls the release done. Capture means either refluxing
the file to its owning real repo, or recording a durability snapshot under
`registry/scratch-durability/`.

## Reflux Targets

- Dashboard frontend integration files belong in
  `workspaces/agent-dev-workspace/external/merchant-portal-refactor`.
- Dashboard assistant deploy/BFF handoff files currently reflux to
  `workspaces/agent-dev-workspace/external/merchant-portal-refactor` unless the
  production B-end owner moves them into `clink-gateway` or `clink-platform`.
- Customer-support agent runtime files are currently snapshot-required. The
  durable owner repo is still pending; until it exists, the snapshot is the
  mandatory capture proof.

Do not use the historical
`workspaces/agent-dev-workspace/agents/customer-support/` package for this
integration.

## Gate

Run:

```sh
scripts/check-scratch-durability
```

The gate compares configured scratch files with the current snapshot pointer in
`registry/scratch-durability/current.json`.

It fails when:

- a configured scratch source file is missing from the current snapshot;
- a configured source file changed after the current snapshot;
- a required artifact class matches no files;
- a concrete owner repo mapping is missing or not a git checkout;
- the configured globs accidentally match a secret-like path.

It warns, but does not fail, when an owner repo is still pending.

## Snapshot

After release-worthy scratch changes are ready, write a snapshot with an explicit
release or mechanism id:

```sh
scripts/check-scratch-durability --write-snapshot <snapshot-id>
```

The snapshot manifest records every configured file's SHA-256 and size. Small
text files marked with `copy_text` are also copied into the snapshot directory
so the source is recoverable from the lab registry. Large, binary, runtime, and
secret-like files are not copied; they are represented by hashes only and should
still be refluxed to a real owner repo when one exists.

Snapshots are not a substitute for production GitLab repos. They are the minimum
durability proof that prevents release-worthy work from existing only as
untracked on-disk bytes.
