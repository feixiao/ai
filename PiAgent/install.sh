#!/usr/bin/env bash
# ==============================================================================
# Pi Agent (pi-coding-agent) 一键安装、反向代理与模型配置管理脚本
# ==============================================================================
#
# 功能说明：
# 1. 自动化检测 Node.js 环境与 Pi Agent CLI (pi / @earendil-works/pi-coding-agent) 安装状态
# 2. 自动化检测反向代理网关及本地推理引擎 (LM Studio, Ollama, vLLM) 连通性
# 3. 部署或智能合并 models.json 与 settings.json 至全局 (~/.pi/agent/) 或工作区 (.pi/)
# 4. 支持自动备份旧配置、可选安装扩展 (如 pi-models-discovery)
#
# ==============================================================================

set -euo pipefail

# 终端输出样式定义
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'
BLUE=$'\033[0;34m'
PURPLE=$'\033[0;35m'
CYAN=$'\033[0;36m'
BOLD=$'\033[1m'
NC=$'\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_MODELS="${SCRIPT_DIR}/models.json"
SOURCE_SETTINGS="${SCRIPT_DIR}/settings.json"

TARGET_GLOBAL_DIR="${HOME}/.pi/agent"
TARGET_GLOBAL_MODELS="${TARGET_GLOBAL_DIR}/models.json"
TARGET_GLOBAL_SETTINGS="${TARGET_GLOBAL_DIR}/settings.json"

# 默认参数
INSTALL_TARGET="global" # "global" 或 "project"
PROJECT_DIR=""
FORCE_OVERWRITE=0
CHECK_ONLY=0
INSTALL_CLI_IF_MISSING=0
INSTALL_EXTENSIONS=0
PROXY_URL=""
PROXY_KEY=""

