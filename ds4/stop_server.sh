#!/bin/bash
# ==============================================================================
# ds4-server 一键停止脚本
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/server.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "🛑 正在停止 ds4-server (PID: $PID)..."
        kill "$PID"
        sleep 1
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -9 "$PID"
        fi
        echo "✅ ds4-server 已成功停止"
    else
        echo "⚠️ PID 为 $PID 的进程已不存在"
    fi
    rm -f "$PID_FILE"
else
    # 尝试按进程名匹配查找并关闭
    PIDS=$(pgrep -f "ds4-server")
    if [ -n "$PIDS" ]; then
        echo "🛑 正在清理 ds4-server 进程: $PIDS"
        pkill -f "ds4-server"
        echo "✅ ds4-server 已停止"
    else
        echo "ℹ️ 没有发现运行中的 ds4-server"
    fi
fi
