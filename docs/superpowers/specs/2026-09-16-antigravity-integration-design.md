# Antigravity (agy) Skills & Agents 部署体系设计规范

- **日期**: 2026-09-16
- **状态**: 已批准 (Approved)
- **目标组件**: `Antigravity/` (针对 Google Antigravity / Gemini CLI `agy`)

---

## 1. 项目背景与设计目标

本仓库已经构建了面向 **Claude Code** (`ClaudeCode/`) 与 **CodeBuddy** (`CodeBuddy/`) 的完整工程实战体系与生态资产移植方案。为了拓展对 Google **Antigravity CLI** (`agy`，基于 Gemini 模型系列) 的支持，需要在本仓库建立对等的 `Antigravity/` 模块。

### 核心目标
1. **生态互通与适配迁移**：提供自动化安装迁移脚本 `install.sh`，从 Claude Code 插件缓存与全局 Agent 仓库提取优质资产，自动抹平 frontmatter、命名格式、环境占位符等差异，安装至 `~/.gemini/`。
2. **三足鼎立对比矩阵**：梳理并输出 Claude Code vs CodeBuddy vs Antigravity 的横向对比，明确不同技术方案在上下文容量、推理模式、MCP 生态与工程开发中的定位。
3. **完善的开发与推荐文档**：提供 `ReadMe.md`、`RECOMMENDED_SKILLS.md`、`RECOMMENDED_AGENTS.md`，指导开发者如何利用 Gemini 1M~2M 超长上下文与多模态特性发挥最大效能。
4. **仓库工程协同**：在仓库根目录 `ReadMe.md` 与 `CLAUDE.md` 注册该模块，形成完整的 Agentic 开发工具矩阵。

---

## 2. 目标运行环境与架构规范

### 2.1 本地环境规范
- **CLI 命令**：`agy` (路径：`~/.local/bin/agy`)
- **配置与数据根目录**：`~/.gemini/`
- **MCP 配置文件**：`~/.gemini/settings.json` (包含 `code-review-graph` 等已注册服务)

### 2.2 目标目录映射
| 资产类型 | 目标存储路径 | 说明 |
| :--- | :--- | :--- |
| **Skills (技能)** | `~/.gemini/skills/<skill-name>/` | 包含 `SKILL.md` 及配套脚本/参考文档 |
| **Agents (角色)** | `~/.gemini/agents/<agent-name>.md` | 统一 ASCII 标识符，保留角色能力说明 |
| **MCP 工具** | `~/.gemini/settings.json` | 原生 STDIO / HTTP MCP 服务声明 |

---

## 3. 详细设计

### 3.1 目录结构 (`Antigravity/`)
```text
Antigravity/
├── install.sh              # 一键自动化提取、适配与安装脚本
├── ReadMe.md               # 核心指南：agy 架构、三端横向对比、MCP 接入与命令速查
├── RECOMMENDED_SKILLS.md   # 适配 Gemini 超长上下文的精选技能清单与场景指引
└── RECOMMENDED_AGENTS.md   # 适配 Google Antigravity 的精选角色专家清单
```

### 3.2 `install.sh` 核心逻辑与阶段
1. **源路径解析**：
   - 优先读取 `CLAUDE_CACHE` (`~/.claude/plugins/cache`)
   - 读取 `CLAUDE_AGENTS` (`~/.claude/agents`)
   - 目标路径设为 `GEMINI_HOME` (`~/.gemini`)
2. **阶段 1：Agents 规范化与安装**：
   - 遍历 `~/.claude/agents/*.md` 与官方内建角色（如 `code-simplifier`）。
   - Python 内联脚本处理：
     - 将 `name` 规范化为纯 ASCII 文件名主干（移除空格、特殊符号）。
     - 移除 Claude 专属元数据（`emoji`, `color`）。
     - 将 Claude 专属模型映射（如 `model: opus`）调整为 `inherit`，交由 `agy` 配置的模型接管。
   - 写入 `~/.gemini/agents/<name>.md`。
3. **阶段 2：Skills 提取与目录复刻**：
   - 覆盖精选核心插件：`superpowers`、`document-skills`、`mattpocock-skills`、`planning-with-files`、`ui-ux-pro-max`、`product-skills` 等。
   - 复制完整目录结构，确保技能内部的 `references/`、`scripts/` 等支持文件不丢失。
4. **阶段 3：路径与占位符改写**：
   - 将 `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` 替换为 `${GEMINI_SKILL_DIR}`。
   - 将硬编码路径 `~/.claude/skills` 改写为 `~/.gemini/skills`。
5. **支持参数**：
   - `--dry-run`：仅演练打印，不改写磁盘。
   - `-h` / `--help`：查看使用帮助。

### 3.3 文档设计规范
1. **`ReadMe.md`**：
   - 包含三足鼎立对比矩阵（模型底座、上下文窗口、多模态支持、插件体系、MCP 配置等）。
   - 提供 `agy` 常用命令行示例与开发技巧。
   - 详细讲解在 `~/.gemini/settings.json` 中配置 `code-review-graph` MCP 服务的完整流程。
2. **`RECOMMENDED_SKILLS.md` & `RECOMMENDED_AGENTS.md`**：
   - 强化对 Gemini 2.5/3.0 高吞吐与超长上下文的场景说明（例如代码库全局拓扑分析、大规模多模态文档生成等）。
3. **根目录更新**：
   - 在 `CLAUDE.md` 和根目录 `ReadMe.md` 添加 `Antigravity/` 入口和模块概览。

---

## 4. 验证策略与成功标准

1. **语法与安装验证**：
   - `bash -n Antigravity/install.sh` 语法检测通过。
   - `./install.sh --dry-run` 能够正确列出所有待抽取的技能与角色。
   - 执行 `./install.sh` 成功在 `~/.gemini/skills` 与 `~/.gemini/agents` 生成文件。
2. **agy CLI 集成验证**：
   - 运行 `agy agents` 或相关 CLI 命令能够正常识别或目录结构符合规范。
3. **文档一致性**：
   - 检查 `Antigravity/ReadMe.md`、`RECOMMENDED_SKILLS.md`、`RECOMMENDED_AGENTS.md` 与根目录 `ReadMe.md`、`CLAUDE.md` 的超链接与内容完备度。
