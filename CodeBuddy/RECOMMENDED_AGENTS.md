# CodeBuddy 高质量 Agent 专家角色选型与实战指南（全栈工程师、产品经理与个人投资者篇）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Category: CodeBuddy Agents](https://img.shields.io/badge/Category-CodeBuddy_Agents-blue.svg)](https://cnb.cool/codebuddy/codebuddy-code)
[![Source: agency-agents-zh](https://img.shields.io/badge/Source-agency--agents--zh-orange.svg)](https://github.com/jnMetaCode/agency-agents-zh)

本文档是 [`../ClaudeCode/RECOMMENDED_AGENTS.md`](../ClaudeCode/RECOMMENDED_AGENTS.md) 的 CodeBuddy 移植版。基于权威开源角色库 [**agency-agents-zh**](https://github.com/jnMetaCode/agency-agents-zh)（上游 [Agency Enterprise / agency-agents](https://github.com/agency-enterprise/agency-agents)），针对全栈工程师、产品经理与个人投资者三重复合工作流，梳理即插即用的专家角色选型、防上下文污染工程实践与端到端调用范式。

---

## 0. 与 Claude Code 的关键差异（先读这一节）

CodeBuddy 的子代理（Subagent）与 Claude Code 高度同源，但有三处会导致"复制过去不生效"的差异：

### 0.1 `name` 必须是 ASCII 标识符（最容易踩的坑）

Claude Code 允许 `name: 软件架构师` 这类中文名；**CodeBuddy 要求 `name` 为小写字母与连字符组成的唯一标识符**，否则代理不会被正确注册。

```yaml
# ❌ 从 agency-agents-zh 直接复制的原文
---
name: 软件架构师
description: 软件架构专家，精通系统设计、领域驱动设计……
emoji: 🏛️
color: indigo
---

# ✅ CodeBuddy 需要的写法（name = 文件名主干，emoji/color 移除）
---
name: engineering-software-architect
description: 软件架构专家，精通系统设计、领域驱动设计……
---
```

本仓库的 `install.sh` 已自动完成该归一化，无需手工处理。

### 0.2 `model` 字段不使用 Claude 别名

`opus` / `sonnet` / `haiku` 在 CodeBuddy 中不是有效模型 ID。脚本会统一改写为 `model: inherit`（继承主会话模型）。CodeBuddy 支持模型 ID、别名或 `lite` / `reasoning` 场景变体，可在 `/agents` 面板中按子代理粒度单独设置。

### 0.3 目录与优先级

| 类型 | 位置 | 作用域 | 优先级 |
| :--- | :--- | :--- | :--- |
| 项目级 | `.codebuddy/agents/` | 当前项目，可随 Git 共享 | 最高 |
| 用户级 | `~/.codebuddy/agents/` | 本机所有会话 | 较低 |
| CLI 动态定义 | `codebuddy --agents '{...}'` | 本次会话 | 介于两者之间 |

---

## 1. 角色能力需求与第一性原理推导

**Agent 角色（Persona）** 不同于通用聊天提示词：它为模型注入领域专家的思维定势（Thinking Patterns）、行业标准操作程序（SOP）、操作红线（Operating Rules）与标准交付物（Deliverables）。

| 身份定位 | 核心业务工作流与痛点 | 所需领域专长与思维模型 | 匹配的核心 Agent 角色 |
| :--- | :--- | :--- | :--- |
| **全栈工程师** | • 系统分层解耦与防腐层设计<br>• 全栈业务编码与设计系统落地<br>• 代码异味排查、安全漏洞挖掘与重构<br>• 慢查询调优、高并发与 CI/CD | • 架构第一性原理（高内聚低耦合、DDD、SOLID）<br>• 前端无障碍 (a11y) 与组件规范<br>• OWASP Top 10 安全红队防守思维<br>• 执行计划 (EXPLAIN) 与运维自动化 | `engineering-software-architect`<br>`engineering-code-reviewer`<br>`engineering-frontend-developer`<br>`engineering-backend-architect`<br>`security-appsec-engineer`<br>`engineering-devops-automator` |
| **产品经理 (PM)** | • 真实痛点识别、伪需求过滤与 JTBD 建模<br>• PRD 规范与验收标准 (AC) 定义<br>• 竞品功能矩阵、转化漏斗与行为助推<br>• Sprint 需求砍伐与 MVP 范围界定 (RICE) | • 产品第一性原理（用户价值 = 新体验 − 旧体验 − 替换成本）<br>• 行为心理学（Fogg 行为模型、Hook 上瘾模型）<br>• 敏捷 MVP 范围削减（MoSCoW / RICE）<br>• 用户旅程与信息架构 (IA) | `product-manager`<br>`product-trend-researcher`<br>`product-sprint-prioritizer`<br>`product-feedback-synthesizer`<br>`product-behavioral-nudge-engine`<br>`design-ux-architect` |
| **个人投资者** | • 商业模式与护城河定性评估<br>• 财报三表交叉核验、现金流质量审计<br>• 并购重组、合规隐患与法律风险<br>• 产业趋势、技术壁垒与竞争格局 | • 商业第一性原理（单位经济学、飞轮效应、定价权）<br>• 审计师视角（盈余管理、减值准备、勾稽关系）<br>• 监管与法务合规抗风险审查<br>• 产业周期与技术扩散曲线 | `finance-financial-analyst`<br>`finance-investment-researcher`<br>`finance-financial-forecaster`<br>`finance-fraud-detector`<br>`specialized-risk-assessor` |

---

## 2. 核心架构认知：为什么严禁全量安装？

`agency-agents-zh` 提供 **277 个结构化角色 + 64 个中国生态原创角色**。生产实践中**千万不要全量安装**：

### 2.1 三大工程大忌

1. **规则稀释与上下文污染 (Rule & Prompt Dilution)**：每个角色含数百行 SOP、思考规则与检查清单。全局载入几十上百个角色会分流模型注意力，导致关键指令被冲淡，代码质量明显劣化。
2. **本地模型显存与窗口瓶颈**：本地部署的开源模型有效上下文常为 8k～32k，全量挂载会瞬间挤占数万 Token，轻则推理变慢，重则触发上下文截断。
3. **领域无关噪声干扰**：写 Rust/Go 后端或分析芯片财报时，"小红书爆款文案手"这类角色纯属认知干扰。

### 2.2 结构化规范对比

| 维度 | 普通提示词 | agency-agents-zh 结构化规范 |
| :--- | :--- | :--- |
| **思考路径** | "你是一个资深架构师，请写出…" | 内置 **Thinking Patterns**，按第一性原理与系统边界逐层推演 |
| **作业程序** | 随意输出，缺乏流程 | 内置 **Standard Procedures (SOP)**，规范调研 → 建模 → 审查 → 交付全流程 |
| **红线约束** | 容易自由发挥、产生幻觉 | 内置 **Operating Rules**，设定架构防劣化、不破坏现有逻辑等硬约束 |
| **交付物标准** | 结构松散 | 内置 **Deliverables**，规定必须输出分层代码、测试用例或结构化报告 |

---

## 3. 已安装 Agent 清单（`~/.codebuddy/agents/`，共 18 个）

> `name` 即文件名主干，也是自然语言点名调用时使用的标识符。

### 3.1 全栈工程师（研发与安全，7 个）

| Agent ID | 核心职能与适用场景 |
| :--- | :--- |
| `engineering-software-architect` | 系统顶层设计、领域驱动分层 (DDD)、解耦重构、技术栈选型与技术债治理 |
| `engineering-code-reviewer` | 代码异味检查、并发竞争排查、重构审查、命名与可维护性对齐 |
| `engineering-frontend-developer` | 现代 React/Vue 组件开发、状态机管理、无障碍 (a11y) 标准与响应式交互落地 |
| `engineering-backend-architect` | 高并发服务治理、微服务边界定义、RESTful/gRPC 接口契约、分布式事务设计 |
| `security-appsec-engineer` | OWASP Top 10 代码层审计、鉴权流转审查、输入验证与反越权设计 |
| `engineering-devops-automator` | GitHub Actions / Docker / K8s 流水线设计、自动化发布与部署配置 |
| `code-simplifier` | 消除过度抽象与重复代码，在不改变行为的前提下提升清晰度与一致性 |

### 3.2 个人投资者（商业研判与财务合规，6 个）

| Agent ID | 核心职能与适用场景 |
| :--- | :--- |
| `finance-investment-researcher` | 行业生命周期、商业模式护城河、竞争格局定性分析与长期价值创造研判 |
| `finance-financial-analyst` | 财报三表穿透、自由现金流核算、资产负债表健康度检验与异常科目挖掘 |
| `finance-financial-forecaster` | DCF 折现模型假设推演、营收敏感性分析、多情景二元矩阵估值表构建 |
| `finance-fraud-detector` | 异常交易与流水模式识别、风控策略与反欺诈审查 |
| `specialized-risk-assessor` | 企业级风险管理、内控合规、ESG 与供应链风险识别、评估与应对 |
| `product-trend-researcher` | 行业生命周期、技术扩散与渗透率测算、产业链上下游议价权分析 |

### 3.3 产品经理与体验设计（5 个）

| Agent ID | 核心职能与适用场景 |
| :--- | :--- |
| `product-manager` | 需求全生命周期管理、PRD 规范编写、验收标准 (AC) 定义与需求边界锁定 |
| `product-sprint-prioritizer` | 运用 RICE / MoSCoW 严苛"砍需求"、MVP 范围裁剪与版本排期 |
| `product-feedback-synthesizer` | 汇总工单、社群与访谈反馈，剔除表面杂音，聚类提炼高价值痛点 (VOC) |
| `product-behavioral-nudge-engine` | 运用 Fogg / Hook 模型设计关键激活时刻 (Aha Moment)、留存与付费转化链路 |
| `design-ux-architect` | 信息架构 (IA) 梳理、核心操作流与异常状态机定义、降低用户认知负荷 |

### 3.4 可选补充角色（按需从上游仓库追加）

原始推荐矩阵中尚未安装、但值得按场景补入的角色：

| Agent ID | 上游相对路径 | 适用场景 |
| :--- | :--- | :--- |
| `engineering-database-optimizer` | `engineering/engineering-database-optimizer.md` | SQL 慢查询分析、索引命中优化、分库分表与死锁排查 |
| `testing-performance-benchmarker` | `testing/testing-performance-benchmarker.md` | 压测场景设计、TPS/吞吐量基准、资源瓶颈定位 |
| `specialized-mcp-builder` | `specialized/specialized-mcp-builder.md` | 自定义 MCP Server 对接私有数据源与行情 API |
| `chief-financial-officer` | `specialized/chief-financial-officer.md` | 资本配置有效性、债务偿付能力与回购/分红政策抗周期分析 |
| `legal-contract-reviewer` | `legal/legal-contract-reviewer.md` | 监管合规风险、反垄断与跨境合规、潜在诉讼排查 |
| `design-ui-designer` | `design/design-ui-designer.md` | 视觉规范落地、高保真组件布局与微交互细节把控 |

补充方式：

```bash
git clone --depth=1 https://github.com/jnMetaCode/agency-agents-zh.git /tmp/agency-agents-zh
cp /tmp/agency-agents-zh/engineering/engineering-database-optimizer.md ~/.codebuddy/agents/
# 注意：复制后需把 frontmatter 的 name 改为文件名主干（参见 0.1 节）
```

---

## 4. 推荐部署姿势

### 方案 A：项目级按需引入（工业界最推荐，零全局污染）

在具体工程或投研项目根目录创建 `.codebuddy/agents/`，只放当前任务直接需要的 2～3 个专家：

```bash
cd your-project
mkdir -p .codebuddy/agents

cp ~/.codebuddy/agents/engineering-software-architect.md .codebuddy/agents/
cp ~/.codebuddy/agents/engineering-frontend-developer.md  .codebuddy/agents/
cp ~/.codebuddy/agents/security-appsec-engineer.md        .codebuddy/agents/
```

### 方案 B：用户级全局组合（本脚本默认）

`./install.sh` 会把 18 个角色写入 `~/.codebuddy/agents/`，对本机所有会话生效。适合三重复合角色高频切换的个人工作流。

### 方案 C：临时动态引用（免安装，零开销）

把 `agency-agents-zh` 当作本地静态字典库，会话中直接按路径点名：

```text
> 参考 ./agency-agents-zh/finance/finance-financial-analyst.md 中的角色规范和 SOP，帮我审查当前财报指标。
```

### 方案 D：CLI 动态定义（一次性、不落盘）

```bash
codebuddy --agents '{
  "code-reviewer": {
    "description": "代码审查专家。代码变更后主动使用。",
    "prompt": "你是一位高级代码审查员，专注代码质量、安全性与最佳实践。",
    "tools": ["Read", "Grep", "Glob", "Bash"]
  }
}'
```

---

## 5. Agent 是如何启动与调用的？

### 5.1 文件解析与自动注册

CodeBuddy 启动时自动扫描 `./.codebuddy/agents/*.md`（项目级，优先级最高）与 `~/.codebuddy/agents/*.md`（用户级）。每个文件由 YAML Frontmatter 与正文 SOP 组成：

```yaml
---
name: engineering-software-architect   # 必填，小写字母 + 连字符
description: 软件架构专家，精通系统设计、领域驱动设计……   # 必填，决定自动委派命中率
tools: Read, Edit, Write, Bash         # 可选，省略则继承全部工具
model: inherit                         # 可选：模型 ID / lite / reasoning / inherit
permissionMode: default                # 可选：default | acceptEdits | bypassPermissions | plan | ignore
skills: xlsx, pdf                      # 可选：启动时自动加载的技能
memory: user                           # 可选：user | project | local 持久记忆作用域
maxTurns: 30                           # 可选：最大执行轮次
background: false                      # 可选：true 时总是后台运行
---
```

> 手动新增文件后需**重启会话**才会加载；想立即使用请改用 `/agents` 命令创建。

### 5.2 四种唤醒姿势

#### 姿势 1：主模型意图匹配自动委派
主模型内置 `Agent` 工具，对比已注册 Agent 的 `description` 自动分发任务：
- **触发机制**：识别到任务适合专职角色时，自动调用 `Agent({ subagent_type: "engineering-software-architect", prompt: "..." })`。
- **技巧**：在 `description` 中加入 "主动使用"、"MUST BE USED" 之类措辞可提高命中率。

#### 姿势 2：自然语言显式点名（最常用）
```text
> 调用 engineering-software-architect，审查当前微服务解耦设计并输出重构方案。
> 让 finance-financial-analyst 分析本财报扣非净利润与经营现金流背离的原因。
> 切换到 product-manager 模式，把上述功能点整理成带 AC 验收标准的规范 PRD。
```

#### 姿势 3：交互式管理面板
```text
/agents
```
可查看全部内置 / 用户 / 项目级子代理，编辑工具权限与模型，为内置子代理（`Explore`、`general-purpose`、`Plan`）单独设置模型或 `lite` / `reasoning` 场景变体。

#### 姿势 4：多智能体编排
```text
> 先用 engineering-software-architect 审查架构并输出设计方案，
> 再让 security-appsec-engineer 基于该方案做代码级安全渗透审查。
```
也可在后台并行：
```text
> 在后台运行 engineering-code-reviewer 审查整个代码库
```

### 5.3 运行时核心优势：独立上下文沙箱

- **上下文完全隔离**：子代理在独立的上下文子进程中运行。假设安全审计员读了 30 个代码文件、产生 50,000 Token 的密集排查过程——这些中间推理**完全不会污染主会话上下文**。
- **只交付高纯度结论**：执行完毕后仅回传提炼后的成果物（审计清单、重构代码或 PRD），主会话始终保持极低 Token 占用。

> **边界**：子代理嵌套深度封顶 5 层（主会话为第 0 层）；每会话 spawn 预算默认 200 次，可用 `CODEBUDDY_CODE_MAX_SUBAGENTS_PER_SESSION` 调整。

---

## 6. 典型工作流端到端实战范式

### 场景 A：全栈工程师——从零设计与构建生产级 SaaS

1. **顶层架构设计与技术栈选型**
   ```text
   调用 engineering-software-architect：我们计划开发一套本地模型与云端 API 混合路由的网关服务，
   日均请求 500 万次。请遵循第一性原理设计微服务拓扑、接口契约与容错降级策略，输出模块分层结构。
   ```
2. **高质量前端重构与无障碍支持**
   ```text
   调用 engineering-frontend-developer：审查 components/Dashboard 下的组件实现，
   依据现代设计系统规范重构状态流转，并补充完整的 ARIA 属性与键盘导航测试。
   ```
3. **安全审计与代码审查防守**
   ```text
   调用 security-appsec-engineer：针对 auth/ 目录中的 JWT 鉴权、Token 刷新与租户隔离逻辑
   做深度安全审计，列出潜在水平越权风险并给出加固代码。
   ```

---

### 场景 B：个人投资者——标的公司深度尽调与财报红队对抗

1. **现金流质量与财报穿透**
   ```text
   调用 finance-financial-analyst：结合过去 3 年财报，穿透分析经营性净现金流与净利润的背离原因，
   重点检查应收账款周转天数 (DSO) 变化与存货减值准备计提是否充分。
   ```
2. **估值与情景压力测试**
   ```text
   调用 finance-financial-forecaster：构建 5 年期 DCF 模型，给出乐观 / 中性 / 悲观三档情景，
   并输出 WACC 与永续增长率的二维敏感性矩阵。
   ```
3. **舞弊信号与下行风险审查**
   ```text
   调用 finance-fraud-detector 排查异常应收与存货科目；
   再调用 specialized-risk-assessor 评估政策监管、流动性与最大回撤风险。
   ```

---

### 场景 C：产品经理——从 0 到 1 打造高转化 SaaS 核心闭环

1. **用户反馈聚类与真实痛点挖掘**
   ```text
   调用 product-feedback-synthesizer：以下是过去一个月的 120 条工单与访谈记录：[...]。
   请按 JTBD 框架过滤表面的"功能诉求"伪需求，聚类出 3 个核心未满足痛点并评估频次与商业影响权重。
   ```
2. **行为助推与转化激活漏斗**
   ```text
   调用 product-behavioral-nudge-engine：针对"自动化周报导出"新功能，用 Fogg 行为模型 (B=MAP)
   设计首次激活体验 (Aha Moment)：梳理降低操作门槛的渐进引导，并设计自然触发契机提升付费转化。
   ```
3. **工业级 PRD 输出**
   ```text
   调用 product-manager：输出完整 PRD——业务背景、目标用户画像、北极星指标、
   核心功能流程图与异常状态转移表，并为研发定义可量化的 Given-When-Then 验收标准。
   ```
4. **敏捷切分与 MVP 需求砍伐**
   ```text
   调用 product-sprint-prioritizer：对 PRD 全部功能点应用 RICE 评分，执行严格的 MVP 范围削减，
   划定 Must-have（首期上线）与 Nice-to-have（后续迭代），确保两周内可交付验证。
   ```

---

## 7. 维护与清理建议

- **定期体检**：`ls ~/.codebuddy/agents/`。若超过 8 个，建议精简，把非常用角色移出或降级为项目级。
- **项目隔离优先**：优先在仓库的 `.codebuddy/agents/` 存放针对性角色，项目归档后随项目沉淀，不污染全局环境。
- **与 Skill 配合增效**：Agent 提供**行业思维模型与作业流程**（How to think & execute），Skill 提供**具体执行工具与协议**（Tools & Capabilities）。例如让 `finance-financial-analyst` 调用 `xlsx` / `pdf` skill 输出估值模型，二者结合才是最佳实践。
- **重新同步**：`./install.sh` 可反复执行；重跑会先 `rm -rf` 同名目录再复制，天然幂等。

---

## 8. 参考

- 原始 Claude Code 版指南：[`../ClaudeCode/RECOMMENDED_AGENTS.md`](../ClaudeCode/RECOMMENDED_AGENTS.md)
- CodeBuddy 子代理官方文档：`/opt/homebrew/lib/node_modules/@tencent-ai/codebuddy-code/dist/web-ui/docs/cn/cli/sub-agents.md`
- 中文角色库：https://github.com/jnMetaCode/agency-agents-zh
- 上游角色库：https://github.com/agency-enterprise/agency-agents
