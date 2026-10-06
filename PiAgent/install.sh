#!/usr/bin/env bash
# ==============================================================================
# Pi Agent (pi-coding-agent) 一键安装、反向代理与模型配置管理脚本
# ==============================================================================
#
# 功能说明：
# 1. 自动化检测 Node.js 环境与 Pi Agent CLI (pi / @earendil-works/pi-coding-agent) 安装状态
# 2. 自动化检测反向代理网关及本地推理引擎 (LM Studio, Ollama, vLLM) 连通性
# 3. 部署或智能合并 models.json 与 settings.json 至全局 (~/.pi/agent/) 或工作区 (.pi/)
# 4. 支持自动备份旧配置、可选安装扩展与基础 Skill 集合
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
INSTALL_SKILLS=0
PROFILE="minimal" # 默认角色: minimal, eng, pm, invest, full
LIST_SKILLS=0
PRUNE_SKILLS=0
FETCH_SKILLS=0
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

${CYAN}基础选项:${NC}
  -g, --global              部署到全局配置目录 (~/.pi/agent/) [默认]
  -p, --project [DIR]       部署到指定工程目录 (默认: 当前目录 ./.pi/)
  -i, --install-cli         若系统未安装 Pi Agent CLI，则自动执行官方安装
  -c, --check               仅检测本地后端/反代服务连通性与模型列表，不写入配置
  -f, --force               强制覆盖目标配置（会自动创建时间戳备份文件）
  -e, --extensions          自动安装推荐扩展 (如 pi-models-discovery 模型自动发现)
      --proxy-url <URL>     快速测试指定的反向代理 BaseURL (如 https://api.proxy.com/v1)
      --proxy-key <KEY>     配合 --proxy-url 测试时使用的 API Key
  -h, --help                显示此帮助信息

${CYAN}技能 (Skills) 选项 (对齐 RECOMMENDED_SKILLS.md 权威规范):${NC}
  -s, --skills              安装高质量 Skill 集合 (根据 --profile 抽取或部署)
      --profile <NAME>      选配技能角色画像: minimal [默认], eng (全栈), pm (产品), invest (投资), full
      --list-skills         打印选定 profile 对应的 Skill 清单后退出
      --prune-skills        清理目标技能目录中不在当前 profile 清单内的旧技能
      --fetch-skills        若本地 Claude 插件缓存缺少某些 Skill，自动从上游 Git 直下

${CYAN}示例:${NC}
  ./install.sh                      # 部署模型与参数配置到 ~/.pi/agent/
  ./install.sh -i -e -s             # 安装 Pi CLI、配置、扩展与精选核心 Skill 集合
  ./install.sh -s --profile eng     # 部署全栈工程师专属 Skill (superpowers, ui-ux, mattpocock, mcp)
  ./install.sh -s --profile pm      # 部署产品经理专属 Skill (PRD/文档, 质询, 商业化, 敏捷协作)
  ./install.sh -s --profile invest  # 部署个人投资者专属 Skill (财报三张表, 研报抽取, 投资论点红队质询)
  ./install.sh --list-skills --profile eng # 仅预览全栈工程师包含的技能清单
  ./install.sh --project . -s       # 为当前项目生成专属配置及本地 .pi/skills/
  ./install.sh --check              # 检查 LM Studio、Ollama 与反代端点连通性
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
# 查看与列出 Skill 清单
# ==============================================================================
list_profile_skills() {
    python3 - "$PROFILE" << 'PY'
import sys

PROFILES = {
    "minimal": [
        "xlsx", "pdf", "docx", "pptx",
        "systematic-debugging", "test-driven-development", "brainstorming", "using-superpowers",
        "using-git-worktrees", "verification-before-completion",
        "grilling", "domain-modeling", "codebase-design",
        "ui-ux-pro-max", "design-system", "ui-styling",
        "planning-with-files",
        "mcp-builder"
    ],
    "eng": [
        "using-superpowers", "brainstorming", "writing-plans", "executing-plans",
        "systematic-debugging", "test-driven-development", "requesting-code-review",
        "receiving-code-review", "verification-before-completion",
        "dispatching-parallel-agents", "subagent-driven-development",
        "finishing-a-development-branch", "using-git-worktrees", "writing-skills",
        "ui-ux-pro-max", "design", "design-system", "ui-styling", "brand", "banner-design", "slides",
        "domain-modeling", "codebase-design", "grilling", "research",
        "resolving-merge-conflicts", "tdd", "wizard", "diagnosing-bugs",
        "mcp-builder", "webapp-testing", "web-artifacts-builder",
        "planning-with-files"
    ],
    "pm": [
        "docx", "pdf", "pptx", "xlsx",
        "grilling", "brainstorming",
        "ui-ux-pro-max", "design", "design-system", "ui-styling", "landing-page-generator",
        "commercial-skills", "pricing-strategist", "commercial-policy", "commercial-forecaster", "deal-desk",
        "product-manager-toolkit", "product-strategist", "product-discovery", "product-analytics",
        "competitive-teardown", "experiment-designer", "roadmap-communicator", "spec-to-repo",
        "saas-scaffolder", "ui-design-system", "ux-researcher-designer",
        "senior-pm", "scrum-master", "jira-expert", "confluence-expert", "atlassian-admin",
        "atlassian-templates", "meeting-analyzer", "team-communications",
        "planning-with-files"
    ],
    "invest": [
        "xlsx", "pdf", "docx", "pptx",
        "grilling", "grill-me", "research", "brainstorming",
        "theme-factory", "frontend-design", "canvas-design", "web-artifacts-builder",
        "planning-with-files"
    ],
    "full": []
}

prof = sys.argv[1]
if prof not in PROFILES:
    print(f"未知 profile: {prof} (可选: minimal, eng, pm, invest, full)", file=sys.stderr)
    sys.exit(1)

if prof == "full":
    print("角色画像: full (全量生态档，安装本地缓存与来源库中找到的所有可用 Skill)")
else:
    skills = PROFILES[prof]
    print(f"角色画像: {prof} (对齐 RECOMMENDED_SKILLS.md 推荐技能，共 {len(skills)} 项):")
    for s in skills:
        print(f"  • {s}")
PY
}

# ==============================================================================
# 安装推荐与定制 Skills (对齐 RECOMMENDED_SKILLS.md 规范)
# ==============================================================================
install_recommended_skills() {
    local target_skills_dir=""
    if [[ "$INSTALL_TARGET" == "global" ]]; then
        target_skills_dir="${TARGET_GLOBAL_DIR}/skills"
    else
        target_skills_dir="${PROJECT_DIR}/.pi/skills"
    fi

    log_info "正在部署技能 (Skills) -> ${target_skills_dir}"
    log_info "所选角色画像 (Profile): ${BOLD}${PROFILE}${NC}"

    mkdir -p "$target_skills_dir"

    python3 - "$target_skills_dir" "$PROFILE" "$PRUNE_SKILLS" "$FETCH_SKILLS" "$HOME/.cache/pi-skills" << 'PY'
import os, sys, shutil, re, subprocess

dest_dir = os.path.abspath(sys.argv[1])
profile = sys.argv[2]
prune = sys.argv[3] == "1"
fetch = sys.argv[4] == "1"
fetch_cache_dir = os.path.abspath(sys.argv[5])

PROFILES = {
    "minimal": [
        "xlsx", "pdf", "docx", "pptx",
        "systematic-debugging", "test-driven-development", "brainstorming", "using-superpowers",
        "using-git-worktrees", "verification-before-completion",
        "grilling", "domain-modeling", "codebase-design",
        "ui-ux-pro-max", "design-system", "ui-styling",
        "planning-with-files",
        "mcp-builder"
    ],
    "eng": [
        "using-superpowers", "brainstorming", "writing-plans", "executing-plans",
        "systematic-debugging", "test-driven-development", "requesting-code-review",
        "receiving-code-review", "verification-before-completion",
        "dispatching-parallel-agents", "subagent-driven-development",
        "finishing-a-development-branch", "using-git-worktrees", "writing-skills",
        "ui-ux-pro-max", "design", "design-system", "ui-styling", "brand", "banner-design", "slides",
        "domain-modeling", "codebase-design", "grilling", "research",
        "resolving-merge-conflicts", "tdd", "wizard", "diagnosing-bugs",
        "mcp-builder", "webapp-testing", "web-artifacts-builder",
        "planning-with-files"
    ],
    "pm": [
        "docx", "pdf", "pptx", "xlsx",
        "grilling", "brainstorming",
        "ui-ux-pro-max", "design", "design-system", "ui-styling", "landing-page-generator",
        "commercial-skills", "pricing-strategist", "commercial-policy", "commercial-forecaster", "deal-desk",
        "product-manager-toolkit", "product-strategist", "product-discovery", "product-analytics",
        "competitive-teardown", "experiment-designer", "roadmap-communicator", "spec-to-repo",
        "saas-scaffolder", "ui-design-system", "ux-researcher-designer",
        "senior-pm", "scrum-master", "jira-expert", "confluence-expert", "atlassian-admin",
        "atlassian-templates", "meeting-analyzer", "team-communications",
        "planning-with-files"
    ],
    "invest": [
        "xlsx", "pdf", "docx", "pptx",
        "grilling", "grill-me", "research", "brainstorming",
        "theme-factory", "frontend-design", "canvas-design", "web-artifacts-builder",
        "planning-with-files"
    ],
    "full": []
}

FETCH_SOURCES = {
    "planning-with-files": ("https://github.com/OthmanAdi/planning-with-files.git", [".pi/skills/planning-with-files", "skills/planning-with-files"]),
    "grilling": ("https://github.com/FeatherHunter/dsh-mattpocock-skills-deck.git", ["package/bundled-skills/grilling"]),
    "domain-modeling": ("https://github.com/FeatherHunter/dsh-mattpocock-skills-deck.git", ["package/bundled-skills/domain-modeling"]),
    "codebase-design": ("https://github.com/FeatherHunter/dsh-mattpocock-skills-deck.git", ["package/bundled-skills/codebase-design"]),
    "ui-ux-pro-max": ("https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git", [".claude/skills/ui-ux-pro-max", "cli/assets/skills/ui-ux-pro-max"]),
    "design-system": ("https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git", [".claude/skills/design-system", "cli/assets/skills/design-system"]),
    "ui-styling": ("https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git", [".claude/skills/ui-styling", "cli/assets/skills/ui-styling"]),
    "systematic-debugging": ("https://github.com/anthropics/claude-plugins-official.git", ["plugins/superpowers/skills/systematic-debugging"]),
    "test-driven-development": ("https://github.com/anthropics/claude-plugins-official.git", ["plugins/superpowers/skills/test-driven-development"]),
    "brainstorming": ("https://github.com/anthropics/claude-plugins-official.git", ["plugins/superpowers/skills/brainstorming"]),
    "using-superpowers": ("https://github.com/anthropics/claude-plugins-official.git", ["plugins/superpowers/skills/using-superpowers"]),
    "xlsx": ("https://github.com/anthropics/skills.git", ["skills/xlsx"]),
    "pdf": ("https://github.com/anthropics/skills.git", ["skills/pdf"]),
    "docx": ("https://github.com/anthropics/skills.git", ["skills/docx"]),
    "pptx": ("https://github.com/anthropics/skills.git", ["skills/pptx"]),
    "mcp-builder": ("https://github.com/anthropics/skills.git", ["skills/mcp-builder"]),
    "commercial-skills": ("https://github.com/alirezarezvani/claude-skills.git", ["skills/commercial-skills", "skills/commercial/pricing-strategist"]),
    "product-skills": ("https://github.com/alirezarezvani/claude-skills.git", ["skills/product-skills", "skills/product/product-manager-toolkit"]),
    "pm-skills": ("https://github.com/alirezarezvani/claude-skills.git", ["skills/pm-skills", "skills/project/senior-pm"])
}

if profile not in PROFILES:
    print(f"\033[0;31m[ERROR]\033[0m 未知的 profile: '{profile}'。可选: minimal, eng, pm, invest, full", file=sys.stderr)
    sys.exit(1)

def get_sort_score(p):
    score = 0
    if ".pi/skills" in p:
        score += 1000
    if "cache" in p:
        score += 500
    ver_match = re.search(r'/(\d+\.\d+[\.\d]*)/', p)
    if ver_match:
        try:
            parts = [int(x) for x in ver_match.group(1).split('.')]
            score += parts[0] * 100 + (parts[1] if len(parts) > 1 else 0)
        except Exception:
            pass
    return score

search_roots = [
    os.path.expanduser("~/.claude/plugins/cache"),
    os.path.expanduser("~/.claude/plugins/marketplaces"),
    os.path.expanduser("~/.codebuddy/plugins/marketplaces"),
    fetch_cache_dir
]

all_skills = {}
for root in search_roots:
    if not os.path.exists(root):
        continue
    for dirpath, dirnames, filenames in os.walk(root):
        if "SKILL.md" in filenames:
            skill_name = os.path.basename(dirpath)
            if skill_name in ["skills", "template"]:
                continue
            if skill_name not in all_skills:
                all_skills[skill_name] = []
            all_skills[skill_name].append(dirpath)

for name in all_skills:
    all_skills[name].sort(key=get_sort_score, reverse=True)

target_skills = PROFILES[profile] if profile != "full" else sorted(list(all_skills.keys()))

installed_count = 0
missing_skills = []

for skill in target_skills:
    src_dir = None
    if skill in all_skills and len(all_skills[skill]) > 0:
        src_dir = all_skills[skill][0]
    elif fetch and skill in FETCH_SOURCES:
        repo_url, subdirs = FETCH_SOURCES[skill]
        repo_name = os.path.splitext(os.path.basename(repo_url))[0]
        clone_dest = os.path.join(fetch_cache_dir, repo_name)
        if not os.path.exists(clone_dest):
            os.makedirs(fetch_cache_dir, exist_ok=True)
            print(f"  • 正在从上游 Git 下载: {repo_url} ...")
            subprocess.run(["git", "clone", "--depth", "1", "-q", repo_url, clone_dest], check=False)
        for sub in subdirs:
            candidate = os.path.join(clone_dest, sub)
            if os.path.exists(os.path.join(candidate, "SKILL.md")):
                src_dir = candidate
                break

    if src_dir and os.path.exists(os.path.join(src_dir, "SKILL.md")):
        dst_dir = os.path.join(dest_dir, skill)
        if os.path.exists(dst_dir):
            if os.path.islink(dst_dir):
                os.unlink(dst_dir)
            else:
                shutil.rmtree(dst_dir)
        shutil.copytree(src_dir, dst_dir)
        installed_count += 1
        print(f"  ✓ 已安装: {skill:<28} (来源: {os.path.basename(os.path.dirname(src_dir))})")
    else:
        missing_skills.append(skill)

if prune:
    for existing in os.listdir(dest_dir):
        existing_path = os.path.join(dest_dir, existing)
        if os.path.isdir(existing_path) and profile != "full" and existing not in target_skills:
            shutil.rmtree(existing_path)
            print(f"  - 已清理非当前 profile 技能: {existing}")

print(f"\n\033[0;32m[OK]\033[0m 成功部署 {installed_count} 个 Skill 到 {dest_dir}")
if missing_skills:
    print(f"\033[0;33m[WARN]\033[0m 暂未在本地缓存中找到 {len(missing_skills)} 个技能: {', '.join(missing_skills)}")
    print("      提示: 可加上 --fetch-skills 参数允许脚本从 Git 上游自动下载缺失技能。")
PY

    if command -v pi >/dev/null 2>&1; then
        echo ""
        log_success "Pi Agent CLI 已就绪。启动 Pi (命令: pi) 进入交互式会话，"
        echo -e "     可在 TUI 会话中直接使用 ${BOLD}/skill:<skill-name>${NC} 显式调用已部署的技能。"
        echo -e "     运行 ${BOLD}pi list${NC} 可查看已安装的扩展与全局包。"
    else
        echo ""
        log_info "提示: 技能文件已准备完毕。系统安装 Pi Agent (./install.sh -i) 后启动即可无缝加载。"
    fi
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
            -s|--skills)
                INSTALL_SKILLS=1
                shift
                ;;
            --profile=*)
                PROFILE="${1#--profile=}"
                INSTALL_SKILLS=1
                shift
                ;;
            --profile)
                if [[ $# -gt 1 && ! "$2" =~ ^- ]]; then
                    PROFILE="$2"
                    INSTALL_SKILLS=1
                    shift 2
                else
                    log_error "--profile 参数缺少角色名称 (例如: minimal, eng, pm, invest, full)"
                    exit 1
                fi
                ;;
            --list-skills)
                LIST_SKILLS=1
                shift
                ;;
            --prune-skills)
                PRUNE_SKILLS=1
                shift
                ;;
            --fetch-skills)
                FETCH_SKILLS=1
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

    if [[ $LIST_SKILLS -eq 1 ]]; then
        list_profile_skills
        exit 0
    fi

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

    if [[ $INSTALL_SKILLS -eq 1 ]]; then
        install_recommended_skills
    fi
}

main "$@"
