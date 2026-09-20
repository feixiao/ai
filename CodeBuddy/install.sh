#!/usr/bin/env bash
#
# CodeBuddy Skills / Agents / Commands 一键安装脚本
# ---------------------------------------------------------------
# 从 CodeBuddy 已添加的 marketplace 与 Claude Code 全局 agents 目录中抽取内容，
# 适配为 CodeBuddy 的目录与格式，安装到 ~/.codebuddy/ 下：
#
#   ~/.codebuddy/skills/<name>/SKILL.md
#   ~/.codebuddy/agents/<name>.md
#   ~/.codebuddy/commands/<name>.md
#
# 用法：
#   ./install.sh                        # 最简安装（默认 profile=minimal）
#   ./install.sh --profile=eng|pm|invest # 按角色安装该角色的 Skill 清单
#   ./install.sh --full                 # 等价于 --profile=full，装全部来源的 Skill
#   ./install.sh --prune                # 删除目标目录里不在当前 profile 清单内的 Skill
#   ./install.sh --fetch                # 清单里 marketplace 没有的 Skill，改从上游 git 仓库直下
#   ./install.sh --dry-run              # 只打印将要执行的动作
#
# 可用环境变量覆盖来源与目标：
#   CB_MARKETPLACES   默认 ~/.codebuddy/plugins/marketplaces
#   CLAUDE_AGENTS     默认 ~/.claude/agents
#   CODEBUDDY_HOME    默认 ~/.codebuddy
#   SKILL_FETCH_DIR   默认 ~/.cache/codebuddy-skills（--fetch 的 clone 缓存目录）
#
set -euo pipefail

CB_MARKETPLACES="${CB_MARKETPLACES:-$HOME/.codebuddy/plugins/marketplaces}"
CLAUDE_AGENTS="${CLAUDE_AGENTS:-$HOME/.claude/agents}"
DEST="${CODEBUDDY_HOME:-$HOME/.codebuddy}"
SKILL_FETCH_DIR="${SKILL_FETCH_DIR:-$HOME/.cache/codebuddy-skills}"
DRY_RUN=0
FULL=0
PRUNE=0
FETCH=0
PROFILE=minimal
PROFILE_SKILLS=()

# 每个 profile 的 Skill 清单。清单为空且 FULL=1 表示全量放行。
# 名字必须与源插件里的 skill 目录名一致；写错只会静默跳过，可用 ./install.sh --list 核对。
load_profile() {
  case "$1" in
    minimal) # 默认档：文档 + 核心工程方法 + 质询 + 设计 + 规划
      PROFILE_SKILLS=(
        xlsx pdf docx pptx
        brainstorming systematic-debugging test-driven-development
        domain-modeling grilling
        mcp-builder ui-ux-pro-max planning-with-files
      )
      # 默认档不裁 agent，command 只留 code-review
      PROFILE_AGENTS=( '*' )
      PROFILE_COMMANDS=( code-review ) ;;
    eng) # 全栈工程：superpowers 全家桶 + 建模质询 + 前端设计 + MCP
      PROFILE_SKILLS=(
        using-superpowers brainstorming writing-plans executing-plans
        systematic-debugging test-driven-development
        requesting-code-review receiving-code-review verification-before-completion
        dispatching-parallel-agents subagent-driven-development
        finishing-a-development-branch using-git-worktrees writing-skills
        domain-modeling codebase-design grilling research
        ui-ux-pro-max design design-system ui-styling brand banner-design slides
        mcp-builder planning-with-files
      )
      PROFILE_AGENTS=( 'engineering-*' 'security-*' 'design-*' code-simplifier )
      PROFILE_COMMANDS=( code-review ralph-loop cancel-ralph help ) ;;
    pm) # 产品经理：文档 + 质询 + 产品 / 项目管理 / 商业化三包
      PROFILE_SKILLS=(
        docx pdf pptx xlsx
        brainstorming grilling
        product-manager-toolkit product-strategist product-discovery product-analytics
        competitive-teardown experiment-designer roadmap-communicator spec-to-repo
        saas-scaffolder landing-page-generator ui-design-system ux-researcher-designer
        senior-pm scrum-master jira-expert confluence-expert atlassian-admin
        atlassian-templates meeting-analyzer team-communications
        pricing-strategist commercial-forecaster commercial-policy deal-desk
        partnerships-architect channel-economics rfp-responder
        ui-ux-pro-max planning-with-files
      )
      PROFILE_AGENTS=( 'product-*' 'design-*' engineering-frontend-developer )
      PROFILE_COMMANDS=( code-review ) ;;
    invest) # 个人投资者：文档三剑客 + 红队质询 + 可视化
      PROFILE_SKILLS=(
        xlsx pdf docx pptx
        grilling grill-me research brainstorming
        theme-factory frontend-design canvas-design
        planning-with-files
      )
      PROFILE_AGENTS=( 'finance-*' 'specialized-*' product-trend-researcher )
      PROFILE_COMMANDS=( code-review ) ;;
    full)
      FULL=1
      PROFILE_SKILLS=()
      PROFILE_AGENTS=( '*' )
      PROFILE_COMMANDS=( '*' ) ;;
    *)
      echo "未知 profile: ${1:-<空>}（可选 minimal|eng|pm|invest|full）" >&2; exit 2 ;;
  esac
}

