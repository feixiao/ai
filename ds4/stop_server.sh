#!/bin/bash
# ==============================================================================
# ds4-server 停止代理脚本 (指向 forbuild 目录)
# ==============================================================================

FORBUILD_DS4_DIR="/Users/frank/forbuild/ds4"

if [ -f "$FORBUILD_DS4_DIR/stop_server.sh" ]; then
    exec "$FORBUILD_DS4_DIR/stop_server.sh" "$@"
else
    echo "❌ 未在 $FORBUILD_DS4_DIR 找到 stop_server.sh"
    exit 1
fi
