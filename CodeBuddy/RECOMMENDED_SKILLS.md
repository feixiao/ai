# CodeBuddy 高质量 Skill 选型与安装指南（全栈工程师、产品经理与个人投资者篇）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Category: CodeBuddy Skills](https://img.shields.io/badge/Category-CodeBuddy_Skills-blue.svg)](https://cnb.cool/codebuddy/codebuddy-code)

本文档是 [`../ClaudeCode/RECOMMENDED_SKILLS.md`](../ClaudeCode/RECOMMENDED_SKILLS.md) 的 CodeBuddy 移植版。内容针对**全栈工程师**、**产品经理 (PM)** 与**个人投资者**三重复合工作流，梳理最适合安装的高质量 Skill 工具链，并把 Claude Code 的 `claude plugin install` 安装方式替换为 CodeBuddy 可用的本地目录部署方案。

---

## 0. 与 Claude Code 的关键差异（先读这一节）

CodeBuddy 与 Claude Code 的 Skill 格式基本同源，但有四处必须注意的差异：

| 维度 | Claude Code | CodeBuddy |
| :--- | :--- | :--- |
| 用户级目录 | `~/.claude/skills/<name>/SKILL.md` | `~/.codebuddy/skills/<name>/SKILL.md` |
| 项目级目录 | `.claude/skills/` | `.codebuddy/skills/`（项目级优先于用户级） |
| 安装方式 | `claude plugin marketplace add ...` | 无等价 marketplace 命令，需**把插件里的 `skills/*` 目录复制/软链**到上述目录（本仓库提供 `install.sh`） |
| 路径占位符 | `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` | `${CODEBUDDY_SKILL_DIR}`（另有 `${CODEBUDDY_PLUGIN_ROOT}`，但**用户级 skill 中不会被替换**） |
| Frontmatter Hooks | 插件来源自动注册 | 需 `~/.codebuddy/settings.json` 中 `"allowUntrustedFrontmatterHooks": true` 才注册 |

**结论**：凡是插件里写 `${CLAUDE_PLUGIN_ROOT}/skills/<name>/...` 的脚本路径，落到 CodeBuddy 必须改成 `${CODEBUDDY_SKILL_DIR}/...`，否则执行时会拿到字面量。本仓库的 `install.sh` 已自动完成该改写。

---

## 1. 角色能力需求与第一性原理推导

| 身份定位 | 核心工作流与痛点 | 所需核心能力 | 匹配的 Skill 类别 |
| :--- | :--- | :--- | :--- |
| **全栈工程师** | • 前端交互、设计系统与原型验证<br>• 后端接口设计、状态机与领域模型 (DDD)<br>• 代码审查、TDD 与根因排查<br>• 私有数据源接入 (MCP) | • 极致 UI/UX 规范与微交互设计<br>• 严格的软件工程与反脆弱设计<br>• 自动化测试与循环自愈能力<br>• MCP 自定义 Server 构建能力 | • 前端设计类：`ui-ux-pro-max`、`design-system`、`ui-styling`、`frontend-design`<br>• 工程方法类：`superpowers` 全家桶（14 项）<br>• 建模与质询类：`domain-modeling`、`codebase-design`、`grilling`<br>• 协议扩展类：`mcp-builder` |
| **产品经理 (PM)** | • 工业级 PRD 与 AC 验收标准<br>• 交互原型与用户旅程图<br>• 伪需求辨析与 MVP 范围削减<br>• 商业化变现与阶梯定价 | • 严谨的 PRD/Word/PDF 规格输出<br>• 对抗性质询与逻辑压力测试<br>• 页面状态机与微交互原型<br>• SaaS 商业化与定价设计 | • 文档规范类：`docx`、`pdf`、`xlsx`、`pptx`<br>• 体验原型类：`ui-ux-pro-max`、`web-artifacts-builder`<br>• 需求审查类：`grilling`、`brainstorming`<br>• 产品与商业化类：`product-skills`、`pm-skills`、`commercial-skills`、`planning-with-files` |
| **个人投资者** | • 研报、公告与年报关键数据提取<br>• DCF 估值模型、敏感性分析<br>• 投资论点反脆弱性审查<br>• 净值走势与资产配置图表 | • 无损长篇 PDF 定位与表格抽取<br>• 严谨的电子表格公式推导与校验<br>• 红队思维与对抗性逻辑拷问<br>• 专业级金融图表可视化 | • 深度文档类：`xlsx`、`pdf`、`docx`、`pptx`<br>• 红队拷问类：`grilling`、`grill-me`、`research`<br>• 策略推演类：`brainstorming`、`planning-with-files`<br>• 可视化类：`theme-factory`、`frontend-design`、`canvas-design` |

