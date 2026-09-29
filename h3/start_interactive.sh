#!/bin/bash
# ==============================================================================
# h3 交互式 REPL 与终端预览代理脚本 (指向 forbuild 目录)
# ==============================================================================

FORBUILD_H3_DIR="/Users/frank/forbuild/h3"

if [ -f "$FORBUILD_H3_DIR/start_interactive.sh" ]; then
    exec "$FORBUILD_H3_DIR/start_interactive.sh" "$@"
else
    echo "❌ 未在 $FORBUILD_H3_DIR 找到 start_interactive.sh"
    exit 1
fi
