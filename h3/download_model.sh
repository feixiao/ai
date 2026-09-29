#!/bin/bash
# ==============================================================================
# h3 模型下载管理代理脚本 (指向 forbuild 目录)
# ==============================================================================

FORBUILD_H3_DIR="/Users/frank/forbuild/h3"

if [ -f "$FORBUILD_H3_DIR/download_model.sh" ]; then
    exec "$FORBUILD_H3_DIR/download_model.sh" "$@"
else
    echo "❌ 未在 $FORBUILD_H3_DIR 找到 download_model.sh"
    exit 1
fi