> **说明**：Claude Code 版的 `dataviz` 属于 Anthropic 内置核心能力，CodeBuddy 无同名内置 skill。需要金融图表时用 `theme-factory`（配色主题）+ `frontend-design`（版式）组合替代。

---

## 2. 核心推荐技能矩阵（对应 CodeBuddy 安装后的目录名）

### 2.1 个人投资者专精

#### ① 官方文档三剑客 `xlsx` / `pdf` / `docx` / `pptx`
- **来源**：Anthropic 官方 Agent Skills 仓库（`anthropics/skills`），经 `install.sh` 从 `document-skills` 插件抽取。
- **能力**：
  - `xlsx`：XLOOKUP、IRR、NPV、INDEX-MATCH 等复杂公式，财报三表联动、DCF 模型与敏感性分析表。
  - `pdf`：长篇财报 / 招股书 / 券商研报，跨页表格提取、图表元数据解析，转 Markdown / JSON。
  - `docx` / `pptx`：投资备忘录 (Investment Memo)、尽调总结、季度策略汇报幻灯片。

#### ② `grilling`（反脆弱红队严苛质询）
- **来源**：`mattpocock/mattpocock-skills`（中文源 `vinvcn/mattpocock-skills-zh-CN`）。
- **价值**：买入或调仓前对投资论点做极限压力测试，AI 切换为对抗性红队模式，围绕幸存者偏差、脆弱预设、宏观下行与黑天鹅逐轮质询。
- **调用**：
  ```text
  /grilling 我看好某半导体龙头在 AI ASIC 领域的长期增长，请对我的投资逻辑做严格的红队审查与反脆弱质询。
  ```

#### ③ `theme-factory` + `frontend-design`（可视化规范）
- 提供可访问的配色主题与版式规范，支持深色 / 浅色自适应，用于净值曲线、最大回撤柱状图、相关性热力图。

---

### 2.2 全栈工程师专精

#### ① `ui-ux-pro-max` 及其子技能
- **来源**：`nextlevelbuilder/ui-ux-pro-max-skill`。安装后包含 `ui-ux-pro-max`、`design`、`design-system`、`ui-styling`、`brand`、`banner-design`、`slides` 共 7 项。
- **能力**：Design System 指导、Tailwind 配色与字体阶梯、微交互动效、WCAG 无障碍与落地页转化优化。
- **注意**：该 skill 通过 `python "${CODEBUDDY_SKILL_DIR}/scripts/search.py" ...` 调用检索脚本，`install.sh` 已把原插件路径改写为 `${CODEBUDDY_SKILL_DIR}`。

#### ② `superpowers` 工程方法论全家桶（14 项）
- **来源**：`anthropics/claude-plugins-official`。
- **核心组件**：
  - `systematic-debugging`：假设驱动 + 日志根因追踪，禁止"碰运气式"改代码。
  - `test-driven-development`：强制红-绿-重构循环。
  - `using-git-worktrees`：独立 worktree 隔离分支，主线上无污染切入 Hotfix。
  - `brainstorming`：技术选型与策略推演的多方案评估。
  - `using-superpowers`：会话前置守卫，先核对技能清单再行动。
  - 另有 `writing-plans` / `executing-plans` / `requesting-code-review` / `receiving-code-review` / `verification-before-completion` / `dispatching-parallel-agents` / `subagent-driven-development` / `finishing-a-development-branch` / `writing-skills`。

#### ③ `domain-modeling` 与 `codebase-design`
- **来源**：`mattpocock/mattpocock-skills`。严格应用领域驱动设计，清晰划分 Aggregate Root / Entity / Value Object；也可用于建模订单薄、交易头寸与多币种结算状态机。

