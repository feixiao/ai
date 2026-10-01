#!/bin/bash
# ==============================================================================
# h3 模型下载管理代理脚本 (指向 forbuild 目录)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORBUILD_H3_DIR="/Users/frank/forbuild/h3"

if [ -f "$FORBUILD_H3_DIR/download_model.sh" ]; then
    exec "$FORBUILD_H3_DIR/download_model.sh" "$@"
elif [ -f "$SCRIPT_DIR/download_h3.py" ]; then
    exec python3 "$SCRIPT_DIR/download_h3.py" "$@"
else
    echo "❌ 未在 $FORBUILD_H3_DIR 找到 download_model.sh 且当前目录无 download_h3.py"
    exit 1
fi
