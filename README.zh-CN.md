# Codex Agent Lab

**[English](README.md) | 简体中文**

面向 Codex 与 Claude 长周期 agent 工作的、干净且按项目隔离的环境。

> **一句话定位:** 一个私人的、受治理的工作台——让 Claude(`~/.claude`)和
> Codex(`~/.codex-api-relay`)两条 AI lane 在同一个仓库上协作,配有持久状态、
> fail-closed 安全门和双 lane 评审协议,使它们的工作可追溯、相互隔离、互不冲突。

### 目录

- [为什么存在](#为什么存在)
- [已建成的部分(治理层,可用)](#已建成的部分治理层可用)
- [诚实定位](#诚实定位)
- [自主执行](#自主执行)
- [路径](#路径)
- [环境分层](#环境分层)
- [启动](#启动)
- [命令速查](#命令速查)
- [Agent 行为内核](#agent-行为内核)
- [Agent 名册](#agent-名册)
- [指引分层](#指引分层)
- [技能与插件](#技能与插件)
- [场景工作区](#场景工作区)
- [工作流模式](#工作流模式)
- [密钥安全](#密钥安全)
- [沙箱安全](#沙箱安全)
- [速度策略](#速度策略)
- [边界](#边界)

### 为什么存在

各自的 agent 工具(OMC/OMX 插件)让每个 agent 单独看都很能干,但并不能让两个
agent 协同工作时不互相覆盖文件、不共享同一个事实来源、也不互相评审。这个 lab
补的正是这缺失的一层:治理、交接(hand-off)、以及防碰撞的协作——插件不提供的
那套管道。

### 已建成的部分(治理层,可用)

- **规则阶梯(Rule ladder)** —— 三层环境(根 → 工作区 → 包),强制父级规则继承
  (`scripts/check-rule-ladder`)。
- **Fail-closed 安全** —— 沙箱、密钥、工作区边界三道门,宁可拒绝也不静默放行
  (`scripts/check-sandbox` / `check-secrets` / `check-workspace-safety`)。
- **诚实的验证** —— 自审会真正*运行*这些门(按退出码判定),不会因为"文件存在"
  就把自己打成假绿。
- **任务生命周期门** —— 开工前先确认规则、并发受限的分发、完成前先验证
  (`scripts/check-gates`、`lab_agents/`)。
- **防碰撞并行** —— git worktree 隔离 + 有序合并队列,其预合并冲突检查 fail-closed
  (`scripts/worktree-merge-queue`)。
- **证据链** —— 结构化、脱敏的逐次运行记录,类型化的 assignments 账本,以及一条
  验证链(`registry/`)。
- **双 lane 协作** —— 带日期的交接 + 独立的跨 lane 评审
  (`docs/codex-claude-collaboration-protocol.md`)。
- **元治理(Meta-governance)** —— 针对"谁来治理那些能改环境的人"这一极限,给出一
  份诚实的宪法:由人来给递归封顶(`docs/meta-governance.md`)。

### 诚实定位

这是一层**治理 / 协作层**,不是一个成熟的运行时(runtime)。它的强项在于可信的
双 lane 协作、安全、以及验证的诚实性;它**刻意不去**做"比 LangGraph/CrewAI/AutoGen
更强"的执行引擎——运行时成熟度和生态是它的短板。毫不留情的自评见
`registry/PLATFORM_SCORECARD_CLAUDE_20260701.md`。

---

这个 lab 是一个场景中立的开发环境,面向任意规模的 agent 项目。UCP 及其它领域专用
agent 是未来的场景工作区,而不是 lab 的边界。

这个环境是 Codex 和 Claude 的力量放大器:持久进度、隔离工作区、Waterflow 监督、
基准、技能、prompt、验证门,都应帮它们更快更安全地工作。它们不替代模型 agent 在
推理、写码、评审、恢复上的职责。

在效果相当的前提下,lab 应保持精简:只要安全、隔离、速度、验证都不受损,就更倾向
更少的规则、更少的生成物、更少的默认检查、更少的常驻进程。

lab 的使命、质量标准、以及用于扩展环境的晋升规则见 `docs/agent-lab-mission.md`。

最大环境、工作区、agent 包各自该放什么资产,见 `docs/environment-layering.md`。

## 自主执行

lab 里的 agent 自主运行:端到端完成任务,不向用户请求批准——决定、执行、验证、
汇报。这是长期授权(standing authorization),不是逐任务授权。

绝不以 yes/no 或"要我…吗?"式的请求许可问句结束一个回合——如果想问要不要继续,
就直接做然后汇报。汇报结论,而不是原始日志:用户在 CLI 里、没有 GUI,所以清晰
呈现是 agent 的职责(`mas` 看环境状态,`duo` 并排看 Claude+Codex 面板)。

这不放松 `AGENTS.md`(`## Isolation`)里的安全边界:不处理密钥/认证,不碰
`~/.codex` / `~/.codex-api-relay` / provider 配置 / LaunchAgents,并且待在 lab 根
以内。自主去掉的是"请求许可"这一步,不是安全线。

## 路径

- lab 根:本仓库 checkout
- 隔离的 Codex home:`.codex-home`
- 可选的全局规则源:`~/.codex/AGENTS.md`
- lab 覆盖规则:`AGENTS.md`
- 项目 agent:`.codex/agents`
- 项目技能:`.agents/skills`
- 持久进度:`registry/current-progress.md`
- 任务工作区:`workspaces`
- 输出:`outputs`

## 环境分层

- **最大环境**:lab 根。只放场景中立的规则、共享技能、协议、接口、Waterflow 引擎
  代码、健康门、以及持久 registry。
- **中等环境**:`workspaces/<scenario>/`。放产品/场景工作、局部契约、局部接口、
  局部验证,必要时放嵌套仓库。
- **小型 agent 包**:中等环境里的文件夹,通常是 `agents/<package>/`。放具体的
  agent 清单、包内技能、知识、工具接线、fixtures 和测试。

## 启动

严格 clean-home lane:

```bash
./scripts/start-clean-home
```

项目隔离的 API-relay lane(默认用已有的 API relay 认证/配置 home 和 OMX):

```bash
./scripts/start-api-relay
```

非 OMX 的 API-relay 回退(仅用于诊断或显式绕过):

```bash
./scripts/start-api-relay-plain
```

clean-home lane 不复制密钥。若需要模型访问,请单独在那个隔离 home 里登录或添加
API 认证。

## 命令速查

所有脚本在 lab 根下执行(`./scripts/<name>`)。

| 命令 | 作用 |
|---|---|
| `check-lab` | 检查安装完整性 |
| `check-sandbox` | 只检查沙箱边界 |
| `check-runtime-compatibility` | 检查运行时兼容性与常见配置漂移 |
| `check-rule-ladder` | 检查根/工作区/包规则阶梯的连续性 |
| `check-agent-packages` | 检查 agent/subagent 名册注册与清单完整性 |
| `check-workspace-safety` | 工作区级安全检查(不阻塞进行中的工作) |
| `check-async-execution` | 检查异步执行安全 |
| `check-sandbox-skills` | 检查沙箱专用技能 |
| `check-speed-contract` | 检查 Waterflow 速度契约 |
| `check-task-state` | 检查轻量任务状态调度器 registry |
| `check-collaboration` | 校验 Codex-Claude 协作面 |
| `check-secrets` | 提交前的密钥扫描 |
| `benchmark-ide-loop [--skip-omx]` | 跑 IDE 循环基准(可跳过模型 smoke test) |
| `lab-dashboard` | 渲染一屏 lab 仪表盘 |
| `development-experience-audit` | 审计 lab 里 Codex/Claude 的开发舒适度 |
| `large-agent-readiness-audit` | 以第三方评审视角审计大 agent 就绪度 |
| `workflow-mode list` / `workflow-mode <mode>` | 列出 / 打印工作流模式契约 |
| `waterflow-scan --root . [--compare-last]` | 跑 Waterflow 审计(可对比上次路径索引) |
| `waterflow-verify` | 跑最新 Waterflow 计划里的真实验证命令 |
| `waterflow-stress --scale-paths <N>` | 跑高压 Waterflow fixtures |
| `waterflow-incident` | 跑复杂 Waterflow 事故 fixture 并生成交接 |

## Agent 行为内核

lab 内置一个领域中立的 agent 行为内核(`lab_agents/agent_kernel/`),让任意大
agent 家族复用同一套经过验证的安全/决策骨架,而不必按领域各自重写守卫。一个家族
把原语组合成一个 `DecisionEngine`:

```python
from lab_agents.agent_kernel import DecisionEngine, policies
engine = DecisionEngine(
    [policies.sensitive_data_request(terms=("api key",)), policies.grounded_answer(keyword="runbook")],
    policies.insufficient_evidence_fallback(),
)
```

`tests/test_kernel_neutrality.py` 通过在内核上搭两条互不相关的 agent 链
(infra-ops、research)来证明它不是单领域引擎。真实场景在自己 `workspaces/` 下的
工作区里搭链。见 `docs/agent-behavior-kernel.md`。

## Agent 名册

lab 保留全部 11 个 `.codex/agents/*.toml` 定义,但常驻名册刻意更小。当前姿态和调用
规则见 `.codex/agents/ROSTER.md`。

**常驻核心:** `context-architect`、`handoff-summarizer`、
`third-party-large-agent-auditor`、`development-experience-auditor`、
`waterflow-auditor`、`foundation-amplifier`。

**按需调用:** `long-horizon-orchestrator`、`research-scout`、
`implementation-worker`、`verification-auditor`、`risk-reviewer`。

委派时用明确的 agent 名。每次运行保持窄范围,并把持久状态写进
`registry/current-progress.md`。

## 指引分层

全局规则留在活跃的 Codex home。本 lab 可以用 `.codex-home/AGENTS.md` 到
`~/.codex/AGENTS.md` 的本地引用,让 clean-home lane 继承全局策略,而不必维护一份会
分叉的副本。本仓库的 `AGENTS.md` 只是环境专属的覆盖层:隔离、lab 路径、agent 角色、
局部技能、验证规则。

关键契约:全局 `~/.codex/AGENTS.md`;lab 覆盖 `AGENTS.md`;Claude lane 覆盖
`CLAUDE.md`;放置契约 `docs/environment-layering.md`;规则继承链
`docs/rule-inheritance.md`;协作协议 `docs/codex-claude-collaboration-protocol.md`;
使命与质量标准 `docs/agent-lab-mission.md`。持久进度与验证在 `registry/`,任务工作
在 `workspaces/`,Waterflow 报告在 `outputs/shared/waterflow/`。

Waterflow 只扫自己的 `waterflow/`、`tests/`、`docs/` 路径。生成的 `outputs/` 是证据
产物、不是源代码水路,已从图中排除以免持续自我 diff 噪声。路径数很大时,先用路径
索引和"仅变更"验证。事故 harness 用于真实故障演练:它通过表示检测与上报有效,不代
表 fixture 或真实 lab 是健康的。

## 技能与插件

Codex 可在活跃 lane 里使用它正常的全局技能和插件。本 lab 专属或某任务专属的技能
应放在 `.agents/skills/` 下。

## 场景工作区

`workspaces/` 下的工作区可面向任意大 agent 家族。当前示例可能包含 UCP 风格或客服
导向的底座,但这些示例不定义 lab 的完整范围。只把可复用的模式从场景工作区晋升回共
享 lab。用 `docs/scenario-workspace-contract.md` 和 `scripts/new-workspace`,让每个
正式场景都声明自己的边界、以及它如何放大 Codex/Claude 的工作。

## 工作流模式

用 `docs/workflow-modes.md` 和 `scripts/workflow-mode` 在日常 App 工作、CLI 诊断、
OMX 长周期执行、多 agent 评审、以及过夜检查点工作之间选择。这些模式是路由契约,不
覆盖全局安全规则。

## 密钥安全

不要提交 API key、GitHub token、`.env` 文件、私钥、cookie,或认证/会话文件。提交前
先跑:

```bash
./scripts/check-secrets
```

仓库还带一个 GitHub Actions 密钥扫描,会拦截常见的 GitHub、OpenAI、AWS、私钥、
`.env` 和认证文件泄露。

## 沙箱安全

clean-home lane 用限定在本仓库 checkout 的 `workspace-write`。系统临时目录被排除;
lab 本地临时文件应放 `.tmp/`。改动沙箱配置、符号链接、临时文件行为或工作区边界后,
跑 `./scripts/check-sandbox`。

## 速度策略

用 `docs/reasoning-speed-playbook.md`,把 `gpt-5.5` + `xhigh` 留给真正难的推理,同时
把查找、验证、扫描、独立检查移到更快或并行的 lane。用
`docs/waterflow-speed-contract.md` 让 Waterflow 监督不拖慢活跃的 Codex/Claude 工作:
默认检查保持仅元数据或仅变更;完整 Waterflow 验证、压力 fixture、事故 fixture 是边界
工具。用 `scripts/benchmark-ide-loop` 长期度量 RED/GREEN 编辑循环,用
`scripts/lab-dashboard` 看紧凑的当前状态。

## 边界

本 lab 不得改动用户默认的 App/Plus lane 或 API-relay lane。它可以用 API-relay
启动器获取模型访问,同时把项目文件、输出、自定义 agent 和任务工作区都留在本 lab 内。

