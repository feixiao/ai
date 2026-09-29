#!/bin/bash
# ==============================================================================
# h3 视频生成代理脚本 (指向 forbuild 目录)
# ==============================================================================

FORBUILD_H3_DIR="/Users/frank/forbuild/h3"

if [ -f "$FORBUILD_H3_DIR/generate.sh" ]; then
    exec "$FORBUILD_H3_DIR/generate.sh" "$@"
else
    echo "❌ 未在 $FORBUILD_H3_DIR 找到 generate.sh"
    exit 1
fi
