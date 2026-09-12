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

## 8. 高质量 Agent 专家角色库推荐指南

针对复杂工程研发、架构设计、安全审计及商业投资分析，本项目基于开源社区的高质量专家角色库 [**agency-agents-zh**](https://github.com/jnMetaCode/agency-agents-zh)（包含 277 个结构化专家角色与 64 个中国生态原创角色），整理了严谨的选型与实战指南：

- 完整指南文档：[Claude Code 高质量 Agent 专家角色选型与实战指南（全栈工程师与个人投资者篇）](./RECOMMENDED_AGENTS.md)
- 核心内容概览：
  - **角色能力第一性原理**：全栈工程师 vs 个人投资者双重工作流的核心能力与思维模型推导。
  - **反模式警示**：为什么严禁全量安装（防规则稀释 Rule Dilution、本地大模型显存防爆）。
  - **高频黄金组合**：系统架构师、代码审查员、全栈/前端工程师、后端架构师、应用安全工程师、DevOps 自动化专家精选。
  - **无污染工作流**：支持项目级按需引入、全局轻量组合、免安装动态临时引用三种纯相对路径姿势。
  - **双场景实战范式**：全栈开发从零构建 SaaS 与个人投资者财报穿透/合规尽调端到端调用提示词。

---

## 9. 反向代理与第三方模型 Token 防暴增治理指南

当通过反向代理网关（如 One-API / New-API / 自定义代理）接入 **Gemini**、**DeepSeek** 或第三方中转 API 时，若发现 Token 消耗极快（仅 5~10 轮交互就消耗数十万甚至上百万 Tokens），其根本原因是 **Anthropic 原生 Prompt Caching（提示词缓存）在反代层失效**。

### 9.1 根因深度剖析（第一性原理）

1. **System Prompt 与元数据常驻膨胀**：
   Claude Code 在每次发起请求时，都会将所有已启用的 **Skills 描述、Agent 角色元数据、Tools 声明、`CLAUDE.md` 及记忆** 全部拼装并注入到 System Prompt 中。一旦全局安装了多个大型插件包，单次请求的初始前缀即高达 **30,000 ~ 60,000+ Tokens**。
2. **反向代理导致 Prompt Caching 完全失效**：
   - **官方原生机制**：支持 Ephemeral Cache。对于前置固定的 System Prompt 和 Skills，后续轮次仅对增量部分计费（缓存命中率可达 90% 以上）。
   - **反向代理现状**：大多数中转网关无法透传或适配 Anthropic 的 `cache_control` 断点机制。Claude Code 每执行一步工具调用（如读取一个文件、执行一条 Bash 命令），反代都会将 **“全量 System Prompt + 所有已启用技能描述 + 全部历史记录”** 当作全新输入重新发给后端模型并全额计费，导致多轮调用中 Token 消耗呈倍数级爆炸。

---

### 9.2 止血与降本最佳实践

#### ① 技能插件按需启停（断舍离）
严禁全局常驻开启大量未使用的插件包，根据当前工作流按需精简：

```bash
# 1. 查看当前所有已安装插件及状态
claude plugin list

# 2. 临时禁用当前任务无需使用的大型插件包（例如专注编码时禁用合规与金融包）
claude plugin disable compliance-os@claude-skills
claude plugin disable engineering-advanced-skills@claude-skills
claude plugin disable finance-skills@claude-skills

# 3. 彻底卸载长期不用的冗余插件
claude plugin uninstall <plugin_name>
```

#### ② Agent 专家角色“动态按需加载”（杜绝常驻注册）
- **反模式**：严禁将几十个角色 `.md` 文件全部丢入 `~/.claude/agents/` 或 `.claude/agents/`（这会导致每次交互都携带巨大的角色列表上下文）。
- **推荐姿势（免安装动态引用）**：将角色库（如 `agency-agents-zh`）保留在本地，仅在需要时通过单次 Prompt 动态读取：
  ```text
  请阅读并遵循 agency-agents-zh/finance/finance-financial-analyst.md 中的规范与流程，帮我分析该公司最新的 10-K 财报。
  ```
  该方式日常会话 **0 Token 常驻开销**，仅在触发时精准消耗单次 Token。

#### ③ 严格控制上下文生命周期（防滚雪球）
- **主动压缩长会话**：多轮排错或复杂任务超过 10~15 轮交互后，输入 `/compact` 压缩上下文。
- **任务切换及时清空**：完成一个独立的开发或分析任务后，务必输入 `/clear` 开启全新会话，阻断历史工具执行日志与中间产物的上下文滚雪球效应。




