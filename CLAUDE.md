# Claude Code in Agent Lab

Machine-wide safety, evidence, and native-client rules remain authoritative.
This file adds only Lab-local placement:

- Current user-authorized changes may be made in the Lab root.
- `workspaces/`, `.worktrees/`, and company repositories require an exact
  target and action; preserve their existing state.
- cmux workspaces contain pure shells. The Lab never starts clients or injects
  client configuration, keys, environment, history, Skills, memory, hooks, or
  orchestration.

These boundaries do not narrow the development scope authorized by the user.
