#!/usr/bin/env bash
#
# Antigravity (agy) Skills & Agents 一键安装与模块化管理脚本
# ---------------------------------------------------------------
# 从 Claude Code 已安装的插件缓存与全局 agents 目录中抽取内容，适配为
# Antigravity / Gemini CLI 的目录与格式，安装到 ~/.gemini/ 下：
#
#   ~/.gemini/skills/<name>/SKILL.md
#   ~/.gemini/agents/<name>.md
#
# 用法：
#   ./install.sh                # 默认极简模式：仅安装最核心 5 个工程技能（推荐，零膨胀）
#   ./install.sh --core         # 核心完整模式：完整工程规范 (14 个) + 规划 (2 个) + 文档 (4 个)
#   ./install.sh --docs         # 叠加原生多模态长文档支持 (PDF/DOCX/XLSX/PPTX)
#   ./install.sh --ui-ux        # 叠加 UI/UX 前端设计套件 (7 个)
#   ./install.sh --biz          # 叠加产品/项目/商业化专家技能包 (~18 个)
#   ./install.sh --mattpocock   # 叠加 Matt Pocock 技能集 (25 个)
#   ./install.sh --all          # 全量模式：安装全部技能包 (80+ 个)
#   ./install.sh --clean        # 清空目标目录后重新安装选定模块
#   ./install.sh --clean-only   # 仅清理已安装的 skills 与 agents
#   ./install.sh --dry-run      # 预演模式：只打印将要执行的动作
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
CLEAN_MODE=0
CLEAN_ONLY=0

# 默认极简模式：仅安装最核心工程技能包（推荐，零 Prompt 膨胀）
INSTALL_SUPERPOWERS_FULL=0
INSTALL_DOCS=0
INSTALL_PLANNING=1
INSTALL_UI_UX=0
INSTALL_BIZ=0
INSTALL_MATTPOCOCK=0
INSTALL_ANTHROPIC_EXTRAS=0

show_help() {
  cat <<'EOF'
Antigravity (agy) Skills & Agents 一键安装与模块化管理脚本
---------------------------------------------------------------
从 Claude Code 已安装的插件缓存与全局 agents 目录中抽取内容，适配为
Antigravity / Gemini CLI 的目录与格式，安装到 ~/.gemini/ 下：

  ~/.gemini/skills/<name>/SKILL.md
  ~/.gemini/agents/<name>.md

用法：
  ./install.sh                # 默认极简模式：仅安装最核心工程技能（推荐，零 Prompt 膨胀）
  ./install.sh --all          # 全量生态模式：安装全部技能包 (80+ 个，按需开启)
  ./install.sh --core         # 核心完整模式：工程规范 (14 个) + 规划 (2 个) + 文档 (4 个)
  ./install.sh --docs         # 叠加多模态长文档支持 (PDF/DOCX/XLSX/PPTX)
  ./install.sh --ui-ux        # 叠加 UI/UX 前端设计技能包 (7 个)
  ./install.sh --biz          # 叠加产品/项目/商业化专家技能包 (~18 个)
  ./install.sh --mattpocock   # 叠加 Matt Pocock 技能集 (25 个)
  ./install.sh --clean        # 清空目标目录后重新安装选定模块
  ./install.sh --clean-only   # 仅清理已安装的 skills 与 agents
  ./install.sh --dry-run      # 预演模式：只打印将要执行的动作
  -h, --help                  # 显示此帮助信息

环境变量：
  CLAUDE_CACHE    默认 ~/.claude/plugins/cache
  CLAUDE_AGENTS   默认 ~/.claude/agents
  GEMINI_HOME     默认 ~/.gemini
EOF
}

for arg in "$@"; do
  case "$arg" in
    --dry-run)
      DRY_RUN=1
      ;;
    --clean)
      CLEAN_MODE=1
      ;;
    --clean-only)
      CLEAN_MODE=1
      CLEAN_ONLY=1
      ;;
    --minimal)
      INSTALL_SUPERPOWERS_FULL=0
      INSTALL_DOCS=0
      INSTALL_PLANNING=1
      INSTALL_UI_UX=0
      INSTALL_BIZ=0
      INSTALL_MATTPOCOCK=0
      INSTALL_ANTHROPIC_EXTRAS=0
      ;;
    --core)
      INSTALL_SUPERPOWERS_FULL=1
      INSTALL_DOCS=1
      INSTALL_PLANNING=1
      INSTALL_UI_UX=0
      INSTALL_BIZ=0
      INSTALL_MATTPOCOCK=0
      INSTALL_ANTHROPIC_EXTRAS=0
      ;;
    --docs)
      INSTALL_DOCS=1
      ;;
    --ui-ux)
      INSTALL_UI_UX=1
      ;;
    --biz|--product)
      INSTALL_BIZ=1
      ;;
    --mattpocock)
      INSTALL_MATTPOCOCK=1
      ;;
    --all|--full)
      INSTALL_SUPERPOWERS_FULL=1
      INSTALL_DOCS=1
      INSTALL_PLANNING=1
      INSTALL_UI_UX=1
      INSTALL_BIZ=1
      INSTALL_MATTPOCOCK=1
      INSTALL_ANTHROPIC_EXTRAS=1
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "未知参数: $arg" >&2
      echo "使用 -h 或 --help 查看帮助" >&2
      exit 2
      ;;
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
# 1. 前置检查与模块规划
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

