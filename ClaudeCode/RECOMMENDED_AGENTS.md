# Claude Code 高质量 Agent 专家角色选型与实战指南（全栈工程师、产品经理与个人投资者篇）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Category: Claude Code Agents](https://img.shields.io/badge/Category-Claude_Code_Agents-blue.svg)](https://github.com/anthropics/claude-code)
[![Source: agency-agents-zh](https://img.shields.io/badge/Source-agency--agents--zh-orange.svg)](https://github.com/jnMetaCode/agency-agents-zh)

本文档针对**全栈工程师**、**产品经理 (PM)** 与**个人投资者**的三重复合工作流，基于权威开源角色库 [**agency-agents-zh**](https://github.com/jnMetaCode/agency-agents-zh)（上游来自 [Agency Enterprise / agency-agents](https://github.com/agency-enterprise/agency-agents)），从第一性原理出发，梳理高价值的即插即用 AI 专家角色选型、防上下文污染工程实践及端到端实战调用范式。

---

## 1. 角色能力需求与第一性原理推导

在 Claude Code 与本地大模型（LM Studio / `clm`）体系中，**Agent 角色（Persona）** 不同于通用聊天提示词，它为大模型注入了领域专家的思维定势（Thinking Patterns）、行业标准操作程序（SOP）、严格的操作红线（Operating Rules）以及标准交付物规范（Deliverables）。

| 身份定位 | 核心业务工作流与痛点 | 所需领域专长与思维模型 | 匹配的核心 Agent 专家角色 |
| :--- | :--- | :--- | :--- |
| **全栈工程师** | • 复杂系统分层解耦与防腐层设计<br>• 高质量全栈业务编码与设计系统落地<br>• 代码异味排查、安全漏洞挖掘与重构<br>• 慢查询调优、高并发设计与 CI/CD 流水线 | • 软件架构第一性原理（高内聚低耦合、DDD、SOLID）<br>• 顶级前端无障碍 (a11y) 与组件规范<br>• OWASP Top 10 安全红队防守思维<br>• 数据库执行计划 (EXPLAIN) 与运维自动化 | • 架构类：`engineering-software-architect`<br>• 研发类：`engineering-frontend-developer`, `engineering-backend-architect`<br>• 质量类：`engineering-code-reviewer`, `security-appsec-engineer`<br>• 运维类：`engineering-devops-automator`, `engineering-database-optimizer` |
| **产品经理 (PM)** | • 真实用户痛点识别、伪需求过滤与 JTBD 建模<br>• 工业级 PRD 规范规格编写与验收标准 (AC) 定义<br>• 竞品功能矩阵、商业化转化漏斗与行为助推设计<br>• 敏捷 Sprint 需求砍伐、MVP 范围界定与排期 (RICE) | • 产品第一性原理（用户价值 = 新体验 - 旧体验 - 替换成本）<br>• 行为心理学与助推理论 (Fogg 行为模型、Hook 上瘾模型)<br>• 敏捷极限 MVP 范围削减思维 (MoSCoW/RICE)<br>• 用户体验旅程 (User Journey) 与信息架构 (IA) | • 需求定义：`product-manager`<br>• 趋势调研：`product-trend-researcher`<br>• 敏捷排期：`product-sprint-prioritizer`<br>• 反馈聚类：`product-feedback-synthesizer`<br>• 行为助推：`product-behavioral-nudge-engine`<br>• 交互架构：`design-ux-architect`, `design-ui-designer` |
| **个人投资者** | • 上市公司商业模式与护城河定性评估<br>• 财报三表交叉核验、现金流质量审计<br>• 并购重组、合规隐患与法律风险排查<br>• 前沿产业趋势、技术壁垒与竞争格局研判 | • 商业第一性原理（单位经济学、飞轮效应、定价权）<br>• 审计师视角（盈余管理、减值准备、勾稽关系）<br>• 监管与法务合规抗风险审查<br>• 产业发展周期与技术扩散曲线分析 | • 财务类：`finance-financial-analyst`, `finance-cfo`<br>• 趋势类：`product-trend-researcher`<br>• 法务类：`legal-compliance-analyst`<br>• 行业类：`specialized-mcp-builder` (行情接入) |

---

## 2. 核心架构认知：为什么严禁全部安装？

`agency-agents-zh` 提供了整整 **277 个结构化角色** 和 **64 个中国生态原创角色**。但在生产实践中，**千万不要执行全量安装！**

### 2.1 三大工程大忌

1. **规则稀释与上下文污染 (Rule & Prompt Dilution)**：
   每个结构化角色都包含数百行的 SOP、思考规则与检查清单。若全局载入几十甚至上百个角色，模型在每次上下文交互时都会被迫分流注意力，导致关键系统指令被冲淡，代码编写质量严重劣化。
2. **本地大模型 (LM Studio / `clm`) 显存与窗口瓶颈**：
   本地部署的开源模型（如 `qwen3.8-27b`、`gemma-4-31b` 等）有效上下文通常在 8k～32k 左右。全量挂载角色将瞬间挤占数万 Token，轻则导致推理变慢、显存爆满，重则直接触发上下文截断崩溃。
3. **领域无关噪声干扰**：
   正在编写 Rust/Go 后端或分析芯片制造财报时，全局挂载的“小红书文案爆款手”、“Godot 脚本开发”等角色没有任何帮助，纯属认知干扰。

### 2.2 结构化规范对比（为什么优质 Agent 远胜简单 Prompt）

| 维度 | 普通提示词 (Simple Prompt) | agency-agents-zh 结构化规范 |
| :--- | :--- | :--- |
| **思考路径** | “你是一个资深架构师，请写出...” | 内置 **Thinking Patterns**，强制按照第一性原理和系统边界逐层推演 |
| **作业程序** | 随意输出，缺乏流程推进 | 内置 **Standard Procedures (SOP)**，规范从调研、建模、审查到交付的全流程 |
| **红线约束** | 容易自由发挥、产生幻觉 | 内置 **Operating Rules**，设定架构防劣化、不破坏现有逻辑、严格安全审计等硬约束 |
| **交付物标准** | 结构松散，缺乏可验证性 | 内置 **Deliverables**，规定必须输出标准分层代码、测试用例或结构化报告 |

---

## 3. 核心精选 Agent 矩阵（精确到文件相对路径）

> **路径规范说明**：`agency-agents-zh` 仓库内的角色文件全部规范命名为 `<部门>/<部门>-<角色名>.md`。以下列出经过实战验证的核心高价值文件相对路径：

### 3.1 全栈工程师必备角色（工程研发与安全）

| 角色标识 (Agent ID) | 仓库真实相对路径 | 核心职能与适用场景 |
| :--- | :--- | :--- |
| **软件架构师** | `engineering/engineering-software-architect.md` | 系统顶层设计、领域驱动分层 (DDD)、解耦重构、技术栈选型与技术债治理 |
| **代码审查专家** | `engineering/engineering-code-reviewer.md` | 自动化代码异味检查、并发竞争排查、重构审查、命名与可维护性对齐 |
| **前端开发专家** | `engineering/engineering-frontend-developer.md` | 现代 React/Vue 组件开发、状态机管理、无障碍 (a11y) 标准与响应式交互落地 |
| **后端架构师** | `engineering/engineering-backend-architect.md` | 高并发服务治理、微服务边界定义、RESTful/gRPC 接口契约、分布式事务设计 |
| **应用安全工程师** | `security/security-appsec-engineer.md` | 代码层 OWASP Top 10 漏洞审计、鉴权流转审查、输入验证与反越权设计 |
| **DevOps 自动化专家** | `engineering/engineering-devops-automator.md` | GitHub Actions / Docker / K8s 流水线设计、自动化发布与部署配置 |
| **数据库优化师** | `engineering/engineering-database-optimizer.md` | SQL 慢查询分析、索引命中优化、分库分表与死锁风险排查 |
| **性能基准测试师** | `testing/testing-performance-benchmarker.md` | 压测场景设计、TPS/吞吐量基准建立、系统资源瓶颈定位 |
| **MCP 插件构建师** | `specialized/specialized-mcp-builder.md` | 自定义 Model Context Protocol 服务构建，快速对接私有数据与工具 |

### 3.2 个人投资者必备角色（商业研判与财务合规）

| 角色标识 (Agent ID) | 仓库真实相对路径 | 核心职能与适用场景 |
| :--- | :--- | :--- |
| **投资研究员** | `finance/finance-investment-researcher.md` | 行业生命周期、商业模式护城河、竞争格局定性分析与长期价值创造研判 |
| **资深财务分析师** | `finance/finance-financial-analyst.md` | 财报三表穿透、自由现金流核算、资产负债表健康度检验与异常科目挖掘 |
| **估值建模预测师** | `finance/finance-financial-forecaster.md` | DCF 折现模型假设推演、营收敏感性分析、多情景二元矩阵估值表构建 |
| **财务舞弊审查员** | `finance/finance-fraud-detector.md` | 异常应收账款/存货暴雷预警、盈余操纵排查与收入确认真实性核验 |
| **虚拟首席财务官 (CFO)** | `specialized/chief-financial-officer.md` | 资本配置有效性评估、债务偿付能力与回购/分红政策抗周期分析 |
| **投资风险评估师** | `specialized/specialized-risk-assessor.md` | 最大回撤风险、政策监管黑天鹅、流动性挤兑与下行保护审查 |
| **产业趋势研究员** | `product/product-trend-researcher.md` | 行业生命周期、技术扩散与渗透率测算、产业链上下游议价权分析 |
| **合规与法律分析师** | `legal/legal-contract-reviewer.md` 等 | 监管政策合规风险、反垄断与海外跨境合规、潜在诉讼排查 |

### 3.3 产品经理与体验设计必备角色（需求定义与转化增长）

| 角色标识 (Agent ID) | 仓库真实相对路径 | 核心职能与适用场景 |
| :--- | :--- | :--- |
| **标准产品经理** | `product/product-manager.md` | 需求全生命周期管理、PRD 规范编写、验收标准 (AC) 定义与需求边界锁定 |
| **产品趋势与竞品研究员** | `product/product-trend-researcher.md` | 市场调研、竞品功能对标矩阵、行业渗透率推演与差异化价值定位 |
| **敏捷 Sprint 优先级排定师** | `product/product-sprint-prioritizer.md` | 运用 RICE/MoSCoW 框架进行严苛的“需求砍伐”、MVP 范围裁剪与版本排期 |
| **用户反馈聚类综合师** | `product/product-feedback-synthesizer.md` | 汇总工单、社群与客户访谈反馈，剔除表面杂音，聚类提炼高价值痛点 (VOC) |
| **行为助推与增长引擎** | `product/product-behavioral-nudge-engine.md` | 运用 Fogg/Hook 行为模型设计用户关键激活时刻 (Aha Moment)、留存与付费转化链路 |
| **用户体验与交互架构师** | `design/design-ux-architect.md` | 信息架构 (IA) 梳理、核心操作流与异常状态机定义、降低用户认知负荷 |
| **UI 界面与设计系统师** | `design/design-ui-designer.md` | 视觉规范落地、高保真组件布局指导、微交互细节把控 |

---

## 4. 推荐部署姿势（三大无污染工作流）

### 准备工作：浅克隆仓库（秒级完成）

无论采用何种方案，首先浅克隆一份角色库到本地（仅拉取最新深度，体积小且不占空间）：

```bash
git clone --depth=1 https://github.com/jnMetaCode/agency-agents-zh.git
```

---

### 方案 A：项目级按需引入（工业界最推荐，零全局污染）

在具体的工程或投研项目根目录下，直接创建 `.claude/agents` 目录，按需拷贝当前任务直接需要的 2～3 个专家：

```bash
# 1. 进入当前的工作项目目录（如你的投研或工程目录）
cd your-project

# 2. 创建当前项目的 Claude Agent 目录
mkdir -p .claude/agents

# 3. 按需复制所需专家（以相对路径复制）
# 示例 1：Web 全栈开发项目按需引入
cp ../agency-agents-zh/engineering/engineering-software-architect.md .claude/agents/
cp ../agency-agents-zh/engineering/engineering-frontend-developer.md .claude/agents/
cp ../agency-agents-zh/security/security-appsec-engineer.md .claude/agents/

# 示例 2：个股深度投研项目按需引入
cp ../agency-agents-zh/finance/finance-investment-researcher.md .claude/agents/
cp ../agency-agents-zh/finance/finance-financial-analyst.md .claude/agents/
cp ../agency-agents-zh/finance/finance-fraud-detector.md .claude/agents/

# 提示：提取完文件后，若不需要保留原克隆仓库，可直接清理：rm -rf ../agency-agents-zh
```

---

### 方案 B-1：程序员全栈必备黄金组合（全局纯相对路径分发）

直接进入克隆后的 `agency-agents-zh` 目录，通过最简洁的相对路径分发 6 张工程高频王牌角色至 `~/.claude/agents/`：

```bash
cd agency-agents-zh
mkdir -p ~/.claude/agents

# 纯相对路径复制程序员必备组合：
# 1. 软件架构师 (顶层把关与系统解耦)
cp engineering/engineering-software-architect.md ~/.claude/agents/
# 2. 代码审查员 (质量把控与防劣化)
cp engineering/engineering-code-reviewer.md ~/.claude/agents/
# 3. 前端开发专家 (业务功能与交互落地)
cp engineering/engineering-frontend-developer.md ~/.claude/agents/
# 4. 后端架构师 (高并发与数据流设计)
cp engineering/engineering-backend-architect.md ~/.claude/agents/
# 5. 应用安全工程师 (漏洞挖掘与合规)
cp security/security-appsec-engineer.md ~/.claude/agents/
# 6. DevOps 自动化专家 (CI/CD 交付流水线)
cp engineering/engineering-devops-automator.md ~/.claude/agents/
```

---

### 方案 B-2：个人投资者专精组合（全局纯相对路径分发）

若主要使用 Claude Code 进行**研报分析、财报核验、DCF 估值建模与投资决策**，可安装投资专精组合：

```bash
cd agency-agents-zh
mkdir -p ~/.claude/agents

# 纯相对路径复制投资者必备 6 大王牌角色：
# 1. 投资研究员 (商业模式与护城河)
cp finance/finance-investment-researcher.md ~/.claude/agents/
# 2. 资深财务分析师 (财报三表交叉核验)
cp finance/finance-financial-analyst.md ~/.claude/agents/
# 3. 估值建模预测师 (DCF 估值与敏感性分析)
cp finance/finance-financial-forecaster.md ~/.claude/agents/
# 4. 财务舞弊审查员 (存货/应收账款暴雷排查)
cp finance/finance-fraud-detector.md ~/.claude/agents/
# 5. 虚拟首席财务官 (CFO 资本配置与分红回购评估)
cp specialized/chief-financial-officer.md ~/.claude/agents/
# 6. 投资风险评估师 (最大回撤与下行风险审查)
cp specialized/specialized-risk-assessor.md ~/.claude/agents/
```

> 💡 **投资配套必装 Skill 工具（大脑 + 双手）**：
> 仅有角色模型还不够，投研还需搭配解析 PDF 财报与生成 Excel 模型的底层能力：
> ```bash
> # 1. 必装：官方文档工具（解析财报 PDF + 自动生成含公式的 .xlsx 估值模型）
> npx @anthropic-ai/skills install document-skills
> 
> # 2. 必装：华尔街级投资论点严苛红队质询（防自嗨与认知盲点）
> git clone https://github.com/mattpocock/skills.git ~/.claude/skills/mattpocock
> 
> # 3. 选装：专业财务分析与 SaaS 指标包（ARR/NRR 算力、同行估值乘数）
> claude plugin marketplace add alirezarezvani/claude-skills
> claude plugin install finance-skills@claude-code-skills
> ```

---

### 方案 B-3：产品经理专精组合（全局纯相对路径分发）

若主要承担 **需求分析、用户调研反馈聚类、PRD 编写、转化漏斗设计与敏捷排期**，可安装产品经理专精组合：

```bash
cd agency-agents-zh
mkdir -p ~/.claude/agents

# 纯相对路径复制产品经理 6 大王牌角色：
# 1. 标准产品经理 (PRD 规范与验收标准 AC 定义)
cp product/product-manager.md ~/.claude/agents/
# 2. 产品趋势与竞品研究员 (市场调研与竞品矩阵)
cp product/product-trend-researcher.md ~/.claude/agents/
# 3. 敏捷 Sprint 优先级排定师 (RICE/MoSCoW 砍需求与 MVP 界定)
cp product/product-sprint-prioritizer.md ~/.claude/agents/
# 4. 用户反馈聚类综合师 (工单/社群 VOC 痛点提炼)
cp product/product-feedback-synthesizer.md ~/.claude/agents/
# 5. 行为助推与增长引擎 (Fogg/Hook 转化留存设计)
cp product/product-behavioral-nudge-engine.md ~/.claude/agents/
# 6. 用户体验与交互架构师 (信息架构 IA 与核心交互流)
cp design/design-ux-architect.md ~/.claude/agents/
```

---

### 方案 C：临时动态引用（免安装，零开销，纯相对路径）

把 `agency-agents-zh` 当作一本**本地静态字典库**。平时不拷贝任何文件，在 Claude Code 会话中直接通过相对路径指定文件，令其加载规范：

```text
> 请参考 ./agency-agents-zh/finance/finance-financial-analyst.md 中的角色规范和 SOP，帮我审查当前财报指标。
```

---

## 5. Agent 是如何启动与调用的？（底层原理与 4 种唤醒姿势）

理解 Claude Code 的 Agent 启动机制，能帮助你最高效地调度专家，并杜绝无谓的上下文浪费。

### 5.1 文件解析与自动注册机制

Claude Code CLI 在初始化时，会自动扫描并加载两处路径下的 Markdown Agent 文件：
1. **项目级 Agent（优先级最高）**：`./.claude/agents/*.md`（仅对当前仓库生效，团队可随 Git 共享）
2. **用户全局级 Agent**：`~/.claude/agents/*.md`（对当前机器所有终端会话生效）

每个 Agent 文件由 **YAML Frontmatter 元数据** 与 **正文提示词/SOP** 组成：
```markdown
---
name: engineering-software-architect
description: 资深软件架构师，精通领域驱动设计 (DDD)、系统分层解耦与技术选型
model: sonnet  # 可选：指定模型（sonnet/opus/haiku），留空则继承当前会话模型
tools: Read, Edit, Write, Bash  # 可选：限制该角色可用的工具集
---

# 思考模式 (Thinking Patterns) 与 SOP 规则正文...
```
只要将 `.md` 放入上述目录，Claude Code 在启动时就会自动将其注册为可用角色。

---

### 5.2 Agent 启动与调用的 4 种姿势

#### 姿势 1：主模型意图匹配自动委派（隐式自动启动）
Claude Code 具备原生的 **Subagent（子代理）架构**。主模型内置了 `Agent` 工具，当你在会话中提出一个复杂且专业的目标时，主模型会对比已注册 Agent 的 `description`：
* **触发机制**：主模型识别到任务适合专职角色，自动调用内置工具 `Agent({ subagent_type: "engineering-software-architect", prompt: "..." })`。
* **特点**：无需记住具体角色名称，主模型会自动寻找最合适的下属分发任务。

#### 姿势 2：自然语言显式指定（最常用推荐，指名道姓唤醒）
在对话输入框中直接点名所需角色，精准强制激活：
* **架构场景**：“调用 `engineering-software-architect` 专家，帮我审查当前微服务解耦设计并输出重构方案。”
* **投资场景**：“让 `finance-financial-analyst` 专家深入分析本财报的扣非净利润与真实经营现金流背离原因。”
* **产品场景**：“切换到 `product-manager` 模式，帮我把上述功能点整理成带 AC 验收标准的规范 PRD。”

#### 姿势 3：交互式命令查看与管理 (`/agents`)
在 Claude Code 会话终端中直接输入斜杠命令：
```text
/agents
```
终端会列出当前已加载生效的全部 Agent 清单、对应模型与描述，可直接查看或选择进入交互。

#### 姿势 4：多智能体工作流脚本驱动 (Workflow / Multi-Agent Orchestration)
在复杂的大型自动化工程或批量审计中，可以通过工作流脚本显式声明式调度不同的 Subagent：
```javascript
// 多智能体流水线示例
const archPlan = await agent("审查当前架构并输出设计方案", { 
  agentType: "engineering-software-architect" 
});

const secAudit = await agent(`基于架构方案 ${archPlan} 进行代码级安全渗透审查`, { 
  agentType: "security-appsec-engineer" 
});
```

---

### 5.3 运行时核心优势：独立上下文沙箱 (Context Sandbox)

为什么强烈推荐通过 Agent 角色运行，而不是把所有长提示词都贴在主会话中？
* **上下文完全隔离**：Subagent 在**独立的上下文沙箱子进程**中运行。假设安全审计员为了找漏洞先后读取了 30 个代码文件，产生了多达 50,000 Token 的密集排查过程——**这些庞大的中间推理过程完全不会污染主会话的上下文窗口！**
* **只交付高纯度结论**：Subagent 执行完毕后，只将提炼后的最终成果物（如审计清单、重构代码或 PRD）回传给主会话。这使得你的主会话始终保持极低的 Token 占用，会话长效不卡顿。

---

## 6. 典型工作流端到端实战范式

### 场景 A：全栈工程师 - 从零设计与构建生产级 SaaS

1. **顶层架构设计与技术栈选型**:
   ```text
   激活软件架构师 (engineering-software-architect) 模式：
   我们计划开发一套本地模型与云端 API 混合路由的网关服务，预计日均请求 500 万次。请遵循第一性原理，设计微服务拓扑图、接口契约以及容错降级策略，输出模块分层结构。
   ```
2. **高质量前端重构与无障碍支持**:
   ```text
   激活前端开发专家 (engineering-frontend-developer) 模式：
   请审查当前 components/Dashboard 目录下的组件实现，依据现代设计系统规范重构其状态流转，并补充完整的 ARIA 属性与键盘导航测试。
   ```
3. **安全审计与代码审查防守**:
   ```text
   激活应用安全工程师 (security-appsec-engineer) 模式：
   请针对 auth/ 目录中的 JWT 鉴权、Token 刷新及用户租户隔离逻辑进行深度安全审计，列出潜在的水平越权风险并提供加固代码。
   ```

---

### 场景 B：个人投资者 - 标的公司深度尽调与财报红队对抗

1. **现金流质量与财报穿透**:
   ```text
   激活财务分析师 (finance-financial-analyst) 模式：
   请结合本公司过去 3 年财报，穿透分析其经营性净现金流与净利润的背离原因，重点检查应收账款周转天数 (DSO) 变化与存货减值准备计提是否充分。
   ```
2. **资本配置与护城河压力测试**:
   ```text
   激活首席财务官 (finance-cfo) 模式：
   该公司管理层计划斥资 10 亿元进行跨界并购。请以审慎 CFO 视角评估该交易对资产负债率、利息保障倍数的影响，并评估其资本配置的长期价值创造效率。
   ```
3. **合规与潜在诉讼风险排查**:
   ```text
   激活合规分析师 (legal-compliance-analyst) 模式：
   请根据该行业最新的监管合规指导意见，评估该公司在数据隐私收集、反不正当竞争以及海外跨境业务上面临的政策法律风险敞口。
   ```

---

### 场景 C：产品经理 - 从 0 到 1 打造高转化 SaaS 核心闭环

1. **用户反馈聚类与真实痛点挖掘**:
   ```text
   激活用户反馈聚类综合师 (product-feedback-synthesizer) 模式：
   以下是过去一个月收集的 120 条用户工单和客户访谈记录：[粘贴反馈数据]。
   请根据 JTBD (Jobs To Be Done) 框架，过滤掉表面的“功能诉求”伪需求，聚类出用户底层的 3 个核心未满足痛点，并评估各痛点的频次与商业影响权重。
   ```
2. **行为助推与转化激活漏斗设计**:
   ```text
   激活行为助推与增长引擎 (product-behavioral-nudge-engine) 模式：
   针对上述痛点设计的“自动化周报导出”新功能，请运用 Fogg 行为模型 (B=MAP) 设计用户的首次激活体验 (Aha Moment)：
   - 梳理降低认知与操作门槛 (Ability) 的渐进式引导步骤。
   - 设计自然发生的触发契机 (Prompt)，提升免费版到付费版的转化意愿。
   ```
3. **工业级 PRD 规范规格输出**:
   ```text
   激活标准产品经理 (product-manager) 模式：
   请根据上述设计，输出完整的工业级 PRD 产品需求规格说明书：
   - 包含业务背景、目标用户画像、核心价值指标 (North Star Metric)。
   - 绘制核心功能流程图与异常边界状态转移表。
   - 为研发团队定义清晰、可量化、无歧义的验收标准 (Acceptance Criteria / Given-When-Then)。
   ```
4. **敏捷切分与 MVP 需求砍伐**:
   ```text
   激活敏捷 Sprint 优先级排定师 (product-sprint-prioritizer) 模式：
   请对该 PRD 中的全部功能点应用 RICE 评分框架 (Reach, Impact, Confidence, Effort)，执行严格的 MVP 范围削减，划定 Must-have（第一期上线）与 Nice-to-have（后续迭代），确保两周内可交付上线验证。
   ```

---

## 6. 维护与清理建议

- **定期体检**：使用 `ls ~/.claude/agents/` 检查全局安装的角色文件，若超过 8 个，建议果断精简，将非常用角色移出。
- **项目隔离优先**：优先在代码仓库的 `.claude/agents/` 存放针对性角色，项目完结或归档后随项目一并沉淀，不污染全局开发环境。
- **与 Skill 配合增效**：Agent 角色提供**行业思维模型与作业流程 (How to think & execute)**，而 Claude Code Skills（如 `document-skills`、`superpowers`）提供**具体执行工具与协议 (Tools & Capabilities)**，二者结合可达成最佳工程实践。
