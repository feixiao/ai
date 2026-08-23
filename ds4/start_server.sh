#!/bin/bash
# ==============================================================================
# ds4-server 启动代理脚本 (指向 forbuild 目录)
# ==============================================================================

FORBUILD_DS4_DIR="/Users/frank/forbuild/ds4"

if [ -f "$FORBUILD_DS4_DIR/start_server.sh" ]; then
    exec "$FORBUILD_DS4_DIR/start_server.sh" "$@"
else
    echo "❌ 未在 $FORBUILD_DS4_DIR 找到 start_server.sh"
    exit 1
fi