if [ "$CLEAN_MODE" = "1" ]; then
  info "清理现有技能与角色目录..."
  run rm -rf "$DEST/skills" "$DEST/agents" "$DEST/config/skills" "$DEST/config/agents"
  if [ "$CLEAN_ONLY" = "1" ]; then
    info "已成功清理 $DEST/skills 与 $DEST/agents"
    exit 0
  fi
fi

run mkdir -p "$DEST/skills" "$DEST/agents" "$DEST/config"

# Antigravity (agy) 全局扫描路径位于 ~/.gemini/config/，建立软链接确保自动加载生效
if [ -L "$DEST/config/skills" ] || [ ! -e "$DEST/config/skills" ]; then
  run ln -sfn "$DEST/skills" "$DEST/config/skills"
fi
if [ -L "$DEST/config/agents" ] || [ ! -e "$DEST/config/agents" ]; then
  run ln -sfn "$DEST/agents" "$DEST/config/agents"
fi

info "已选安装方案与模块："
if [ "$INSTALL_SUPERPOWERS_FULL" = "1" ]; then
  echo "  - 工程流程 (superpowers):              ✓ 完整工程规范 (14 个)"
else
  echo "  - 工程流程 (superpowers):              ✓ 极简核心 (调试/TDD/头脑风暴/验收 4 个)"
fi
echo "  - 跨会话设计规划 (planning-with-files):  ✓ 启用 (2 个)"
echo "  - 原生多模态文档 (PDF/DOCX/XLSX/PPTX):  $([ "$INSTALL_DOCS" = "1" ] && echo "✓ 启用 (4 个)" || echo "- 未勾选 (可选 --docs)")"
echo "  - 前端设计系统 (ui-ux-pro-max):          $([ "$INSTALL_UI_UX" = "1" ] && echo "✓ 启用 (7 个)" || echo "- 未勾选 (可选 --ui-ux)")"
echo "  - 产品与商业化 (product/biz):            $([ "$INSTALL_BIZ" = "1" ] && echo "✓ 启用 (~18 个)" || echo "- 未勾选 (可选 --biz)")"
echo "  - Matt Pocock 技能集:                   $([ "$INSTALL_MATTPOCOCK" = "1" ] && echo "✓ 启用 (25 个)" || echo "- 未勾选 (可选 --mattpocock)")"
if [ "$INSTALL_ANTHROPIC_EXTRAS" = "1" ]; then
  echo "  - Anthropic 扩展实验组件:               ✓ 启用"
fi

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

# 3.1 superpowers (极简 4 个 或 完整 14 个)
SP="$(latest_version "$CLAUDE_CACHE/claude-plugins-official/superpowers" || true)"
if [ -n "${SP:-}" ]; then
  if [ "$INSTALL_SUPERPOWERS_FULL" = "1" ]; then
    copy_skills_in "${SP}skills"
  else
    for s in using-superpowers brainstorming systematic-debugging test-driven-development verification-before-completion; do
      [ -d "${SP}skills/$s" ] && copy_skill_dir "${SP}skills/$s"
    done
  fi
fi

# 3.2 planning-with-files (跨会话持久化设计 2 个)
if [ "$INSTALL_PLANNING" = "1" ]; then
  PF="$(latest_version "$CLAUDE_CACHE/planning-with-files/planning-with-files" || true)"
  if [ -n "${PF:-}" ]; then
    [ -d "${PF}skills/planning-with-files" ] && copy_skill_dir "${PF}skills/planning-with-files"
    if [ -d "${PF}skills/i18n/planning-with-files-zh" ]; then
      copy_skill_dir "${PF}skills/i18n/planning-with-files-zh"
    fi
  fi
fi

