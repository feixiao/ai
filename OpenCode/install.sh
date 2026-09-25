#!/usr/bin/env bash
# ==============================================================================
# OpenCode 本地模型 Provider (LM Studio) 一键安装与配置管理脚本
# ==============================================================================
#
# 功能说明：
# 1. 自动化检测本地 LM Studio 服务状态及核心模型可用性 (127.0.0.1:1234)
# 2. 幂等部署或合并 LM Studio Provider 配置至 OpenCode 全局配置目录 (~/.config/opencode/opencode.json)
# 3. 支持备份已有配置、按需单项目安装与非交互自动化部署
#
# ==============================================================================

set -euo pipefail

# 终端输出样式定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_CONFIG="${SCRIPT_DIR}/opencode.json"
TARGET_GLOBAL_DIR="${HOME}/.config/opencode"
TARGET_GLOBAL_FILE="${TARGET_GLOBAL_DIR}/opencode.json"

# 默认参数
LM_PORT="${LM_PORT:-1234}"
LM_HOST="${LM_HOST:-127.0.0.1}"
INSTALL_TARGET="global" # "global" 或 "project"
FORCE_OVERWRITE=0
CHECK_ONLY=0

# ==============================================================================
# 帮助与说明函数
# ==============================================================================
show_help() {
    cat << EOF
OpenCode 本地模型 Provider (LM Studio) 一键安装工具

用法:
  ./install.sh [选项]

选项:
  -g, --global          安装/合并到全局配置 (~/.config/opencode/opencode.json) [默认]
  -p, --project [DIR]   安装到指定工作区或当前目录 (默认: 当前目录 ./opencode.json)
  -c, --check           仅检测 LM Studio 服务连通性与模型列表，不写入配置
  -f, --force           强制覆盖目标配置（会自动创建时间戳备份）
      --port <PORT>     指定 LM Studio 监听端口 (默认: 1234)
      --host <HOST>     指定 LM Studio 监听主机 (默认: 127.0.0.1)
  -h, --help            显示此帮助信息

示例:
  ./install.sh                  # 智能合并到全局配置
  ./install.sh --check          # 检测本地模型与服务状态
  ./install.sh --project .      # 生成当前项目的专属配置
EOF
}

# ==============================================================================
# 打印日志函数
# ==============================================================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ==============================================================================
# 检测 LM Studio 服务与模型状态
# 参数:
#   $1 - 目标主机 IP
#   $2 - 目标端口
# 返回值:
#   0 - 服务正常响应
#   1 - 服务未启动或无法连接
# ==============================================================================
check_lm_studio_status() {
    local target_host="$1"
    local target_port="$2"
    local endpoint_url="http://${target_host}:${target_port}/v1/models"

    log_info "正在检测 LM Studio 服务状态 (${endpoint_url})..."

    if ! curl -s --connect-timeout 3 "${endpoint_url}" > /dev/null 2>&1; then
        log_warn "未能连接到 LM Studio 服务 (${target_host}:${target_port})。"
        log_warn "请确认 LM Studio 已启动，并在 'Local Server' 页面开启 API 监听 (默认端口: 1234)。"
        return 1
    fi

    log_success "LM Studio 服务运行正常！"

    # 获取当前已注册的模型列表
    local model_response
    model_response="$(curl -s --connect-timeout 5 "${endpoint_url}" || true)"

    local required_primary="qwen3.8-27b-splash"
    local required_subagent="google/gemma-4-26b-a4b-qat"

    echo ""
    echo -e "${BOLD}核心模型加载自检：${NC}"

    if echo "${model_response}" | grep -q "${required_primary}"; then
        echo -e "  [+] 主力编码模型 (${required_primary}): ${GREEN}已就绪${NC}"
    else
        echo -e "  [-] 主力编码模型 (${required_primary}): ${YELLOW}未在列表中发现 (请在 LM Studio 中下载或加载)${NC}"
    fi

    if echo "${model_response}" | grep -q "${required_subagent}"; then
        echo -e "  [+] 极速子代理模型 (${required_subagent}): ${GREEN}已就绪${NC}"
    else
        echo -e "  [-] 极速子代理模型 (${required_subagent}): ${YELLOW}未在列表中发现 (请在 LM Studio 中下载或加载)${NC}"
    fi
    echo ""

    return 0
}

