#!/bin/bash
# ==============================================================================
# Claude Code 接入本地 LM Studio 启动包装脚本
# ==============================================================================
#
# 本地模型列表与角色分配（基于 Apple Silicon / Mac Studio 本地已下载模型）：
# ------------------------------------------------------------------------------
# 1. qwopus3.5-9b-v3       ( 6.0 GB, 9B  ) -> 极轻量快速 / Haiku / Subagent
# 2. mlx-qwopus3.5-9b-v3   ( 9.5 GB, 9B  ) -> MLX 快速推理 / Haiku / Subagent
# 3. qwen3.8-27b-mlx@4bit  (16.1 GB, 27B ) -> 专用编码主力 / Sonnet / 默认主力
# 4. qwen3.8-27b-mlx@8bit  (29.5 GB, 27B ) -> Qwen 27B 高精度版 / Opus
# 5. gemma-4-26b-a4b-it    (15.6 GB, 26B ) -> Gemma MoE 高吞吐 / Sonnet / Haiku
# 6. gemma-4-31b-it        (18.4 GB, 31B ) -> Gemma 31B Dense 强推理 / Opus / Fable
# ==============================================================================

# 1. 独立配置目录，避免与官方 Claude Code 登录凭证（Keychain/OAuth）冲突
export CLAUDE_CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.lmstudio/claude_config}"
mkdir -p "$CLAUDE_CONFIG_DIR"

# 自动初始化 LM Studio 独立的 Claude Code 配置（跳过初次引导与 API Key 确认弹窗）
if [ ! -f "$CLAUDE_CONFIG_DIR/.claude.json" ]; then
    cat << 'EOF' > "$CLAUDE_CONFIG_DIR/.claude.json"
{
  "hasCompletedOnboarding": true,
  "bypassPermissionsModeAccepted": true,
  "customApiKeyResponses": {
    "approved": ["dummy-key", "lmstudio", "sk-ant-api03-local", "local"],
    "rejected": []
  }
}
EOF
fi

# 2. 避免代理干扰本地 127.0.0.1 通信
export NO_PROXY="127.0.0.1,localhost,$NO_PROXY"
export no_proxy="127.0.0.1,localhost,$no_proxy"

# 3. 基础端点与本地鉴权配置
# LM Studio 默认 API 端口通常为 1234（也可配置为 8000）
unset ANTHROPIC_AUTH_TOKEN
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-lmstudio}"
export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-http://127.0.0.1:1234}"

# ==============================================================================
# 预设模型策略切换（可通过环境变量 PRESET=xxx 或命令行参数灵活切换）
# 可选 PRESET:
#   - coder     (默认推荐: 主力编码=qwen3.8-27b-mlx@4bit, 架构推理=gemma-4-31b-it, 轻量Agent=mlx-qwopus3.5-9b-v3)
#   - reasoning (深度推理: 架构/主力=gemma-4-31b-it, 代码=qwen3.8-27b-mlx@4bit)
#   - qwen      (Qwen全家桶: Sonnet=qwen3.8-27b-mlx@4bit, Opus=qwen3.8-27b-mlx@8bit, Haiku=qwopus3.5-9b-v3)
#   - gemma     (Gemma全家桶: Sonnet=gemma-4-26b-a4b-it, Opus=gemma-4-31b-it, Haiku=gemma-4-26b-a4b-it)
#   - single    (统一单模型模式: 将 Sonnet/Haiku/Opus/Subagent 全部重定向至单一模型，避免显存反复切换)
# ==============================================================================
PRESET="${PRESET:-coder}"
LM_SINGLE_MODEL="${LM_SINGLE_MODEL:-}"

# 提取自定义参数，剩余参数透传给 claude 命令
PASSTHROUGH_ARGS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --preset)
            PRESET="$2"
            shift 2
            ;;
        --single|--lm-model)
            LM_SINGLE_MODEL="$2"
            shift 2
            ;;
        *)
            PASSTHROUGH_ARGS+=("$1")
            shift
            ;;
    esac
done

if [ -n "$LM_SINGLE_MODEL" ]; then
    # 单模型统一模式：当 LM Studio 本地仅加载单个模型时使用
    DEFAULT_MODEL="$LM_SINGLE_MODEL"
    OPUS_MODEL="$LM_SINGLE_MODEL"
    FABLE_MODEL="$LM_SINGLE_MODEL"
    SONNET_MODEL="$LM_SINGLE_MODEL"
    HAIKU_MODEL="$LM_SINGLE_MODEL"
    SUBAGENT_MODEL="$LM_SINGLE_MODEL"
