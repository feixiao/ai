#!/usr/bin/env bash
# ==============================================================================
# omp (oh-my-pi) 一键安装、环境检测、模型与规则配置部署脚本
# ==============================================================================
#
# 功能说明：
# 1. 自动化检测 omp CLI、Bun/Node 运行环境
# 2. 自动化检测本地推理后端 (Magpie 3425, LM Studio 1234, Ollama 11434) 连通性
# 3. 部署或智能合并 models.yml 与 config.yml 至全局 (~/.omp/agent/) 或工作区 (./.omp/)
# 4. 支持可选同步 Claude/Antigravity 技能 (Skills) 与 专家角色 (Agents)
#
# ==============================================================================

set -euo pipefail

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'
BLUE=$'\033[0;34m'
PURPLE=$'\033[0;35m'
CYAN=$'\033[0;36m'
BOLD=$'\033[1m'
NC=$'\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_MODELS="${SCRIPT_DIR}/models.yml"
SOURCE_CONFIG="${SCRIPT_DIR}/config.yml"

TARGET_GLOBAL_DIR="${HOME}/.omp/agent"
TARGET_GLOBAL_MODELS="${TARGET_GLOBAL_DIR}/models.yml"
TARGET_GLOBAL_CONFIG="${TARGET_GLOBAL_DIR}/config.yml"

INSTALL_TARGET="global" # "global" 或 "project"
PROJECT_DIR=""
FORCE_OVERWRITE=0
CHECK_ONLY=0
INSTALL_SKILLS=0
LIST_MODELS=0

show_help() {
    cat << EOF
${BOLD}omp (oh-my-pi) 一键配置与环境管理工具${NC}

${CYAN}用法:${NC}
  ./install.sh [选项]

${CYAN}基础选项:${NC}
  -g, --global              部署到全局配置目录 (~/.omp/agent/) [默认]
  -p, --project [DIR]       部署到指定工程目录 (默认: 当前目录 ./.omp/)
  -c, --check               仅检测本地后端/网关连通性与模型列表，不写入配置
  -f, --force               强制覆盖现有配置文件 (自动保留 .bak 备份)
  -s, --skills              同步并挂载精选 Skills 到目标目录
  -l, --list-models         查询已接入的可用模型列表
  -h, --help                显示本帮助信息

${CYAN}示例:${NC}
  # 1. 连通性预检
  ./install.sh --check

  # 2. 全局标准安装 (部署 models.yml 与 config.yml)
  ./install.sh

  # 3. 为当前仓库初始化 .omp 项目级配置
  ./install.sh -p .
EOF
}

# 参数解析
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
        -c|--check)
            CHECK_ONLY=1
            shift
            ;;
        -f|--force)
            FORCE_OVERWRITE=1
            shift
            ;;
        -s|--skills)
            INSTALL_SKILLS=1
            shift
            ;;
        -l|--list-models)
            LIST_MODELS=1
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "${RED}错误: 未知参数 $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

echo "${BOLD}${PURPLE}======================================================${NC}"
echo "${BOLD}${PURPLE}          omp (oh-my-pi) 部署与环境集成工具           ${NC}"
echo "${BOLD}${PURPLE}======================================================${NC}"

# 1. 检查 CLI
echo -e "\n${BLUE}==> [1/4] 检查系统环境与 CLI 二进制...${NC}"
if command -v omp >/dev/null 2>&1; then
    OMP_PATH=$(command -v omp)
    OMP_VER=$(omp --version 2>/dev/null || echo "已安装")
    echo -e "${GREEN}✓ 找到 omp: ${OMP_PATH} (${OMP_VER})${NC}"
else
    echo -e "${YELLOW}! 未在 PATH 中找到 omp 命令${NC}"
    echo -e "  请确保已将 omp 安装并加入 PATH (例如 ~/.local/bin/omp)"
fi

if command -v bun >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 找到 Bun 运行时: $(bun --version)${NC}"
fi

# 2. 检查后端服务
echo -e "\n${BLUE}==> [2/4] 探测本地推理后端与网关服务...${NC}"

check_port() {
    local name="$1"
    local url="$2"
    if curl -s --connect-timeout 2 "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ [在线] ${name} 连通成功: ${url}${NC}"
        return 0
    else
        echo -e "${YELLOW}○ [离线] ${name} 未响应: ${url}${NC}"
        return 1
    fi
}

