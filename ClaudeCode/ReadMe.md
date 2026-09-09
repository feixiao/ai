[English](./ReadMe_EN.md)

# Use your LM Studio Models in Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: Shell](https://img.shields.io/badge/Language-Shell-blue.svg)](https://www.gnu.org/software/bash/)

本项目提供免配置、防 Keychain 冲突、自动配置隔离与双向会话同步的启动脚本 `claude-lm.sh`，帮助您将官方 Claude Code CLI 无缝接入本地 [LM Studio](https://lmstudio.ai/) 运行的大语言模型。

---

## 1. 前置准备与安装指南

### 1.1 安装 Claude Code CLI

确保本地已正确安装官方 `claude` 命令行工具：

```bash
# 官方标准安装方式
npm install -g @anthropic-ai/claude-code

# 或使用官方一键安装脚本
curl -fsSL https://claude.ai/install.sh | bash
```

安装完成后，验证可执行路径：
```bash
which claude
# 输出通常为 ~/.local/bin/claude 或 /usr/local/bin/claude
```

---

### 1.2 安装并启动 LM Studio 本地服务

1. 从 [LM Studio 官网](https://lmstudio.ai/) 下载并安装对应系统版本（推荐 Apple Silicon Mac 版本）。
2. 在 LM Studio 中下载所需的模型（如 `qwen3.8-27b-mlx@4bit`、`gemma-4-31b-it`、`mlx-qwopus3.5-9b-v3` 等）。
3. 切换至 **Developer** 标签页（本地服务器模式）：
   - 点击 **Start Server** 开启服务。
   - 默认监听端口为 `1234`（访问地址：`http://127.0.0.1:1234`）。
   - 确认已勾选 **Enable CORS**。

---

### 1.3 安装 `clm` / `claude-lm` 到系统命令（推荐）

将包装脚本及配套会话同步工具复制到系统的 `~/.local/bin` 目录中，即可在任意终端目录下直接调用：

```bash
# 进入 ClaudeCode 目录
cd /Users/frank/wk/github/ai/ClaudeCode

# 赋予执行权限
chmod +x claude-lm.sh sync_sessions.sh

# 1. 拷贝脚本到全局可执行命令目录 (~/.local/bin)
mkdir -p ~/.local/bin
cp claude-lm.sh ~/.local/bin/clm
cp claude-lm.sh ~/.local/bin/claude-lm
cp sync_sessions.sh ~/.local/bin/sync_sessions.sh

# 2. 确保全局可执行
chmod +x ~/.local/bin/clm ~/.local/bin/claude-lm ~/.local/bin/sync_sessions.sh

# 3. 验证安装
which clm
which claude-lm
```

> **提示**：
> 1. 请确保 `~/.local/bin` 已加入系统 `PATH`（在 `~/.zshrc` 或 `~/.bashrc` 中包含 `export PATH="$HOME/.local/bin:$PATH"`）。
> 2. 若您后续修改了仓库中的 `claude-lm.sh`，重新执行上述 `cp` 命令覆盖即可更新。

---

## 2. 快速使用与命令详解

### 2.1 基础启动

```bash
# 1. 默认推荐模式启动 (Coder 预设: qwen3.8-27b-mlx@4bit + gemma-4-31b-it + mlx-qwopus3.5-9b-v3)
clm

# 或使用完整别名
claude-lm
```

---

### 2.2 切换预设策略 (`--preset`)

脚本内置 4 种典型开发场景预设：

```bash
# 1. 编程主力模式 (默认: 27B 编码主力 + 31B 架构推理 + 9B 极速 Agent)
clm --preset coder

# 2. 深度推理模式 (以 gemma-4-31b-it 进行深度规划与复杂逻辑分析)
clm --preset reasoning

# 3. Qwen 系列全家桶 (qwen3.8-27b 4bit/8bit + qwopus3.5-9b)
clm --preset qwen

# 4. Gemma 系列全家桶 (gemma-4-26b-a4b-it + gemma-4-31b-it)
clm --preset gemma
```

---

### 2.3 统一单模型模式 (`--single`)

当 LM Studio 本地仅加载单个模型时，使用 `--single` 将所有角色（Sonnet/Opus/Haiku/Subagent）统一路由至该模型，避免多模型切换导致的显存重载开销：

```bash
# 全部角色统一使用 qwen3.8-27b-mlx@4bit
clm --single qwen3.8-27b-mlx@4bit

# 全部角色统一使用 gemma-4-31b-it
clm --single gemma-4-31b-it
```

---

### 2.4 会话恢复与参数透传

脚本原生支持透传所有官方 Claude Code 参数：

```bash
# 恢复最近一次会话
clm --resume

# 恢复指定 UUID 历史会话
clm --resume 2ce044f6-9934-4e69-b974-c6881e1764da

# 单次 Prompt 执行模式 (Print 模式)
clm -p "编写一个基于 FastAPI 的流式聊天后端接口"
```

---

## 3. 本地模型库与分层角色推荐

针对 Apple Silicon (M-series / Mac Studio) 本地部署的模型，推荐分工如下：

| 本地模型名称 | 显存占用 | 参数量 | 推荐路由角色 | 特点与适用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **`qwen3.8-27b-mlx@4bit`** | 16.1 GB | 27B | **`ANTHROPIC_DEFAULT_SONNET_MODEL`**<br>+ **默认主力模型 (`ANTHROPIC_MODEL`)** | 专为代码生成与重构优化，4-bit 平衡版主力选择 |
| **`gemma-4-31b-it`** | 18.4 GB | 31B | **`ANTHROPIC_DEFAULT_OPUS_MODEL`** / **Fable** | Dense 强推理指令模型，适合复杂架构设计与全局规划 |
| **`qwen3.8-27b-mlx@8bit`** | 29.5 GB | 27B | **`ANTHROPIC_DEFAULT_OPUS_MODEL`** (可选) | 高精度 8-bit Qwen 模型，数学与逻辑推理能力突出 |
| **`gemma-4-26b-a4b-it`** | 15.6 GB | 26B | **`ANTHROPIC_DEFAULT_SONNET_MODEL`** / **Haiku** | MoE 高吞吐架构，在保持智能的同时生成速度极快 |
| **`mlx-qwopus3.5-9b-v3`** | 9.5 GB | 9B | **`ANTHROPIC_DEFAULT_HAIKU_MODEL`**<br>+ **`CLAUDE_CODE_SUBAGENT_MODEL`** | MLX 优化版 9B，极低延迟，适合子代理与轻量辅助任务 |
| **`qwopus3.5-9b-v3`** | 6.0 GB | 9B | **`ANTHROPIC_DEFAULT_HAIKU_MODEL`**<br>+ **`CLAUDE_CODE_SUBAGENT_MODEL`** | 极致轻量 6GB 显存，极快首字响应 |

---

## 4. 环境变量与底层配置详情

脚本内置了针对本地推理引擎的底层优化与路由配置：

```bash
# 1. LM Studio 本地服务接入点与防代理设置
export NO_PROXY="127.0.0.1,localhost,$NO_PROXY"
export ANTHROPIC_BASE_URL="http://127.0.0.1:1234/v1"
export ANTHROPIC_API_KEY="lmstudio"

# 2. 全量重定向 Sonnet / Haiku / Opus / Fable / 子 Agent 角色
export ANTHROPIC_MODEL="qwen3.8-27b-mlx@4bit"
export ANTHROPIC_DEFAULT_MODEL="qwen3.8-27b-mlx@4bit"
export ANTHROPIC_DEFAULT_SONNET_MODEL="qwen3.8-27b-mlx@4bit"
export ANTHROPIC_DEFAULT_OPUS_MODEL="gemma-4-31b-it"
export ANTHROPIC_DEFAULT_FABLE_MODEL="gemma-4-31b-it"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="mlx-qwopus3.5-9b-v3"
export CLAUDE_CODE_SUBAGENT_MODEL="mlx-qwopus3.5-9b-v3"

# 3. 禁用 1M 上下文后缀与流量/超时调优
export CLAUDE_CODE_DISABLE_1M_CONTEXT=1
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK=1
export CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1
export CLAUDE_STREAM_IDLE_TIMEOUT_MS=600000
export API_TIMEOUT_MS=3000000

# 4. 上下文压缩窗口调优
unset DISABLE_COMPACT
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=100000
```

---

## 5. 会话双向同步工具 (`sync_sessions.sh`)

为了避免使用本地模型时污染或冲突官方 Claude Code 的登录状态，脚本将配置隔离在 `~/.lmstudio/claude_config` 目录中。

通过配套的 `sync_sessions.sh`，可实现官方 `~/.claude` 与本地环境之间的无缝双向会话同步（在 `clm` 启动和退出时会自动执行）：

```bash
# 手动增量同步所有官方会话到本地 LM Studio 配置
./sync_sessions.sh

# 双向同步（两边均保留最新文件）
./sync_sessions.sh -b

# 单独同步指定 UUID 的会话记录
./sync_sessions.sh 2ce044f6-9934-4e69-b974-c6881e1764da
```

---

## 6. 常见问题排查 (Troubleshooting)

### 6.1 报错：`zsh: no such file or directory: /Users/.../claude-lmstudio.sh`
- **原因**：当前终端进程中加载了旧的 `alias`（指向了已移动或废弃的旧路径）。`source ~/.zshrc` 只会新增或覆盖配置，不会从当前终端内存中注销已存在的别名。
- **解决方法**：
  1. 在当前终端窗口执行清除命令：
     ```bash
     unalias claude-lm 2>/dev/null
     unalias clm 2>/dev/null
     ```
  2. 检查 `~/.zshrc` 中是否仍有旧的 `alias claude-lm=...` 定义，若有则删除或注释掉。
  3. 确认 `~/.local/bin` 已在 PATH 中并生效：
     ```bash
     export PATH="$HOME/.local/bin:$PATH"
     source ~/.zshrc
     ```
  4. 新开一个终端窗口或标签页，直接运行 `clm` 或 `claude-lm` 即可。

### 6.2 报错：未找到 claude 可执行文件
- 执行 `which claude` 检查安装路径，若未安装请执行 `npm install -g @anthropic-ai/claude-code` 或 `curl -fsSL https://claude.ai/install.sh | bash`。

### 6.3 连接超时或 Connection Refused
- 检查 LM Studio 的 **Local Server** 是否已启动，并确认监听端口是否为 `1234`。
- 若 LM Studio 自定义了端口（例如 `8000`），可通过环境变量覆盖：`ANTHROPIC_BASE_URL="http://127.0.0.1:8000/v1" clm`。

### 6.4 模型推理显存不足或频繁换出
- 建议在 LM Studio 中只常驻加载 1 个主力模型，并启动时添加 `--single <model_name>` 参数统一所有角色。

---

## 7. 高质量 Skill 与插件推荐指南

针对全栈工程师与个人投资者的特定工作流，本项目整理了权威来源、第一性原理推导及一键安装命令集：

- 完整指南文档：[Claude Code 高质量 Skill 选型指南（全栈工程师与个人投资者）](./RECOMMENDED_SKILLS.md)
- 包含工具：`document-skills` (Excel/PDF/Word/PPT)、`mattpocock-skills` (投资论点严苛质询与领域建模)、`ui-ux-pro-max` (顶级前端设计规范)、`superpowers` (工程方法论全家桶)、`mcp-builder` (行情与数据接入)、`planning-with-files` (持久化长期规划)。

---

## 8. 开源即插即用 AI 专家角色库：agency-agents-zh

为了让 Claude Code 及本地大模型在软件工程与复杂专业场景中发挥出最大效能，推荐配合开源社区的高质量专家角色库：[**agency-agents-zh**](https://github.com/jnMetaCode/agency-agents-zh)（基于上游 [Agency Enterprise / agency-agents](https://github.com/agency-enterprise/agency-agents) 进行深度中文本土化与生态扩展）。

### 8.1 什么是 agency-agents-zh？

`agency-agents-zh` 是专为 AI 编码助手及自主 Agent 打造的**即插即用专家角色全家桶**：
- **277 个结构化专家角色**：涵盖 20 个企业职能与专业细分领域，不仅包含工程研发、DevOps、架构设计，还延伸至产品、设计、法务、财务、营销、游戏开发、安全审计等全流程。
- **64 个中国生态原创角色**：针对国内平台与业务场景深度定制，支持小红书/抖音/微信/B站运营、飞书/钉钉企业应用集成、工业 Qt 控制软件开发、跨境出海合规等。
- **四维结构化规范（超越普通 Prompt）**：每个 Agent 角色内置严谨的工业级规范，而非脆弱的简单人设提示：
  - **思考模式 (Thinking Patterns)**：引导大模型以特定领域第一性原理和严谨推演逻辑思考。
  - **标准作业程序 (SOP)**：分步骤指导任务推进，确保工程与交付逻辑闭环。
  - **操作准则 (Operating Rules)**：定义架构防劣化规范、代码边界约束、编码风格与安全红线。
  - **交付物标准 (Deliverables)**：明确输出格式、代码骨架、测试覆盖标准或审查清单。

### 8.2 与 Claude Code 的原生集成（千万不要全部安装！）

> ⚠️ **重要原则：强烈反对全部安装（277 个角色全装是大忌）！**
> 1. **上下文污染与规则稀释 (Rule Dilution)**：如果全局注入几百个角色，会导致模型在推理时注意力分散，系统提示词冲突或被稀释，反而降低代码生成质量。
> 2. **本地大模型 (LM Studio / clm) 显存与窗口限制**：本地模型有效上下文较紧凑（通常在 8k~32k），加载过多角色会占用有效上下文，导致推理变慢甚至上下文截断。
> 3. **工程最佳实践：项目级按需引入 (推荐) 或 挑选 3~5 个高频核心角色**。

#### 准备工作：先浅克隆角色库到本地（秒级完成）

```bash
# 浅克隆角色库（仅拉取最新深度，速度极快且体积轻量）
git clone --depth=1 https://github.com/jnMetaCode/agency-agents-zh.git
```

#### 方案 A：项目级按需引入（官方与工业界最推荐）

在你的业务项目根目录下，直接通过相对路径把所需的 2~3 个角色拷贝进来即可。用完即走，项目隔离：

```bash
# 进入你当前的业务项目目录
cd your-project

# 创建该项目的专属 agent 目录
mkdir -p .claude/agents

# 直接使用相对路径按需复制所需专家（例如与 agency-agents-zh 同级时）：
cp ../agency-agents-zh/engineering/engineering-software-architect.md .claude/agents/
cp ../agency-agents-zh/engineering/engineering-frontend-developer.md .claude/agents/
cp ../agency-agents-zh/security/security-appsec-engineer.md .claude/agents/

# 提示：若是在临时目录下提取完角色，可随时清理克隆仓库保持清爽：rm -rf agency-agents-zh
```

#### 方案 B：全局轻量精简组合（直接进入目录，用纯相对路径分发）

直接进入克隆后的 `agency-agents-zh` 目录，通过最简洁的相对路径分发 6 张高频王牌角色至 `~/.claude/agents/`：

```bash
cd agency-agents-zh
mkdir -p ~/.claude/agents

# 直接使用简洁的相对路径一键复制黄金组合：
# 1. 系统架构师 (顶层把关与系统设计)
cp engineering/engineering-software-architect.md ~/.claude/agents/
# 2. 代码审查专家 (质量把控与重构)
cp engineering/engineering-code-reviewer.md ~/.claude/agents/
# 3. 前端开发专家 (业务功能开发)
cp engineering/engineering-frontend-developer.md ~/.claude/agents/
# 4. 后端架构师 (高并发与数据流设计)
cp engineering/engineering-backend-architect.md ~/.claude/agents/
# 5. 应用安全工程师 (漏洞挖掘与合规)
cp security/security-appsec-engineer.md ~/.claude/agents/
# 6. DevOps 自动化专家 (CI/CD 流水线)
cp engineering/engineering-devops-automator.md ~/.claude/agents/
```

#### 方案 C：临时引用（免安装，零污染）

平时完全不需要向配置目录复制任何文件，直接在 Claude Code 提问时指定相对路径让它读取对应的 `.md` 角色定义文件即可：
```text
> 请参考 ./agency-agents-zh/engineering/engineering-software-architect.md 中的角色规范与 SOP，帮我审查当前工程架构。
```

---

#### 附：全量安装脚本说明（仅建议作为本地角色离线资料库查阅，不推荐日常挂载）

```bash
cd agency-agents-zh
# 仅供离线检索参考，不要轻易将全量执行脚本挂载到生产环境
# ./scripts/install.sh --tool claude-code
```

### 8.3 角色目录精选索引

> 注：`agency-agents-zh` 文件命名规范为 `<部门目录>/<部门>-<角色名>.md`（部分多层级子目录如 `game-development/<引擎>/<角色>.md`）。

| 职能大类 | 仓库目录 | 核心代表文件路径（精确到文件名） | 适用典型场景 |
| :--- | :--- | :--- | :--- |
| **工程研发** | `engineering/` | `engineering-software-architect.md`<br>`engineering-frontend-developer.md`<br>`engineering-backend-architect.md`<br>`engineering-devops-automator.md`<br>`engineering-database-optimizer.md`<br>`engineering-code-reviewer.md` | 复杂系统架构、全栈重构、CI/CD 自动化流水线、SQL 慢查询调优、代码审查 |
| **安全合规** | `security/` | `security-appsec-engineer.md`<br>`security-cloud-security-architect.md`<br>`security-penetration-tester.md` | 代码安全审计、OWASP 漏洞挖掘、威胁建模与权限安全基线检查 |
| **测试质检** | `testing/` | `testing-performance-benchmarker.md`<br>`testing-reality-checker.md` | 压力与性能基准测试、交付可行性与质量验收 |
| **产品与设计** | `product/`<br>`design/` | `product/product-manager.md`<br>`design/design-ui-designer.md`<br>`design/design-ux-architect.md` | 需求 PRD 编写、界面交互设计规范、Design System 落地 |
| **专业垂直领域** | `game-development/`<br>`specialized/` | `game-development/unity/unity-architect.md`<br>`game-development/godot/godot-gameplay-scripter.md`<br>`specialized/specialized-mcp-builder.md` | 游戏引擎系统开发、3D 资产脚本、MCP (Model Context Protocol) 插件构建 |
| **中国生态原创** | 各目录 `*-zh.md` / `original/` | `engineering-dingtalk-integration-developer.md` 等 | 国内平台生态对接、私域与内容矩阵增长、本土化企业协同开发 |

### 8.4 实战调用与激活示例

在 `clm` 或 `claude` 会话中，可直接以自然语言激活角色执行专项任务：

```text
> 激活软件架构师 (engineering-software-architect) 模式：请审查当前仓库的代码结构与接口解耦设计，输出高内聚低耦合的重构方案。
> 激活应用安全工程师 (security-appsec-engineer) 模式：请对当前鉴权中间件与数据流转路径进行全面安全审计，找出潜在越权漏洞。
> 激活前端专家 (engineering-frontend-developer) 模式：帮我根据现有设计系统重构组件，并补充完整的 a11y 无障碍支持与单元测试。
```