#### ④ `mcp-builder`
- **来源**：`anthropics/skills`。指导构建符合 MCP 规范的自定义 Server——接入本地 PostgreSQL/Redis、内部微服务 API，或把行情数据源（Yahoo Finance、Alpha Vantage、富途 OpenAPI、IB）封装为 MCP 工具。

#### ⑤ `code-review` 与 `code-simplifier`
- `code-review`：Claude Code 中它是 **command**，CodeBuddy 里同样安装为 command（`~/.codebuddy/commands/code-review.md`），用 `/code-review` 触发。
- `code-simplifier`：本质是 **agent**，已安装到 `~/.codebuddy/agents/code-simplifier.md`。

#### ⑥ `ralph-loop`（长链路循环自愈）
- 以 command 形式安装：`/ralph-loop "<任务>" --max-iterations N --completion-promise "..."`，自动循环 `写代码 → 跑测试 → 捕错 → 修正` 直到通过。
- 依赖脚本位于 `~/.codebuddy/commands/ralph-loop/scripts/`。

---

### 2.3 产品经理专精

#### ① `docx` / `pdf`（工业级 PRD）
自带标准化模块：文档版本历史、需求背景、用户画像、核心业务逻辑流、页面状态转移表与 Given-When-Then 验收标准。

#### ② `grilling`（PRD 对抗质询 / 砍需求）
扮演极端尖锐的业务合伙人拷问："这个功能真的有人用吗？用户当前替代方案是什么？两周开发换 0.5% 次日留存是否值得？"

#### ③ `product-skills`（13 项）与 `pm-skills`（9 项）
- **来源**：`alirezarezvani/claude-skills`。
- `product-skills`：`product-manager-toolkit`、`product-strategist`、`product-discovery`、`product-analytics`、`competitive-teardown`、`experiment-designer`、`roadmap-communicator`、`spec-to-repo`、`saas-scaffolder`、`landing-page-generator`、`ui-design-system`、`ux-researcher-designer`。
- `pm-skills`：`senior-pm`、`scrum-master`、`jira-expert`、`confluence-expert`、`atlassian-admin`、`atlassian-templates`、`meeting-analyzer`、`team-communications`。

#### ④ `commercial-skills`（8 项，SaaS 商业化）
`pricing-strategist`、`commercial-forecaster`、`commercial-policy`、`deal-desk`、`partnerships-architect`、`channel-economics`、`rfp-responder`。用于设计 Free / Pro / Team 的功能隔离栅栏、阶梯定价与增收转化飞轮。

---

### 2.4 复合场景：跨会话持久化规划

#### `planning-with-files`
- 英文主版 + `planning-with-files-zh` 中文版均已安装。
- 产品场景：跨会话维护 Roadmap、Backlog 状态与里程碑。全栈场景：跨多天的重构/分库分表用持久化 Markdown 记录任务树。投资场景：跨季度研究笔记、估值模型更新与再平衡日志。
- 该 skill 的 frontmatter hooks 需要 `allowUntrustedFrontmatterHooks: true` 才会生效。

---

## 3. 安装与配置实操

### 步骤 1：执行安装脚本

```bash
cd /Users/hy/wk/github/ai/CodeBuddy
chmod +x install.sh

# 先空跑确认动作
./install.sh --dry-run

# 实际安装（默认写入 ~/.codebuddy/）
./install.sh
```

脚本会依次完成：
1. 复制 `~/.claude/agents/*.md` → `~/.codebuddy/agents/`；
2. 复制各插件 `skills/*` → `~/.codebuddy/skills/`；
3. 复制 `code-review` / `ralph-loop` command → `~/.codebuddy/commands/`（含 ralph-loop 的 `scripts/` 与 `hooks/`）；
4. 归一化 agent 的 `name` 字段、移除 `emoji` / `color`、把 Claude 模型别名改为 `inherit`；
5. 把 `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` / `~/.claude/skills` 改写为 CodeBuddy 等价路径。

可用环境变量覆盖来源与目的地：

```bash
CLAUDE_CACHE=/path/to/cache CLAUDE_AGENTS=/path/to/agents CODEBUDDY_HOME=$HOME/.codebuddy ./install.sh
```

