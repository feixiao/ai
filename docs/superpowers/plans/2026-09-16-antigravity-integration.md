# Antigravity (agy) 适配与部署实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建针对 Google Antigravity (`agy` / Gemini) 的完整工程配置、自动化迁移安装工具及三足鼎立生态文档体系。

**Architecture:** 
1. 编写 `Antigravity/install.sh`，从 Claude Code 插件缓存与 Agent 目录自动化提取资源，通过内联 Python 进行 frontmatter 归一化与路径变量改写，部署至 `~/.gemini/`；
2. 编写 `Antigravity/ReadMe.md` 提供 agy CLI 全景指南、Claude Code vs CodeBuddy vs Antigravity 三足鼎立横向对比矩阵与 MCP 接入配置；
3. 编写 `Antigravity/RECOMMENDED_SKILLS.md` 和 `Antigravity/RECOMMENDED_AGENTS.md`，深度结合 Gemini 1M~2M 超长上下文与多模态特性；
4. 同步更新根目录 `CLAUDE.md` 与 `ReadMe.md`。

**Tech Stack:** Bash, Python 3, Markdown, Google Antigravity CLI (`agy`), Gemini 2.5/3.0 系列模型

**Spec:** `docs/superpowers/specs/2026-09-16-antigravity-integration-design.md`

## Global Constraints

- 目标部署目录默认为 `$HOME/.gemini`，支持通过 `GEMINI_HOME` 环境变量覆盖。
- 源目录默认为 `$HOME/.claude/plugins/cache` 与 `$HOME/.claude/agents`。
- 脚本必须保证幂等性，支持 `--dry-run` 和 `-h/--help`。
- Agent 的 `name` 字段必须清洗为合规 ASCII 标识符，Claude 专有的 `emoji`/`color` 需移除，`model: opus/sonnet` 改写为 `inherit`。
- 变量 `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` 改写为 `${GEMINI_SKILL_DIR}`，`~/.claude/skills` 改写为 `~/.gemini/skills`。

---

### Task 1: 创建 `Antigravity/install.sh` 核心安装与迁移脚本

**Files:**
- Create: `Antigravity/install.sh`

- [ ] **Step 1: 编写 `Antigravity/install.sh` 脚本**
实现包含参数解析（`--dry-run`）、源目录检测、Agent 提取与 frontmatter 归一化、Skill 目录抽取与占位符路径改写的完整逻辑。

- [ ] **Step 2: 赋予执行权限并进行语法检查**
运行：
```bash
chmod +x Antigravity/install.sh
bash -n Antigravity/install.sh
```
预期输出：无语法错误。

- [ ] **Step 3: 测试 `--dry-run` 模式验证抽取逻辑**
运行：
```bash
./Antigravity/install.sh --dry-run
```
预期输出：显示预演复制的 Agent 和 Skill 清单，无报错。

- [ ] **Step 4: 执行真实安装并验证 `~/.gemini/` 目录结构**
运行：
```bash
./Antigravity/install.sh
ls -la ~/.gemini/skills | head -n 15
ls -la ~/.gemini/agents | head -n 15
```
预期输出：成功输出安装的 Skills 与 Agents 数量统计，目录中包含对应文件。

- [ ] **Step 5: 提交脚本**
```bash
git add Antigravity/install.sh
git commit -m "feat(antigravity): add install.sh for skills and agents migration"
```

---

### Task 2: 编写核心指南 `Antigravity/ReadMe.md`

**Files:**
- Create: `Antigravity/ReadMe.md`

- [ ] **Step 1: 撰写 `Antigravity/ReadMe.md`**
包含内容：
1. 模块定位与背景（Antigravity CLI / `agy` 基于 Gemini 模型）；
2. **三足鼎立对比矩阵**（Claude Code vs CodeBuddy vs Antigravity：模型、上下文、多模态、插件机制、MCP、配置目录、擅长场景）；
3. 前置依赖与一键安装指引；
4. `agy` CLI 核心用法速查表（常用命令、单次执行、会话交互、沙箱模式）；
5. MCP 配置实战（`~/.gemini/settings.json` 与 `code-review-graph` 接入）；
6. 目录结构说明与 FAQ。

- [ ] **Step 2: 验证文档超链接与格式**
检查文档内部锚点与外部链接（指向 `../ClaudeCode/` 和 `../CodeBuddy/`）。

- [ ] **Step 3: 提交核心文档**
```bash
git add Antigravity/ReadMe.md
git commit -m "docs(antigravity): add ReadMe with three-way comparison matrix"
```

---

### Task 3: 编写精选技能与角色文档

**Files:**
- Create: `Antigravity/RECOMMENDED_SKILLS.md`
- Create: `Antigravity/RECOMMENDED_AGENTS.md`

- [ ] **Step 1: 撰写 `Antigravity/RECOMMENDED_SKILLS.md`**
结合 Gemini 1M~2M 超长上下文与多模态特性，对 `superpowers`、`document-skills`、`planning-with-files`、`code-review`、`ui-ux-pro-max` 等技能进行场景分类和最佳实践说明。

- [ ] **Step 2: 撰写 `Antigravity/RECOMMENDED_AGENTS.md`**
整理并分类 20+ 个垂直领域的专家角色，涵盖技术架构（软件架构师、后端架构师、UX 架构师、代码审查员、`code-simplifier` 等）与产品策略角色。

- [ ] **Step 3: 提交技能与角色推荐文档**
```bash
git add Antigravity/RECOMMENDED_SKILLS.md Antigravity/RECOMMENDED_AGENTS.md
git commit -m "docs(antigravity): add recommended skills and agents guides"
```

---

### Task 4: 更新仓库全局索引与架构说明

**Files:**
- Modify: `CLAUDE.md`
- Modify: `ReadMe.md`

- [ ] **Step 1: 更新 `CLAUDE.md`**
在 `Architecture & Module Structure` 章节中登记 `Antigravity/` 模块，明确其定位为面向 Google Antigravity / Gemini 的配置体系。

- [ ] **Step 2: 更新根目录 `ReadMe.md`**
在三端 Agentic 开发助手部分添加 Antigravity (`agy`)，更新快速导航和架构目录树。

- [ ] **Step 3: 全局检查与验证**
运行 git status 确认所有文件均已更新，无遗留未跟踪文件或语法破损。

- [ ] **Step 4: 提交全局更新与规范文件**
```bash
git add CLAUDE.md ReadMe.md docs/
git commit -m "docs: register Antigravity module in repository root docs"
```
