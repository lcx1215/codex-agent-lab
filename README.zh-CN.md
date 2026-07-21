# Codex Agent Lab

**[English](README.md) | 简体中文**

这是 Codex 和 Claude 做 agent 开发的本地工作台。

根层要保持薄：安全锁、放置规则、小证明循环、快速健康门。场景历史、公司细节、
发布流水和重 harness 证据放到 `workspaces/`、`docs/`、`outputs/` 或 `registry/`。

## 定位

- 这是治理和协作层，不是生产 agent runtime。
- Codex 和 Claude 共用这个 lab 根，靠持久状态和验证门减少误判。
- 根层保持场景中立；产品或公司任务进 `workspaces/`。
- 默认用最小证据证明当前结论，证明后停止或进入下一轮。

## 入口

| 需要 | 命令或文件 |
| --- | --- |
| 根层快速体检 | `./scripts/check-lab` |
| clean-home Codex lane | `./scripts/start-clean-home` |
| API-relay Codex lane | `./scripts/start-api-relay` |
| 工作流模式 | `./scripts/workflow-mode list` |
| 当前仪表盘 | `./scripts/lab-dashboard` |
| Clink 上下文 | `workspaces/clink-internal-dev-context/README.md` |

不是 Clink 公司任务时，不要默认读取 Clink context，也不要用 `.current-agent` 指针。

## 规则和放置

- Codex 根规则：`AGENTS.md`
- Claude 根规则：`CLAUDE.md`
- 放置契约：`docs/environment-layering.md`
- 规则继承：`docs/rule-inheritance.md`
- 场景工作区契约：`docs/scenario-workspace-contract.md`
- Codex-Claude 协作协议：`docs/codex-claude-collaboration-protocol.md`
- mission 和晋升标准：`docs/agent-lab-mission.md`

根层只放通用资产。工作区放产品或公司上下文。Agent 包放在工作区里的
`agents/` 或 `subagents/`。

## 快检查

普通编辑循环优先跑这些：

| 检查 | 命令 |
| --- | --- |
| 项目规则 | `./scripts/check-project-rules` |
| 运行时兼容 | `./scripts/check-runtime-compatibility` |
| 规则阶梯 | `./scripts/check-rule-ladder` |
| Agent 包 | `./scripts/check-agent-packages` |
| 沙箱 | `./scripts/check-sandbox` |
| 沙箱技能 | `./scripts/check-sandbox-skills` |
| 速度契约 | `./scripts/check-speed-contract` |
| 任务状态 | `./scripts/check-task-state` |
| 密钥扫描 | `./scripts/check-secrets` |

改了什么，就优先跑能证明这件事的最小测试。

## 边界检查

提交、发布、晋升、交接或明确审计时再跑重检查：

| 边界 | 命令 |
| --- | --- |
| 工作区安全 | `./scripts/check-workspace-safety` |
| 并发执行 | `./scripts/check-async-execution` |
| IDE 循环基准 | `./scripts/benchmark-ide-loop` |
| Waterflow 扫描 | `./scripts/waterflow-scan --root . --compare-last` |
| Waterflow 验证 | `./scripts/waterflow-verify` |
| Waterflow 压测 | `./scripts/waterflow-stress --scale-paths 1200` |
| Waterflow 事故演练 | `./scripts/waterflow-incident` |
| 协作面 | `./scripts/check-collaboration` |

`docs/waterflow-speed-contract.md` 规定这些重 harness 不能默认进每次编辑循环。

## Agents 和技能

常驻支持 agent：

- `foundation-amplifier`
- `development-experience-auditor`
- `third-party-large-agent-auditor`
- `context-architect`
- `handoff-summarizer`
- `waterflow-auditor`

审计入口：

- `./scripts/development-experience-audit`
- `./scripts/large-agent-readiness-audit`

Lab 技能在 `.agents/skills/`。当前沙箱技能是 `secret-boundary-auditor`、
`async-race-detector`、`sandbox-artifact-hygiene`。

## 报告

- 持久进度：`registry/current-progress.md`
- 验证证据：`registry/VALIDATION.md`
- Agent 名册：`registry/AGENT_REGISTRY.md`
- 运行时兼容报告：`outputs/shared/compatibility/runtime-compatibility.md`
- 工作区安全报告：`outputs/shared/workspace-safety/workspace-safety.md`
- 仪表盘：`outputs/shared/dashboard/lab-dashboard.md`
- 基准历史：`outputs/shared/benchmarks/ide-loop/history.md`

报告是证据，不是根层规则。

## 边界

- 不读取、复制、打印或迁移密钥、认证文件、token、cookie、OTP、API key、
  provider config 或账号会话。
- 没有当前精确授权，不改公司仓库、分支、部署配置或 TEST/UAT/PROD 状态。
- Jenkins 只能用户手动操作；Codex 只分析用户提供的截图、复制日志或状态文本。
- 不改默认 App/Plus lane、API-relay 认证、provider config、LaunchAgents 或插件，
  除非用户明确点名这个本地任务。