### 步骤 2：可选——启用 Skill 的 Frontmatter Hooks

`planning-with-files` 等 skill 依赖 frontmatter 声明的 hooks。出于安全考虑，非内置来源的 hooks 默认不注册。需要时在 `~/.codebuddy/settings.json` 加入：

```json
{
  "allowUntrustedFrontmatterHooks": true
}
```

### 步骤 3：重启会话并验证

```text
/skills      # 查看 User skills / Project skills / Plugin skills 及预估 token
/agents      # 查看已注册的子代理
```

---

## 4. 技能的选择、路由与动态启停管理

### 4.1 底层机制：渐进式自适应加载

与 Claude Code 一致，CodeBuddy 遵循"渐进式揭示"：
1. 所有 Skill 默认只把 YAML frontmatter（`name` / `description`）载入系统提示词的技能索引，上下文开销很小；
2. 命中职责范围时模型主动调用 `Skill` 工具，按需把完整 `SKILL.md` 载入上下文；
3. 声明 `context: fork` 的 Skill 可在独立 subagent 上下文中执行，避免污染主会话。

> ⚠️ **本次共安装 101 个 Skill**。索引本身开销不大，但如果发现模型注意力被稀释，建议按 4.3 的表做角色化裁剪。

### 4.2 三种触发姿势

| 姿势 | 说明 | 示例 |
| :--- | :--- | :--- |
| 模型自动识别 | 根据 `description` 语义匹配，自动调用 | "帮我解析这份 10-K 财报" → 自动命中 `pdf` |
| 手动斜杠命令 | 用户显式调用 | `/xlsx`、`/grilling`、`/ui-ux-pro-max` |
| Skill 内部引用 | `user-invocable: false` 的背景类 Skill 由其他 Skill 引用 | — |

### 4.3 动态启停治理

CodeBuddy 提供 `skillOverrides` 设置，可在**不修改 SKILL.md** 的前提下控制单个 Skill 可见性。按 Skill 名索引，取四态之一：

| 值 | 对模型可见 | 在 `/` 菜单 | 用途 |
| :--- | :--- | :--- | :--- |
| `on` | 名称 + 描述 | 是 | 默认，不覆盖 |
| `name-only` | 仅名称 | 是 | 折叠描述，省 context 预算 |
| `user-invocable-only` | 隐藏 | 是 | 对模型隐藏，但 `/name` 仍可调用 |
| `off` | 隐藏 | 隐藏 | 完全禁用 |

写入 `~/.codebuddy/settings.json`（或项目级 `.codebuddy/settings.local.json`，优先级更高，适合提交进共享仓库）：

```json
{
  "skillOverrides": {
    "academy-guide": "off",
    "slack-gif-creator": "off",
    "algorithmic-art": "off"
  }
}
```

也可以直接在 `/skills` 面板用 `↑/↓` 选择、`enter` / `space` / `←/→` 切换状态，按 `Esc` 写入 `.codebuddy/settings.local.json`。

#### 双重角色管理最佳实践

| 角色工作阶段 | 建议保持 `on` 的核心技能 | 建议设为 `off` | 收益 |
| :--- | :--- | :--- | :--- |
| **全栈研发与重构** | `superpowers` 系列、`ui-ux-pro-max`、`mcp-builder`、`domain-modeling`、`codebase-design` | `atlassian-*`、`jira-expert`、`confluence-expert`、`pricing-strategist`、`rfp-responder`、`slack-gif-creator` | 保证调试、审查与设计系统指令精准，无项目管理/商业语义干扰 |
| **投资尽调与估值建模** | `xlsx`、`pdf`、`docx`、`pptx`、`grilling`、`research`、`theme-factory` | `superpowers` 系列、`ui-ux-pro-max`、`jira-expert`、`scrum-master` | 强化财务模型推导、表格联动与红队质询 |
| **产品需求与商业化** | `docx`、`pdf`、`product-skills`、`pm-skills`、`commercial-skills`、`planning-with-files` | `xlsx`、`pptx`、`mcp-builder`、`systematic-debugging` | 聚焦 PRD、路线图与定价推演 |
| **长期跨周期项目** | `planning-with-files` | 无 | 保持全局任务追踪文件常态化更新 |

