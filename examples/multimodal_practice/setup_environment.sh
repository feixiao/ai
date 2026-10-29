#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Mac Studio 本地与 Pixel 10 端侧多模态环境一键就绪与部署工具
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python3}"

show_help() {
    cat <<EOF
用法: $(basename "$0") [选项]

选项:
  --check                 (默认) 探测 Mac Studio 与 Pixel 10 本地部署工具链完整性
  --install-mac-mlx       安装针对 Apple Silicon 优化的 MLX 生产级多模态库 (mlx-vlm, mlx-whisper)
  --push-pixel10 <文件>    通过 ADB 将量化后的端侧模型 (.task/.tflite) 推送到 Pixel 10
  --help                  显示本帮助文档
EOF
}

check_environment() {
    echo "=================================================================="
    echo "🔍 Mac Studio 与 Pixel 10 多模态落地环境探测"
    echo "=================================================================="

    OS_NAME="$(uname -s)"
    ARCH_NAME="$(uname -m)"
    echo "  - 宿主机系统: ${OS_NAME} (${ARCH_NAME})"

    # 1. Mac Studio / Apple Silicon 专项检查
    if [[ "${OS_NAME}" == "Darwin" ]]; then
        CPU_BRAND="$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Apple Silicon")"
        MEM_BYTES="$(sysctl -n hw.memsize 2>/dev/null || echo "0")"
        MEM_GB=$(( MEM_BYTES / 1024 / 1024 / 1024 ))
        echo "  - 芯片规格: ${CPU_BRAND}"
        echo "  - 统一内存 (UMA): ${MEM_GB} GB"
        
        # 检查 MLX
        if "$PYTHON_BIN" -c "import mlx.core" >/dev/null 2>&1; then
            echo "  - Apple MLX 框架: ✅ 已就绪"
        else
            echo "  - Apple MLX 框架: ⚪ 未安装 (可执行: $(basename "$0") --install-mac-mlx)"
        fi

        # 检查 mlx-vlm
        if "$PYTHON_BIN" -c "import mlx_vlm" >/dev/null 2>&1; then
            echo "  - MLX-VLM 视觉推理: ✅ 已就绪"
        else
            echo "  - MLX-VLM 视觉推理: ⚪ 未安装 (实操练习内置纯 Python 引擎可直接运行)"
        fi
    fi

    # 2. 检查多媒体编解码
    if command -v ffmpeg >/dev/null 2>&1; then
        echo "  - FFmpeg 编解码器: ✅ 已安装 ($(command -v ffmpeg))"
    else
        echo "  - FFmpeg 编解码器: ⚪ 未安装 (建议: brew install ffmpeg)"
    fi

    # 3. 检查 Pixel 10 连接状态 (通过 Android ADB)
    if command -v adb >/dev/null 2>&1; then
        echo "  - Android Debug Bridge (ADB): ✅ 已安装 ($(command -v adb))"
        # 探测设备
        DEVICES="$(adb devices | grep -v "List of devices" | grep "device$" || true)"
        if [[ -n "${DEVICES}" ]]; then
            echo "  - 连接中的 Android 设备: ✅ 检测到在线设备"
            echo "${DEVICES}" | while read -r line; do
                echo "      * ${line}"
            done
        else
            echo "  - 连接中的 Android 设备: ⚪ 暂无在线设备 (若需部署至 Pixel 10 请开启 USB 调试连接)"
        fi
    else
        echo "  - Android Debug Bridge (ADB): ⚪ 未安装 (若需向 Pixel 10 部署建议安装 Android Platform Tools)"
    fi

    echo "=================================================================="
}

install_mac_mlx() {
    echo "▶️ 正在通过 pip 为当前 Python 环境安装 Apple MLX 多模态加速组件..."
    "$PYTHON_BIN" -m pip install --upgrade mlx-vlm mlx-whisper
    echo "✅ MLX 安装完毕！"
}

push_to_pixel10() {
    local model_path="${1:-}"
    if [[ -z "${model_path}" || ! -f "${model_path}" ]]; then
        echo "❌ 错误: 指定的模型文件不存在: '${model_path}'"
        exit 1
    fi

    if ! command -v adb >/dev/null 2>&1; then
        echo "❌ 错误: 未检测到 adb 命令，请先安装 Android Platform-Tools。"
        exit 1
    fi

    local target_dir="/data/local/tmp/models"
    echo "▶️ 正在创建 Pixel 10 端侧模型目录: ${target_dir} ..."
    adb shell "mkdir -p ${target_dir}"

    echo "▶️ 正在推送 '${model_path}' 到 Pixel 10 (${target_dir}) ..."
    adb push "${model_path}" "${target_dir}/"
    echo "✅ 模型推送成功！Pixel 10 端侧路径: ${target_dir}/$(basename "${model_path}")"
}

case "${1:-}" in
    --check|"")
        check_environment
        ;;
    --install-mac-mlx)
        install_mac_mlx
        ;;
    --push-pixel10)
        push_to_pixel10 "${2:-}"
        ;;
    --help|-h)
        show_help
        ;;
    *)
        echo "未知选项: $1"
        show_help
        exit 1
        ;;
esac
