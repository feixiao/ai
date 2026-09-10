#!/usr/bin/env bash
#
# CodeBuddy Skills / Agents / Commands 一键安装脚本
# ---------------------------------------------------------------
# 从 Claude Code 已安装的插件缓存与全局 agents 目录中抽取内容，适配为
# CodeBuddy 的目录与格式，安装到 ~/.codebuddy/ 下：
#
#   ~/.codebuddy/skills/<name>/SKILL.md
#   ~/.codebuddy/agents/<name>.md
#   ~/.codebuddy/commands/<name>.md
#
# 用法：
#   ./install.sh              # 安装全部（工程 / 产品 / 投资 三类角色）
#   ./install.sh --dry-run    # 只打印将要执行的动作
#
# 可用环境变量覆盖来源与目标：
#   CLAUDE_CACHE    默认 ~/.claude/plugins/cache
#   CLAUDE_AGENTS   默认 ~/.claude/agents
#   CODEBUDDY_HOME  默认 ~/.codebuddy
#
set -euo pipefail

CLAUDE_CACHE="${CLAUDE_CACHE:-$HOME/.claude/plugins/cache}"
CLAUDE_AGENTS="${CLAUDE_AGENTS:-$HOME/.claude/agents}"
DEST="${CODEBUDDY_HOME:-$HOME/.codebuddy}"
DRY_RUN=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "未知参数: $arg" >&2; exit 2 ;;
  esac
done

info() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }

run() {
  if [ "$DRY_RUN" = "1" ]; then echo "  [dry-run] $*"; else "$@"; fi
}

# 取插件目录下最新的版本目录（形如 <plugin>/<version>/）
latest_version() { ls -d "$1"/*/ 2>/dev/null | sort -V | tail -1; }

copy_skill_dir() { # $1 = 源 skill 目录
  local src="${1%/}" name
  name="$(basename "$src")"
  run rm -rf "$DEST/skills/$name"
  run cp -R "$src" "$DEST/skills/$name"
}

copy_skills_in() { # $1 = 含若干 skill 子目录的父目录
  local p
  for p in "$1"/*/; do
    [ -d "$p" ] || continue
    copy_skill_dir "$p"
  done
}

require_dir() {
  [ -d "$1" ] || { warn "缺少目录：$1（跳过）"; return 1; }
}

info "来源： $CLAUDE_CACHE"
info "目标： $DEST"
run mkdir -p "$DEST/skills" "$DEST/agents" "$DEST/commands"

