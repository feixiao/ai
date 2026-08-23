#!/bin/bash
# ==============================================================================
# ds4-server 启动代理脚本 (指向实际 ds4 仓库)
# ==============================================================================

REAL_DS4_DIR="/Users/frank/wk/github/ds4"

if [ -f "$REAL_DS4_DIR/start_server.sh" ]; then
    exec "$REAL_DS4_DIR/start_server.sh" "$@"
else
    echo "❌ 未在 $REAL_DS4_DIR 找到 start_server.sh"
    exit 1
fi
