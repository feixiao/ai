#!/usr/bin/env bash
#
# Antigravity (agy) Skills & Agents 一键安装脚本
# ---------------------------------------------------------------
# 从 Claude Code 已安装的插件缓存与全局 agents 目录中抽取内容，适配为
# Antigravity / Gemini CLI 的目录与格式，安装到 ~/.gemini/ 下：
#
#   ~/.gemini/skills/<name>/SKILL.md
#   ~/.gemini/agents/<name>.md
#
# 用法：
#   ./install.sh              # 安装全部（工程 / 产品 / 设计 / 商业等系列）
#   ./install.sh --dry-run    # 预演模式：只打印将要执行的动作
#
# 可用环境变量覆盖来源与目标：
#   CLAUDE_CACHE    默认 ~/.claude/plugins/cache
#   CLAUDE_AGENTS   默认 ~/.claude/agents
#   GEMINI_HOME     默认 ~/.gemini
#
set -euo pipefail

CLAUDE_CACHE="${CLAUDE_CACHE:-$HOME/.claude/plugins/cache}"
CLAUDE_AGENTS="${CLAUDE_AGENTS:-$HOME/.claude/agents}"
DEST="${GEMINI_HOME:-$HOME/.gemini}"
DRY_RUN=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) echo "未知参数: $arg" >&2; exit 2 ;;
  esac
done

info() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }

run() {
  if [ "$DRY_RUN" = "1" ]; then echo "  [dry-run] $*"; else "$@"; fi
}

# 取插件目录下最新的版本目录（形如 <plugin>/<version>/）
latest_version() {
  local parent="$1"
  [ -d "$parent" ] || return 0
  local res
  res="$(ls -d "$parent"/*/ 2>/dev/null | sort -V | tail -1 || true)"
  [ -n "$res" ] && echo "$res"
}

copy_skill_dir() {
  local src="${1%/}" name
  name="$(basename "$src")"
  run rm -rf "$DEST/skills/$name"
  run cp -R "$src" "$DEST/skills/$name"
}

