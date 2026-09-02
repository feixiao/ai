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
2. 在 LM Studio 中下载所需的模型（如 `qwopus3.6-27b-coder`、`gemma-4-31b-it`、`mlx-qwopus3.5-9b-v3` 等）。
3. 切换至 **Developer** 标签页（本地服务器模式）：
   - 点击 **Start Server** 开启服务。
   - 默认监听端口为 `1234`（访问地址：`http://127.0.0.1:1234`）。
   - 确认已勾选 **Enable CORS**。

---

### 1.3 安装 `clm` / `claude-lm` 到系统命令

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
# 1. 默认推荐模式启动 (Coder 预设: qwopus3.6-27b-coder + gemma-4-31b-it + mlx-qwopus3.5-9b-v3)
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
# 全部角色统一使用 qwopus3.6-27b-coder
clm --single qwopus3.6-27b-coder

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
| **`qwopus3.6-27b-coder`** | 16.1 GB | 27B | **`ANTHROPIC_DEFAULT_SONNET_MODEL`**<br>+ **默认主力模型 (`ANTHROPIC_MODEL`)** | 专为代码生成与重构优化，代码能力最强的主力选择 |
| **`gemma-4-31b-it`** | 18.4 GB | 31B | **`ANTHROPIC_DEFAULT_OPUS_MODEL`** | Dense 强推理指令模型，适合复杂架构设计与全局规划 |
| **`qwen3.8-27b-mlx@8bit`** | 29.5 GB | 27B | **`ANTHROPIC_DEFAULT_OPUS_MODEL`** (可选) | 高精度 8-bit Qwen 模型，数学与逻辑推理能力突出 |
| **`qwen3.8-27b-mlx@4bit`** | 16.1 GB | 27B | **`ANTHROPIC_DEFAULT_SONNET_MODEL`** (可选) | 4-bit 平衡版，显存占用低，适合日常通用对话与开发 |
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

# 2. 全量重定向 Sonnet / Haiku / Opus / 子 Agent 角色
export ANTHROPIC_MODEL="qwopus3.6-27b-coder"
export ANTHROPIC_DEFAULT_OPUS_MODEL="gemma-4-31b-it"
export ANTHROPIC_DEFAULT_SONNET_MODEL="qwopus3.6-27b-coder"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="mlx-qwopus3.5-9b-v3"
export CLAUDE_CODE_SUBAGENT_MODEL="mlx-qwopus3.5-9b-v3"

# 3. 流量与流式超时调优
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

1. **报错：未找到 claude 可执行文件**
   - 执行 `which claude` 检查安装路径，若未安装请执行 `npm install -g @anthropic-ai/claude-code`。
2. **报错：`zsh: no such file or directory: ...`（如旧脚本路径找不到）**
   - 检查当前 Shell 环境中是否存在旧别名拦截：
     ```bash
     type -a claude-lm
     type -a clm
     ```
   - 若输出显示 `aliased to ~/forbuild/.../claude-lmstudio.sh` 等失效路径，请打开 `~/.zshrc`（或 `~/.bashrc`）清理或更新对应的 `alias` 行，然后执行 `source ~/.zshrc` 重新加载。
3. **连接超时或 Connection Refused**
   - 检查 LM Studio 的 **Local Server** 是否已启动，并确认监听端口是否为 `1234`。
   - 若 LM Studio 自定义了端口（例如 `8000`），可通过环境变量覆盖：`ANTHROPIC_BASE_URL="http://127.0.0.1:8000/v1" clm`。
4. **模型推理显存不足或频繁换出**
   - 建议在 LM Studio 中只常驻加载 1 个主力模型，并启动时添加 `--single <model_name>` 参数。
