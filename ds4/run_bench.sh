#!/bin/bash
# ==============================================================================
# ds4-bench 评测代理脚本 (指向 forbuild 目录)
# ==============================================================================

FORBUILD_DS4_DIR="/Users/frank/forbuild/ds4"

if [ -f "$FORBUILD_DS4_DIR/run_bench.sh" ]; then
    exec "$FORBUILD_DS4_DIR/run_bench.sh" "$@"
else
    echo "❌ 未在 $FORBUILD_DS4_DIR 找到 run_bench.sh"
    exit 1
fi
