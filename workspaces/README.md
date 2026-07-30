# Local Workspaces

`workspaces/` is ignored local storage for project directories and Git
repositories. Each project owns its own instructions, tools, history, and
runtime state.

Lab root checks do not recursively inspect or mutate this directory. Opening a
workspace through `scripts/open-workbench` only passes its resolved directory
to cmux.
