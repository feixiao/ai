# Claude Code 高质量 Skill 选型与安装指南（全栈工程师与个人投资者篇）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Category: Claude Code Skills](https://img.shields.io/badge/Category-Claude_Code_Skills-blue.svg)](https://github.com/anthropics/claude-code)

本文档针对**全栈工程师**与**个人投资者**的双重身份，从实际生产力与第一性原理出发，梳理最适合安装与配置的高质量 Skill / Plugin 工具链，并标注官方权威来源（Primary Sources）、核心应用场景与一键安装指令。

---

## 1. 角色能力需求与第一性原理推导

| 身份定位 | 核心工作流与痛点 | 所需核心能力 | 匹配的 Skill 工具类别 |
| :--- | :--- | :--- | :--- |
| **全栈工程师** | • 前端交互、设计系统与原型验证<br>• 后端接口设计、状态机与领域模型 (DDD)<br>• 代码审查、测试驱动开发 (TDD) 与根因排查<br>• 个人工具与私有数据源接入 (MCP) | • 极致 UI/UX 规范与微交互设计<br>• 严格的软件工程与反脆弱设计<br>• 自动化测试与循环自愈能力<br>• MCP 自定义 Server 构建能力 | • 前端与设计类 (`ui-ux-pro-max`, `frontend-design`)<br>• 研发规范与工程类 (`superpowers`, `code-review`, `code-simplifier`)<br>• 架构建模与测试类 (`mattpocock-skills`, `ralph-loop`)<br>• 协议与扩展类 (`mcp-builder`) |
| **个人投资者** | • 研报、公告与 10-K/年报关键数据提取<br>• 复杂财务估值模型 (DCF)、敏感性分析与联动表格<br>• 投资论点 (Thesis) 反脆弱性审查与压力测试<br>• 投资组合净值走势、持仓分布与资产配置图表呈现 | • 无损长篇 PDF 研报定位与表格抽取<br>• 严谨的电子表格公式推导与校验<br>• 红队思维与对抗性逻辑拷问 (Red Teaming)<br>• 专业级金融图表与深浅色数据可视化 | • 深度文档处理类 (`document-skills`: `xlsx`, `pdf`, `docx`, `pptx`)<br>• 逻辑推演与红队拷问类 (`mattpocock-skills:grilling`, `research`)<br>• 策略头脑风暴与规划类 (`superpowers:brainstorming`, `planning-with-files`)<br>• 金融图表与可视化类 (`dataviz`, `web-artifacts-builder`) |

---

## 2. 核心推荐技能矩阵（权威源与应用清单）

### 2.1 个人投资者专精技能

#### ① `document-skills`（官方文档三剑客）
- **权威来源**: Anthropic 官方 Agent Skills 仓库 (`anthropics/skills`)
- **包含 Skill**:
  - `xlsx`: 支持复杂公式计算（XLOOKUP、IRR、NPV、INDEX-MATCH）、财报三张表联动、DCF 折现现金流模型构建与敏感性分析表格输出。
  - `pdf`: 专门针对长篇上市公司财报、招股说明书与券商研报，支持提取跨页表格、解析图表元数据并转为 Markdown / JSON。
  - `docx` & `pptx`: 自动编排专业版投资备忘录 (Investment Memo)、尽职调查总结报告以及季度策略汇报幻灯片。
- **安装源**: `anthropic-agent-skills`

#### ② `mattpocock-skills:grilling`（反脆弱红队严苛质询）
- **权威来源**: Matt Pocock Engineering Skills (`vinvcn/mattpocock-skills-zh-CN` / `mattpocock/mattpocock-skills`)
- **核心价值**: **个人投资者不可或缺的防亏损利器**。在拟定买入或调仓策略前，启动该 Skill 对投资论点进行极限压力测试。AI 切换至对抗性红队模式，针对投资者的幸存者偏差、脆弱预设、宏观下行风险与黑天鹅变量进行连续多轮严肃质询，避免盲目自信。
- **典型用法**:
  ```text
  /mattpocock-skills:grilling 我看好某半导体龙头公司在 AI ASIC 领域的长期增长，请对我接下来的投资逻辑进行严格的红队审查与反脆弱质询。
  ```