usage() {
  cat <<'USAGE'
用法：
  ./install.sh                         最简安装（默认 profile=minimal）
  ./install.sh --profile=eng            按角色安装：minimal|eng|pm|invest|full
  ./install.sh --profile eng            同上，等号与空格两种写法都支持
  ./install.sh --full                   等价于 --profile=full
  ./install.sh --prune                  删除目标目录里不在当前档清单内的 Skill / Agent / Command
  ./install.sh --fetch                  清单里 marketplace 找不到的 Skill，改从上游 git 直下（需 git）
  ./install.sh --list                   打印当前 profile 的 Skill 清单后退出
  ./install.sh --dry-run                只打印将要执行的动作，不写盘
  ./install.sh -h|--help                打印本帮助

环境变量：
  CB_MARKETPLACES   默认 ~/.codebuddy/plugins/marketplaces
  CLAUDE_AGENTS     默认 ~/.claude/agents
  CODEBUDDY_HOME    默认 ~/.codebuddy
  SKILL_FETCH_DIR   默认 ~/.cache/codebuddy-skills（--fetch 的 clone 缓存目录）
USAGE
}

LIST_ONLY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)     DRY_RUN=1 ;;
    --full)        PROFILE=full ;;
    --prune)       PRUNE=1 ;;
    --fetch)       FETCH=1 ;;
    --list)        LIST_ONLY=1 ;;
    --profile=*)   PROFILE="${1#--profile=}" ;;
    --profile)
      [ $# -ge 2 ] || { echo "--profile 缺少取值" >&2; exit 2; }
      shift; PROFILE="$1" ;;
    -h|--help)     usage; exit 0 ;;
    *) echo "未知参数: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done
load_profile "$PROFILE"

if [ "$LIST_ONLY" = "1" ]; then
  if [ "$FULL" = "1" ]; then
    echo "profile: full（不筛选，装全部来源的 Skill / Agent / Command）"
  else
    echo "profile: ${PROFILE}"
    echo "  skills (${#PROFILE_SKILLS[@]}):"
    printf '    %s\n' "${PROFILE_SKILLS[@]}"
    echo "  agents (${#PROFILE_AGENTS[@]} pattern):"
    printf '    %s\n' "${PROFILE_AGENTS[@]}"
    echo "  commands (${#PROFILE_COMMANDS[@]}):"
    printf '    %s\n' "${PROFILE_COMMANDS[@]}"
  fi
  exit 0
fi

info() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }

run() {
  if [ "$DRY_RUN" = "1" ]; then echo "  [dry-run] $*"; else "$@"; fi
}

