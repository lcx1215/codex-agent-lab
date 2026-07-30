# Codex Agent Lab

Agent Lab 是原生 Codex、Claude Code 和 Codex App 的可选开发入口。

它只负责：

- 打开或复用正确的 cmux 工作目录。
- 显示当前项目、Git 和 cmux 状态。
- 按需检查原生客户端是否被覆盖或拖慢。

它不管理认证、模型、Provider、Skill、记忆、插件、会话、Agent、
worktree 或项目开发流程，也不要求任何客户端 API Key。

## 日常使用

打开普通项目：

```bash
./scripts/lab open /path/to/repo
```

打开当前客服 Agent：

```bash
./scripts/lab open --current-agent
```

cmux workspace 固定包含三个初始纯 Shell：

- 左侧：`Codex CLI`
- 右上：`Claude Code`
- 右下：`Shell`

Lab 不会自动启动 Codex 或 Claude。进入对应 Shell 后，由用户运行原生
`codex` 或 `claude`。

只查看将执行的 cmux 命令：

```bash
./scripts/lab open --dry-run /path/to/repo
```

只检查已有 workspace，不创建或聚焦：

```bash
./scripts/lab open --check /path/to/repo
```

## 查看现场

```bash
./scripts/lab status /path/to/repo
./scripts/lab status --current-agent
./scripts/lab status --json /path/to/repo
```

`status` 只读取真实路径、分支、HEAD、tracked dirty 状态和 cmux workspace。
Git 检查最多等待 2 秒，不扫描未跟踪文件；超时显示 `unknown`，不会阻塞开发。
cmux 未安装或未运行不会影响 Git 状态。

## 检查客户端

静态检查：

```bash
./scripts/lab doctor
./scripts/lab doctor --json
```

真实 Codex/Claude A/B：

```bash
./scripts/lab doctor --live
```

`--live` 会在空目录和 Lab 根目录各运行三轮 Codex 与 Claude，共 12 次模型
调用。结果保存到 `.tmp/native-parity/latest.json`。每个客户端由 Lab 增加的
上下文不得超过 2048 tokens。

在 cmux Shell 中比较 direct-Lab 基线：

```bash
./scripts/lab doctor --inside-cmux
./scripts/lab doctor --inside-cmux --live
```

cmux 可能提供命令 shim，因此路径可不同；客户端版本、配置指纹和 Skill
清单必须一致。`--inside-cmux --live` 会在同一个 cmux Shell 中交错比较原生
绝对路径和 shim 路径，共执行 12 次模型调用。

## 直接使用原生客户端

Lab 从来不是必经入口：

```bash
cd /path/to/repo
codex
```

或：

```bash
cd /path/to/repo
claude
```

如果 Lab 增加了等待、理解成本或能力限制，应直接绕过并运行
`./scripts/lab doctor` 定位差异。

## 本地验证

```bash
python3 -m unittest discover -s tests
./scripts/check-lab
./scripts/check-secrets
./scripts/check-side-effects
git diff --check
```

`workspaces/`、`.worktrees/` 和其中的公司仓库不属于 Lab 根修改范围。
