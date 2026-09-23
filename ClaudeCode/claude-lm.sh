#!/bin/bash
# ==============================================================================
# Claude Code 接入本地 LM Studio 启动包装脚本
# ==============================================================================
#
# 本地模型列表与角色分配（基于 Apple Silicon / Mac Studio 本地已下载模型）：
# ------------------------------------------------------------------------------
# 1. qwen3.8-27b-splash     (17.4 GB, 27B ) -> 专用编码主力 / Sonnet / 默认主力
# 2. qwen3.6-35b-a3b-splash (21.0 GB, 35B ) -> MoE 高速推理 / Haiku / Subagent / 架构推理
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

if [ ! -f "$CLAUDE_CONFIG_DIR/settings.json" ]; then
    cat << 'EOF' > "$CLAUDE_CONFIG_DIR/settings.json"
{
  "model": "sonnet",
  "autoCompactEnabled": true,
  "autoCompactWindow": 100000,
  "skipDangerousModePermissionPrompt": true
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
#   - coder / dual (默认推荐: 主力编码=qwen3.8-27b-splash, 快速Agent/架构推理=qwen3.6-35b-a3b-splash)
#   - 27b          (全量使用 qwen3.8-27b-splash: 专用代码主力)
#   - 35b          (全量使用 qwen3.6-35b-a3b-splash: 35B MoE 极速吞吐)
#   - single       (统一单模型模式: 将 Sonnet/Haiku/Opus/Subagent 全部重定向至单一模型)
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
        --27b)
            PRESET="27b"
            shift
            ;;
        --35b)
            PRESET="35b"
            shift
            ;;
        --dual|--hybrid)
            PRESET="dual"
            shift
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
        27b|qwen27b|qwen3.8)
            DEFAULT_MODEL="qwen3.8-27b-splash"
            OPUS_MODEL="qwen3.8-27b-splash"
            FABLE_MODEL="qwen3.8-27b-splash"
            SONNET_MODEL="qwen3.8-27b-splash"
            HAIKU_MODEL="qwen3.8-27b-splash"
            SUBAGENT_MODEL="qwen3.8-27b-splash"
            ;;
        35b|qwen35b|qwen3.6)
            DEFAULT_MODEL="qwen3.6-35b-a3b-splash"
            OPUS_MODEL="qwen3.6-35b-a3b-splash"
            FABLE_MODEL="qwen3.6-35b-a3b-splash"
            SONNET_MODEL="qwen3.6-35b-a3b-splash"
            HAIKU_MODEL="qwen3.6-35b-a3b-splash"
            SUBAGENT_MODEL="qwen3.6-35b-a3b-splash"
            ;;
        coder|dual|hybrid|*)
            # 默认推荐组合：27B 编程主力 (Sonnet) + 35B MoE 架构推理 (Opus) 与极速 Agent (Haiku)
            DEFAULT_MODEL="qwen3.8-27b-splash"
            OPUS_MODEL="qwen3.6-35b-a3b-splash"
            FABLE_MODEL="qwen3.6-35b-a3b-splash"
            SONNET_MODEL="qwen3.8-27b-splash"
            HAIKU_MODEL="qwen3.6-35b-a3b-splash"
            SUBAGENT_MODEL="qwen3.6-35b-a3b-splash"
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

# 流量与流式超时优化
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK=1
export CLAUDE_STREAM_IDLE_TIMEOUT_MS=3000000
export API_TIMEOUT_MS=3000000

# 上下文控制在 100k 以内并自动压缩配置
# 1. 设定最大上下文窗口与自动压缩触发窗口为 100k
export CLAUDE_CODE_MAX_CONTEXT_TOKENS="${CLAUDE_CODE_MAX_CONTEXT_TOKENS:-100000}"
export CLAUDE_CODE_AUTO_COMPACT_WINDOW="${CLAUDE_CODE_AUTO_COMPACT_WINDOW:-100000}"

# 2. 启用未知模型的窗口强制约束（确保本地模型在接近 100k 时主动触发自动压缩，而不是被动等待 API 报错）
unset CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT

# 3. 确保压缩功能全量启用（防被外部环境意外禁用）
unset DISABLE_COMPACT
unset DISABLE_AUTO_COMPACT

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
CLAUDE_BIN="${CLAUDE_BIN:-$HOME/.local/bin/claude}"
if [ ! -f "$CLAUDE_BIN" ]; then
    CLAUDE_BIN="$(which claude 2>/dev/null)"
fi

if [ -z "$CLAUDE_BIN" ] || [ ! -x "$CLAUDE_BIN" ]; then
    echo "❌ 未找到 claude 可执行文件，请确认 Claude Code 已正确安装在 ~/.local/bin/claude"
    exit 1
fi

"$CLAUDE_BIN" "${PASSTHROUGH_ARGS[@]}"