# ---- CodeBuddy marketplace 源定位 ----
# 支持两种布局（<mkt> = ~/.codebuddy/plugins/marketplaces/<marketplace>）：
#   <mkt>/<plugins|external_plugins>/<plugin>/skills/<name>/SKILL.md   插件打包多个 skill
#   <mkt>/<plugins|external_plugins>/<name>/SKILL.md                   插件根目录自身即 skill
# codebuddy-plugins-official 排在前面，同名 skill 优先取官方源。
list_all_skill_sources() { # 每行输出 "<name>\t<srcdir>"
  local mkt d
  for mkt in "$CB_MARKETPLACES/codebuddy-plugins-official" "$CB_MARKETPLACES"/*/; do
    [ -d "$mkt" ] || continue
    for d in "$mkt"/*/*/skills/*/; do
      if [ -f "${d}SKILL.md" ]; then printf '%s\t%s\n' "$(basename "$d")" "${d%/}"; fi
    done
    for d in "$mkt"/*/*/ "$mkt"/*/; do
      if [ -f "${d}SKILL.md" ]; then printf '%s\t%s\n' "$(basename "$d")" "${d%/}"; fi
    done
  done
}

# 只扫一次盘建索引，后续按名字查表（逐个 skill 遍历 marketplace 太慢）
SKILL_INDEX="$(mktemp -t cb-skill-index)"
trap 'rm -f "$SKILL_INDEX"' EXIT
list_all_skill_sources > "$SKILL_INDEX"

find_skill_source() { # $1 = skill 名；命中则输出源目录，未命中输出空
  awk -F'\t' -v n="$1" '$1 == n { print $2; exit }' "$SKILL_INDEX"
}

find_agent_file() { # $1 = agent 名（不含 .md）；命中则输出 .md 路径
  local f
  for f in "$CB_MARKETPLACES/codebuddy-plugins-official"/*/*/agents/"$1".md \
           "$CB_MARKETPLACES"/*/*/agents/"$1".md; do
    if [ -f "$f" ]; then printf '%s\n' "$f"; return 0; fi
  done
  return 1
}

find_command_file() { # $1 = command 名（不含 .md）；命中则输出 .md 路径
  local f
  for f in "$CB_MARKETPLACES/codebuddy-plugins-official"/*/*/commands/"$1".md \
           "$CB_MARKETPLACES"/*/*/commands/"$1".md; do
    if [ -f "$f" ]; then printf '%s\n' "$f"; return 0; fi
  done
  return 1
}

# ---- marketplace 里没有的 skill，走上游 git 直下（仅 --fetch 启用，需要 git） ----
# 格式："<skill 名>|<git 仓库>|<仓库内相对路径>"
# 注意：mattpocock/mattpocock-skills 已不存在，grilling / domain-modeling 取自其镜像仓库。
FETCH_SOURCES=(
  "grilling|https://github.com/FeatherHunter/dsh-mattpocock-skills-deck|package/bundled-skills/grilling"
  "domain-modeling|https://github.com/FeatherHunter/dsh-mattpocock-skills-deck|package/bundled-skills/domain-modeling"
  "planning-with-files|https://github.com/OthmanAdi/planning-with-files|.codebuddy/skills/planning-with-files"
)

fetch_skill() { # $1 = skill 名；命中并就绪则输出本地目录，未命中输出空
  local name="$1" entry rest repo sub workdir
  for entry in "${FETCH_SOURCES[@]}"; do
    [ "${entry%%|*}" = "$name" ] || continue
    rest="${entry#*|}"
    repo="${rest%%|*}"
    sub="${rest#*|}"
    workdir="$SKILL_FETCH_DIR/$(basename "$repo" .git)"
    if [ "$DRY_RUN" = "1" ]; then
      # 走 stderr，避免被 $(fetch_skill ...) 捕获后混进后面的 cp -R 行
      echo "  [dry-run] git clone --depth 1 ${repo} ${workdir}（取 ${sub}）" >&2
      printf '%s\n' "$workdir/$sub"
      return 0
    fi
    if [ ! -d "$workdir/.git" ]; then
      run mkdir -p "$SKILL_FETCH_DIR"
      run rm -rf "$workdir"
      if ! run git clone --depth 1 -q "$repo" "$workdir"; then
        warn "clone 失败：$repo"
        return 1
      fi
    fi
    if [ -f "$workdir/$sub/SKILL.md" ]; then printf '%s\n' "$workdir/$sub"; return 0; fi
    warn "${name}：${repo} 中未找到 ${sub}/SKILL.md"
    return 1
  done
  return 1
}

SKIPPED=0 # 各阶段跳过计数，供结尾统计
SKIP_AGENTS=0
SKIP_CMDS=0
MISSING_SKILLS=() # 清单里有、但 marketplace 中找不到的 skill
MISSING_CMDS=()

want_skill() { # $1 = skill 目录名；全量档一律放行
  [ "$FULL" = "1" ] && return 0
  local n
  for n in "${PROFILE_SKILLS[@]}"; do
    [ "$n" = "$1" ] && return 0
  done
  return 1
}