check_port "Magpie Gateway" "http://127.0.0.1:3425/v1/models" || true
check_port "LM Studio" "http://127.0.0.1:1234/v1/models" || true
check_port "Ollama" "http://127.0.0.1:11434/api/tags" || true

if [[ "${LIST_MODELS}" -eq 1 ]]; then
    if command -v omp >/dev/null 2>&1; then
        echo -e "\n${CYAN}当前 omp 可用模型矩阵:${NC}"
        omp models || true
    fi
    exit 0
fi

if [[ "${CHECK_ONLY}" -eq 1 ]]; then
    echo -e "\n${GREEN}连通性检测完毕 (Check Mode)。未修改任何文件。${NC}"
    exit 0
fi

# 3. 部署配置文件
echo -e "\n${BLUE}==> [3/4] 部署配置文件...${NC}"

if [[ "${INSTALL_TARGET}" == "global" ]]; then
    TARGET_DIR="${TARGET_GLOBAL_DIR}"
    TARGET_MODELS="${TARGET_GLOBAL_MODELS}"
    TARGET_CONFIG="${TARGET_GLOBAL_CONFIG}"
else
    TARGET_DIR="${PROJECT_DIR}/.omp"
    TARGET_MODELS="${TARGET_DIR}/models.yml"
    TARGET_CONFIG="${TARGET_DIR}/config.yml"
fi

mkdir -p "${TARGET_DIR}"
echo -e "目标目录: ${CYAN}${TARGET_DIR}${NC}"

deploy_file() {
    local src="$1"
    local dest="$2"
    local filename
    filename=$(basename "$dest")

    if [[ -f "$dest" && "$FORCE_OVERWRITE" -eq 0 ]]; then
        echo -e "${YELLOW}! ${filename} 已存在，跳过覆盖 (使用 -f 或 --force 强制覆盖)${NC}"
    else
        if [[ -f "$dest" ]]; then
            cp "$dest" "${dest}.bak.$(date +%s)"
            echo -e "${CYAN}已备份旧文件至 ${filename}.bak${NC}"
        fi
        cp "$src" "$dest"
        echo -e "${GREEN}✓ 成功部署 ${filename}${NC}"
    fi
}

deploy_file "${SOURCE_MODELS}" "${TARGET_MODELS}"
deploy_file "${SOURCE_CONFIG}" "${TARGET_CONFIG}"

# 4. 可选技能安装
if [[ "${INSTALL_SKILLS}" -eq 1 ]]; then
    echo -e "\n${BLUE}==> [4/4] 挂载推荐技能 (Skills)...${NC}"
    SKILLS_DIR="${TARGET_DIR}/skills"
    mkdir -p "${SKILLS_DIR}"
    
    FOUND_ANY=0
    for candidate in "${HOME}/.codebuddy/skills" "${HOME}/.claude/skills" "${HOME}/.gemini/skills" "${HOME}/.agents/skills" "${HOME}/wk/github/andrej-karpathy-skills/skills"; do
        if [[ -d "$candidate" ]]; then
            echo -e "${GREEN}✓ 发现本地技能库: ${candidate}${NC}"
            for skill_path in "${candidate}"/*; do
                if [[ -d "$skill_path" && -f "${skill_path}/SKILL.md" ]]; then
                    skill_name=$(basename "$skill_path")
                    if [[ ! -e "${SKILLS_DIR}/${skill_name}" ]]; then
                        ln -s "$skill_path" "${SKILLS_DIR}/${skill_name}"
                        echo -e "  + 挂载技能: ${CYAN}${skill_name}${NC}"
                        FOUND_ANY=1
                    else
                        echo -e "  ○ 已存在: ${skill_name}"
                        FOUND_ANY=1
                    fi
                fi
            done
        fi
    done
    if [[ "$FOUND_ANY" -eq 0 ]]; then
        echo -e "${YELLOW}! 未找到包含 SKILL.md 的源技能目录${NC}"
    fi
else
    echo -e "\n${BLUE}==> [4/4] 跳过技能挂载 (可传入 -s 参数开启)${NC}"
fi

echo -e "\n${GREEN}${BOLD}部署完成！${NC}"
echo -e "运行以下命令即可验证:"
echo -e "  ${CYAN}omp models${NC}           # 查看已加载的模型矩阵"
echo -e "  ${CYAN}omp \"你好\"${NC}            # 启动交互式会话"
