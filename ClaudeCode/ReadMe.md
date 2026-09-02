## Use your LM Studio Models in Claude Code

### 🚀 一键启动包装脚本 (`claude-lmstudio.sh`)

项目提供了参考 `claude-ds4` 架构的免配置、防 Keychain 冲突、自动配置隔离与双向会话同步的启动脚本：

```bash
# 1. 默认推荐模式启动 (Coder 预设: qwopus3.6-27b-coder + gemma-4-31b-it + mlx-qwopus3.5-9b-v3)
claude-lmstudio
# 或简短命令
claude-lm
clm

# 2. 支持通过 --preset 一键切换预设策略
claude-lmstudio --preset coder      # 默认：编程主力 + 强架构推理 + 极速轻量 Agent
claude-lmstudio --preset reasoning  # 深度推理：gemma-4-31b-it 深度架构与规划
claude-lmstudio --preset qwen       # Qwen全家桶：qwen3.8-27b-mlx@4bit / 8bit
claude-lmstudio --preset gemma      # Gemma全家桶：gemma-4-26b-a4b-it / 31b-it

# 3. 统一单模型模式（当 LM Studio 仅加载单一模型时，避免多模型显存切换换页）
claude-lmstudio --single qwopus3.6-27b-coder
claude-lmstudio --single gemma-4-31b-it

# 4. 透传任意官方 Claude Code 命令与参数
claude-lmstudio --resume
claude-lmstudio --resume <session-id>
claude-lmstudio -p "编写一个基于 FastAPI 的流式聊天后端"
```

---

### 📦 本地模型库与角色分工推荐

针对本地已下载的 7 款核心模型：

| 模型名称 | 显存/大小 | 参数量 | 推荐路由角色 | 特点与适用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **`qwopus3.6-27b-coder`** | 16.1 GB | 27B | **`ANTHROPIC_DEFAULT_SONNET_MODEL`** / **主力默认** | 专为代码生成与重构优化，代码能力最强的主力选择 |
| **`gemma-4-31b-it`** | 18.4 GB | 31B | **`ANTHROPIC_DEFAULT_OPUS_MODEL`** | Dense 强推理指令模型，适合复杂架构设计与全局规划 |
| **`qwen3.8-27b-mlx@8bit`** | 29.5 GB | 27B | **`ANTHROPIC_DEFAULT_OPUS_MODEL`** (可选) | 高精度 8-bit Qwen 模型，数学与逻辑推理能力突出 |
| **`qwen3.8-27b-mlx@4bit`** | 16.1 GB | 27B | **`ANTHROPIC_DEFAULT_SONNET_MODEL`** (可选) | 4-bit 平衡版，显存占用低，适合日常通用对话与开发 |
| **`gemma-4-26b-a4b-it`** | 15.6 GB | 26B | **`ANTHROPIC_DEFAULT_SONNET_MODEL`** / **Haiku** | MoE 高吞吐架构，在保持智能的同时生成速度极快 |
| **`mlx-qwopus3.5-9b-v3`** | 9.5 GB | 9B | **`ANTHROPIC_DEFAULT_HAIKU_MODEL`** / **Subagent** | MLX 优化版 9B，极低延迟，适合子代理与轻量辅助任务 |
| **`qwopus3.5-9b-v3`** | 6.0 GB | 9B | **`ANTHROPIC_DEFAULT_HAIKU_MODEL`** / **Subagent** | 极致轻量 6GB 显存，极快首字响应 |

---

### ⚙️ 环境变量路由映射

脚本内置全量路由重定向环境变量（对应 `ds4` 启动脚本同款规范）：

```bash
# LM Studio 本地服务接入点（默认 1234 端口）
export ANTHROPIC_BASE_URL="http://127.0.0.1:1234/v1"
export ANTHROPIC_API_KEY="lmstudio"

# 全量将 Sonnet / Haiku / Opus / 子 Agent 路由重定向到本地模型
export ANTHROPIC_MODEL="qwopus3.6-27b-coder"
export ANTHROPIC_DEFAULT_OPUS_MODEL="gemma-4-31b-it"
export ANTHROPIC_DEFAULT_SONNET_MODEL="qwopus3.6-27b-coder"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="mlx-qwopus3.5-9b-v3"
export CLAUDE_CODE_SUBAGENT_MODEL="mlx-qwopus3.5-9b-v3"

# 流量与流式超时调优
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK=1
export CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1
export CLAUDE_STREAM_IDLE_TIMEOUT_MS=600000
export API_TIMEOUT_MS=3000000

# 自动上下文压缩（100k 黄金窗口）
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=100000
```

---

### 🔄 会话双向同步工具 (`sync_sessions.sh`)

解决配置隔离后历史会话无法互通的问题：

```bash
cd ClaudeCode

# 1. 默认将官方 ~/.claude 会话增量同步到 ~/.lmstudio/claude_config
./sync_sessions.sh

# 2. 双向同步（两边保持最新）
./sync_sessions.sh -b

# 3. 指定单个会话 UUID 迁移
./sync_sessions.sh 2ce044f6-9934-4e69-b974-c6881e1764da
```

---

### 📚 参考与扩展

- [LM Studio 官方文档: Use your LM Studio Models in Claude Code](https://lmstudio.ai/blog/claudecode)
- [ds4 (DwarfStar) 本地部署指南](../ds4/README.md)