---

## 5. 典型工作流调用范例

### 场景 A：个人投资者——新股研报拆解与红队投资决策

1. **财报提取**
   ```text
   用 pdf 技能解析该公司最新 10-K 财报，提炼过去 3 年自由现金流 (FCF)、毛利率趋势与潜在诉讼风险。
   ```
2. **构建 DCF 估值模型**
   ```text
   用 xlsx 技能建立一个 5 年期 DCF 折现现金流模型，WACC 9.5%，永续增长率 2.5%，并附敏感性分析表。
   ```
3. **红队质询**
   ```text
   /grilling 我打算把该标的纳入核心仓位，以下是我的投资逻辑：[...]。请做极度严格的红队审查，指出我未曾考虑的致命盲点。
   ```

---

### 场景 B：全栈工程师——开发个人投资组合管理看板

1. **领域驱动建模**
   ```text
   /domain-modeling 为投资组合系统设计领域模型，涵盖 Asset、Position、Transaction、Dividend 与 Realized/Unrealized PnL 计算。
   ```
2. **设计系统与前端构建**
   ```text
   /design-system 为投资组合仪表盘构建深色金融科技风格 UI 原型，集成净值曲线图与持仓分布卡片。
   ```
3. **对接自定义数据源 MCP**
   ```text
   用 mcp-builder 指导我开发一个 Python FastMCP 服务，抓取并暴露自选股实时行情。
   ```
4. **自动化评审与交付**
   ```text
   /code-review
   ```

---

### 场景 C：产品经理——商业化 SaaS 功能的 PRD 与商业闭环

1. **极端用例头脑风暴**
   ```text
   /brainstorming 我们正在规划"多租户团队协作"付费功能。请推演极端用例：权限冲突、成员跨组织迁移、离职交接与计费席位溢出。
   ```
2. **无情的对抗质询**
   ```text
   /grilling 这是该功能的初步 Feature List：[...]。请充当极端挑剔的业务合伙人做红队质询，逼问核心假设，砍掉性价比不高的非核心功能。
   ```
3. **输出工业级 PRD**
   ```text
   用 docx 技能导出标准 PRD 规格说明书 (PRD_Team_Workspace.docx)：业务目标、用户画像、用户旅程图、页面状态机转移表，并为每个功能给出 Given-When-Then 验收标准。
   ```
4. **商业化阶梯定价**
   ```text
   用 pricing-strategist 设计 Free / Pro / Enterprise 三档，明确席位单价、用量配额与升级触发契机。
   ```

---

## 6. 维护与清理建议

- **定期体检**：`ls ~/.codebuddy/skills/` 超过约 20 个时，建议用 `skillOverrides` 精简非常用项。
- **重新同步**：Claude Code 侧升级插件后，重跑 `./install.sh` 即可覆盖更新（脚本对同名目录先 `rm -rf` 再复制）。
- **占位符巡检**：升级后可检查是否残留未改写的插件路径：
  ```bash
  grep -rl 'CLAUDE_PLUGIN_ROOT' ~/.codebuddy/skills
  ```
  正常情况下仅 `planning-with-files` 的 `${CLAUDE_PLUGIN_ROOT:-...}` 兜底表达式与 `ui-ux-pro-max/scripts/tests/` 下的开发测试文件会命中，二者均不影响运行。

---

## 7. 参考

- 原始 Claude Code 版指南：[`../ClaudeCode/RECOMMENDED_SKILLS.md`](../ClaudeCode/RECOMMENDED_SKILLS.md)
- CodeBuddy Skills 官方文档：`/opt/homebrew/lib/node_modules/@tencent-ai/codebuddy-code/dist/web-ui/docs/cn/cli/skills.md`
- Anthropic 官方技能库：https://github.com/anthropics/skills
- Matt Pocock 技能库：https://github.com/mattpocock/mattpocock-skills
- UI/UX Pro Max：https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- planning-with-files：https://github.com/OthmanAdi/planning-with-files
- 垂类专家技能库：https://github.com/alirezarezvani/claude-skills