# ==============================================================================
# 安全合并 JSON 配置
# 参数:
#   $1 - 原有配置文件路径
#   $2 - 补丁模板配置路径
#   $3 - 目标输出文件路径
# 返回值:
#   0 - 合并成功
#   1 - 合并失败
# ==============================================================================
merge_config_json() {
    local base_config_path="$1"
    local patch_config_path="$2"
    local output_config_path="$3"

    python3 -c "
import json
import sys

base_path = sys.argv[1]
patch_path = sys.argv[2]
out_path = sys.argv[3]

with open(patch_path, 'r', encoding='utf-8') as f:
    patch_data = json.load(f)

try:
    with open(base_path, 'r', encoding='utf-8') as f:
        base_data = json.load(f)
except Exception:
    base_data = {}

# 1. 补充 Schema
if '\$schema' not in base_data and '\$schema' in patch_data:
    base_data['\$schema'] = patch_data['\$schema']

# 2. 合并 Provider
if 'provider' not in base_data:
    base_data['provider'] = {}
for provider_id, provider_value in patch_data.get('provider', {}).items():
    base_data['provider'][provider_id] = provider_value

# 3. 设置默认模型与快速模型（若不存在或用户指定时更新）
base_data['model'] = patch_data.get('model', base_data.get('model'))
base_data['small_model'] = patch_data.get('small_model', base_data.get('small_model'))

# 4. 合并 Agent 设定
if 'agent' not in base_data:
    base_data['agent'] = {}
for agent_id, agent_value in patch_data.get('agent', {}).items():
    base_data['agent'][agent_id] = agent_value

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(base_data, f, indent=2, ensure_ascii=False)
    f.write('\n')
" "${base_config_path}" "${patch_config_path}" "${output_config_path}"
}

# ==============================================================================
# 部署配置文件
# 参数:
#   $1 - 目标文件路径
# ==============================================================================
deploy_config() {
    local target_file="$1"
    local target_dir
    target_dir="$(dirname "${target_file}")"

    mkdir -p "${target_dir}"

    if [ -f "${target_file}" ]; then
        local timestamp
        timestamp="$(date +%Y%m%d_%H%M%S)"
        local backup_file="${target_file}.bak.${timestamp}"

        cp "${target_file}" "${backup_file}"
        log_info "已备份已有配置至: ${backup_file}"

        if [ "${FORCE_OVERWRITE}" -eq 1 ]; then
            cp "${SOURCE_CONFIG}" "${target_file}"
            log_success "已强制覆盖目标配置: ${target_file}"
        else
            merge_config_json "${backup_file}" "${SOURCE_CONFIG}" "${target_file}"
            log_success "已平滑合并 LM Studio Provider 到: ${target_file}"
        fi
    else
        cp "${SOURCE_CONFIG}" "${target_file}"
        log_success "已创建 OpenCode 配置文件: ${target_file}"
    fi
}

# ==============================================================================
# 命令行参数解析
# ==============================================================================
TARGET_PROJECT_PATH=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -g|--global)
            INSTALL_TARGET="global"
            shift
            ;;
        -p|--project)
            INSTALL_TARGET="project"
            if [[ $# -gt 1 && ! "$2" =~ ^- ]]; then
                TARGET_PROJECT_PATH="$2"
                shift 2
            else
                TARGET_PROJECT_PATH="."
                shift
            fi
            ;;
        -c|--check)
            CHECK_ONLY=1
            shift
            ;;
        -f|--force)
            FORCE_OVERWRITE=1
            shift
            ;;
        --port)
            LM_PORT="$2"
            shift 2
            ;;
        --host)
            LM_HOST="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# ==============================================================================
# 执行流程
# ==============================================================================
echo -e "${BOLD}======================================================${NC}"
echo -e "${BOLD} OpenCode 本地模型 (LM Studio) 配置部署工具${NC}"
echo -e "${BOLD}======================================================${NC}"

# 1. 检查源文件是否存在
if [ ! -f "${SOURCE_CONFIG}" ]; then
    log_error "未找到模板配置文件: ${SOURCE_CONFIG}"
    exit 1
fi

# 2. 检测本地 LM Studio 状态
check_lm_studio_status "${LM_HOST}" "${LM_PORT}" || true

if [ "${CHECK_ONLY}" -eq 1 ]; then
    log_info "已完成连通性检查，未做任何文件修改。"
    exit 0
fi

# 3. 部署配置
if [ "${INSTALL_TARGET}" = "global" ]; then
    log_info "目标模式: 全局配置 (${TARGET_GLOBAL_FILE})"
    deploy_config "${TARGET_GLOBAL_FILE}"
else
    local_target_file="${TARGET_PROJECT_PATH}/opencode.json"
    log_info "目标模式: 项目配置 (${local_target_file})"
    deploy_config "${local_target_file}"
fi

echo ""
log_success "OpenCode 本地模型配置完成！"
echo -e "模型调度概要："
echo -e "  • 核心编码智能体 (coder): ${GREEN}lmstudio/qwen3.8-27b-splash${NC} (27B Dense, 100K 窗口, 深度推理)"
echo -e "  • 极速轻量智能体 (fast):  ${GREEN}lmstudio/google/gemma-4-26b-a4b-qat${NC} (26B/4B MoE, 高吞吐)"
echo ""
echo -e "启动建议："
echo -e "  • 命令行交互: 运行 ${BOLD}opencode${NC} 即可自动识别配置并生效"
echo -e "  • 切换角色: 在 OpenCode 中使用 ${BOLD}@coder${NC} 或 ${BOLD}@fast${NC} 调度对应模型"
echo -e "${BOLD}======================================================${NC}"
