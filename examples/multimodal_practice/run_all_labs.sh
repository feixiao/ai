#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# 一键运行全部音视频多模态实操练习 (Mac Studio / PC / Linux 零依赖通用)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python3}"

echo "=================================================================="
echo "🚀 启动 2026 音视频多模态大模型 4 套端到端实操练习流水线"
echo "=================================================================="

echo -e "\n▶️ [1/4] 运行实操 1：视频抽帧与视觉语言模型 (VLM) 批处理..."
"$PYTHON_BIN" "${SCRIPT_DIR}/01_video_vlm_inference.py" --demo

echo -e "\n▶️ [2/4] 运行实操 2：音频大模型 (Whisper ASR + TTS) 双向交互闭环..."
"$PYTHON_BIN" "${SCRIPT_DIR}/02_audio_whisper_tts.py" --demo

echo -e "\n▶️ [3/4] 运行实操 3：Mac Studio 多模态大模型 LoRA 微调与数学梯度下降..."
"$PYTHON_BIN" "${SCRIPT_DIR}/03_vlm_lora_dataset_and_train.py" --demo

echo -e "\n▶️ [4/4] 运行实操 4：W4A16 4-bit 量化导出与 Pixel 10 内存防爆校验..."
"$PYTHON_BIN" "${SCRIPT_DIR}/04_export_to_pixel10.py" --demo

echo -e "\n=================================================================="
echo "🎉 全部 4 套音视频实操练习执行完毕，所有验证与契约均通过！"
echo "=================================================================="
