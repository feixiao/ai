# Antigravity (agy) 精选技能库推荐 (Recommended Skills)

Google Antigravity (`agy`) 依托 **Gemini 2.5 / 3.0** 系列模型，具备 **1M~2M+ 超大上下文窗口** 与 **原生全模态 (Multimodal)** 处理能力。通过 `./install.sh` 脚本，可将 Claude 生态中积累的 100+ 个高质量技能一键导入到 `~/.gemini/skills/`。

本文档精选出最能发挥 Gemini 模型特性的核心技能，并提供实战调用指南。

---

## 1. 核心工程与系统级技能 (Engineering & Architecture)

在超大代码库场景下，Gemini 能够一次性吞吐多个模块的全量代码，配合结构化技能可实现高保真分析。

| 技能名称 | 适用场景 | 核心价值 |
| :--- | :--- | :--- |
| **`superpowers:brainstorming`** | 方案预研、需求拆解 | 将发散的想法转化为严谨的架构设计，避免直接写代码造成的返工 |
| **`superpowers:systematic-debugging`** | 复杂 Bug 定位与根因分析 | 4 步调试法（重现、假设、验证、防御），告别盲目修改 |
| **`superpowers:test-driven-development`** | 严格的红绿重构 (TDD) 循环 | 先写失败测试，编写极简通过代码，再做无害化重构 |
| **`planning-with-files`** | 复杂跨会话超大特性开发 | 在磁盘保留 `task_plan.md`，保障跨上下文会话进度不丢失 |
| **`code-review`** | 代码提交与 PR 质量审查 | 结合 `code-review-graph` MCP 进行影响面与潜在逻辑漏洞扫描 |
| **`refactor-safely`** | 历史代码重构与坏味道清理 | 严格确保重构前后外部行为与公共接口一致 |

---

## 2. 原生多模态与文档类技能 (Multimodal & Documents)

Gemini 的一大杀手锏是原生支持长文档、表格与视觉材料解析，配合 `document-skills` 能轻松应对企业级文档工程：

| 技能名称 | 支持格式 | 推荐用法与典型任务 |
| :--- | :--- | :--- |
| **`document-skills:pdf`** | `.pdf` | 深度阅读技术白皮书、API 规格说明书并提取架构关键点 |
| **`document-skills:docx`** | `.docx` | 自动生成需求规格说明书 (PRD)、工程立项提案与交付总结 |
| **`document-skills:xlsx`** | `.xlsx` | 解析财务模型、工程吞吐量测试数据、成本测算与生成对比分析 |
| **`document-skills:pptx`** | `.pptx` | 自动生成技术架构汇报、年度路线图演示文稿 |

---

## 3. 前端与体验设计技能 (UI / UX Design)

利用 Gemini 的多模态视觉感知与代码生成结合：

| 技能名称 | 核心能力 |
| :--- | :--- |
| **`ui-ux-pro-max:design-system`** | 建立设计系统规范、CSS 变量体系、间距与排版 Token |
| **`ui-ux-pro-max:ui-styling`** | Tailwind CSS / CSS Modules 现代前端美化与响应式适配 |
| **`ui-ux-pro-max:brand`** | 企业品牌色彩搭配、视觉一致性约束 |

---

## 4. 产品战略与商业决策类技能 (Product & Commercial)

在复杂业务逻辑或创业项目中，调用商业化专家技能辅助产品规划：

| 技能名称 | 适用角色 | 核心任务 |
| :--- | :--- | :--- |
| **`product-skills:cs-product`** | 产品经理 / 负责人 | 产出结构化 PRD、竞品拆解、MVP 范围界定 |
| **`commercial-skills:pricing-strategist`** | 商业化架构师 | SaaS 定价模型、成本测算、计费单元拆解 |
| **`product-skills:roadmap-communicator`** | 研发主管 / PMO | 输出面向不同管理层级的里程碑甘特与演进规划 |

---

## 5. 技能调用建议与最佳实践

1. **组合调用**：
   - 复杂功能开发前：先调用 `superpowers:brainstorming` 进行方案论证 $\to$ 敲定设计后调用 `planning-with-files` 建立任务看板 $\to$ 使用 `superpowers:test-driven-development` 推进代码。
2. **充分释放上下文红利**：
   - 面对跨数十个文件的重构，可直接指示 `agy` 使用全局上下文配合 `code-review` 技能，无需人工频繁切换切片。
