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
