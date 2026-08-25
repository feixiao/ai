#!/bin/bash
# ==============================================================================
# Claude Code <-> LM Studio 会话数据与配置双向同步工具
# ==============================================================================
# 用途：
#   解决官方 Claude Code (~/.claude) 与本地 LM Studio (~/.lmstudio/claude_config)
#   因目录隔离导致的 --resume 历史会话无法读取、全局规则/Skills 不同步的问题。
#
# 使用方式：
#   ./sync_sessions.sh              # 默认：将官方 ~/.claude 会话增量同步到 LM Studio
#   ./sync_sessions.sh -b           # 双向同步 (两边均保留最新文件)
#   ./sync_sessions.sh -r           # 反向同步：将 LM Studio 会话同步回官方 ~/.claude
#   ./sync_sessions.sh <session-id> # 快速同步单个特定 UUID 会话
# ==============================================================================

set -e

# 颜色输出定义
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

OFFICIAL_DIR="$HOME/.claude"
LMSTUDIO_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.lmstudio/claude_config}"

# 需要同步的会话与上下文子目录
SESSION_SUBDIRS=("projects" "session-env" "file-history" "tasks" "plans" "paste-cache")

# 需要建立共享软链接的全局指令与配置
SHARED_FILES=("CLAUDE.md" "writing-style.md" "mcp_servers.json")
SHARED_DIRS=("skills")

# 打印帮助信息
print_help() {
    cat << EOF
用法: $(basename "$0") [选项] [session-id]

选项:
  -f, --from-official   从官方 Claude (~/.claude) 同步到 LM Studio 配置目录 (默认行为)
  -r, --to-official     从 LM Studio 配置目录反向同步到官方 Claude
  -b, --two-way         双向增量同步 (两边各自同步更新的文件)
  -l, --link-shared     仅软链接全局配置文件 (CLAUDE.md, writing-style.md, skills)
  -h, --help            显示帮助信息

示例:
  $(basename "$0")                                     # 默认增量同步所有官方会话到 LM Studio
  $(basename "$0") -b                                  # 双向同步
  $(basename "$0") 2ce044f6-9934-4e69-b974-c6881e1764da # 仅同步指定 UUID 会话
EOF
}

# 确保目标目录基础结构存在
init_directories() {
    mkdir -p "$OFFICIAL_DIR"
    mkdir -p "$LMSTUDIO_DIR"
    for sub in "${SESSION_SUBDIRS[@]}"; do
        mkdir -p "$OFFICIAL_DIR/$sub"
        mkdir -p "$LMSTUDIO_DIR/$sub"
    done
}

# 软链接共享全局规则与技能
link_shared_configs() {
    printf "${BLUE}🔗 检查并建立全局规则与 Skills 软链接...${NC}\n"

    for file_name in "${SHARED_FILES[@]}"; do
        if [ -f "$OFFICIAL_DIR/$file_name" ]; then
            if [ ! -e "$LMSTUDIO_DIR/$file_name" ]; then
                ln -sf "$OFFICIAL_DIR/$file_name" "$LMSTUDIO_DIR/$file_name"
                printf "  ${GREEN}✓${NC} 链接文件: %s -> ~/.lmstudio/claude_config/%s\n" "$file_name" "$file_name"
            fi
        fi
    done

    for dir_name in "${SHARED_DIRS[@]}"; do
        if [ -d "$OFFICIAL_DIR/$dir_name" ]; then
            if [ ! -e "$LMSTUDIO_DIR/$dir_name" ]; then
                ln -sf "$OFFICIAL_DIR/$dir_name" "$LMSTUDIO_DIR/$dir_name"
                printf "  ${GREEN}✓${NC} 链接目录: %s -> ~/.lmstudio/claude_config/%s\n" "$dir_name" "$dir_name"
            fi
        fi
    done
}

# 单向同步函数
# 参数: $1 (源目录), $2 (目标目录), $3 (描述信息)
sync_directory_data() {
    local source_root="$1"
    local target_root="$2"
    local description="$3"

    printf "${BLUE}📦 同步会话数据: %s...${NC}\n" "$description"

    for sub in "${SESSION_SUBDIRS[@]}"; do
        if [ -d "$source_root/$sub" ]; then
            rsync -au "$source_root/$sub/" "$target_root/$sub/"
        fi
    done

    printf "${GREEN}✓ 会话数据同步完成 (${description})${NC}\n"
}