#### ③ `dataviz`（金融与数据可视化核心规范）
- **权威来源**: Claude Code 内置官方核心能力 (`anthropics/claude-code`)
- **核心价值**: 确保生成的资产净值曲线（NAV）、最大回撤柱状图、自选股相关性热力图与资产配置饼图具备无歧视可访问性，并完美支持深色/浅色模式自适应。

---

### 2.2 全栈工程师专精技能

#### ① `ui-ux-pro-max`（现代前端设计与体验总控）
- **权威来源**: `nextlevelbuilder/ui-ux-pro-max-skill`
- **核心价值**: 提供全栈工程师所需的高品质 UI/UX 规范。包含完整 Design System 指导、Tailwind CSS 配色与字体阶梯系统、微交互动效设计、无障碍规范 (WCAG) 以及落地页转化优化。无论是开发商业 SaaS 还是构建个人量化交易看板，都能杜绝粗糙界面。
- **包含指令**: `/ui-ux-pro-max:design-system`, `/ui-ux-pro-max:ui-styling`, `/ui-ux-pro-max:banner-design`

#### ② `superpowers`（高标准工程方法论全家桶）
- **权威来源**: Anthropic 官方插件市场 (`claude-plugins-official/superpowers`)
- **核心组件**:
  - `systematic-debugging`: 彻底禁止“碰运气式”改代码，以假设驱动和日志根因追踪方式定位前后端复杂 Bug。
  - `test-driven-development`: 强制红-绿-重构循环，保障核心业务算法（如计费、量化撮合、认证鉴权）零差错。
  - `using-git-worktrees`: 极速创建独立 Worktree 隔离分支，方便在主线开发中无污染切入紧急 Hotfix。
  - `brainstorming`: 在技术选型与投资策略推演阶段进行多方案全方位评估。

#### ③ `mattpocock-skills:domain-modeling` 与 `codebase-design`
- **权威来源**: `mattpocock/mattpocock-skills`
- **核心价值**: 严格应用领域驱动设计 (DDD)。在全栈工程中清晰定义 Aggregate Root、Entity、Value Object；在投资工程中用于建模订单薄 (OrderBook)、交易头寸 (Position) 与多币种结算状态机。

#### ④ `example-skills:mcp-builder`
- **权威来源**: Anthropic 官方技能库 (`anthropics/skills/skills/mcp-builder`)
- **核心价值**: 快速指导构建符合 Model Context Protocol 规范的自定义 MCP Server。
  - **全栈场景**: 快速接入本地开发数据库（PostgreSQL/Redis）、内部微服务 API。
  - **投资场景**: 将自选行情数据源（Yahoo Finance、Alpha Vantage、富途 Open API、Interactive Brokers）封装为 MCP 工具，供 Claude 实时读取最新行情与财报数据。

#### ⑤ `code-review` & `code-simplifier`
- **权威来源**: 官方插件市场 (`claude-plugins-official`)
- **核心价值**:
  - `code-review`: 执行生产级安全性检查（SQL 注入、XSS、未校验输入、并发竞态），适合发布前验收。
  - `code-simplifier`: 消除过度抽象与重复代码，保持全栈代码库高可维护性。

#### ⑥ `ralph-loop`（长链路循环自愈）
- **权威来源**: 官方插件市场 (`claude-plugins-official/ralph-loop`)
- **核心价值**: 针对重构、迁移或复杂功能开发，自动循环执行 `编写代码 -> 运行测试 -> 捕获报错 -> 修正代码`，直到全部测试通过才退出。

---

### 2.3 复合场景：规划与持久化追踪

#### `planning-with-files`（基于文件的跨会话深度规划）
- **权威来源**: `OthmanAdi/planning-with-files`
- **双重价值**:
  - **全栈场景**: 大型全栈系统（如重构认证体系、数据库分库分表）跨多天、跨多会话开发时，用持久化 Markdown 文件记录任务树与进度。
  - **投资场景**: 跟踪跨季度的标的研究笔记、估值模型更新历程与组合再平衡日志。

