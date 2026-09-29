#!/bin/bash
# ==============================================================================
# h3 硬件自检与算子测试代理脚本 (指向 forbuild 目录)
# ==============================================================================

FORBUILD_H3_DIR="/Users/frank/forbuild/h3"

if [ -f "$FORBUILD_H3_DIR/run_tests.sh" ]; then
    exec "$FORBUILD_H3_DIR/run_tests.sh" "$@"
else
    echo "❌ 未在 $FORBUILD_H3_DIR 找到 run_tests.sh"
    exit 1
fi
