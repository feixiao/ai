# CodeBuddy Skills & Agents 部署指南

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: Shell](https://img.shields.io/badge/Language-Shell-blue.svg)](https://www.gnu.org/software/bash/)

本目录是 [`../ClaudeCode/`](../ClaudeCode/) 的 CodeBuddy 对等物：把 Claude Code 生态里已经在用的高质量 **Skill**（技能）与 **Agent**（专家角色）移植到 CodeBuddy，并提供一个可重复执行的安装脚本 `install.sh`。

之所以需要移植而不是直接复用：CodeBuddy 没有 `claude plugin marketplace add` 这类命令，Skill 与 Agent 只能从 `.codebuddy/` 目录加载，且有几处格式差异（Agent 的 `name` 必须是 ASCII 标识符、路径占位符从 `CLAUDE_*` 改为 `CODEBUDDY_*`）。`install.sh` 负责抹平这些差异。

---

## 1. 前置条件

脚本从 **CodeBuddy 已添加的 marketplace 目录**与 **Claude Code 全局 agents 目录**中抽取内容：

| 依赖 | 默认路径 | 说明 |
| :--- | :--- | :--- |
| CodeBuddy marketplace | `~/.codebuddy/plugins/marketplaces/` | Skill 与 Command 的来源，由 `/plugin` 添加 marketplace 后产生 |
| 全局 agents | `~/.claude/agents/` | agency-agents-zh 角色文件（仍来自 Claude Code 侧） |
| CodeBuddy CLI | `codebuddy` | 需能正常启动会话 |
| Python 3 | `python3` | 用于 frontmatter 归一化与占位符改写 |

脚本会扫描 marketplace 下两种布局的 Skill：`…/<plugin>/skills/<name>/SKILL.md`（插件打包多个 skill）与 `…/<name>/SKILL.md`（插件根目录自身即 skill）。清单里点了名但扫描不到的 Skill / Command，会在结束时显式列出告警，不会静默跳过。

---

## 2. 快速开始

```bash
cd /Users/hy/wk/github/ai/CodeBuddy
chmod +x install.sh

# 1) 先空跑，确认将要执行的动作
./install.sh --dry-run

# 2) 实际安装（默认 profile=minimal：12 个核心 Skill，写入 ~/.codebuddy/）
./install.sh

# 按角色换档：eng / pm / invest / full
./install.sh --profile=eng
```

各档清单写在 `install.sh` 的 `load_profile()` 里，用 `./install.sh --profile=eng --list` 打印。四档定位：

| profile | Skill | Agent（pattern） | Command |
| :--- | :--- | :--- | :--- |
| `minimal`（默认） | 12：文档三剑客 + 核心工程方法 + 质询 + 设计 + 规划 | 全部（`*`） | `code-review` |
| `eng` | 27：superpowers 全家桶、建模质询、前端设计 7 项、MCP、规划 | `engineering-*`、`security-*`、`design-*`、`code-simplifier` | `code-review`、`ralph-loop`、`cancel-ralph`、`help` |
| `pm` | 35：文档 + 质询 + product / pm / commercial 三包 | `product-*`、`design-*`、`engineering-frontend-developer` | `code-review` |
| `invest` | 12：文档三剑客 + 红队质询 + 可视化 | `finance-*`、`specialized-*`、`product-trend-researcher` | `code-review` |
| `full` | 不筛选 | 不筛选 | 不筛选 |

Agent 用 glob pattern 匹配（不是逐个列名），因此上游新增 `engineering-xxx.md` 会自动归入 `eng` 档。

中文版 `planning-with-files-zh` 随英文主版一起装，不单列进清单。

重启 CodeBuddy 会话后验证：

```text
/skills      # 查看 User skills / Project skills / Plugin skills
/agents      # 查看已注册的子代理
```

可选：启用 Skill 的 frontmatter hooks（`planning-with-files` 需要）：

```json
// ~/.codebuddy/settings.json
{
  "allowUntrustedFrontmatterHooks": true
}
```

---

## 3. 安装后的目录结构

```
~/.codebuddy/
├── skills/                # full 档 101 个 Skill（默认 minimal 档只装 12 项），每个目录一个 SKILL.md（可含 scripts/、references/）
│   ├── xlsx/  pdf/  docx/  pptx/          # 官方文档三剑客 + PPT
│   ├── mcp-builder/  web-artifacts-builder/  frontend-design/
│   ├── brainstorming/  systematic-debugging/  test-driven-development/   # superpowers 全家桶（14 项）
│   ├── grilling/  domain-modeling/  codebase-design/  research/          # mattpocock 质询与建模
│   ├── ui-ux-pro-max/  design/  design-system/  ui-styling/  ...         # 前端设计（7 项）
│   ├── product-skills/  ...   pm-skills/  ...   commercial-skills/  ...  # 产品 / 项目管理 / 商业化
│   └── planning-with-files/  planning-with-files-zh/                     # 跨会话持久化规划
├── agents/                # full 档 18 个 Agent，每个一个 .md（默认 minimal 档全装，eng/pm/invest 档按前缀裁剪）
│   ├── engineering-software-architect.md   engineering-code-reviewer.md
│   ├── engineering-frontend-developer.md   engineering-backend-architect.md
│   ├── security-appsec-engineer.md         engineering-devops-automator.md
│   ├── finance-financial-analyst.md        finance-investment-researcher.md
│   ├── finance-financial-forecaster.md     finance-fraud-detector.md
│   ├── specialized-risk-assessor.md        product-trend-researcher.md
│   ├── product-manager.md                  product-sprint-prioritizer.md
│   ├── product-feedback-synthesizer.md     product-behavioral-nudge-engine.md
│   ├── design-ux-architect.md              code-simplifier.md
└── commands/              # 4 个 Command（full / eng 档全装，minimal / pm / invest 档只留 code-review）
    ├── code-review.md
    ├── ralph-loop.md   cancel-ralph.md   help.md
    └── ralph-loop/             # ralph-loop 依赖的脚本与 hooks
        ├── scripts/
        └── hooks/
```

---

## 4. 脚本做了什么

| 阶段 | 动作 |
| :--- | :--- |
| **1. Agents** | 复制 `~/.claude/agents/*.md`，把 `name` 归一化为文件名主干，移除 Claude 专属的 `emoji` / `color`，把 `model: opus` 之类别名改为 `inherit`；额外补入官方 `code-simplifier` agent（按档位的 `PROFILE_AGENTS` pattern 过滤） |
| **2. Skills** | 扫描 `~/.codebuddy/plugins/marketplaces/` 下所有 marketplace，按 `load_profile()` 的清单按名抽取 Skill 目录（默认档只装清单内项；`--full` 装扫描到的全部） |
| **3. Commands** | 按名在 marketplace 的 `commands/` 里找 `code-review`、`ralph-loop`、`cancel-ralph`、`help`，并带上 ralph-loop 的 `scripts/` 与 `hooks/`（按 `PROFILE_COMMANDS` 过滤；`ralph-loop` 不在档内时连资源目录一起不装） |
| **4. 适配** | 把 `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` / `${CODEBUDDY_PLUGIN_ROOT}` / `~/.claude/skills` 改写为 CodeBuddy 等价路径（`${CODEBUDDY_SKILL_DIR}`、`~/.codebuddy/skills`）。前两者在用户级 skill 中不会再被替换，留着字面量会让脚本路径失效，必须改写 |

脚本**幂等**：重跑会先 `rm -rf` 同名目录再复制，因此 Claude Code 侧插件升级后重跑即可同步。默认不会删除清单外的旧内容——要从宽档回退到窄档，用 `./install.sh --profile=invest --prune`，它会清掉三类目标下不在该档清单内的内容：`~/.codebuddy/skills/<dir>/`（目录）、`~/.codebuddy/agents/*.md`、`~/.codebuddy/commands/*.md`，以及 `ralph-loop` 不在档内时的 `commands/ralph-loop/` 资源目录。你自己手动放的文件同样会被删。`--profile=full --prune` 是 no-op。`agents/` 下非 `.md` 的目录不处理。

### 可用参数与环境变量

```bash
./install.sh                    # 默认 profile=minimal：只装该档清单内的 Skill
./install.sh --profile=eng      # 换档：minimal|eng|pm|invest|full（也支持 --profile eng）
./install.sh --full             # 等价于 --profile=full
./install.sh --prune            # 删除不在当前档清单内的 Skill / Agent / Command（full 档为 no-op）
./install.sh --fetch            # marketplace 里找不到的 Skill，改从上游 git 直下（需 git，默认关闭）
./install.sh --list             # 打印当前档的 Skill / Agent / Command 清单后退出
./install.sh --dry-run          # 空跑
./install.sh -h                 # 打印用法

CB_MARKETPLACES=$HOME/.codebuddy/plugins/marketplaces \  # Skill / Command 来源
CLAUDE_AGENTS=$HOME/.claude/agents \                     # Agent 来源
CODEBUDDY_HOME=$HOME/.codebuddy \                        # 安装目标
SKILL_FETCH_DIR=$HOME/.cache/codebuddy-skills \          # --fetch 的 clone 缓存目录
./install.sh
```

---

## 5. 常见问题排查

### 5.1 `/skills` 里看不到新装的 Skill
手动新增的文件需要**重启会话**才会加载。重启后仍不出现，检查：
- 目录层级是否正确：`~/.codebuddy/skills/<name>/SKILL.md`（不是 `<name>.md`）；
- SKILL.md 是否以 `---` 开头的合法 frontmatter。

### 5.2 Agent 没有被注册
最常见原因是 `name` 不是 ASCII 标识符。检查：
```bash
head -5 ~/.codebuddy/agents/engineering-software-architect.md
```
`name:` 必须是小写字母 + 连字符。若重跑 `install.sh` 仍未修正，说明该文件的 frontmatter 未以 `---` 起始。

### 5.3 技能调用脚本时报路径不存在
说明残留了未改写的插件占位符：
```bash
grep -rn 'CLAUDE_PLUGIN_ROOT' ~/.codebuddy/skills
```
正常情况下只会有两处命中，且都不影响运行：
- `planning-with-files` 的 `${CLAUDE_PLUGIN_ROOT:-$HOME/.codebuddy/skills/planning-with-files}` 兜底表达式（该变量在用户级 skill 中保持字面量，因此会正确走 fallback 分支）；
- `ui-ux-pro-max/scripts/tests/` 下的开发测试文件。

### 5.4 `planning-with-files` 的 hooks 没生效
非内置来源的 Skill frontmatter hooks 默认不注册。在 `~/.codebuddy/settings.json` 加入 `"allowUntrustedFrontmatterHooks": true` 后重启会话。

### 5.5 清单里点了名的 Skill 没装上

脚本结束时若有 `[!] 清单中有 N 个 Skill … 找不到` 的告警，说明这些 Skill 在你本机的 marketplace 里没有。两条路：

1. 登记过上游的用 `--fetch` 直下（需要 `git`，仓库缓存在 `~/.cache/codebuddy-skills/`，重跑会复用）。上游登记表写在 `install.sh` 的 `FETCH_SOURCES` 里，目前收录 `grilling`、`domain-modeling`、`planning-with-files`——注意原上游 `mattpocock/mattpocock-skills` 已不存在，前两个取自镜像仓库。
2. 没登记过的手动放：`~/.codebuddy/skills/<name>/SKILL.md`。

### 5.6 装的 Skill 太多，感觉模型注意力被稀释
用 `skillOverrides` 按角色裁剪，详见 [`RECOMMENDED_SKILLS.md` § 4.3](./RECOMMENDED_SKILLS.md)。示例：

```json
{
  "skillOverrides": {
    "atlassian-admin": "off",
    "jira-expert": "off",
    "confluence-expert": "off",
    "slack-gif-creator": "off",
    "algorithmic-art": "off"
  }
}
```

---

## 6. 配套文档

- [CodeBuddy 高质量 Skill 选型与安装指南](./RECOMMENDED_SKILLS.md)——全栈工程师 / 产品经理 / 个人投资者三类角色的技能矩阵、调用范例与启停治理。
- [CodeBuddy 高质量 Agent 专家角色选型与实战指南](./RECOMMENDED_AGENTS.md)——18 个专家角色的职能说明、部署姿势、唤醒方式与端到端实战范式。
- [Claude Code 版原始指南](../ClaudeCode/)——本目录内容的来源与上游参考。
