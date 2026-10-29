#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# 2026 音视频多模态大模型实战体系根极速启动入口 (Root Quickstart Launcher)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python3}"

show_help() {
    cat <<EOF
==================================================================
🚀 2026 音视频多模态实战体系极速启动入口 (Mac Studio & Pixel 10)
==================================================================
用法: $(basename "$0") [选项]

选项:
  --demo       (默认) 运行全量 6 阶段音视频多模态实操练习流水线
  --menu       打开交互式终端控制台菜单 (TUI 选项 0~10)
  --test       运行全量 61 项标准单元测试套件 (unittest)
  --check      探测宿主机 Apple Silicon 芯片、UMA 内存及 Pixel 10 ADB 状态
  --report     打印多模态技术雷达与基准全景看板
  --server     在前台启动本地 OpenAI 兼容 HTTP 网关服务 (端口 8000)
  --clean      清理临时音频与数据测试缓存
  --download-models 打印各大官方渠道模型权重极速拉取指令
  --help       显示本帮助文档
==================================================================
EOF
}

case "${1:-}" in
    --menu|-m)
        exec "$PYTHON_BIN" "${SCRIPT_DIR}/examples/multimodal_practice/interactive_menu.py"
        ;;
    --test|-t)
        exec "$PYTHON_BIN" "${SCRIPT_DIR}/tools/multimodal_tools/test_multimodal_suite.py"
        ;;
    --check|-c)
        exec bash "${SCRIPT_DIR}/examples/multimodal_practice/setup_environment.sh" --check
        ;;
    --report|-r)
        exec "$PYTHON_BIN" "${SCRIPT_DIR}/tools/multimodal_tools/benchmark_summary.py"
        ;;
    --server|-s)
        exec "$PYTHON_BIN" "${SCRIPT_DIR}/examples/multimodal_practice/05_local_multimodal_server.py" --port 8000 --host 0.0.0.0
        ;;
    --clean)
        rm -rf /tmp/test_multimodal_audio.wav /tmp/multimodal_lora_data
        echo "🧹 临时缓存已清理完毕。"
        ;;
    --download-models)
        exec bash "${SCRIPT_DIR}/examples/multimodal_practice/setup_environment.sh" --download-models
        ;;
    --help|-h)
        show_help
        exit 0
        ;;
    --demo|"")
        exec bash "${SCRIPT_DIR}/examples/multimodal_practice/run_all_labs.sh"
        ;;
    *)
        echo "未知选项: $1"
        show_help
        exit 1
        ;;
esac
