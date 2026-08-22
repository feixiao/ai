#!/bin/bash
# ==============================================================================
# ds4-server 一键启动脚本 (针对 Mac Studio M4 Max 128GB 优化)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 默认配置
DS4_BIN="$SCRIPT_DIR/ds4-server"
MODEL_PATH="${DS4_MODEL:-$SCRIPT_DIR/ds4flash.gguf}"
HOST="${DS4_HOST:-127.0.0.1}"
PORT="${DS4_PORT:-8400}"
CTX="${DS4_CTX:-100000}"
KV_DIR="${DS4_KV_DIR:-$HOME/.ds4/kvcache}"
KV_SPACE="${DS4_KV_SPACE:-16384}"
LOG_FILE="$SCRIPT_DIR/server.log"
PID_FILE="$SCRIPT_DIR/server.pid"

# 检查二进制是否存在
if [ ! -f "$DS4_BIN" ]; then
    echo "❌ 未找到 ds4-server 可执行文件，正在尝试自动编译..."
    make -C "$SCRIPT_DIR"
    if [ ! -f "$DS4_BIN" ]; then
        echo "❌ 编译失败，请先在 $SCRIPT_DIR 执行 make 编译"
        exit 1
    fi
fi

# 检查模型是否存在
if [ ! -f "$MODEL_PATH" ]; then
    echo "⚠️ 未检测到默认模型：$MODEL_PATH"
    echo "👉 请先执行 ./download_model.sh ds4f-q2 下载模型"
    exit 1
fi

mkdir -p "$KV_DIR"

# 检查是否已在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️ ds4-server 已经在运行中 (PID: $OLD_PID)，访问地址: http://$HOST:$PORT"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

CMD=(
    "$DS4_BIN"
    "-m" "$MODEL_PATH"
    "--host" "$HOST"
    "--port" "$PORT"
    "--ctx" "$CTX"
    "--kv-disk-dir" "$KV_DIR"
    "--kv-disk-space-mb" "$KV_SPACE"
    "--cors"
)

# 判断是否后台运行 (传参数 -d 或 --bg)
if [[ "$1" == "-d" || "$1" == "--bg" || "$1" == "daemon" ]]; then
    echo "🚀 正在后台启动 ds4-server..."
    nohup "${CMD[@]}" > "$LOG_FILE" 2>&1 &
    PID=$!
    echo "$PID" > "$PID_FILE"
    echo "✅ 服务已在后台启动 (PID: $PID)"
    echo "🌐 API 接口地址: http://$HOST:$PORT"
    echo "📄 日志文件: $LOG_FILE (可使用 tail -f $LOG_FILE 查看)"
    echo "🛑 停止服务请执行: ./stop_server.sh"
else
    echo "🚀 正在前台启动 ds4-server (按 Ctrl+C 退出)..."
    echo "🌐 API 接口地址: http://$HOST:$PORT"
    echo "💡 提示: 传入 -d 参数可在后台静默运行，如: ./start_server.sh -d"
    echo "---------------------------------------------------------"
    exec "${CMD[@]}"
fi