# 3.3 document-skills (精确安装 4 大原生多模态核心文档技能: PDF/DOCX/XLSX/PPTX)
if [ "$INSTALL_DOCS" = "1" ]; then
  DOCS="$(latest_version "$CLAUDE_CACHE/anthropic-agent-skills/document-skills" || true)"
  if [ -n "${DOCS:-}" ]; then
    for doc_skill in pdf docx xlsx pptx; do
      [ -d "${DOCS}skills/$doc_skill" ] && copy_skill_dir "${DOCS}skills/$doc_skill"
    done
  fi
fi

# 3.4 anthropic-agent-skills 额外套件与示例技能 (mcp-builder / skill-creator / theme-factory 等)
if [ "$INSTALL_ANTHROPIC_EXTRAS" = "1" ]; then
  for pkg in document-skills example-skills; do
    PKG_PATH="$(latest_version "$CLAUDE_CACHE/anthropic-agent-skills/$pkg" || true)"
    if [ -n "${PKG_PATH:-}" ] && [ -d "${PKG_PATH}skills" ]; then
      for s in "${PKG_PATH}skills"/*/; do
        [ -d "$s" ] || continue
        name="$(basename "$s")"
        case "$name" in
          pdf|docx|xlsx|pptx)
            [ "$INSTALL_DOCS" = "1" ] || copy_skill_dir "$s"
            ;;
          *) copy_skill_dir "$s" ;;
        esac
      done
    fi
  done
fi

# 3.5 ui-ux-pro-max 前端与界面设计系统
if [ "$INSTALL_UI_UX" = "1" ]; then
  UX="$(latest_version "$CLAUDE_CACHE/ui-ux-pro-max-skill/ui-ux-pro-max" || true)"
  [ -n "${UX:-}" ] && copy_skills_in "${UX}.claude/skills"
fi

# 3.6 垂类专家技能包：产品 / 项目管理 / 商业化
if [ "$INSTALL_BIZ" = "1" ]; then
  for pkg in product-skills pm-skills commercial-skills; do
    V="$(latest_version "$CLAUDE_CACHE/claude-code-skills/$pkg" || true)"
    [ -n "${V:-}" ] && copy_skills_in "${V}skills"
  done
fi

# 3.7 mattpocock-skills (engineering & productivity)
if [ "$INSTALL_MATTPOCOCK" = "1" ]; then
  MP="$(latest_version "$CLAUDE_CACHE/mattpocock/mattpocock-skills" || true)"
  if [ -n "${MP:-}" ]; then
    copy_skills_in "${MP}skills/engineering"
    copy_skills_in "${MP}skills/productivity"
  fi
fi

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
                    # 规范化 name 为文件标识符（如 design-ux-architect）
                    clean_stem = re.sub(r"[^A-Za-z0-9_-]", "-", stem).strip("-")
                    new_lines.append(f"name: {clean_stem}")
                    continue
                if re.match(r"^model:", line):
                    new_lines.append("model: inherit")
                    continue
                new_lines.append(line)
            if not has_name:
                clean_stem = re.sub(r"[^A-Za-z0-9_-]", "-", stem).strip("-")
                new_lines.insert(0, f"name: {clean_stem}")
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

if [ "$INSTALL_SUPERPOWERS_FULL" = "0" ] && [ "$INSTALL_DOCS" = "0" ] && [ "$INSTALL_UI_UX" = "0" ] && [ "$INSTALL_BIZ" = "0" ] && [ "$INSTALL_MATTPOCOCK" = "0" ]; then
  echo ""
  echo "提示：当前为【默认极简模式】(仅 5 个高频工程核心技能)，实现最轻量的 Prompt 开销。"
  echo "若需其他模块，可自由叠加参数："
  echo "  ./install.sh --core         # 切换为完整工程+多模态文档核心包 (20 个)"
  echo "  ./install.sh --docs         # 叠加 PDF/DOCX/XLSX/PPTX 多模态文档支持 (4 个)"
  echo "  ./install.sh --ui-ux        # 叠加 UI/UX 前端设计技能 (7 个)"
  echo "  ./install.sh --biz          # 叠加产品/项目管理/商业化技能 (~18 个)"
  echo "  ./install.sh --mattpocock   # 叠加 Matt Pocock 技能集 (25 个)"
  echo "  ./install.sh --all          # 全量安装全部技能 (80+ 个)"
  echo "  ./install.sh --clean        # 清空旧目录后重新安装"
fi
echo ""
echo "常用验证命令："
echo "  agy agents            # 列出可用角色专家"
echo "  agy mcp list          # 查看当前启用的 MCP 服务"
echo "  agy -p 'Hello'        # 快速测试连通性"
echo "==============================================================="