# agent / command 走 pattern 匹配，元素可以是字面量或 glob（如 'engineering-*'）
# $p 故意不加引号，让 * 生效
want_agent() { # $1 = agent 名（不含 .md）
  [ "$FULL" = "1" ] && return 0
  local p
  for p in "${PROFILE_AGENTS[@]}"; do
    case "$1" in $p) return 0 ;; esac
  done
  return 1
}

want_command() { # $1 = command 名（不含 .md）
  [ "$FULL" = "1" ] && return 0
  local p
  for p in "${PROFILE_COMMANDS[@]}"; do
    case "$1" in $p) return 0 ;; esac
  done
  return 1
}

copy_skill_dir() { # $1 = 源 skill 目录
  local src="${1%/}" name
  name="$(basename "$src")"
  if ! want_skill "$name"; then
    SKIPPED=$((SKIPPED + 1))
    return 0
  fi
  run rm -rf "$DEST/skills/$name"
  run cp -R "$src" "$DEST/skills/$name"
}

require_dir() {
  [ -d "$1" ] || { warn "缺少目录：$1（跳过）"; return 1; }
}

if [ ! -d "$CB_MARKETPLACES" ]; then
  warn "缺少 marketplace 目录：${CB_MARKETPLACES}（Skill / Command 阶段将全部落空）"
fi
info "来源： $CB_MARKETPLACES"
info "目标： $DEST"
if [ "$FULL" = "1" ]; then
  info "档位： 全量（profile=full）"
else
  info "档位： ${PROFILE}（清单 ${#PROFILE_SKILLS[@]} 项）"
fi
run mkdir -p "$DEST/skills" "$DEST/agents" "$DEST/commands"

