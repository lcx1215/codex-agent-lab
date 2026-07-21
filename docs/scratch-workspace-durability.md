# Scratch Workspace Durability

Some historical integration work happened in assembly directories that were
useful for speed but were not git-backed source-of-truth repos. The retired
Clink dashboard assistant assembly is:

`workspaces/agent-dev-workspace/external/merchant-portal-refactor-main-agent/`

It is not a current implementation or release source. The rule is simple: a
release-worthy file authored in a scratch workspace must
be captured before anyone calls the release done. Capture means either refluxing
the file to its owning real repo, or recording a durability snapshot under
`registry/scratch-durability/`.

## Reflux Targets

- Dashboard frontend integration belongs to the real company repository
  `clink/merchant-portal-refactor`.
- Customer-support Agent runtime belongs to the real company repository
  `clink/pay/clink-merchant-assistant`.
- Old deploy/BFF handoffs are retired and must not be refluxed into
  `clink-gateway`, `clink-platform`, or ArgoCD configuration.

Do not use either historical local package for current integration:

- `workspaces/agent-dev-workspace/agents/customer-support/`
- `workspaces/agent-dev-workspace/external/merchant-portal-refactor-main-agent/agents/customer-support/`

## Gate

Run:

```sh
scripts/check-scratch-durability
```

This is an explicit boundary gate, not part of the root default fast path. Run
it only when validating retired scratch captures or release-worthy assembly
work; it can inspect historical company-adjacent scratch trees.

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
