# Antigravity (agy) Skills & Agents 部署指南

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: Shell](https://img.shields.io/badge/Language-Shell-blue.svg)](https://www.gnu.org/software/bash/)
[![Engine: Gemini](https://img.shields.io/badge/Engine-Gemini%202.5%2F3.0-orange.svg)](https://deepmind.google/technologies/gemini/)

本目录是 [`../ClaudeCode/`](../ClaudeCode/) 与 [`../CodeBuddy/`](../CodeBuddy/) 的 **Antigravity (Google `agy` CLI)** 对等物：将 Claude Code 生态与 Superpowers 体系中沉淀的高质量 **Skills**（技能）与 **Agents**（专家角色）无缝移植到 Antigravity，并提供一键化、幂等的适配安装工具 `install.sh`。

---

## 1. 核心定位与三足鼎立横向对比

在现代 AI Agentic 编程工作流中，不同大模型体系与 CLI 工具有着不同的专长与生态定位。以下是本仓库支持的三大主流终端助手的全景对比：

| 对比维度 | Claude Code (`claude`) | CodeBuddy (`codebuddy`) | Antigravity (`agy`) |
| :--- | :--- | :--- | :--- |
| **所属生态 / 背靠模型** | Anthropic (Claude 3.5/3.7 Sonnet, Opus) | 腾讯 / 混元 / 本地通用兼容 | **Google DeepMind (Gemini 2.5 / 3.0 Flash & Pro)** |
| **原生上下文吞吐** | 200K (超长按需扩展) | 128K ~ 200K | **1M ~ 2M+ 超大上下文** (原生吞吐整个代码库) |
| **多模态理解** | 图像、基础文档结构 | 基础代码解析 | **全原生多模态** (文本、音视频、图表、复杂 PDF/DOCX) |
| **推理与逻辑风格** | 极其严谨、代码极简、防过度工程 | 国内研发规范对齐、团队协同 | **深度推理 (High Reasoning) + 极速响应** |
| **配置目录** | `~/.claude/` | `~/.codebuddy/` | `~/.gemini/config/` (主配置) / `~/.gemini/` |
| **技能存放路径** | `~/.claude/skills/` | `~/.codebuddy/skills/` | `~/.gemini/config/skills/` (软链至 `~/.gemini/skills/`) |
| **角色存放路径** | `~/.claude/agents/` | `~/.codebuddy/agents/` | `~/.gemini/agents/` (同步软链 `~/.gemini/config/agents/`) |
| **MCP 工具协议** | 原生 STDIO / HTTP MCP | 原生 MCP | **原生 STDIO / HTTP MCP (`settings.json`)** |
| **核心优势场景** | 精细化 TDD、架构重构、安全代码审查 | 国内大模型适配、企业私有化部署 | **超大代码库全局拓扑分析、快速原型探索、经济吞吐** |

---

## 2. 为什么需要适配移植？

虽然技能与角色均基于 Markdown 提示词工程，但各平台之间存在特定的兼容性差异，直接复制会导致解析错误：

1. **Agent Frontmatter 差异**：
   - Claude Code 支持在 `agents/*.md` 中声明 `emoji`、`color` 以及 `model: opus` / `model: sonnet` 等模型别名；
   - `agy` 的角色要求纯净的 ASCII 标识符，且模型应设置为 `inherit`，以便动态遵循 `agy --model` 的全局调度。
2. **环境变量与路径宏差异**：
   - 上游技能大量引用 `${CLAUDE_PLUGIN_ROOT}`、`${CLAUDE_SKILL_DIR}` 或硬编码 `~/.claude/skills`；
   - 适配器将其智能改写为 `${GEMINI_SKILL_DIR}` 与 `~/.gemini/skills`。
3. **生态沉淀复用**：
   - 无需在 Google 生态重复造轮子，可直接享受 `superpowers`、`document-skills`、`ui-ux-pro-max` 与商业化等上百个成熟技能包。

---

## 3. 快速安装

### 3.1 默认安装：极简模式（推荐，零 Prompt 膨胀）

直接运行脚本即为**极简安装模式**，仅安装 **核心工程与规划技能**（`using-superpowers` + `brainstorming` + `systematic-debugging` + `test-driven-development` + `verification-before-completion` + `planning-with-files`）与 **6 大核心角色**，最大限度降低上下文开销并保持专注：

```bash
cd Antigravity
./install.sh
```

### 3.2 模块化按需与全量安装

根据你的工作流场景，可按需叠加特定模块，或开启全量模式：

```bash
# 全量生态模式：一键安装全部 80+ 个技能包（文档、UI-UX、商业化等）
./install.sh --all

# 完整核心模式：工程规范 (14 个) + 规划 (2 个) + 多模态长文档 (4 个)
./install.sh --core

# 仅叠加原生多模态长文档支持 (PDF/DOCX/XLSX/PPTX)
./install.sh --docs

# 仅叠加 UI/UX 前端设计系统技能包 (7 个)
./install.sh --ui-ux

# 仅叠加产品规划、项目管理与商业化专家技能包 (~18 个)
./install.sh --biz

# 仅叠加 Matt Pocock 技能集 (25 个)
./install.sh --mattpocock

# 清空旧技能与角色后干净重装
./install.sh --clean
```

### 3.3 预演模式（Dry-Run）

若想先查看将要迁移的文件清单，可运行：

```bash
./install.sh --dry-run
```

脚本是**完全幂等**的：重跑会自动清理同名旧技能与角色并覆盖，当 Claude Code 插件升级后，随时重跑 `./install.sh` 即可同步最新能力。

---

## 4. Antigravity (`agy`) 常用命令速查

`agy` 提供了高效的交互式与非交互式命令行操作：

```bash
# 启动交互式编程会话（默认模型）
agy

# 指定模型启动（如高性能 Gemini 2.5 Pro 或高吞吐 Flash）
agy --model gemini-2.5-pro

# 单次非交互式执行（批处理/管道输出）
agy -p "分析当前代码库的目录结构，并输出关键架构图"

# 交互式带初始 Prompt
agy --prompt-interactive "审查最近一次 git commit 的代码质量"

# 查看当前已挂载的角色专家
agy agents

# 查看与管理当前已启用的 MCP 外部工具
agy mcp list
```

---

## 5. MCP (Model Context Protocol) 增强配置

Antigravity 原生支持 MCP 协议。我们推荐在 `~/.gemini/settings.json` 中配置 [`code-review-graph`](https://github.com/tursodatabase/code-review-graph) 等工具，将静态代码知识图谱直接赋予 `agy`：

### 示例配置 (`~/.gemini/settings.json`)

```json
{
  "security": {
    "auth": {
      "selectedType": "gemini-api-key"
    }
  },
  "mcpServers": {
    "code-review-graph": {
      "command": "uvx",
      "args": [
        "code-review-graph",
        "serve"
      ],
      "cwd": "/Users/hy"
    }
  }
}
```

启用后，Gemini 可直接调用 `semantic_search_nodes_tool`、`get_impact_radius_tool`、`detect_changes_tool` 实现秒级的全库拓扑级依赖与影响面分析。

---

## 6. 目录结构概览

```text
Antigravity/
├── install.sh              # 一键抽取、转换与部署脚本
├── ReadMe.md               # 本指南：agy 架构、对比矩阵与 MCP 配置
├── RECOMMENDED_SKILLS.md   # 适配 Gemini 超长上下文的精选技能清单
└── RECOMMENDED_AGENTS.md   # 适配 agy 体系的精选角色专家矩阵
```