# =====================================================================
# 1. Agents —— agency-agents-zh 专家角色 + 官方 code-simplifier
# =====================================================================
info "安装 Agents -> $DEST/agents"
if require_dir "$CLAUDE_AGENTS"; then
  for f in "$CLAUDE_AGENTS"/*.md; do
    [ -f "$f" ] || continue
    name="$(basename "$f" .md)"
    if ! want_agent "$name"; then
      SKIP_AGENTS=$((SKIP_AGENTS + 1))
      continue
    fi
    run cp "$f" "$DEST/agents/$(basename "$f")"
  done
fi

# code-simplifier 是官方插件自带的 agent，不在 ~/.claude/agents 下，单独从 marketplace 取
if want_agent code-simplifier; then
  CS="$(find_agent_file code-simplifier || true)"
  if [ -n "${CS:-}" ]; then
    run cp "$CS" "$DEST/agents/code-simplifier.md"
  else
    warn "marketplace 中未找到 agent：code-simplifier（跳过）"
    SKIP_AGENTS=$((SKIP_AGENTS + 1))
  fi
else
  SKIP_AGENTS=$((SKIP_AGENTS + 1))
fi

# =====================================================================
# 2. Skills —— 按 profile 清单从 marketplace 抽取
# =====================================================================
info "安装 Skills -> $DEST/skills"

if [ "$FULL" = "1" ]; then
  # 全量档：装 marketplace 里能找到的全部 skill，同名只取第一个来源
  while IFS=$'\t' read -r name src; do
    [ -n "$name" ] || continue
    copy_skill_dir "$src"
  done < <(awk -F'\t' '!seen[$1]++' "$SKILL_INDEX")
else
  for name in "${PROFILE_SKILLS[@]}"; do
    src="$(find_skill_source "$name")"
    # marketplace 里没有、且开了 --fetch 的，退回上游 git 直下
    if [ -z "$src" ] && [ "$FETCH" = "1" ]; then
      src="$(fetch_skill "$name" || true)"
    fi
    if [ -z "$src" ]; then
      MISSING_SKILLS+=("$name")
      continue
    fi
    copy_skill_dir "$src"
  done
fi

# =====================================================================
# 3. Commands —— code-review / ralph-loop（含配套脚本）
# =====================================================================
info "安装 Commands -> $DEST/commands"

RL_ROOT="" # ralph-loop 插件根目录，供后面拷 scripts/ 与 hooks/
for name in code-review ralph-loop cancel-ralph help; do
  if ! want_command "$name"; then
    SKIP_CMDS=$((SKIP_CMDS + 1))
    continue
  fi
  f="$(find_command_file "$name" || true)"
  if [ -z "$f" ]; then
    MISSING_CMDS+=("$name")
    continue
  fi
  run cp "$f" "$DEST/commands/$(basename "$f")"
  if [ "$name" = ralph-loop ]; then RL_ROOT="$(dirname "$(dirname "$f")")"; fi
done

# ralph-loop 依赖 scripts/setup-ralph-loop.sh 与 hooks/stop-hook.sh
if [ -n "$RL_ROOT" ]; then
  run mkdir -p "$DEST/commands/ralph-loop"
  [ -d "$RL_ROOT/scripts" ] && run cp -R "$RL_ROOT/scripts" "$DEST/commands/ralph-loop/"
  [ -d "$RL_ROOT/hooks" ]   && run cp -R "$RL_ROOT/hooks"   "$DEST/commands/ralph-loop/"
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
    # 该占位符只对插件来源的 skill 生效；复制到用户级目录后会保留字面量，故一并改写
    t = t.replace("${CODEBUDDY_PLUGIN_ROOT}", SKILL_DIR)
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
# 5. 清理 —— 删除目标目录里不在当前档清单内的 Skill / Agent / Command
# =====================================================================
if [ "$PRUNE" = "1" ] && [ "$FULL" = "0" ]; then
  info "清理清单外内容（--prune）"

  for d in "$DEST"/skills/*/; do
    [ -d "$d" ] || continue
    n="$(basename "$d")"
    want_skill "$n" && continue
    # 中文版随英文主版保留
    [ "$n" = "planning-with-files-zh" ] && want_skill planning-with-files && continue
    run rm -rf "$d"
  done

  for f in "$DEST"/agents/*.md; do
    [ -f "$f" ] || continue
    n="$(basename "$f" .md)"
    want_agent "$n" || run rm -f "$f"
  done

  for f in "$DEST"/commands/*.md; do
    [ -f "$f" ] || continue
    n="$(basename "$f" .md)"
    want_command "$n" || run rm -f "$f"
  done
  # ralph-loop 的资源目录随 command 一起走
  if ! want_command ralph-loop && [ -d "$DEST/commands/ralph-loop" ]; then
    run rm -rf "$DEST/commands/ralph-loop"
  fi
fi

# =====================================================================
# 6. 统计
# =====================================================================
if [ "$DRY_RUN" = "0" ]; then
  n_skills=$(find "$DEST/skills" -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
  n_agents=$(find "$DEST/agents" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
  n_cmds=$(find "$DEST/commands" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
  info "完成：$n_skills 个 Skill / $n_agents 个 Agent / $n_cmds 个 Command"
  if [ "$FULL" = "0" ] && [ $((SKIPPED + SKIP_AGENTS + SKIP_CMDS)) -gt 0 ]; then
    echo "  profile=${PROFILE}：跳过 $SKIPPED 个 Skill / $SKIP_AGENTS 个 Agent / $SKIP_CMDS 个 Command。换档用 --profile=...，清理用 --prune。"
  fi
  # 清单里点了名但 marketplace 里没有的，必须显式报出来——否则会静默少装
  if [ "${#MISSING_SKILLS[@]}" -gt 0 ]; then
    warn "清单中有 ${#MISSING_SKILLS[@]} 个 Skill 在 $CB_MARKETPLACES 下找不到：$(printf '%s ' "${MISSING_SKILLS[@]}")"
    if [ "$FETCH" = "0" ]; then
      echo "    其中登记过上游的可用 --fetch 直下（需 git）；未登记的需手动放入 ~/.codebuddy/skills/<name>/SKILL.md"
    fi
  fi
  if [ "${#MISSING_CMDS[@]}" -gt 0 ]; then
    warn "清单中有 ${#MISSING_CMDS[@]} 个 Command 在 $CB_MARKETPLACES 下找不到：$(printf '%s ' "${MISSING_CMDS[@]}")"
  fi
  echo
  echo "  在 CodeBuddy 会话中用 /skills 与 /agents 查看已加载内容（需重启会话）。"
  echo "  若需要 Skill 的 frontmatter hooks 生效，在 ~/.codebuddy/settings.json 加入："
  echo '    { "allowUntrustedFrontmatterHooks": true }'
fi
