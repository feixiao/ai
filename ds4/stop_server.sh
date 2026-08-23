#!/bin/bash
# ==============================================================================
# ds4-server 停止代理脚本 (指向实际 ds4 仓库)
# ==============================================================================

REAL_DS4_DIR="/Users/frank/wk/github/ds4"

if [ -f "$REAL_DS4_DIR/stop_server.sh" ]; then
    exec "$REAL_DS4_DIR/stop_server.sh" "$@"
else
    echo "❌ 未在 $REAL_DS4_DIR 找到 stop_server.sh"
    exit 1
fi
