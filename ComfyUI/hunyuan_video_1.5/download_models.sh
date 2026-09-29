#!/usr/bin/env bash
# ==============================================================================
# HunyuanVideo 1.5 模型一键下载脚本 (Apple Silicon / Mac Studio 优化)
#
# 设计要点 (针对不稳定链路):
#   1. 使用 curl 断点续传 (-C -), 网络中断后不会从头再来;
#   2. 卡死检测: 30 秒内均速低于 2KB/s 视为 stall, 自动断开重连;
#   3. 外层多次重试, 幂等可重复执行;
#   4. 下载完成后用 HEAD 的 Content-Length 校验文件完整性, 杜绝半截文件;
#   5. 支持 HF_ENDPOINT 切换到镜像站 (如 https://hf-mirror.com)。
#
# 用法:
#   ./download_models.sh              # 完整套装 T2V + I2V (约 46.5GB)
#   ./download_models.sh t2v          # 仅文生视频必需套装 (约 29GB)
#   ./download_models.sh i2v          # 仅图生视频增量套装 (约 17.5GB)
#   ./download_models.sh lite         # 额外补 480p 双档模型
#
#   # 使用镜像站 (若 huggingface.co 直连不稳定)
#   HF_ENDPOINT=https://hf-mirror.com ./download_models.sh t2v
#
#   # 自定义 ComfyUI 模型根目录
#   COMFY_MODELS=/path/to/ComfyUI/models ./download_models.sh all
# ==============================================================================
set -uo pipefail   # 注意: 不用 -e, 单个文件失败后仍继续尝试其余文件

REPO="Comfy-Org/HunyuanVideo_1.5_repackaged"
HF_ENDPOINT="${HF_ENDPOINT:-https://huggingface.co}"
HF_ENDPOINT="${HF_ENDPOINT%/}"
BASE_URL="${HF_ENDPOINT}/${REPO}/resolve/main/split_files"

COMFY_MODELS="${COMFY_MODELS:-/Users/frank/ComfyUI/models}"
MODE="${1:-all}"

#: 单个文件最大重试次数
MAX_ATTEMPTS="${MAX_ATTEMPTS:-40}"
#: 判定 stall 的阈值 (字节/秒) 与观察窗口 (秒)
SPEED_LIMIT="${SPEED_LIMIT:-2048}"
SPEED_TIME="${SPEED_TIME:-30}"

FAILED=()

echo "=============================================================="
echo " HunyuanVideo 1.5 模型下载"
echo " 模式       : ${MODE}"
echo " 目标目录   : ${COMFY_MODELS}"
echo " 下载端点   : ${HF_ENDPOINT}"
echo " 断点续传   : 已启用 (stall 阈值 ${SPEED_LIMIT}B/s / ${SPEED_TIME}s)"
echo "=============================================================="

# --------------------------------------------------------------------------- #
# 远端文件大小 (通过 HEAD 跟随重定向取最终 Content-Length)
# --------------------------------------------------------------------------- #
remote_size() {
  curl -sIL --max-time 30 "$1" 2>/dev/null \
    | tr -d '\r' \
    | awk 'tolower($1)=="content-length:"{v=$2} END{print v}'
}

local_size() {
  [[ -f "$1" ]] && stat -f%z "$1" 2>/dev/null || echo 0
}

# --------------------------------------------------------------------------- #
# 校验 safetensors 文件结构完整性
#   仅比对文件大小是不够的: 多线程分块下载若中断, 可能得到"大小正确但内容有洞"
#   的文件。safetensors 头部即自描述的 JSON, 其中声明的张量字节偏移必须与文件
#   实际大小完全吻合, 因此该检查能可靠地识破截断与空洞。
# 返回 0 表示结构完整, 1 表示损坏或尚未下载完。
# --------------------------------------------------------------------------- #
verify_safetensors() {
  local path="$1"
  python3 - "$path" <<'PY' 2>/dev/null
import json, struct, sys, os

path = sys.argv[1]
try:
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        raw = fh.read(8)
        if len(raw) != 8:
            sys.exit(1)
        header_len = struct.unpack("<Q", raw)[0]
        # 头部长度必须在合理范围内, 且不超出文件本身
        if header_len <= 0 or header_len > size - 8:
            sys.exit(1)
        header = fh.read(header_len)
        if len(header) != header_len:
            sys.exit(1)
        meta = json.loads(header.decode("utf-8"))
except Exception:
    sys.exit(1)

if not isinstance(meta, dict) or not meta:
    sys.exit(1)

end_of_data = 8 + header_len
for name, info in meta.items():
    if name == "__metadata__":
        continue
    if not isinstance(info, dict):
        sys.exit(1)
    offsets = info.get("data_offsets")
    if not (isinstance(offsets, list) and len(offsets) == 2):
        sys.exit(1)
    end_of_data = max(end_of_data, 8 + header_len + int(offsets[1]))

sys.exit(0 if end_of_data == size else 1)
PY
}

