# Runtime Compatibility Report

- Generated: `2026-06-30T09:17:12.898512+00:00`
- Status: `pass`
- Checks: `40`
- Passed: `40`
- Warnings: `0`
- Failed: `0`

## Findings

### pass: required command: awk

required command is available

- `/usr/bin/awk`
- `awk version 20200816`

### pass: required command: bash

required command is available

- `/bin/bash`
- `GNU bash, version 3.2.57(1)-release (arm64-apple-darwin25)`

### pass: required command: find

required command is available

- `/usr/bin/find`
- `version probe unavailable`

### pass: required command: git

required command is available

- `/opt/homebrew/bin/git`
- `git version 2.48.1`

### pass: required command: grep

required command is available

- `/usr/bin/grep`
- `grep (BSD grep, GNU compatible) 2.6.0-FreeBSD`

### pass: required command: python3

required command is available

- `/opt/homebrew/bin/python3`
- `Python 3.14.3`

### pass: required command: rg

required command is available

- `/Applications/Codex.app/Contents/Resources/rg`
- `ripgrep 15.1.0 (rev af60c2de9d)`

### pass: required command: sed

required command is available

- `/usr/bin/sed`
- `version probe unavailable`

### pass: required command: sort

required command is available

- `/usr/bin/sort`
- `2.3-Apple (199)`

### pass: required command: stat

required command is available

- `/usr/bin/stat`
- `version probe unavailable`

### pass: required command: tr

required command is available

- `/usr/bin/tr`
- `version probe unavailable`

### pass: required command: wc

required command is available

- `/usr/bin/wc`
- `version probe unavailable`

### pass: optional command: codex

optional agent/runtime command is available

- `/Users/liuchengxu/.nvm/versions/node/v24.18.0/bin/codex`
- `codex-cli 0.142.4`

### pass: optional command: omx

optional agent/runtime command is available

- `/Users/liuchengxu/.local/bin/omx`
- `oh-my-codex v0.18.16`

### pass: optional command: tmux

optional agent/runtime command is available

- `/opt/homebrew/bin/tmux`
- `tmux 3.7`

### pass: python version

python3 supports tomllib and current lab scripts

- `3.14.3`

### pass: python stdlib modules

required Python stdlib modules import

### pass: directory: .codex-home

required directory exists

### pass: directory: .codex/agents

required directory exists

### pass: directory: .agents/skills

required directory exists

### pass: directory: .tmp

required directory exists

### pass: directory: docs

required directory exists

### pass: directory: outputs

required directory exists

### pass: directory: registry

required directory exists

### pass: directory: scripts

required directory exists

### pass: directory: tests

required directory exists

### pass: directory: workspaces

required directory exists

### pass: script shebangs

all scripts declare an interpreter

### pass: script executability

all scripts are executable

### pass: script line endings

scripts use LF line endings

### pass: check-lab aggregation

check-lab references required lightweight gates

### pass: gitignore: .omx/state/example.json

OMX runtime state should be ignored

### pass: gitignore: .omc/state/example.json

OMC runtime state should be ignored

### pass: gitignore: .omc/skills/example/SKILL.md

project OMC skills should remain committable

### pass: CODEX_HOME environment

CODEX_HOME is unset for this preflight

### pass: clean-home auth boundary

clean home has no auth.json

### pass: documentation: docs/runtime-compatibility.md

compatibility gate is documented

### pass: documentation: README.md

compatibility gate is documented

### pass: documentation: AGENTS.md

compatibility gate is documented

### pass: documentation: registry/CAPABILITY_LAYERS.md

compatibility gate is documented
