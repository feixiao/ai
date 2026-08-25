#!/bin/sh
# ==============================================================================
# Claude Code 接入本地 ds4-server 启动包装脚本
# ==============================================================================

# 1. 独立配置目录，避免与官方 Claude Code 登录凭证（Keychain/OAuth）冲突
export CLAUDE_CONFIG_DIR="$HOME/.ds4/claude_config"
mkdir -p "$CLAUDE_CONFIG_DIR"

# 自动初始化 ds4 独立的 Claude Code 配置（跳过初次引导与 API Key 确认弹窗）
if [ ! -f "$CLAUDE_CONFIG_DIR/.claude.json" ]; then
    cat << 'EOF' > "$CLAUDE_CONFIG_DIR/.claude.json"
{
  "hasCompletedOnboarding": true,
  "bypassPermissionsModeAccepted": true,
  "customApiKeyResponses": {
    "approved": ["dsv4-local", "sk-ant-api03-local", "local"],
    "rejected": []
  }
}
EOF
fi

# 2. 避免代理干扰本地 127.0.0.1 通信
export NO_PROXY="127.0.0.1,localhost,$NO_PROXY"
export no_proxy="127.0.0.1,localhost,$no_proxy"

# 3. 基础端点与本地鉴权配置
unset ANTHROPIC_AUTH_TOKEN
export ANTHROPIC_API_KEY="dsv4-local"
export ANTHROPIC_BASE_URL="http://127.0.0.1:8400"
export ANTHROPIC_MODEL="deepseek-v4-flash"

# 自定义模型名称与展示信息
export ANTHROPIC_CUSTOM_MODEL_OPTION="deepseek-v4-flash"
export ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="DeepSeek V4 Flash local ds4"
export ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION="ds4.c local GGUF"

# 全量将 Sonnet / Haiku / Opus / 子 Agent 路由重定向到本地模型
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-flash"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-flash"
export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"

# 流量与流式超时及未知模型窗口优化
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK=1
export CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1
export CLAUDE_STREAM_IDLE_TIMEOUT_MS=600000

# 4. 自动增量同步会话与共享配置（使官方 Claude 与 ds4 会话互通、支持无缝 --resume）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync_sessions.sh"
if [ ! -f "$SYNC_SCRIPT" ]; then
    SYNC_SCRIPT="$HOME/forbuild/ds4/sync_sessions.sh"
fi

if [ "${CLAUDE_DS4_NO_SYNC:-0}" != "1" ] && [ -f "$SYNC_SCRIPT" ] && [ -x "$SYNC_SCRIPT" ]; then
    # 启动前同步官方会话到 ds4
    "$SYNC_SCRIPT" -b >/dev/null 2>&1 || true
    # 退出时同步 ds4 会话回官方目录
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

"$CLAUDE_BIN" "$@"