# =====================================================================
# 1. Agents —— agency-agents-zh 专家角色 + 官方 code-simplifier
# =====================================================================
info "安装 Agents -> $DEST/agents"
if require_dir "$CLAUDE_AGENTS"; then
  for f in "$CLAUDE_AGENTS"/*.md; do
    [ -f "$f" ] || continue
    run cp "$f" "$DEST/agents/$(basename "$f")"
  done
fi

CS_VER="$(latest_version "$CLAUDE_CACHE/claude-plugins-official/code-simplifier" || true)"
if [ -n "${CS_VER:-}" ] && [ -f "${CS_VER}agents/code-simplifier.md" ]; then
  run cp "${CS_VER}agents/code-simplifier.md" "$DEST/agents/code-simplifier.md"
fi

# =====================================================================
# 2. Skills —— 按插件来源分批复制
# =====================================================================
info "安装 Skills -> $DEST/skills"

# 2.1 Anthropic 官方文档三剑客（xlsx / pdf / docx / pptx / mcp-builder 等）
DS="$(latest_version "$CLAUDE_CACHE/anthropic-agent-skills/document-skills" || true)"
[ -n "${DS:-}" ] && copy_skills_in "${DS}skills"

# 2.2 superpowers 工程方法论全家桶（TDD / 根因调试 / worktree / 头脑风暴 等）
SP="$(latest_version "$CLAUDE_CACHE/claude-plugins-official/superpowers" || true)"
[ -n "${SP:-}" ] && copy_skills_in "${SP}skills"

# 2.3 mattpocock-skills —— 只取 engineering / productivity 两个稳定目录
MP="$(latest_version "$CLAUDE_CACHE/mattpocock/mattpocock-skills" || true)"
if [ -n "${MP:-}" ]; then
  copy_skills_in "${MP}skills/engineering"
  copy_skills_in "${MP}skills/productivity"
fi

# 2.4 planning-with-files 持久化跨会话规划（英文主版 + 中文版）
PF="$(latest_version "$CLAUDE_CACHE/planning-with-files/planning-with-files" || true)"
if [ -n "${PF:-}" ]; then
  [ -d "${PF}skills/planning-with-files" ] && copy_skill_dir "${PF}skills/planning-with-files"
  if [ -d "${PF}skills/i18n/planning-with-files-zh" ]; then
    run rm -rf "$DEST/skills/planning-with-files-zh"
    run cp -R "${PF}skills/i18n/planning-with-files-zh" "$DEST/skills/planning-with-files-zh"
  fi
fi

# 2.5 ui-ux-pro-max 前端设计系统
UX="$(latest_version "$CLAUDE_CACHE/ui-ux-pro-max-skill/ui-ux-pro-max" || true)"
[ -n "${UX:-}" ] && copy_skills_in "${UX}.claude/skills"

# 2.6 alirezarezvani/claude-skills 垂类专家包：产品 / 项目管理 / 商业化
for pkg in product-skills pm-skills commercial-skills; do
  V="$(latest_version "$CLAUDE_CACHE/claude-code-skills/$pkg" || true)"
  [ -n "${V:-}" ] && copy_skills_in "${V}skills"
done

# =====================================================================
# 3. Commands —— code-review / ralph-loop（含配套脚本）
# =====================================================================
info "安装 Commands -> $DEST/commands"

CR="$(latest_version "$CLAUDE_CACHE/claude-plugins-official/code-review" || true)"
if [ -n "${CR:-}" ] && [ -f "${CR}commands/code-review.md" ]; then
  run cp "${CR}commands/code-review.md" "$DEST/commands/code-review.md"
fi

RL="$(latest_version "$CLAUDE_CACHE/claude-plugins-official/ralph-loop" || true)"
if [ -n "${RL:-}" ] && [ -d "${RL}commands" ]; then
  for f in "${RL}commands"/*.md; do
    [ -f "$f" ] || continue
    run cp "$f" "$DEST/commands/$(basename "$f")"
  done
  # ralph-loop 依赖 scripts/setup-ralph-loop.sh 与 hooks/stop-hook.sh
  run mkdir -p "$DEST/commands/ralph-loop"
  [ -d "${RL}scripts" ] && run cp -R "${RL}scripts" "$DEST/commands/ralph-loop/"
  [ -d "${RL}hooks" ]   && run cp -R "${RL}hooks"   "$DEST/commands/ralph-loop/"
fi

# =====================================================================
# 4. 格式适配 —— name 规范化 + 占位符/路径改写
# =====================================================================
if [ "$DRY_RUN" = "0" ]; then
  info "适配 frontmatter 与占位符"
  python3 - "$DEST" <<'PY'
import pathlib, sys

dest = pathlib.Path(sys.argv[1])
SKILL_DIR = "${CODEBUDDY_SKILL_DIR}"
RALPH_ASSETS = "${HOME}/.codebuddy/commands/ralph-loop"

# ---- 4.1 Agents：name 规范化为文件标识符，移除 Claude 专属字段 ----
DROP = ("emoji:", "color:")
for f in sorted((dest / "agents").glob("*.md")):
    stem = f.stem
    text = f.read_text(encoding="utf-8")
    if not text.startswith("---"):
        continue
    end = text.find("\n---", 3)
    if end == -1:
        continue
    head, body = text[: end + 4], text[end + 4 :]
    out = []
    for ln in head.split("\n"):
        if ln.startswith("name:"):
            out.append(f"name: {stem}")
        elif ln.startswith(DROP):
            continue
        elif ln.startswith("model:"):
            # Claude 的 opus/sonnet/haiku 别名在 CodeBuddy 里不通用，统一继承会话模型
            out.append("model: inherit")
        else:
            out.append(ln)
    f.write_text("\n".join(out) + body, encoding="utf-8")

# ---- 4.2 Skills：${CLAUDE_PLUGIN_ROOT}/.../<skill> -> ${CODEBUDDY_SKILL_DIR} ----
for md in sorted((dest / "skills").rglob("*.md")):
    t = orig = md.read_text(encoding="utf-8")
    if md.name == "SKILL.md":
        skill = md.parent.name
        for pat in (
            "${{CLAUDE_PLUGIN_ROOT}}/.claude/skills/{}".format(skill),
            "${{CLAUDE_PLUGIN_ROOT}}/skills/{}".format(skill),
        ):
            t = t.replace(pat, SKILL_DIR)
    t = t.replace("${CLAUDE_PLUGIN_ROOT}", SKILL_DIR)
    t = t.replace("${CLAUDE_SKILL_DIR}", SKILL_DIR)
    t = t.replace("${CLAUDE_SESSION_ID}", "${CODEBUDDY_SESSION_ID}")
    t = t.replace("$HOME/.claude/skills", "$HOME/.codebuddy/skills")
    t = t.replace("~/.claude/skills", "~/.codebuddy/skills")
    t = t.replace(".claude/agents", ".codebuddy/agents")
    if t != orig:
        md.write_text(t, encoding="utf-8")

# ---- 4.3 Commands：ralph-loop 的插件根改写到安装后的资源目录 ----
for md in sorted((dest / "commands").glob("*.md")):
    t = orig = md.read_text(encoding="utf-8")
    t = t.replace("${CLAUDE_PLUGIN_ROOT}", RALPH_ASSETS)
    t = t.replace("${CLAUDE_SKILL_DIR}", RALPH_ASSETS)
    if t != orig:
        md.write_text(t, encoding="utf-8")

hj = dest / "commands/ralph-loop/hooks/hooks.json"
if hj.exists():
    t = hj.read_text(encoding="utf-8")
    hj.write_text(t.replace("${CLAUDE_PLUGIN_ROOT}", RALPH_ASSETS), encoding="utf-8")
PY
fi

# =====================================================================
# 5. 统计
# =====================================================================
if [ "$DRY_RUN" = "0" ]; then
  n_skills=$(find "$DEST/skills" -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
  n_agents=$(find "$DEST/agents" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
  n_cmds=$(find "$DEST/commands" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
  info "完成：$n_skills 个 Skill / $n_agents 个 Agent / $n_cmds 个 Command"
  echo
  echo "  在 CodeBuddy 会话中用 /skills 与 /agents 查看已加载内容（需重启会话）。"
  echo "  若需要 Skill 的 frontmatter hooks 生效，在 ~/.codebuddy/settings.json 加入："
  echo '    { "allowUntrustedFrontmatterHooks": true }'
fi