---

### 2.4 进阶垂类专项补充库（按需即插即用）

#### `alirezarezvani/claude-skills`（388+ 垂类专家技能军火库）
- **权威来源**: [`alirezarezvani/claude-skills`](https://github.com/alirezarezvani/claude-skills)（开源庞大技能合集，按需精准装载）
- **定位与引入原则**: **坚决不做全量引入，避免上下文污染**；只在跨入深度行业垂直场景、现有基础通用工具出现能力瓶颈时作为“专项补丁”按需启用。
- **何时补充（针对双重角色）**:
  1. **个人投资者 - 垂直赛道与前沿科技尽调时补充**:
     - `finance/saas-metrics-coach`: 美股/港股 SaaS 及订阅制公司深度研报拆解（ARR、NRR 净留存率、CAC Payback、Rule of 40 专项指标计算与校验）。
     - `finance/stock-analysis`: 自动构建包含同行估值乘数对比（P/E、EV/EBITDA）、护城河定性评估的标准机构级研究框架。
     - `research/deep-research`、`research/litreview` 与 `research/patent`: 投资 AI 芯片、半导体新工艺或生物医药等硬科技时，跨学术文献与专利库进行技术壁垒与潜在诉讼风险交叉验证。
  2. **全栈工程师 - AI 原生架构与生产级韧性演习时补充**:
     - `engineering/rag-architect`: 工业级 RAG 架构选型（分块策略、混合检索 BM25 + 向量、Rerank 模型调优与召回评估）。
     - `engineering/agent-workflow-designer` 与 `engineering/memory-engineering`: 多智能体复杂拓扑路由、长短期状态机及 Agent 上下文生命周期设计。
     - `engineering/slo-architect`、`chaos-engineering` 与 `performance-profiler`: 建立生产级 SLI/SLO 监控、故障注入/网络分区演练以及全栈性能瓶颈剖析。
     - `compliance-os` 与 `commercial/pricing-strategist`: 独立 SaaS 产品商业化出海（GDPR/SOC 2 证据链自查）与阶梯定价（Tiered Pricing/Freemium）转化模型设计。
- **安装与引入方式**:
  - **推荐方式（按需轻量引入，无上下文污染）**: 直接克隆该仓库到本地临时目录，仅将所需的单个技能文件夹软链或复制到项目或全局 skills 目录中：
    ```bash
    # 1. 克隆仓库至本地目录
    git clone --depth 1 https://github.com/alirezarezvani/claude-skills.git ~/.claude/repos/claude-skills

    # 2. 针对性软链所需技能到全局 ~/.claude/skills/（即插即用）
    ln -s ~/.claude/repos/claude-skills/skills/finance/saas-metrics-coach ~/.claude/skills/saas-metrics-coach
    ln -s ~/.claude/repos/claude-skills/skills/engineering/rag-architect ~/.claude/skills/rag-architect
    ```
  - **Marketplace 分领域插件包安装（按需装载对应专业包）**:
    该仓库通过 `.claude-plugin/marketplace.json` 将 388+ 项技能按领域打包拆分为多个模块化插件包（Marketplace 名称统一为 `claude-code-skills`）。你可以根据自身任务需求，仅安装对应的领域包：

    ```bash
    # 步骤 0：首先注册该市场源
    claude plugin marketplace add alirezarezvani/claude-skills

    # ====== 1. 金融分析与投资决策包 (Finance & Capital) ======
    claude plugin install finance-skills@claude-code-skills             # 基础财务与量化包（SaaS 估值、财报指标、选股框架）
    claude plugin install business-investment-advisor@claude-code-skills # 商业投资决策与资本配置专业顾问

    # ====== 2. 软件工程与进阶架构包 (Engineering & Architecture) ======
    claude plugin install engineering-skills@claude-code-skills          # 32项通用核心工程能力（重构、规范、API设计）
    claude plugin install engineering-advanced-skills@claude-code-skills # 37项高阶架构（RAG架构、Agent拓扑、内存工程、SLO/混沌工程）
    claude plugin install pw@claude-code-skills                          # 生产级 Playwright E2E 自动化端到端测试套件

    # ====== 3. 深度研究、文献与知识产权包 (Deep Research & Tech) ======
    claude plugin install research-ops-skills@claude-code-skills         # 企业级跨领域研究操作体系 (Research Ops)
    claude plugin install deep-research@claude-code-skills               # 针对高权重问题的规范多源元研究 (Meta-Research)
    claude plugin install litreview@claude-code-skills                   # 学术前沿文献研读与综合评述
    claude plugin install patent@claude-code-skills                      # 专利现有技术与知识产权格局分析 (IP Landscape)
    claude plugin install pulse@claude-code-skills                       # 多源前沿动态与资讯实时追踪

    # ====== 4. 商业变现、定价与出海合规包 (Commercial & Compliance) ======
    claude plugin install commercial-skills@claude-code-skills          # 商业化变现策略、打包与增收模型
    claude plugin install compliance-os@claude-code-skills              # 跨框架合规元编排（SOC 2 / GDPR 等）
    claude plugin install compliance-team-eu-ai-act@claude-code-skills  # 欧盟 AI 法案 (EU AI Act) 合规专项
    claude plugin install compliance-team-iso42001@claude-code-skills   # ISO 42001 人工智能管理体系专精
    claude plugin install ra-qm-skills@claude-code-skills               # 医疗/健康科技法规事务与质量管理 (14 项专精)

    # ====== 5. 产品设计与项目管理包 (Product & Project Management) ======
    claude plugin install product-skills@claude-code-skills              # 13 项产品技能 + 22 个实用 Python 工具
    claude plugin install pm-skills@claude-code-skills                   # 9 项项目管理技能 + 15 个实用 Python 工具
    claude plugin install business-growth-skills@claude-code-skills      # 5 项业务增长与增长黑客模型
    claude plugin install business-operations-skills@claude-code-skills  # 内部 BizOps 运营与效率优化包

    # ====== 6. 高管与创始人战略顾问包 (C-Level & Executive) ======
    claude plugin install c-level-skills@claude-code-skills              # 33 项高管顾问技能（CEO/CTO/CFO 顶层视角）
    claude plugin install c-level-agents@claude-code-skills              # 创始人模式高管智能体团队协作
    ```

---

## 3. 安装与配置实操清单

### 步骤 1：注册官方与高质量第三方插件市场 (Marketplaces)

在终端或 Claude Code 会话中添加以下权威源：

```bash
# 1. 官方插件市场 (包含 superpowers, code-review, code-simplifier, ralph-loop 等)
claude plugin marketplace add anthropics/claude-plugins-official

# 2. Anthropic 官方 Agent Skills 库 (包含 document-skills, example-skills 等)
claude plugin marketplace add anthropics/skills

# 3. Matt Pocock 专家技能库中文源
claude plugin marketplace add vinvcn/mattpocock-skills-zh-CN

# 4. 前端顶级设计与规范库 UI/UX Pro Max
claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill

# 5. 持久化文件任务规划插件
claude plugin marketplace add OthmanAdi/planning-with-files

# 6. 进阶垂类专家技能军火库（包含 388+ 项技能的分包源）
claude plugin marketplace add alirezarezvani/claude-skills
```

---

### 步骤 2：精选插件一键安装命令

```bash
# ====== 个人投资者核心必备 ======
claude plugin install document-skills@anthropic-agent-skills    # Excel/PDF/Word/PPT 处理
claude plugin install mattpocock-skills@mattpocock              # 投资论点红队质询、一手事实调研与领域建模

# ====== 全栈工程师核心必备 ======
claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill          # 顶级前端设计系统与 UI 交互规范
claude plugin install superpowers@claude-plugins-official        # 工程方法论全家桶 (TDD/根因调试/Git Worktree)
claude plugin install example-skills@anthropic-agent-skills      # MCP Server 编写、Web 测试与原型工具
claude plugin install code-review@claude-plugins-official        # 自动化安全与代码审查
claude plugin install code-simplifier@claude-plugins-official    # 消除冗余抽象与代码精炼
claude plugin install ralph-loop@claude-plugins-official         # 自动化循环修复闭环

# ====== 架构与长周期跟踪共同必备 ======
claude plugin install planning-with-files@planning-with-files    # 跨会话长期规划与进度管理

# ====== 进阶垂类专项补充包（选装，按需启用对应领域包） ======
# claude plugin install finance-skills@claude-code-skills             # 财务与量化基础包
# claude plugin install business-investment-advisor@claude-code-skills # 商业投资与资本配置顾问
# claude plugin install engineering-skills@claude-code-skills          # 32项通用核心工程能力
# claude plugin install engineering-advanced-skills@claude-code-skills # 37项高阶架构与多智能体系统
# claude plugin install deep-research@claude-code-skills               # 硬科技深度调研与研报分析
# claude plugin install patent@claude-code-skills                      # 专利与知识产权壁垒分析
# claude plugin install compliance-os@claude-code-skills              # SaaS 出海合规 (GDPR/SOC2)
```

---

## 4. 典型工作流调用范例

### 场景 A：个人投资者 - 新股研报拆解与红队投资决策
1. **财报提取**:
   ```text
   使用 document-skills:pdf 解析该公司最新的 10-K 财报，提炼过去 3 年自由现金流 (FCF)、毛利率变化趋势与潜在诉讼风险。
   ```
2. **构建 DCF 估值模型**:
   ```text
   使用 document-skills:xlsx 编写一个 5 年期 DCF 折现现金流模型，WACC 设定为 9.5%，永续增长率设定为 2.5%，并附带敏感性分析表格。
   ```
3. **红队质询与反脆弱测试**:
   ```text
   /mattpocock-skills:grilling 我打算将该标的纳入核心仓位，以下是我的投资逻辑：[输入投资逻辑]。请对我进行极度严格的红队审查，指出我未曾考虑的致命盲点。
   ```

---

### 场景 B：全栈工程师 - 开发个人投资组合管理看板
1. **领域驱动建模**:
   ```text
   /mattpocock-skills:domain-modeling 为投资组合系统设计领域模型，涵盖 Asset、Position、Transaction、Dividend 以及 Realized/Unrealized PnL 计算。
   ```
2. **设计系统与前端构建**:
   ```text
   /ui-ux-pro-max:design 为投资组合仪表盘构建一套深色金融科技风格的 UI 原型，集成净值曲线图与持仓分布卡片。
   ```
3. **对接自定义数据源 MCP**:
   ```text
   使用 example-skills:mcp-builder 指导我开发一个 Python FastMCP 服务，抓取并暴露自选股的实时行情数据。
   ```
4. **自动化代码评审与交付**:
   ```text
   /code-review:code-review 对本次提交的前后端代码进行安全性与逻辑严密性审查。
   ```

---

## 5. 技能自主选择、路由与动态启停管理（Meta-Skills & Router）

随着安装的插件和技能数量增多，如果将所有技能内容全量塞入 Prompt，不仅会消耗大量上下文 Token，还会导致模型注意力稀释与技能指令冲突。因此，Claude Code 生态从底层机制到应用层设计了完备的**自主选择、分流路由与动态启停治理机制**。

### 5.1 底层运行逻辑：渐进式自适应加载（Progressive Disclosure）

Claude Code 的原生架构遵循“渐进式揭示”的第一性原理：
1. **轻量化元数据索引常驻**：安装的所有 Skill 默认仅将其 YAML Frontmatter（即 `name`、`description` 和 `when_to_use` 规则，通常仅几行文字）加载到底层系统提示词的可用技能索引表中，上下文开销微乎其微；
2. **意图匹配与自主调起**：当用户在会话中输入任务需求时，模型会自发进行语义匹配。一旦判定当前任务命中某项 Skill 的职责范围，模型会**主动调用内置的 `Skill` 内部工具**，动态将该技能的完整实操指南（`SKILL.md`）按需加载进上下文窗口并执行；
3. **隔离执行**：部分特殊技能（如测试评估、代码精简）还可声明在独立子代理（Subagent）中运行，避免污染主会话上下文。

---

### 5.2 调度指挥与元技能（Meta-Skills / Routers）

除了模型自发的意图识别，还可以引入专职的“元技能（Meta-Skill）”来对技能进行主动调度与决策编排：

#### ① 官方核心元技能：`superpowers:using-superpowers`
- **定位**：会话前置决策总控。
- **运行逻辑**：作为全局守卫，强制 Agent 在回答任何问题或采取行动之前，先核对技能清单。它内置了强逻辑推导：
  - 遇到“修复 Bug / 报错排查” $\rightarrow$ 强制先行拉起 `superpowers:systematic-debugging`；
  - 遇到“实现新功能 / 架构设计” $\rightarrow$ 强制先行拉起 `superpowers:brainstorming`；
  - 遇到“前端交互 / 视觉优化” $\rightarrow$ 自动转接 `ui-ux-pro-max`；
  - 遇到“投资论点审查” $\rightarrow$ 自动拉起 `mattpocock-skills:grilling`。

#### ② 社区智能路由元技能：`skill-router`
- **定位**：面向多技能环境的轻量意图路由器。
- **运行方式**：
  - **建议模式（Suggest Mode）**：识别用户输入后，列出最匹配的 1~3 个候选 Skill 并解释原因，由用户确认后加载；
  - **自动模式（Auto Mode）**：设置 `/skill-router on --auto` 后，由 Router 智能体静默判定最佳技能并在后台完成自动无缝调度。

#### ③ 垂直任务级混合路由器：`research-orchestrator` 与 `agent-harness`
- **权威来源**：[`alirezarezvani/claude-skills`](https://github.com/alirezarezvani/claude-skills)
- **核心场景**：针对长链路研究任务，`research-orchestrator` 会根据问题深度动态按序调度 `pulse`（动态资讯）、`litreview`（学术论文）和 `patent`（专利壁垒），实现复杂任务链的自适应分流。

---

### 5.3 插件与技能的动态启停控制（用户级手动治理）

当安装了大量专业领域插件包后，可以通过 Claude Code 提供的管理工具实现即开即关：

#### ① 交互式终端可视化管理：`/plugin`
在 Claude Code 终端中输入：
```text
/plugin
```
会启动一个终端 TUI 交互面板。支持通过键盘方向键、空格和回车键，随时对已安装插件进行 **Enable（启用）**、**Disable（禁用）** 与 **Uninstall（卸载）** 的无缝切换。

#### ② CLI 命令行精准控制：
```bash
# 1. 列出当前所有已安装插件及其激活状态 (enabled / disabled)
claude plugin list

# 2. 临时禁用某一领域包（如在专注工程时关闭金融包，避免意图干扰）
claude plugin disable finance-skills@claude-code-skills

# 3. 重新启用指定插件包
claude plugin enable finance-skills@claude-code-skills

# 4. 彻底卸载不再使用的插件包
claude plugin uninstall compliance-os@claude-code-skills
```

---

### 5.4 双重角色管理最佳实践清单

| 角色工作阶段 | 建议激活的核心插件组合 | 临时禁用的插件组合 | 收益 |
| :--- | :--- | :--- | :--- |
| **全栈研发与重构** | • `superpowers`<br>• `ui-ux-pro-max`<br>• `code-review`<br>• `engineering-skills` | • `finance-skills`<br>• `research-ops-skills` | 保证代码审查、调试与前端设计系统指令绝对精准，无金融语义干扰。 |
| **投资尽调与估值建模** | • `document-skills`<br>• `mattpocock-skills`<br>• `finance-skills`<br>• `dataviz` | • `engineering-skills`<br>• `ui-ux-pro-max` | 强化财务模型推导、表格联动与红队逻辑质询，提高长文本财报处理速度。 |
| **长期跨周期项目** | • `planning-with-files` | 无 | 无论研发还是投研，保持全局任务追踪文件常态化更新。 |

