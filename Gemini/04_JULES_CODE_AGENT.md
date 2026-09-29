# 04. Jules 异步编程 Agent 实战指南

Google Jules 是专门面向 GitHub 生态设计的云端自主软件工程师（AI Software Engineer Agent）。与需要在本地终端实时交互的开发工具不同，Jules 运行在完全托管的云端隔离沙箱中，能够异步接管 GitHub 仓库中的 Issue，自主执行代码定位、修改、构建验证与单元测试，并最终以规范的 Pull Request 形式交付成果。

---

## 1. Jules 运行架构与工作流

Jules 的生命周期与标准软件工程的工作流完全贴合：

```
[GitHub Issue 委派任务]
          │
          ▼
┌─────────────────────────┐
│ 1. 云端沙箱环境准备     │ ── 自动拉取目标分支代码，检测依赖环境与构建脚本
└─────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│ 2. 跨文件代码定位与编辑 │ ── 利用 Gemini 3.1 Pro 超大代码理解能力定位根因并修改
└─────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│ 3. 本地构建与单测自我验证│ ── 执行 npm test / pytest，若报错则进入自愈循环修改
└─────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│ 4. 提交分支并创建 PR    │ ── 生成遵循 Conventional Commits 的提交与详细变更说明
└─────────────────────────┘
          │
          ▼
[人类工程师在 GitHub 审核合并]
```

---

## 2. 工具分工：Jules 与 Claude Code 协同矩阵

在全栈开发日常中，Jules 与本地交互式 CLI 工具（如 Claude Code）不是替代关系，而是“异步工单托管”与“本地实时结对”的互补协同：

| 评估维度 | Claude Code（本地交互式 CLI） | Google Jules（云端异步 Agent） |
| :--- | :--- | :--- |
| **运行环境** | 运行在开发者本地终端，直连本地文件系统 | 运行在 Google 云端托管容器，直连 GitHub Repo |
| **交互模式** | 高敏捷实时交互，适合连续追问与毫秒级反馈 | 异步离线托管，提交任务后即可关闭电脑 |
| **优势场景** | 复杂新特性设计、实时排错调试、本地文件重构 | 明确 Bug 修复、补全单测、TypeScript 类型补全、依赖升级 |
| **工程师角色** | 实时驾驶员（Pair Programming 结对伙伴） | 最终代码审查者（Code Reviewer & PR Approver） |

---

## 3. 高成功率 Issue 编写规范

Jules 的交付质量直接取决于输入的 Issue 质量。为了让 Jules 一次性顺利跑通测试并生成完美的 PR，建议在 GitHub Issue 中遵循如下结构模版：

### 3.1 实战模版：严苛类型收敛与 Bug 修复 Issue

```markdown
### 任务目标 (Objective)
修复 `src/services/market_data.ts` 中的并发行情去重失效缺陷，并收敛涉及模块的 TypeScript 类型定义。

### 问题描述 (Bug Description)
当 WebSocket 在 100ms 内推送超过 50 条同一标的的报价更新时，由于异步队列未加锁，导致去重 Map 产生竞态覆盖，最终入库数据出现重复记录。

### 预期改动范围 (Expected Changes)
1. 在 `src/services/market_data.ts` 中引入轻量异步互斥锁或基于原子操作的去重队列。
2. 将该文件及 `src/types/market.ts` 中所有临时使用的 `any` 替换为具体严格的接口定义，严禁引入类型断言 `as any`。
3. 补充针对高并发乱序输入的单测用例。

### 验收与验证指令 (Verification Commands)
在提交 PR 之前，请在沙箱中按顺序执行以下命令，确保全部通过无警告：
- 构建校验：`npm run build`
- 语法与类型校验：`npm run lint && npm run type-check`
- 单元测试：`npm run test -- test/market_data.spec.ts`
```

---

## 4. Jules 核心实战场景与落地策略

### 4.1 场景一：单元测试覆盖率攻坚
- **痛点**：全栈项目中核心业务逻辑需要高覆盖率，但手工编写上百个 Corner Case 的边界测试极其耗费心力。
- **Jules 打法**：向 Jules 发起 Issue：“为 `src/finance/valuation_dcf.ts` 补充完备的单元测试，要求覆盖自由现金流为负数、折现率除零保护、永续增长率大于折现率的边界异常，单测覆盖率需提升至 95% 以上，测试框架使用 Vitest”。

### 4.2 场景二：TypeScript 严格模式推进
- **痛点**：遗留代码中存在大量历史包袱与宽松类型，手动逐行修复枯燥且耗时。
- **Jules 打法**：拆解模块，每次给 Jules 分派一个独立的目录：“将 `src/utils/` 下所有文件的 TypeScript 配置切换为 `strict: true` 兼容标准，清除所有隐式 any，重构后运行全量单测验证”。

### 4.3 场景三：第三方依赖主版本升级（Breaking Changes 迁移）
- **痛点**：开源库大版本升级（例如从 Next.js Pages 迁 App Router，或从 Pydantic v1 升 v2）涉及大量 API 重构。
- **Jules 打法**：将官方升级指南链接贴在 Issue 中，委托 Jules 执行批量代码改写与配置调整，并自动跑测试修复语法变动。

---

## 5. 安全门禁与审核守则

尽管 Jules 能自动通过自动化测试，但合并其 Pull Request 时必须坚持以下底线：
1. **审查依赖变动**：警惕在 `package.json` 或 `requirements.txt` 中引入未经审核的冷门第三方依赖包。
2. **严防测试降级**：检查 Jules 是否修改了现有的测试断言（Assert），严禁通过降低测试标准或注释测试用例来“虚假通过测试”。
3. **敏感凭证防泄漏**：确保 Jules 生成的任何测试配置文件均未包含明文 API Key 或密码。