# 单个特定 UUID 会话的精准同步
# 参数: $1 (会话 UUID)
sync_specific_session() {
    local target_uuid="$1"
    printf "${BLUE}🔍 精准同步特定会话: %s${NC}\n" "$target_uuid"

    local found_count=0

    # 1. 查找 projects 目录下的 session 文件与子目录
    while IFS= read -r project_path; do
        if [ -n "$project_path" ]; then
            local rel_project="${project_path#$OFFICIAL_DIR/projects/}"
            local lm_proj_dir="$LMSTUDIO_DIR/projects/$rel_project"
            mkdir -p "$lm_proj_dir"

            # 复制 jsonl 与可能存在的目录
            if [ -f "$project_path/$target_uuid.jsonl" ]; then
                cp -f "$project_path/$target_uuid.jsonl" "$lm_proj_dir/"
                found_count=$((found_count + 1))
            fi
            if [ -d "$project_path/$target_uuid" ]; then
                cp -rf "$project_path/$target_uuid" "$lm_proj_dir/"
                found_count=$((found_count + 1))
            fi
        fi
    done < <(find "$OFFICIAL_DIR/projects" -mindepth 1 -maxdepth 1 -type d 2>/dev/null)

    # 2. 复制 session-env, file-history, tasks 等以 UUID 命名的文件或目录
    for sub in "session-env" "file-history" "tasks"; do
        if [ -e "$OFFICIAL_DIR/$sub/$target_uuid" ]; then
            mkdir -p "$LMSTUDIO_DIR/$sub"
            cp -rf "$OFFICIAL_DIR/$sub/$target_uuid"* "$LMSTUDIO_DIR/$sub/" 2>/dev/null || true
            found_count=$((found_count + 1))
        fi
    done

    if [ "$found_count" -gt 0 ]; then
        printf "${GREEN}✓ 成功同步会话 [%s] 至 LM Studio 配置环境！${NC}\n" "$target_uuid"
    else
        printf "${YELLOW}⚠️ 在 ~/.claude 中未找到匹配 UUID [%s] 的会话文件。${NC}\n" "$target_uuid"
    fi
}

# ==============================================================================
# 主逻辑入口
# ==============================================================================
init_directories
link_shared_configs

SYNC_MODE="from-official"
TARGET_SESSION_ID=""

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            print_help
            exit 0
            ;;
        -f|--from-official)
            SYNC_MODE="from-official"
            shift
            ;;
        -r|--to-official)
            SYNC_MODE="to-official"
            shift
            ;;
        -b|--two-way)
            SYNC_MODE="two-way"
            shift
            ;;
        -l|--link-shared)
            SYNC_MODE="link-only"
            shift
            ;;
        *)
            # 匹配类似 2ce044f6-9934-4e69-b974-c6881e1764da 的 UUID 参数
            TARGET_SESSION_ID="$1"
            SYNC_MODE="single-session"
            shift
            ;;
    esac
done

case "$SYNC_MODE" in
    "single-session")
        sync_specific_session "$TARGET_SESSION_ID"
        ;;
    "from-official")
        sync_directory_data "$OFFICIAL_DIR" "$LMSTUDIO_DIR" "~/.claude -> ~/.lmstudio/claude_config"
        ;;
    "to-official")
        sync_directory_data "$LMSTUDIO_DIR" "$OFFICIAL_DIR" "~/.lmstudio/claude_config -> ~/.claude"
        ;;
    "two-way")
        sync_directory_data "$OFFICIAL_DIR" "$LMSTUDIO_DIR" "1. ~/.claude -> ~/.lmstudio/claude_config"
        sync_directory_data "$LMSTUDIO_DIR" "$OFFICIAL_DIR" "2. ~/.lmstudio/claude_config -> ~/.claude"
        ;;
    "link-only")
        printf "${GREEN}✓ 共享配置链接完成。${NC}\n"
        ;;
esac