# ==============================================================================
# 帮助信息
# ==============================================================================
show_help() {
    cat << EOF
${BOLD}Pi Agent (pi-coding-agent) 一键安装与配置管理工具${NC}

${CYAN}用法:${NC}
  ./install.sh [选项]

${CYAN}选项:${NC}
  -g, --global              部署到全局配置目录 (~/.pi/agent/) [默认]
  -p, --project [DIR]       部署到指定工程目录 (默认: 当前目录 ./.pi/)
  -i, --install-cli         若系统未安装 Pi Agent CLI，则自动执行官方安装
  -c, --check               仅检测本地后端/反代服务连通性与模型列表，不写入配置
  -f, --force               强制覆盖目标配置（会自动创建时间戳备份文件）
  -e, --extensions          自动安装推荐扩展 (如 pi-models-discovery 模型自动发现)
      --proxy-url <URL>     快速测试指定的反向代理 BaseURL (如 https://api.proxy.com/v1)
      --proxy-key <KEY>     配合 --proxy-url 测试时使用的 API Key
  -h, --help                显示此帮助信息

${CYAN}示例:${NC}
  ./install.sh                      # 部署模型与参数配置到 ~/.pi/agent/
  ./install.sh -i -e                # 自动安装 Pi CLI，部署配置并安装推荐扩展
  ./install.sh --check              # 检查 LM Studio、Ollama 与反代端点连通性
  ./install.sh --project .          # 为当前项目生成工作区专属配置 (.pi/)
  ./install.sh --proxy-url https://api.siliconflow.cn/v1 --proxy-key sk-xxx
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
# 检查依赖与 Pi CLI
# ==============================================================================
check_prerequisites() {
    log_info "检查基础运行环境..."

    # 检查 Node.js
    if command -v node >/dev/null 2>&1; then
        local node_ver
        node_ver="$(node -v)"
        log_success "Node.js 已就绪: ${node_ver}"
    else
        log_warn "未检测到 Node.js。Pi Agent 需要 Node.js (推荐 v18+)。"
    fi

    # 检查 Pi CLI
    if command -v pi >/dev/null 2>&1; then
        local pi_ver
        pi_ver="$(pi --version 2>/dev/null || echo '已安装')"
        log_success "Pi Agent CLI 已就绪: ${pi_ver}"
    else
        log_warn "未在 PATH 中检测到 'pi' 命令。"
        if [[ $INSTALL_CLI_IF_MISSING -eq 1 ]]; then
            install_pi_cli
        else
            echo -e "  ${YELLOW}提示${NC}: 您可以运行: ${BOLD}./install.sh -i${NC} 来自动安装 Pi Agent，"
            echo -e "         或者执行: ${BOLD}curl -fsSL https://pi.dev/install.sh | sh${NC}"
            echo -e "         或者通过 npm: ${BOLD}npm install -g --ignore-scripts @earendil-works/pi-coding-agent${NC}"
        fi
    fi
}

# ==============================================================================
# 安装 Pi CLI
# ==============================================================================
install_pi_cli() {
    log_info "正在自动安装 Pi Agent CLI..."
    if command -v curl >/dev/null 2>&1; then
        log_info "通过官方脚本安装 (https://pi.dev/install.sh)..."
        curl -fsSL https://pi.dev/install.sh | sh
    elif command -v npm >/dev/null 2>&1; then
        log_info "通过 npm 全局安装 @earendil-works/pi-coding-agent..."
        npm install -g --ignore-scripts @earendil-works/pi-coding-agent
    else
        log_error "系统中未找到 curl 或 npm，无法自动安装 Pi Agent，请先手动安装。"
        exit 1
    fi

    if command -v pi >/dev/null 2>&1; then
        log_success "Pi Agent CLI 安装成功！"
    else
        log_warn "安装完成，但 'pi' 暂不在当前 PATH 中，可能需要执行: export PATH=\"\$HOME/.pi/bin:\$PATH\""
    fi
}

# ==============================================================================
# 服务连通性检测
# ==============================================================================
check_endpoint() {
    local name="$1"
    local url="$2"
    local auth_header="${3:-}"

    printf "  • 正在探测 %-22s: %s ... " "$name" "$url"
    local http_code=0
    if [[ -n "$auth_header" ]]; then
        http_code="$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 -m 3 -H "$auth_header" "$url" 2>/dev/null || echo "000")"
    else
        http_code="$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 -m 3 "$url" 2>/dev/null || echo "000")"
    fi

    if [[ "$http_code" =~ ^(200|201|401|403|404)$ ]]; then
        if [[ "$http_code" == "200" ]]; then
            echo -e "${GREEN}在线 (HTTP 200)${NC}"
            return 0
        else
            echo -e "${YELLOW}可达 (HTTP ${http_code})${NC}"
            return 0
        fi
    else
        echo -e "${RED}离线或超时 (HTTP ${http_code})${NC}"
        return 1
    fi
}

run_health_checks() {
    echo ""
    echo -e "${BOLD}======== 本地推理引擎与代理连通性自检 ========${NC}"
    check_endpoint "LM Studio" "http://127.0.0.1:1234/v1/models" || true
    check_endpoint "Ollama" "http://127.0.0.1:11434/api/tags" || true
    check_endpoint "vLLM 本地集群" "http://127.0.0.1:8000/v1/models" || true
    check_endpoint "硅基流动 (国内反代)" "https://api.siliconflow.cn/v1/models" "Authorization: Bearer ${SILICONFLOW_API_KEY:-guest}" || true

    if [[ -n "$PROXY_URL" ]]; then
        local auth=""
        if [[ -n "$PROXY_KEY" ]]; then
            auth="Authorization: Bearer ${PROXY_KEY}"
        fi
        check_endpoint "自定义反向代理" "${PROXY_URL}/models" "$auth" || true
    fi
    echo -e "${BOLD}===============================================${NC}\n"
}

# ==============================================================================
# 安装扩展 (Extensions)
# ==============================================================================
install_recommended_extensions() {
    if ! command -v pi >/dev/null 2>&1; then
        log_warn "未找到 pi CLI，跳过扩展安装。"
        return
    fi

    log_info "正在安装推荐扩展: pi-models-discovery (模型动态探测与自动发现)..."
    pi install npm:pi-models-discovery || log_warn "扩展安装可能需要网络或权限，可后续手动运行: pi install npm:pi-models-discovery"
}

# ==============================================================================
# 部署配置文件
# ==============================================================================
deploy_config() {
    local target_dir=""
    local target_models=""
    local target_settings=""

    if [[ "$INSTALL_TARGET" == "global" ]]; then
        target_dir="$TARGET_GLOBAL_DIR"
        target_models="$TARGET_GLOBAL_MODELS"
        target_settings="$TARGET_GLOBAL_SETTINGS"
        log_info "部署目标: 全局配置目录 (${target_dir})"
    else
        target_dir="${PROJECT_DIR}/.pi"
        target_models="${target_dir}/models.json"
        target_settings="${target_dir}/settings.json"
        log_info "部署目标: 工作区专属配置目录 (${target_dir})"
    fi

    mkdir -p "$target_dir"

    # 处理 models.json
    if [[ -f "$target_models" ]]; then
        if [[ $FORCE_OVERWRITE -eq 1 ]]; then
            local bak_file="${target_models}.bak.$(date +%Y%m%d%H%M%S)"
            cp "$target_models" "$bak_file"
            log_warn "目标 models.json 已存在，已备份至: ${bak_file}"
            cp "$SOURCE_MODELS" "$target_models"
            log_success "已覆盖更新 models.json"
        else
            log_warn "目标 models.json 已存在。为保护自定义 Provider，未强制覆盖。"
            echo -e "  可使用 ${BOLD}--force${NC} 强制覆盖（带备份），或手动将 ${SOURCE_MODELS} 合并进去。"
        fi
    else
        cp "$SOURCE_MODELS" "$target_models"
        log_success "成功创建配置文件: ${target_models}"
    fi

    # 处理 settings.json
    if [[ -f "$target_settings" ]]; then
        if [[ $FORCE_OVERWRITE -eq 1 ]]; then
            local bak_file="${target_settings}.bak.$(date +%Y%m%d%H%M%S)"
            cp "$target_settings" "$bak_file"
            log_warn "目标 settings.json 已存在，已备份至: ${bak_file}"
            cp "$SOURCE_SETTINGS" "$target_settings"
            log_success "已覆盖更新 settings.json"
        else
            log_warn "目标 settings.json 已存在。如需重置，请添加 --force 参数。"
        fi
    else
        cp "$SOURCE_SETTINGS" "$target_settings"
        log_success "成功创建全局设置: ${target_settings}"
    fi

    echo ""
    echo -e "${GREEN}${BOLD}✓ Pi Agent 配置部署完成！${NC}"
    echo ""
    echo -e "${CYAN}常用环境变量配置建议 (可加入 ~/.zshrc 或 ~/.bashrc):${NC}"
    echo -e "  export CUSTOM_PROXY_API_KEY=\"sk-xxxx\"     # 反代网关 API Key"
    echo -e "  export SILICONFLOW_API_KEY=\"sk-xxxx\"      # 硅基流动国内反代 Key"
    echo -e "  export ANTHROPIC_PROXY_KEY=\"sk-xxxx\"      # Claude 专属反代 Key"
    echo ""
    echo -e "${CYAN}快速启动与切模指南:${NC}"
    echo -e "  ${BOLD}pi${NC}                                    # 启动进入交互式 TUI 界面"
    echo -e "  在交互界面按 ${BOLD}Ctrl+P${NC} 或输入 ${BOLD}/model${NC}      # 实时切换模型 (反代、本地、公有云)"
    echo -e "  输入 ${BOLD}/thinking${NC}                          # 调节推理深度 (off/low/medium/high/max)"
    echo -e "  ${BOLD}pi -m reverse-proxy-openai/claude-3-5-sonnet-20241022${NC} # 命令行直接使用指定反代模型"
    echo ""
}

# ==============================================================================
# 主入口参数解析
# ==============================================================================
main() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -g|--global)
                INSTALL_TARGET="global"
                shift
                ;;
            -p|--project)
                INSTALL_TARGET="project"
                if [[ $# -gt 1 && ! "$2" =~ ^- ]]; then
                    PROJECT_DIR="$2"
                    shift 2
                else
                    PROJECT_DIR="."
                    shift
                fi
                ;;
            -i|--install-cli)
                INSTALL_CLI_IF_MISSING=1
                shift
                ;;
            -c|--check)
                CHECK_ONLY=1
                shift
                ;;
            -f|--force)
                FORCE_OVERWRITE=1
                shift
                ;;
            -e|--extensions)
                INSTALL_EXTENSIONS=1
                shift
                ;;
            --proxy-url)
                if [[ $# -gt 1 ]]; then
                    PROXY_URL="$2"
                    shift 2
                else
                    log_error "--proxy-url 参数缺少目标 URL"
                    exit 1
                fi
                ;;
            --proxy-key)
                if [[ $# -gt 1 ]]; then
                    PROXY_KEY="$2"
                    shift 2
                else
                    log_error "--proxy-key 参数缺少密钥"
                    exit 1
                fi
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done

    check_prerequisites
    run_health_checks

    if [[ $CHECK_ONLY -eq 1 ]]; then
        log_info "仅自检模式完成，未修改配置文件。"
        exit 0
    fi

    deploy_config

    if [[ $INSTALL_EXTENSIONS -eq 1 ]]; then
        install_recommended_extensions
    fi
}

main "$@"
