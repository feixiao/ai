#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# 一键运行全部音视频多模态实操练习 (Mac Studio / PC / Linux 零依赖通用)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python3}"

if [[ "${1:-}" == "--menu" || "${1:-}" == "-m" ]]; then
    exec "$PYTHON_BIN" "${SCRIPT_DIR}/interactive_menu.py"
fi

echo "=================================================================="
echo "🚀 启动 2026 音视频多模态大模型 4 套端到端实操练习流水线"
echo "=================================================================="

# 1. 硬件环境与就绪探测
OS_NAME="$(uname -s)"
ARCH_NAME="$(uname -m)"
echo -e "\n🔍 [环境探测]"
echo "  - 操作系统: ${OS_NAME} (${ARCH_NAME})"

if [[ "${OS_NAME}" == "Darwin" ]]; then
    CPU_BRAND="$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Apple Silicon")"
    TOTAL_MEM_BYTES="$(sysctl -n hw.memsize 2>/dev/null || echo "0")"
    TOTAL_MEM_GB=$(( TOTAL_MEM_BYTES / 1024 / 1024 / 1024 ))
    echo "  - 芯片型号: ${CPU_BRAND}"
    echo "  - 统一内存 (UMA): ${TOTAL_MEM_GB} GB"
    if [[ "${ARCH_NAME}" == "arm64" ]]; then
        echo "  - 加速硬件: Metal GPU + Apple Neural Engine (ANE) 就绪"
    fi
fi

# 检查可选辅助工具
for tool in ffmpeg ollama; do
    if command -v "${tool}" >/dev/null 2>&1; then
        echo "  - 可选工具 [${tool}]: 已安装 ($(command -v "${tool}"))"
    else
        echo "  - 可选工具 [${tool}]: 未检测到 (使用内置纯 Python 仿真引擎，无影响)"
    fi
done

# 2. 依次执行 6 套实操练习与客户端流水线
echo -e "\n=================================================================="
echo "▶️ [1/6] 运行实操 1：视频抽帧与视觉语言模型 (VLM) 批处理..."
"$PYTHON_BIN" "${SCRIPT_DIR}/01_video_vlm_inference.py" --demo

echo -e "\n▶️ [2/6] 运行实操 2：音频大模型 (Whisper ASR + TTS) 双向交互闭环..."
"$PYTHON_BIN" "${SCRIPT_DIR}/02_audio_whisper_tts.py" --demo

echo -e "\n▶️ [3/6] 运行实操 3：Mac Studio 多模态大模型 LoRA 微调与数学梯度下降..."
"$PYTHON_BIN" "${SCRIPT_DIR}/03_vlm_lora_dataset_and_train.py" --demo --use-sample-data
echo -e "\n▶️ [4/6] 运行实操 4：W4A16 4-bit 量化导出与 Pixel 10 内存防爆校验..."
"$PYTHON_BIN" "${SCRIPT_DIR}/04_export_to_pixel10.py" --demo

echo -e "\n▶️ [5/6] 运行实操 5：Mac Studio 本地 OpenAI 兼容多模态 API 网关自测..."
"$PYTHON_BIN" "${SCRIPT_DIR}/05_local_multimodal_server.py" --demo

echo -e "\n▶️ [6/6] 运行轻量客户端 (client_example) 原生多模态请求自测..."
"$PYTHON_BIN" "${SCRIPT_DIR}/client_example.py" --demo

echo -e "\n=================================================================="
echo "🎉 全部 6 套音视频实操练习与客户端流水线执行完毕，全部验证通过！"
echo "=================================================================="
