# Pi Agent (pi-coding-agent) 高质量 Skill 选型、部署与使用指南

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Engine: Pi Agent](https://img.shields.io/badge/Engine-Pi%20Agent-purple.svg)](https://pi.dev)
[![Category: Agent Skills](https://img.shields.io/badge/Category-Agent_Skills-blue.svg)](https://agentskills.io)

本文档是 [`../ClaudeCode/RECOMMENDED_SKILLS.md`](../ClaudeCode/RECOMMENDED_SKILLS.md) 面向 **Pi Agent**（由 Mario Zechner 发起的下一代极简 AI 终端 Coding Agent，包名 `@earendil-works/pi-coding-agent`）的深度落地与使用指南。

内容针对**全栈工程师**、**产品经理 (PM)** 与**个人投资者**三重复合工作流，从底层运行原理、角色画像矩阵、本地自动化部署到终端交互调用，提供完整的使用方案。

---

## 0. 与 Claude Code 的关键差异与 Pi Agent 特性

Pi Agent 原生实现 [Agent Skills 规范](https://agentskills.io/specification)，与 Claude Code 具备极高的格式兼容性，但在目录机制、包管理和模型调用上有其独特的优势与差异：

| 维度 | Claude Code (`claude`) | Pi Agent (`pi`) |
| :--- | :--- | :--- |
| **用户全局技能目录** | `~/.claude/skills/<name>/SKILL.md` | `~/.pi/agent/skills/<name>/SKILL.md`（或 `~/.agents/skills/`） |
| **项目工作区技能目录** | `.claude/skills/<name>/SKILL.md` | `.pi/skills/<name>/SKILL.md`（或 `.agents/skills/`，工作区优先于全局） |
| **技能安装机制** | `claude plugin marketplace add ...`<br>`claude plugin install ...` | 本地目录原生发现（`./install.sh -s` 自动抽取同步），同时支持 `pi install` 管理 npm/git 形式的 Pi Package |
| **技能显式调用方式** | `/<name>` 或 `/<plugin>:<name>` | `/skill:<skill-name>` 显式指定，或启动后输入 `/skills` 查看 |
| **上下文加载策略** | 启动常驻 YAML 描述，命中后拉取 `SKILL.md` | 原生渐进式自适应加载（Progressive Disclosure），按需读取完整指令 |
| **模型与长上下文配合** | 深度绑定 Claude 3.5 / Opus 系列 | 原生支持 Google Gemini Pro (1M~2M 上下文)、DeepSeek-R1、Claude 及各类反向代理网关，切模极速 (`Ctrl+P`) |
| **热重载机制** | 重启会话或重新加载配置 | 在会话中输入 `/reload` 即可实时热重载所有 Skill |

---

## 1. 角色能力需求与第一性原理推导

| 身份定位 | 核心工作流与痛点 | 所需核心能力 | 匹配的 Skill 工具类别 |
| :--- | :--- | :--- | :--- |
| **全栈工程师** | • 前端交互、设计系统与原型验证<br>• 后端接口设计、状态机与领域模型 (DDD)<br>• 代码审查、测试驱动开发 (TDD) 与根因排查<br>• 私有数据源接入与自定义 MCP 工具构建 | • 极致 UI/UX 规范与微交互设计<br>• 严格的软件工程与反脆弱设计<br>• 自动化测试与循环自愈能力<br>• MCP 自定义 Server 构建能力 | • 前端设计类 (`ui-ux-pro-max`, `design-system`, `ui-styling`)<br>• 研发规范类 (`superpowers` 14 项全家桶)<br>• 建模质询类 (`domain-modeling`, `codebase-design`, `grilling`)<br>• 协议与扩展类 (`mcp-builder`, `planning-with-files`) |
| **产品经理 (PM)** | • 工业级 PRD 产品需求规格说明书与 AC 验收标准<br>• 交互原型与高转化 Landing Page 布局<br>• 伪需求辨析、需求砍伐与敏捷 MVP 范围削减<br>• 商业化变现策略、阶梯定价模型与转化漏斗设计 | • 严谨规范的 PRD/Word/PDF 规格输出能力<br>• 对抗性质询与业务逻辑压力测试 (防伪需求)<br>• 页面状态机与微交互原型验证<br>• SaaS 商业化增收与定价设计 | • 文档规范类 (`document-skills`: `docx`, `pdf`, `xlsx`, `pptx`)<br>• 体验与原型类 (`ui-ux-pro-max`, `landing-page-generator`)<br>• 需求审查类 (`grilling`, `brainstorming`)<br>• 商业与敏捷类 (`commercial-skills`, `product-skills`, `pm-skills`, `planning-with-files`) |
| **个人投资者** | • 研报、公告与 10-K/年报关键数据提取<br>• 复杂财务估值模型 (DCF)、敏感性分析与联动表格<br>• 投资论点 (Thesis) 反脆弱性审查与压力测试<br>• 投资组合净值走势、持仓分布与资产配置图表呈现 | • 无损长篇 PDF 研报定位与跨页表格抽取<br>• 严谨的电子表格公式推导与校验<br>• 红队思维与对抗性逻辑拷问 (Red Teaming)<br>• 专业级金融图表与深浅色数据可视化 | • 深度文档类 (`document-skills`: `xlsx`, `pdf`, `docx`, `pptx`)<br>• 逻辑推演与红队拷问类 (`grilling`, `grill-me`, `research`)<br>• 策略推演与规划类 (`brainstorming`, `planning-with-files`)<br>• 金融图表与可视化类 (`theme-factory`, `frontend-design`, `canvas-design`) |

---

## 2. 核心推荐技能矩阵（对应 Pi Agent 安装后的目录名）

### 2.1 个人投资者专精技能

#### ① 官方文档三剑客 `xlsx` / `pdf` / `docx` / `pptx`
- **来源**: Anthropic 官方 Agent Skills 库 (`anthropics/skills`)。
- **核心能力**:
  - `xlsx`: 支持复杂公式计算（XLOOKUP、IRR、NPV、INDEX-MATCH）、财报三张表联动、DCF 折现现金流模型构建与敏感性分析表格输出。
  - `pdf`: 专门针对长篇上市公司财报、招股说明书与券商研报，提取跨页表格、解析图表元数据并转为 Markdown / JSON。结合 Pi Agent 的 Gemini Pro 1M+ 上下文，可一次性丢入整份年报全文进行无损解析。
  - `docx` & `pptx`: 自动编排专业版投资备忘录 (Investment Memo)、尽职调查总结报告以及季度策略汇报幻灯片。
- **调用方式**:
  ```text
  /skill:pdf 解析附件 10-K 财报中的第 7 节 MD&A 及第 8 节财务报表，提取过去 3 年自由现金流 (FCF) 变化。
  /skill:xlsx 建立一个标准 5 年期 DCF 模型，WACC 设为 9.2%，永续增长率 2.5%，并附带敏感性矩阵。
  ```

#### ② `grilling`（反脆弱红队严苛质询 / 防亏损利器）
- **来源**: `mattpocock/mattpocock-skills`（中文镜像源 `vinvcn/mattpocock-skills-zh-CN`）。
- **核心价值**: 在拟定买入或调仓策略前，启动该 Skill 对投资论点进行极限压力测试。AI 切换至对抗性红队模式，针对投资者的幸存者偏差、脆弱预设、宏观下行风险与黑天鹅变量进行连续多轮严肃质询，避免盲目自信。
- **调用方式**:
  ```text
  /skill:grilling 我看好某半导体龙头公司在 AI ASIC 领域的长期增长，请对我接下来的投资逻辑进行严格的红队审查与反脆弱质询。
  ```

#### ③ `theme-factory` + `frontend-design` / `web-artifacts-builder`（专业金融可视化）
- **核心价值**: 提供金融终端级的数据图表与配色规范，支持资产净值曲线（NAV）、最大回撤柱状图、自选股相关性热力图与资产配置饼图，完美自适应深浅色模式。

---

### 2.2 全栈工程师专精技能

#### ① `ui-ux-pro-max` 及其设计规范子集
- **来源**: `nextlevelbuilder/ui-ux-pro-max-skill`。
- **包含技能**: `ui-ux-pro-max`, `design`, `design-system`, `ui-styling`, `brand`, `banner-design`, `slides` (共 7 项)。
- **核心价值**: 提供全栈工程师所需的高品质 UI/UX 规范。包含完整 Design System 指导、Tailwind CSS 配色与字体阶梯系统、微交互动效设计、无障碍规范 (WCAG) 以及落地页转化优化。
- **调用方式**:
  ```text
  /skill:ui-ux-pro-max 为当前后台看板设计一套深色科技风格设计规范，包含主色阶、阴影阶梯和圆角定义。
  /skill:design-system 重构 components/ 目录下的 Button 与 Modal 组件，确保严格对齐设计系统 Token。
  ```

#### ② `superpowers`（高标准工程方法论全家桶，14 项）
- **来源**: 官方插件生态 (`claude-plugins-official/superpowers`)。
- **核心组件**:
  - `systematic-debugging`: 彻底禁止“碰运气式”改代码，以假设驱动和日志根因追踪方式排查前后端复杂 Bug。
  - `test-driven-development`: 强制红-绿-重构循环，保障核心业务算法零差错。
  - `using-git-worktrees`: 极速创建独立 Worktree 隔离分支，方便在主线开发中无污染切入紧急 Hotfix。
  - `brainstorming`: 在技术选型与架构设计阶段进行多方案全方位评估。
  - `using-superpowers`: 会话前置守卫，确保先核对方法论再写代码。
  - `writing-plans` / `executing-plans`: 任务拆解与分步执行控制。
  - `verification-before-completion`: 交付前严格的证据链验证，杜绝未经验证的断言。
- **调用方式**:
  ```text
  /skill:systematic-debugging 后端订单结算接口在高并发时偶发 500 报错，请使用根因追踪法排查。
  /skill:test-driven-development 使用 TDD 方式为权限校验模块编写失败测试，再实现极简代码并通过。
  ```

#### ③ `domain-modeling` 与 `codebase-design`（领域驱动设计 DDD）
- **来源**: `mattpocock/mattpocock-skills`。
- **核心价值**: 严格应用领域驱动设计 (DDD)。在全栈工程中清晰定义 Aggregate Root、Entity、Value Object；在量化/交易工程中用于建模订单薄 (OrderBook)、交易头寸 (Position) 与多币种结算状态机。
- **调用方式**:
  ```text
  /skill:domain-modeling 为用户订阅与配额计费系统设计领域模型与状态转移矩阵。
  ```

#### ④ `mcp-builder`（Model Context Protocol 构建专家）
- **来源**: Anthropic 官方技能库 (`anthropics/skills/skills/mcp-builder`)。
- **核心价值**: 指导快速开发符合 MCP 规范的自定义服务，如接入本地 PostgreSQL/Redis，或把自选股行情接口封装为 MCP 工具供 Pi Agent 调用。

#### ⑤ `planning-with-files`（跨会话持久化任务树规划）
- **来源**: `OthmanAdi/planning-with-files`（专配 Pi Agent 的 `.pi/skills/planning-with-files` 适配版）。
- **核心价值**: 跨多天、跨多会话大型重构时，在磁盘持久化生成 `task_plan.md`、`findings.md` 与 `progress.md`，彻底防止上下文断层。

---

### 2.3 产品经理专精技能

#### ① `docx` & `pdf`（工业级 PRD 与需求规格书生成）
- **核心价值**: 告别结构松散的零碎文档。自动输出标准 PRD 规格书，涵盖文档版本历史、需求背景、用户画像、状态机转移表与 Given-When-Then 验收标准 (AC)。
- **调用方式**:
  ```text
  /skill:docx 导出标准 PRD 文档 (PRD_Team_Workspace.docx)，包含多租户切换完整业务流程与 AC 验收标准。
  ```

#### ② `grilling`（PRD 严苛对抗质询 / 砍需求神器）
- **核心价值**: 在功能立项前，充当极端尖锐的业务合伙人拷问伪需求：“开发 2 周换来次日留存提升 0.2% 是否值得？用户的现有替代方案是什么？”

#### ③ `commercial-skills`（SaaS 商业化阶梯定价与增收模型）
- **来源**: `alirezarezvani/claude-skills`。
- **包含组件**: `commercial-skills`, `pricing-strategist`, `commercial-policy`, `commercial-forecaster`, `deal-desk`。
- **核心价值**: 设计 Free / Pro / Enterprise 阶梯定价门槛 (Paywall)、席位单价 (Per-seat) 与用量配额，构建商业转化模型。

#### ④ `product-skills` 与 `pm-skills`（大厂产品经理与项目管理工具箱）
- **包含技能**:
  - `product-skills`: `product-manager-toolkit`, `product-strategist`, `product-discovery`, `product-analytics`, `competitive-teardown`, `experiment-designer`, `roadmap-communicator`, `spec-to-repo`, `saas-scaffolder`, `ui-design-system`, `ux-researcher-designer` (11 项)。
  - `pm-skills`: `senior-pm`, `scrum-master`, `jira-expert`, `confluence-expert`, `atlassian-admin`, `atlassian-templates`, `meeting-analyzer`, `team-communications` (8 项)。

---

## 3. 一键部署与角色安装实操

Pi Agent 的配置部署脚本 `install.sh` 已原生内置角色画像管理与技能提取逻辑：

### 3.1 预设角色画像 (Profiles)

| Profile 标识 | 角色名称 | 技能数量 | 包含技能概览 |
| :--- | :--- | :--- | :--- |
| **`minimal`** [默认] | 核心精选必备 | **18 个** | 文档三剑客 (`xlsx`, `pdf`, `docx`, `pptx`) + `superpowers` 核心规范 + `grilling` + `domain-modeling` + `ui-ux-pro-max` + `planning-with-files` + `mcp-builder` |
| **`eng`** | 全栈工程师 | **33 个** | `superpowers` 14 项全家桶 + `ui-ux-pro-max` 7 项设计系统 + `mattpocock` 建模质询 + `mcp-builder` + `webapp-testing` + `web-artifacts-builder` + `planning-with-files` |
| **`pm`** | 产品经理 | **36 个** | `docx`/`pdf` 规格书 + `grilling` + `ui-ux-pro-max` + `commercial-skills` 商业化 + `product-skills` (11项) + `pm-skills` (8项) + `planning-with-files` |
| **`invest`** | 个人投资者 | **13 个** | `xlsx`/`pdf`/`docx`/`pptx` 财报三剑客 + `grilling` + `grill-me` + `research` + `brainstorming` + 可视化套件 + `planning-with-files` |
| **`full`** | 全量生态档 | **1000+ 个** | 安装本地缓存与来源库中找到的所有可用 Skill |

---

### 3.2 常用安装命令

```bash
# 1. 部署全局精选必备技能 (minimal: 18 个核心技能，部署至 ~/.pi/agent/skills/)
./PiAgent/install.sh -s

# 2. 为全栈工程师一键部署完整工程技能库 (33 个技能)
./PiAgent/install.sh -s --profile eng

# 3. 为产品经理一键部署 PRD/商业化/敏捷协作技能库 (36 个技能)
./PiAgent/install.sh -s --profile pm

# 4. 为个人投资者一键部署财报建模/红队质询技能库 (13 个技能)
./PiAgent/install.sh -s --profile invest

# 5. 仅预览选定角色包含的技能清单 (不写盘)
./PiAgent/install.sh --list-skills --profile eng

# 6. 为当前工作区创建项目级专属配置及技能目录 (.pi/skills/)
./PiAgent/install.sh --project . -s --profile minimal

# 7. 清理目标技能目录中不在当前 profile 清单内的旧技能
./PiAgent/install.sh -s --profile minimal --prune-skills

# 8. 全新环境无 Claude 缓存时，允许自动从 GitHub 上游克隆缺失技能
./PiAgent/install.sh -s --profile eng --fetch-skills
```

---

## 4. 典型工作流调用范例

### 场景 A：个人投资者 - 新股研报与财报拆解、DCF 估值与红队质询

启动 Pi Agent 并选用超长上下文模型（如 Gemini 1.5/2.0 Pro 或 Claude 3.5 Sonnet）：

```bash
pi -m google-gemini/gemini-1.5-pro
```

1. **财报跨页长表提取**:
   ```text
   /skill:pdf 解析附件中该公司近 3 年 10-K 财报，提炼经营现金流 (OCF)、资本开支 (CapEx) 与递延所得税变动。
   ```
2. **构建 DCF 折现模型**:
   ```text
   /skill:xlsx 依据上述现金流数据构建一个 5 年期 DCF 折现现金流模型表格，WACC 设为 9.5%，永续增长率设为 2.5%，并附带敏感性矩阵。
   ```
3. **红队对抗性压力测试**:
   ```text
   /skill:grilling 我打算重仓该半导体标的，以下是我的核心投资论点：[输入论点]。请对我进行极度严苛的红队质询，逼出我的盲区与下行黑天鹅。
   ```

---

### 场景 B：全栈工程师 - DDD 领域驱动建模、高品质 UI 与 TDD 根因排查

```bash
pi -m reverse-proxy-openai/claude-3-5-sonnet-20241022
```

1. **领域驱动建模 (DDD)**:
   ```text
   /skill:domain-modeling 为当前交易订单中心设计领域模型，明确 Aggregate Root、Entity、Value Object 及多币种结算状态机。
   ```
2. **设计系统规范落地**:
   ```text
   /skill:ui-ux-pro-max 为前端交易面板设计一套科技深色风格的 UI 原型，集成实时持仓曲线与买卖盘口深度图卡片。
   ```
3. **TDD 与根因调试**:
   ```text
   /skill:systematic-debugging 订单并发创建时偶发余额扣减异常，请按照根因追踪法排查日志并重现。
   /skill:test-driven-development 用 TDD 方式编写并发失败测试用例，重构扣减事务逻辑直到测试全部通过。
   ```

---

### 场景 C：产品经理 - 工业级 PRD、严苛砍需求与 SaaS 商业化闭环

```bash
pi
```

1. **方案发散与极端边界推演**:
   ```text
   /skill:brainstorming 我们正在规划付费版“跨组织成员协作”功能。请推演极端边界场景：权限冲突、数据越权隔离与并发席位溢出。
   ```
2. **对抗质询（无情砍需求）**:
   ```text
   /skill:grilling 这是该功能的初步功能清单：[功能列表]。请充当极端挑剔的商业合伙人对这些需求进行红队质询，砍掉非核心伪需求。
   ```
3. **导出工业级 PRD 规格文档**:
   ```text
   /skill:docx 导出标准 PRD 规格说明书 (PRD_Workspace.docx)，包含用户画像、状态转移表与 Given-When-Then 研发验收标准 (AC)。
   ```
4. **制定 SaaS 商业化阶梯定价策略**:
   ```text
   /skill:commercial-skills 为该功能设计出海阶梯定价策略 (Free vs Pro vs Enterprise)，明确席位单价、功能硬隔离栅栏 (Paywall) 与配额限制。
   ```

---

## 5. 运行时加载、热重载与治理最佳实践

1. **渐进式揭示（Progressive Disclosure）**:
   Pi Agent 在初始化时只加载 Skill 的名称与简要描述，不会把数万行的 `SKILL.md` 全部塞进 Prompt。只有在任务命中或通过 `/skill:<name>` 显式调用时，才会按需读取完整指令，大幅节约 Token 并保护 Prompt Cache。
2. **热重载无需重启**:
   如果你在开发过程中手动编辑了 `~/.pi/agent/skills/<name>/SKILL.md` 或通过 `./install.sh -s` 重新部署了技能，直接在 Pi 终端交互会话中输入：
   ```text
   /reload
   ```
   Pi 将立即重新发现并加载全部最新的技能与扩展。
3. **配合大模型超长上下文优势**:
   结合 Pi Agent 的 `/model`（或 `Ctrl+P`）快捷切模功能，在处理长文档、长代码库重构时切换至 **Google Gemini Pro 1M+** 模型；在精细代码审查与重构时切换至 **Claude 3.5 Sonnet** 或 **DeepSeek-R1**（配合 `/thinking high`），达到最佳工程效能比。