copy_skills_in() {
  local p
  [ -d "$1" ] || return 0
  for p in "$1"/*/; do
    [ -d "$p" ] || continue
    copy_skill_dir "$p"
  done
}

# ===============================================================
# 1. 前置检查与目录初始化
# ===============================================================
info "检查环境与依赖..."
command -v python3 >/dev/null 2>&1 || { warn "缺少 python3"; exit 1; }

if [ ! -d "$CLAUDE_CACHE" ]; then
  warn "未找到 Claude 插件缓存: $CLAUDE_CACHE"
  warn "请先安装基础插件后再执行此脚本"
  exit 1
fi

info "来源插件缓存: $CLAUDE_CACHE"
info "目标目录:     $DEST"
run mkdir -p "$DEST/skills" "$DEST/agents"

# ===============================================================
# 2. 阶段一：安装与适配 Agents
# ===============================================================
info "阶段 1/3: 抽取与安装 Agents -> $DEST/agents"

# 2.1 从 ~/.claude/agents 提取
if [ -d "$CLAUDE_AGENTS" ]; then
  for f in "$CLAUDE_AGENTS"/*.md; do
    [ -f "$f" ] || continue
    run cp "$f" "$DEST/agents/$(basename "$f")"
  done
fi

# 2.2 补充官方 code-simplifier agent
CS="$(latest_version "$CLAUDE_CACHE/claude-plugins-official/code-simplifier" || true)"
if [ -n "${CS:-}" ] && [ -f "${CS}agents/code-simplifier.md" ]; then
  run cp "${CS}agents/code-simplifier.md" "$DEST/agents/code-simplifier.md"
fi

# ===============================================================
# 3. 阶段二：安装 Skills
# ===============================================================
info "阶段 2/3: 抽取与安装 Skills -> $DEST/skills"

# 3.1 document-skills (PDF/DOCX/XLSX/PPTX)
DOCS="$(latest_version "$CLAUDE_CACHE/anthropic-agent-skills/document-skills" || true)"
[ -n "${DOCS:-}" ] && copy_skills_in "${DOCS}skills"

# 3.2 superpowers (核心工程流程: TDD, 调试, 规划等)
SP="$(latest_version "$CLAUDE_CACHE/claude-plugins-official/superpowers" || true)"
[ -n "${SP:-}" ] && copy_skills_in "${SP}skills"

# 3.3 mattpocock-skills (engineering & productivity)
MP="$(latest_version "$CLAUDE_CACHE/mattpocock/mattpocock-skills" || true)"
if [ -n "${MP:-}" ]; then
  copy_skills_in "${MP}skills/engineering"
  copy_skills_in "${MP}skills/productivity"
fi

# 3.4 planning-with-files (跨会话持久化设计)
PF="$(latest_version "$CLAUDE_CACHE/planning-with-files/planning-with-files" || true)"
if [ -n "${PF:-}" ]; then
  [ -d "${PF}skills/planning-with-files" ] && copy_skill_dir "${PF}skills/planning-with-files"
  if [ -d "${PF}skills/i18n/planning-with-files-zh" ]; then
    run rm -rf "$DEST/skills/planning-with-files-zh"
    run cp -R "${PF}skills/i18n/planning-with-files-zh" "$DEST/skills/planning-with-files-zh"
  fi
fi

# 3.5 ui-ux-pro-max 前端与界面设计系统
UX="$(latest_version "$CLAUDE_CACHE/ui-ux-pro-max-skill/ui-ux-pro-max" || true)"
[ -n "${UX:-}" ] && copy_skills_in "${UX}.claude/skills"

# 3.6 垂类专家技能包：产品 / 项目管理 / 商业化
for pkg in product-skills pm-skills commercial-skills; do
  V="$(latest_version "$CLAUDE_CACHE/claude-code-skills/$pkg" || true)"
  [ -n "${V:-}" ] && copy_skills_in "${V}skills"
done

# ===============================================================
# 4. 阶段三：格式适配与环境变量改写 (Frontmatter & Path Rewriting)
# ===============================================================
info "阶段 3/3: 格式适配与环境变量改写..."

python3 - "$DEST" "$DRY_RUN" <<'PY'
import sys, os, re

dest, dry_run = sys.argv[1], sys.argv[2] == "1"
agents_dir = os.path.join(dest, "agents")
skills_dir = os.path.join(dest, "skills")

# 4.1 适配 Agents Frontmatter
if os.path.exists(agents_dir):
    for fn in os.listdir(agents_dir):
        if not fn.endswith(".md"):
            continue
        p = os.path.join(agents_dir, fn)
        stem = os.path.splitext(fn)[0]
        try:
            with open(p, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            continue

        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
        if not m:
            clean_stem = re.sub(r"[^A-Za-z0-9_-]", "-", stem).strip("-")
            out = f"---\nname: {clean_stem}\n---\n\n" + text
        else:
            fm, body = m.group(1), m.group(2)
            lines = fm.splitlines()
            new_lines = []
            has_name = False
            for line in lines:
                if re.match(r"^(emoji|color):", line):
                    continue
                if re.match(r"^name:", line):
                    has_name = True
                    val = line.split(":", 1)[1].strip().strip("\"'")
                    clean = re.sub(r"[^A-Za-z0-9_-]", "-", val).strip("-")
                    new_lines.append(f"name: {clean or stem}")
                    continue
                if re.match(r"^model:", line):
                    new_lines.append("model: inherit")
                    continue
                new_lines.append(line)
            if not has_name:
                new_lines.insert(0, f"name: {stem}")
            out = "---\n" + "\n".join(new_lines) + "\n---\n" + body

        if not dry_run and out != text:
            with open(p, "w", encoding="utf-8") as f:
                f.write(out)

# 4.2 适配 Skills 中的占位符与环境路径
replaces = [
    ("${CLAUDE_PLUGIN_ROOT}", "${GEMINI_SKILL_DIR}"),
    ("${CLAUDE_SKILL_DIR}", "${GEMINI_SKILL_DIR}"),
    ("~/.claude/skills", "~/.gemini/skills"),
    ("$HOME/.claude/skills", "$HOME/.gemini/skills"),
]

for root_dir in [skills_dir, agents_dir]:
    if not os.path.exists(root_dir):
        continue
    for root, _, files in os.walk(root_dir):
        for fn in files:
            if not (fn.endswith(".md") or fn.endswith(".sh") or fn.endswith(".py") or fn.endswith(".json")):
                continue
            p = os.path.join(root, fn)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                new_content = content
                for old, new in replaces:
                    new_content = new_content.replace(old, new)
                if not dry_run and new_content != content:
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(new_content)
            except Exception:
                pass
PY

info "所有适配与安装工作已就绪！"
echo ""
echo "==============================================================="
echo "Antigravity (agy) 生态部署完成！"
echo "  - Skills 安装路径: $DEST/skills"
echo "  - Agents 安装路径: $DEST/agents"
if [ "$DRY_RUN" = "0" ]; then
  skills_count=$(find "$DEST/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  agents_count=$(find "$DEST/agents" -mindepth 1 -maxdepth 1 -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
  echo "  - 实际部署: $skills_count 个 Skills, $agents_count 个 Agents"
fi
echo ""
echo "常用验证命令："
echo "  agy agents            # 列出可用角色专家"
echo "  agy mcp list          # 查看当前启用的 MCP 服务"
echo "  agy -p 'Hello'        # 快速测试连通性"
echo "==============================================================="
