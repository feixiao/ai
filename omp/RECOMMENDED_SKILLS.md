# omp 推荐精选技能包 (Recommended Skills)

`omp` 拥有完备的技能发现机制，不仅支持自身配置目录（`~/.omp/agent/skills/` 与 `./.omp/skills/`），还会根据回退机制直接兼容并加载 `~/.claude/skills/`、`~/.gemini/skills/` 及 `.codex/skills/`。

本文档汇总最适合在 `omp` 高并发、多模型架构下使用的优质技能包。

---

## 1. 核心架构与工程研发技能 (Core Engineering)

### 1.1 `tdd` (测试驱动开发)
- **触发场景**：实现任何新功能或修复严重 Bug 时。
- **行为规范**：强制编写先失败的测试用例（Red）➔ 实现最小可行逻辑（Green）➔ 架构重构（Refactor）。
- **适配建议**：结合 `omp --smol` 进行快速测试修复。

### 1.2 `code-review` (深度代码审查)
- **触发场景**：合并代码前、提交 PR 前或重构后。
- **行为规范**：结合 LSP 语法树分析，重点排查内存泄漏、并发竞态、边界空指针与类型完整性。
- **适配建议**：指定 `omp --slow` 调用高推理模型执行。

### 1.3 `grill-me` (技术方案压力测试)
- **触发场景**：在敲定复杂系统架构或选型决策前。
- **行为规范**：Agent 扮演严苛架构师，连续追问高并发瓶颈、降级方案、容灾设计和边界场景。
- **适配建议**：搭配 `omp --plan` 执行。

### 1.4 `codebase-design` (代码库全局架构梳理)
- **触发场景**：接手新仓库、多模块微服务治理。
- **行为规范**：输出组件依赖拓扑图、数据流向图与关键接口边界。

---

## 2. 跨生态与多平台工具技能 (Cross-Ecosystem)

### 2.1 `mcp-builder` (MCP 服务器构建器)
- **触发场景**：编写或集成新的 Model Context Protocol 工具时。
- **规范**：基于 TypeBox / ArkType 快速声明工具契约。

### 2.2 `create-rule` & `create-skill` (Agent 规则与技能生成器)
- **触发场景**：为团队或项目固化工作流规范与自动化动作。
- **规范**：生成符合 RFC 2119 规范的标准 Markdown 提示词文件。

### 2.3 `split-to-prs` (拆分为小颗粒度 PR)
- **触发场景**：大型重构或多任务合并时。
- **规范**：将跨越数十个文件的大 Diff 分解为具备自包含语义的短小分支。

---

## 3. 安装与管理命令

在 `omp` 交互界面或命令行中可直接管理技能：

```bash
# 搜索并安装 Skillshare 官方仓库中的技能
omp skill search tdd
omp skill install tdd

# 查看当前已加载的技能列表
omp skill list

# 禁用或开启特定技能
omp --skills "tdd,code-review" "完成重构"
omp --no-skills "执行极速检查"
```