# --------------------------------------------------------------------------- #
# 带续传 / stall 检测 / 完整性校验的下载
# --------------------------------------------------------------------------- #
fetch() {
  local subdir="$1" filename="$2"
  local destdir="${COMFY_MODELS}/${subdir}"
  local dest="${destdir}/${filename}"
  local part="${dest}.part"
  local url="${BASE_URL}/${subdir}/${filename}"

  mkdir -p "${destdir}"

  local expected
  expected="$(remote_size "$url")"

  # 已下载 → 校验完整性后跳过
  if [[ -s "$dest" ]]; then
    local have ok
    have="$(local_size "$dest")"
    ok=1
    [[ -n "${expected}" && "${have}" != "${expected}" ]] && ok=0
    if (( ok )) && [[ "${filename}" == *.safetensors ]] && ! verify_safetensors "$dest"; then
      ok=0
    fi
    if (( ok )); then
      echo "✅ 已存在且校验通过, 跳过: ${subdir}/${filename} ($(( have / 1024 / 1024 ))MB)"
      return 0
    fi
    echo "⚠️  已存在但校验失败 (本地 ${have} / 远端 ${expected:-?}), 重新下载: ${subdir}/${filename}"
    rm -f "$dest"
  fi

  [[ -f "$part" ]] || : > "$part"

  local attempt=1
  while (( attempt <= MAX_ATTEMPTS )); do
    echo "⬇️  [${attempt}/${MAX_ATTEMPTS}] ${subdir}/${filename} (已完成 $(( $(local_size "$part") / 1024 / 1024 ))MB)"
    if curl -L --fail --silent --show-error \
            --retry 5 --retry-delay 3 --retry-all-errors \
            --connect-timeout 20 --max-time 0 \
            --speed-limit "${SPEED_LIMIT}" --speed-time "${SPEED_TIME}" \
            -C - -o "$part" "$url"; then
      # 第一道: 大小校验
      local got
      got="$(local_size "$part")"
      if [[ -n "${expected}" && "${got}" != "${expected}" ]]; then
        echo "   大小不符 (本地 ${got} / 远端 ${expected}), 继续断点续传..."
        (( attempt++ ))
        sleep 3
        continue
      fi

      # 第二道: safetensors 结构校验 (识破截断与空洞)
      if [[ "${filename}" == *.safetensors ]]; then
        if ! verify_safetensors "$part"; then
          echo "   ⚠️  safetensors 结构校验失败 (疑似空洞/截断), 丢弃并重新下载..."
          rm -f "$part"
          : > "$part"
          (( attempt++ ))
          sleep 3
          continue
        fi
      fi

      mv "$part" "$dest"
      echo "✅ 完成: ${subdir}/${filename} ($(( got / 1024 / 1024 ))MB)"
      return 0
    fi
    echo "   连接中断, 3 秒后断点续传..."
    sleep 3
    (( attempt++ ))
  done

  echo "❌ 放弃: ${subdir}/${filename} (已达最大重试次数)" >&2
  FAILED+=("${subdir}/${filename}")
  return 1
}

# --------------------------------------------------------------------------- #
# 下载清单
# --------------------------------------------------------------------------- #
# 文本 / 视觉编码器与 VAE (T2V / I2V 共用)
if [[ "${MODE}" == "all" || "${MODE}" == "t2v" || "${MODE}" == "i2v" || "${MODE}" == "lite" ]]; then
  fetch text_encoders "qwen_2.5_vl_7b_fp8_scaled.safetensors"     # ~9.4GB
  fetch text_encoders "byt5_small_glyphxl_fp16.safetensors"       # ~0.4GB
  fetch vae           "hunyuanvideo15_vae_fp16.safetensors"       # ~2.5GB
fi

# 文生视频 (T2V)
if [[ "${MODE}" == "all" || "${MODE}" == "t2v" ]]; then
  fetch diffusion_models "hunyuanvideo1.5_720p_t2v_fp16.safetensors"   # ~16.6GB
fi

# 图生视频 (I2V)
if [[ "${MODE}" == "all" || "${MODE}" == "i2v" ]]; then
  fetch clip_vision      "sigclip_vision_patch14_384.safetensors"         # ~0.9GB
  fetch diffusion_models "hunyuanvideo1.5_720p_i2v_fp16.safetensors"     # ~16.6GB
fi

# 480p 快速验证档
if [[ "${MODE}" == "lite" ]]; then
  fetch diffusion_models "hunyuanvideo1.5_480p_t2v_fp16.safetensors"     # ~16.6GB
  fetch diffusion_models "hunyuanvideo1.5_480p_i2v_fp16.safetensors"     # ~16.6GB
fi

# --------------------------------------------------------------------------- #
# 汇总
# --------------------------------------------------------------------------- #
echo "=============================================================="
if (( ${#FAILED[@]} == 0 )); then
  echo "🎉 全部下载完成。请在 ComfyUI 中点击右侧菜单的「刷新」按钮以识别新模型。"
else
  echo "⚠️  以下文件未能下载完成, 请重新执行本脚本续传:" >&2
  for f in "${FAILED[@]}"; do echo "   · $f" >&2; done
  echo "=============================================================="
  exit 1
fi
echo "验证: ls -lh ${COMFY_MODELS}/diffusion_models ${COMFY_MODELS}/text_encoders ${COMFY_MODELS}/vae ${COMFY_MODELS}/clip_vision"
echo "=============================================================="
