# omp (oh-my-pi) 全面配置与落地指南

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: TypeScript / Rust / Bun](https://img.shields.io/badge/Language-Bun%20%7C%20Rust-black.svg)](https://bun.sh)
[![Engine: omp](https://img.shields.io/badge/Engine-omp%20v18.8-purple.svg)](omp://)
[![Platform: macOS Apple Silicon](https://img.shields.io/badge/Platform-Apple%20Silicon%20M4-blue.svg)](https://apple.com)

本目录提供 **omp (oh-my-pi)** 的架构定位、本地模型网关（Magpie / LM Studio / Ollama）接入、配置规范（`models.yml` / `config.yml`）以及一键部署脚本。

---

## 1. 架构定位与核心哲学

`omp` 是基于 **Bun** 运行时与 **Rust 原生模块 (`@oh-my-pi/pi-natives`)** 构建的次世代 Coding Agent CLI：

```text
┌─────────────────────────────────────────────────────────────┐
│                         omp CLI                             │
├──────────────┬──────────────┬───────────────┬───────────────┤
│ 交互 TUI 模式 │ 打印 Print-P │  ACP 协议服务 │  RPC 守护进程 │
└──────────────┴──────────────┴───────────────┴───────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
     ┌───────────────────┐           ┌───────────────────┐
     │   pi-agent-core   │           │     pi-natives    │
     │   智能体循环/工具集   │           │ PTY/文本搜索/系统 │
     └───────────────────┘           └───────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
     ┌───────────────────┐           ┌───────────────────┐
     │       pi-ai       │           │   Magpie 网关     │
     │ 多厂商协议统合引擎 │           │ 统一路由与端侧推理 │
     └───────────────────┘           └───────────────────┘
               │                               │
       ┌───────┴───────┬───────────────┬───────┴───────┐
       ▼               ▼               ▼               ▼
  [Claude Opus]   [GPT-6/Luna]    [Gemini 3.8]    [本地 LM Studio/Ollama]
  (Anthropic API) (OpenAI 协议)   (超长上下文)    (DeepSeek / Qwen Coder)
```

### 核心特性

1. **Bun 原生驱动 + Rust 极致加速**：
   - 依赖 Bun 现代化运行时，避免重型 Node.js 开销；
   - 底层集成 Rust 原生 PTY 终端模拟、高速文本查找与内存缓存。
2. **多层级配置与角色路由（Model Roles）**：
   - 支持 `default`、`smol`（轻量极速）、`slow`（深度推理）与 `plan`（架构规划）四大角色；
   - 支持 `--prewalk` 和 `--plan-yolo` 模式，在架构设计与编码实现阶段智能切换大/小模型。
3. **强大的工具执行沙箱与内省**：
   - 原生支持 `read`, `edit`, `write`, `grep`, `glob`, `lsp`, `task` (并发子 Agent), `browser`, `todo`, `web_search`；
   - 支持 `tools.approvalMode: yolo` 全自动无阻塞执行，或 `write` 仅敏感修改确认。
4. **统一技能（Skills）与规则（Rules）生态**：
   - 原生扫描 `.omp`、`.claude`、`.gemini`、`.codex` 多源配置目录，实现各生态技能库的零成本复用。

---

## 2. 目录结构概览

```text
omp/
├── models.yml              # 核心模型网关与 Provider 定义 (Magpie/LM Studio/Ollama)
├── config.yml              # Agent 行为偏好、角色路由、思考深度及审批策略
├── install.sh              # 一键环境检查、后端探测与配置部署脚本 (支持 -g / -p)
├── RECOMMENDED_SKILLS.md   # 适配 omp 运行时的高价值 Skill 推荐与分类
├── RECOMMENDED_AGENTS.md   # 核心专家角色配置 (Architect, Reviewer, Sonic 等)
└── ReadMe.md               # 本指南文档
```

---

## 3. 核心配置文件说明

### 3.1 `models.yml` (模型提供商定义)

`omp` 的模型注册表通过 `providers` 组织。例如接入本地运行的 **Magpie** 网关与 **LM Studio**：

```yaml
providers:
  magpie:
    baseUrl: http://127.0.0.1:3425/v1
    api: openai-completions
    auth: none
    models:
      - id: antigravity/gemini-3.8-flash
        name: Gemini 3.8 Flash · Antigravity
        api: openai-responses
        reasoning: true
        contextWindow: 1048576
        maxTokens: 65536
        input: [text, image]
      - id: antigravity/claude-opus-4-6-thinking
        name: Claude Opus 4.6 Thinking · Antigravity
        api: openai-responses
        reasoning: true
        contextWindow: 256000
        maxTokens: 65536
        input: [text, image]
      - id: codex/gpt-6-astra
        name: GPT-6-Astra · Codex
        api: openai-responses
        reasoning: true
        contextWindow: 272000
        maxTokens: 128000
        input: [text, image]

  lmstudio:
    baseUrl: http://127.0.0.1:1234/v1
    api: openai-completions
    auth: none
    models:
      - id: deepseek-r1-qwen-32b
        name: DeepSeek R1 Distill Qwen 32B (Local)
        reasoning: true
        contextWindow: 65536
        maxTokens: 16384
```

### 3.2 `config.yml` (系统与角色行为配置)

```yaml
setupVersion: 2

# 模型角色映射
modelRoles:
  default: magpie/antigravity/gemini-3.8-flash # 默认日常对话与轻量修改
  smol: magpie/antigravity/gemini-3.8-flash    # 快速辅助与简单执行
  slow: magpie/antigravity/claude-opus-4-6-thinking # 复杂重构与深度推理
  plan: magpie/codex/gpt-6-astra              # 顶层架构设计与任务拆解

# 思考推理预算
defaultThinkingLevel: medium

# 工具审批策略 (yolo: 全自动; write: 仅写文件提示; always-ask: 全部提示)
tools:
  approvalMode: yolo
```

---

## 4. 快速开始与一键安装

通过配套的 `install.sh` 脚本可快速完成部署与连通性验证：

```bash
cd omp

# 1. 仅检测本地各推理后端连通性与模型可用性
./install.sh --check

# 2. 全局部署 (写入 ~/.omp/agent/models.yml 和 config.yml)
./install.sh

# 3. 为当前工程初始化项目级配置 (写入 ./.omp/)
./install.sh -p .

# 4. 部署同时挂载推荐技能
./install.sh -s
```

---

## 5. 常用命令速查

```bash
# 启动交互式 TUI 会话
omp

# 启动并直接输入初始任务
omp "重构当前项目模块的导入规范"

# 目标驱动模式 (Goal Mode)
omp --goal "实现用户身份校验模块"

# 非交互式单次执行 (Print / Headless 模式)
omp -p "查看项目所有未通过的测试用例并输出修复方案"

# 指定模型或切换角色
omp --model opus "进行全面代码安全审查"
omp --slow "排查死锁与并发边界问题"

# 跨会话恢复与历史继续
omp --continue          # 继续最近一次会话
omp --resume            # 打开交互式会话选择器

# 模型管理与基准测试
omp models              # 查看所有已配置的模型矩阵
omp bench               # 对当前模型进行吞吐与延迟基准评测
```

---

## 6. 与其他 Coding CLI 的生态协同

| 维度 | omp (oh-my-pi) | Pi Agent (`pi`) | Antigravity (`agy`) | Claude Code (`claude`) |
| :--- | :--- | :--- | :--- | :--- |
| **运行时** | **Bun + Rust 原生扩展** | Node.js | Go / Native | Node.js |
| **角色路由** | 支持 `default`, `smol`, `slow`, `plan` | 运行时单一模型 | 全局调度 | 单一模型 |
| **工具箱** | 内置 AST, LSP, PTY, Sub-agents | 基础 Tools + Extensions | MCP 原生 | Bash, Edit, Grep |
| **配置目录** | `~/.omp/agent/` | `~/.pi/agent/` | `~/.gemini/` | `~/.claude/` |
| **生态兼容** | **全兼容**（自动读取 `.claude`, `.gemini`, `.codex`） | 独立扩展 | Google 生态 | 官方专属 |