else
    case "$PRESET" in
        reasoning)
            DEFAULT_MODEL="gemma-4-31b-it"
            OPUS_MODEL="gemma-4-31b-it"
            FABLE_MODEL="gemma-4-31b-it"
            SONNET_MODEL="qwen3.8-27b-mlx@4bit"
            HAIKU_MODEL="mlx-qwopus3.5-9b-v3"
            SUBAGENT_MODEL="mlx-qwopus3.5-9b-v3"
            ;;
        qwen)
            DEFAULT_MODEL="qwen3.8-27b-mlx@4bit"
            OPUS_MODEL="qwen3.8-27b-mlx@8bit"
            FABLE_MODEL="qwen3.8-27b-mlx@8bit"
            SONNET_MODEL="qwen3.8-27b-mlx@4bit"
            HAIKU_MODEL="qwopus3.5-9b-v3"
            SUBAGENT_MODEL="qwopus3.5-9b-v3"
            ;;
        gemma)
            DEFAULT_MODEL="gemma-4-26b-a4b-it"
            OPUS_MODEL="gemma-4-31b-it"
            FABLE_MODEL="gemma-4-31b-it"
            SONNET_MODEL="gemma-4-26b-a4b-it"
            HAIKU_MODEL="gemma-4-26b-a4b-it"
            SUBAGENT_MODEL="gemma-4-26b-a4b-it"
            ;;
        coder|*)
            # 默认推荐 Coder 组合：27B 编程主力 + 31B 架构推理 + 9B 极速 Agent
            DEFAULT_MODEL="qwen3.8-27b-mlx@4bit"
            OPUS_MODEL="gemma-4-31b-it"
            FABLE_MODEL="gemma-4-31b-it"
            SONNET_MODEL="qwen3.8-27b-mlx@4bit"
            HAIKU_MODEL="mlx-qwopus3.5-9b-v3"
            SUBAGENT_MODEL="mlx-qwopus3.5-9b-v3"
            ;;
    esac
fi

# 导出基础模型与各级路由
export ANTHROPIC_MODEL="$DEFAULT_MODEL"
export ANTHROPIC_DEFAULT_MODEL="$DEFAULT_MODEL"

# 清理冗余自定义模型选项，避免 /model 出现重复项目
unset ANTHROPIC_CUSTOM_MODEL_OPTION
unset ANTHROPIC_CUSTOM_MODEL_OPTION_NAME
unset ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION

# 全量将 Sonnet / Haiku / Opus / Fable / 子 Agent 路由重定向到本地模型并设置展示名称
export ANTHROPIC_DEFAULT_SONNET_MODEL="$SONNET_MODEL"
export ANTHROPIC_DEFAULT_SONNET_MODEL_NAME="$SONNET_MODEL"
export ANTHROPIC_DEFAULT_SONNET_MODEL_DESCRIPTION="Sonnet tier (Primary coding)"

export ANTHROPIC_DEFAULT_OPUS_MODEL="$OPUS_MODEL"
export ANTHROPIC_DEFAULT_OPUS_MODEL_NAME="$OPUS_MODEL"
export ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION="Opus tier (Deep reasoning / Architecture)"

export ANTHROPIC_DEFAULT_FABLE_MODEL="$FABLE_MODEL"
export ANTHROPIC_DEFAULT_FABLE_MODEL_NAME="$FABLE_MODEL"
export ANTHROPIC_DEFAULT_FABLE_MODEL_DESCRIPTION="Fable tier (Deep reasoning)"

export ANTHROPIC_DEFAULT_HAIKU_MODEL="$HAIKU_MODEL"
export ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME="$HAIKU_MODEL"
export ANTHROPIC_DEFAULT_HAIKU_MODEL_DESCRIPTION="Haiku tier (Fast subagents)"

export CLAUDE_CODE_SUBAGENT_MODEL="$SUBAGENT_MODEL"

# 禁用 1M 上下文后缀（避免本地推理引擎因 [1m] 后缀报错）
export CLAUDE_CODE_DISABLE_1M_CONTEXT=1

# 流量与流式超时及未知模型窗口优化
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK=1
export CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1
export CLAUDE_STREAM_IDLE_TIMEOUT_MS=600000
export API_TIMEOUT_MS=3000000

# 上下文压缩与上下文上限配置（适配长上下文对话）
unset DISABLE_COMPACT
export CLAUDE_CODE_MAX_CONTEXT_TOKENS="${CLAUDE_CODE_MAX_CONTEXT_TOKENS:-100000}"

# 4. 自动增量同步会话与共享配置（使官方 Claude 与 LM Studio 会话互通、支持无缝 --resume）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync_sessions.sh"
if [ ! -f "$SYNC_SCRIPT" ]; then
    SYNC_SCRIPT="$HOME/.local/bin/sync_sessions.sh"
fi
if [ ! -f "$SYNC_SCRIPT" ]; then
    SYNC_SCRIPT="$HOME/.lmstudio/sync_sessions.sh"
fi
if [ ! -f "$SYNC_SCRIPT" ]; then
    SYNC_SCRIPT="$HOME/wk/github/ai/ClaudeCode/sync_sessions.sh"
fi

if [ "${CLAUDE_LMSTUDIO_NO_SYNC:-0}" != "1" ] && [ -f "$SYNC_SCRIPT" ] && [ -x "$SYNC_SCRIPT" ]; then
    # 启动前同步官方会话到 LM Studio
    "$SYNC_SCRIPT" -b >/dev/null 2>&1 || true
    # 退出时同步 LM Studio 会话回官方目录
    trap '"$SYNC_SCRIPT" -b >/dev/null 2>&1 || true' EXIT
fi

# 5. 查找实际安装的 claude 二进制路径
CLAUDE_BIN="$HOME/.local/bin/claude"
if [ ! -f "$CLAUDE_BIN" ]; then
    CLAUDE_BIN="$(which claude 2>/dev/null)"
fi

if [ -z "$CLAUDE_BIN" ] || [ ! -x "$CLAUDE_BIN" ]; then
    echo "❌ 未找到 claude 可执行文件，请确认 Claude Code 已正确安装在 ~/.local/bin/claude"
    exit 1
fi

"$CLAUDE_BIN" "${PASSTHROUGH_ARGS[@]}"
