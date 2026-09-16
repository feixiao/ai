# Antigravity (agy) 精选角色专家推荐 (Recommended Agents)

在 Google Antigravity (`agy`) 中，**Agents（专家角色）** 用于在不同的技术与业务语境下切换专业的决策思维模型与提示词体系。

通过 `./install.sh` 脚本，角色定义文件已自动归一化处理（净化 Frontmatter、清洗 Claude 专属字段、设置模型继承）并安装至 `~/.gemini/agents/<name>.md`。

你可以通过 `agy agents` 列出所有就绪的角色，并在交互会话或单次指令中唤醒他们。

---

## 1. 软件工程与架构专家矩阵 (Engineering & Architecture)

| 角色标识 (`name`) | 中文名称 | 核心职责与思维模型 |
| :--- | :--- | :--- |
| **`engineering-software-architect`** | **软件架构专家** | 专精分布式系统设计、DDD（领域驱动设计）、系统边界划分、技术选型与长期可维护性架构评估。 |
| **`engineering-backend-architect`** | **资深后端架构师** | 专精高性能服务端、高并发设计、数据库存储引擎与索引设计、API 治理与微服务通信机制。 |
| **`engineering-frontend-developer`** | **现代前端工程师** | 精通现代 Web 生态（React / Vue / Next.js）、状态管理、Web Vitals 性能指标优化与复杂交互。 |
| **`design-ux-architect`** | **UX 架构师** | 技术与体验的桥梁，为开发者提供坚实的基础设施：CSS 设计系统、弹性网格布局框架、交互规范。 |
| **`engineering-code-reviewer`** | **专业代码审查专家** | 严谨苛刻的审查者，聚焦正确性、安全性漏洞、并发隐患与性能瓶颈，拒绝无意义的代码风格指责。 |
| **`code-simplifier`** | **代码极简优化专家** | 审视复杂代码，在 100% 保持外部功能与接口不变的前提下，精简冗余抽象、提升可读性。 |

---

## 2. 产品与商业化战略矩阵 (Product & Commercial)

对于需要进行业务建模、需求分析、用户旅程规划的任务，可挂载以下产品专家：

| 角色标识 (`name`) | 中文名称 | 典型应用场景 |
| :--- | :--- | :--- |
| **`product-manager`** | **产品经理** | 需求梳理、用户故事 (User Stories) 编写、MVP 范围裁剪与验收标准制定。 |
| **`product-sprint-prioritizer`** | **敏捷优先级决策者** | 基于 RICE / MoSCoW 模型评估迭代功能优先级，平衡工程成本与业务收益。 |
| **`product-feedback-synthesizer`** | **用户声音提炼师** | 从海量用户工单、社区反馈和日志中聚类提取真实痛点并转化为功能需求。 |
| **`product-behavioral-nudge-engine`** | **行为设计与增长专家** | 基于行为经济学与增长黑客理念，优化产品关键转化链路与用户留存体验。 |

---

## 3. 在 Antigravity 中使用 Agents 的最佳实践

1. **角色上下文继承**：
   - 导出的所有 Agent 均配置为 `model: inherit`，这意味着你在使用 `agy --model gemini-2.5-pro` 时，角色将自动运行在最适合该任务的 Gemini 高阶模型上。
2. **结合 MCP 形成超级专家**：
   - 当 `engineering-code-reviewer` 配合 `code-review-graph` MCP 时，Gemini 不仅拥有苛刻的评审原则，还能通过知识图谱即时洞察全局影响面（Impact Radius），极大降低误报率。
3. **复合协作**：
   - 典型工作流：先由 `engineering-software-architect` 规划模块拓扑 $\to$ 交由开发角色产出代码 $\to$ 最后由 `code-simplifier` 进行最终收敛优化。
