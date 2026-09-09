# 成为 Claude Code 顶尖 1% 用户的完整操作手册 (The Top 1% Claude Code Playbook)

> **导语**：大多数开发者把 Claude Code 当成一个更高阶的代码自动补全工具或更快的 Stack Overflow。而顶尖 1% 的开发者把它当成一个**可编程的工程团队与系统级基础设施**。本文档深度总结自 JOTO AI 智库文章《成为 ClaudeCode 顶尖 1% 用户的完整指南》，涵盖架构理解、`CLAUDE.md` 黄金法则、生命周期 Hooks、子智能体（Subagents）并行编排、MCP 协议集成、端到端全自动实战流以及 5 日落地行动计划。

---

## 目录

1. [认知重塑：你可能只用了 Claude Code 20% 的能力](#1-认知重塑你可能只用了-claude-code-20-的能力)
2. [全景架构：智能体编排框架的分层机制](#2-全景架构智能体编排框架的分层机制)
3. [工具横评：Claude Code vs. Copilot vs. Cursor](#3-工具横评claude-code-vs-copilot-vs-cursor)
4. [精通 CLAUDE.md：持久化上下文与指令预算管理](#4-精通-claudemd持久化上下文与指令预算管理)
5. [Hooks 机制：不依赖模型意志的确定性质量门禁](#5-hooks-机制不依赖模型意志的确定性质量门禁)
6. [子智能体（Subagents）：上下文隔离与专业分工](#6-子智能体subagents上下文隔离与专业分工)
7. [MCP 集成：打通真实研发基础设施与最小权限原则](#7-mcp-集成打通真实研发基础设施与最小权限原则)
8. [端到端实战：从需求 Interview 到全自动 PR 交付](#8-端到端实战从需求-interview-到全自动-pr-交付)
9. [进阶模式与工程落地模板](#9-进阶模式与工程落地模板)
10. [这周行动计划：5 天阶梯式落地指南](#10-这周行动计划5-天阶梯式落地指南)

---

## 1. 认知重塑：你可能只用了 Claude Code 20% 的能力

### 典型反模式场景（99% 开发者的日常）
1. 打开终端输入 `claude`。
2. 描述一个功能需求，让 Claude 编写多份代码文件。
3. 人工 Code Review 并在对话中反复微调纠错。
4. 人工运行测试、打补丁，最终提交上线。

**本质**：这种用法只是把 Claude Code 当成了快速代码生成器。开发者仍然扮演“所有线程串联者”、“频繁上下文切换管理者”和“每一个微小决策审核者”。

### 顶尖 1% 开发者的系统化思维
- **不再把 AI 当工具，而是设计让 AI 零人工干预自主运转的系统**。
- **完善的上下文基础设施**：配置分层 `CLAUDE.md`，每次会话自动加载最精准上下文。
- **确定性门禁**：通过 `Hooks` 在工具执行前后强制运行 Lint、格式化及危险命令拦截。
- **上下文隔离与并行**：使用 `Subagents`（子智能体）并发处理测试生成、安全审计、Diff 冷审查。
- **系统生态互联**：通过 `MCP`（Model Context Protocol）实时打通本地代码库、数据库只读副本、GitHub Actions 与 Jira。

> **核心哲学**：不是让自己成为更好的司机，而是为智能体修建更好的高速公路。

---

## 2. 全景架构：智能体编排框架的分层机制

Claude Code 不是简单的编码助手，而是一个**以大语言模型为驱动的智能体编排框架（Agent Orchestration Framework）**：

| 架构层次 | 核心职责 | 典型组件与能力 |
|---|---|---|
| **E 层：外部生态层 (Ecosystem)** | 连接外部数据源与协同工具 | MCP Servers（GitHub, Postgres, Slack, Jira） |
| **D 层：并行智能体层 (Subagents)** | 上下文隔离的专业子代理 | `code-reviewer`, `security-auditor`, `pm-spec` |
| **C 层：确定性流水线 (Pipelines & Hooks)** | 生命周期钩子与自动化执行 | PreToolUse, PostToolUse, SubagentStop, Stop |
| **B 层：核心交互层 (Agent Core)** | 工具调用循环与文件系统编辑 | Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion |
| **A 层：持久记忆层 (Memory & Config)** | 跨会话约束、技术栈与项目认知 | `CLAUDE.md`, `CLAUDE.local.md`, `settings.json` |

*绝大多数开发者仅停留在 B 层（让模型写文件与运行命令）；顶尖专家则调度 A 至 E 全部五层。*

---

## 3. 工具横评：Claude Code vs. Copilot vs. Cursor

| 维度 | GitHub Copilot | Cursor | Claude Code |
|---|---|---|---|
| **核心定位** | 行内逐词自动补全 | 文件级增强与 GUI 交互编辑 | **全项目级自主交付系统** |
| **运作边界** | 当前编辑行 / 当前文件 | 单文件或有限多文件 (Composer) | **整套代码库与 Git 工作树** |
| **项目记忆** | 无（每次交互无状态） | 局部索引、向量检索 | **结构化分层 `CLAUDE.md` 永久记忆** |
| **质量闭环** | 依赖开发者人工验证 | 半自动化运行命令 | **自主编写、运行测试、读报错自修复闭环** |
| **扩展机制** | 预置插件 | 扩展插件 | **Hooks 生命周期 + Subagents + 原生 MCP** |
| **工作形态** | 必须在 IDE 内 | 锁定于定制版 VS Code | **终端 CLI / Headless 脚本 / IDE 插件 / Web 远程** |

---

## 4. 精通 CLAUDE.md：持久化上下文与指令预算管理

### 指令预算与稀释定律
- 每个 Claude Code 会话开局皆为冷启动。`CLAUDE.md` 是每次会话唯一强制加载的文件。
- **指令预算大约仅为 150～200 条**。系统自带 Prompt 已占用约 50 条。
- **每添加一条 Claude 默认就会做对的显性规则，都在稀释那些决定项目成败的关键规则！**

### CLAUDE.md 的三维框架：WHAT, WHY, HOW

```
                  ┌──────────────────────────────┐
                  │           WHAT               │  技术栈与依赖（引用而非复制）
                  ├──────────────────────────────┤
                  │           WHY                │  架构动机与全局决策背景
                  ├──────────────────────────────┤
                  │           HOW                │  高发错误纠偏与行为边界
                  └──────────────────────────────┘
```

1. **WHAT（技术栈定义）**：
   - ❌ 错误：把整份 `package.json` 或庞大的 README 贴进来。
   - ✅ 正确：指引引用入口。例如：`See @package.json for dependencies`, `See @docs/architecture.md for system design`。
2. **WHY（架构决策动机）**：
   - 给 Claude 提供决策背后的目的，理解宏观上下文能极大优化微观决策。
   - *示例*：“我们强制使用 SSR 服务端渲染，是因为 40% 的用户处于弱网移动端环境。”
3. **HOW（做错清单与行为守则）**：
   - **记录模型在当前代码库中容易犯的错，而非记它做对的事**。
   - 如果 Claude 经常在 ESM 项目误写 `require()`，或在路由注册时混淆 Auth 与限流中间件顺序，务必精确记录。

### 目录层级加载机制
```bash
~/.claude/CLAUDE.md          # 全局配置，对本机所有项目生效
./CLAUDE.md                  # 项目根目录，纳入 Git 版本控制（团队共享）
./CLAUDE.local.md            # 本地个人覆盖规则，加入 .gitignore
./src/api/CLAUDE.md          # 仅当任务涉及该目录时按需动态加载
./src/db/CLAUDE.md           # 仅当涉及数据库模块时按需动态加载
```

> **CLAUDE.md 准入测试**：在添加任何一行指令前自问——*“如果没有这一行，Claude 会在我的代码库上犯错吗？”* 如果不会，立即删除该行！

---

## 5. Hooks 机制：不依赖模型意志的确定性质量门禁

Hooks 是 Claude Code 区别于普通聊天界面的最大分水岭。它们是**系统级确定性触发的 Shell 脚本**，无论模型意图如何都会强行执行。

### 核心 Hook 事件与执行流
- `PreToolUse`：调用工具前执行（可拦截高危命令）。
- `PostToolUse`：调用工具成功后执行（如自动 Lint、格式化）。
- `SubagentStop`：子智能体退出时触发（用于串联下一个流水线任务）。
- `Stop`：会话结束时触发（生成会话摘要、清理临时工件）。

### 生产级 `.claude/settings.json` 配置

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "cd $PROJECT_ROOT && npm run lint --fix"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/block_dangerous.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/session_summary.py"
          }
        ]
      }
    ]
  }
}
```

### 拦截脚本原理 (`.claude/hooks/block_dangerous.py`)
- 从标准输入 `stdin` 获取 JSON 格式的 `tool_input.command`。
- 匹配正则黑名单（如 `rm -rf /`, `git push --force`, `DROP TABLE`, `truncate` 等）。
- **退出码机制**：
  - `exit(0)`：放行操作。
  - `exit(2)`：拒绝执行，并将 stderr 错误提示直接反馈给 Claude 调整思路。

---

## 6. 子智能体（Subagents）：上下文隔离与专业分工

### 为什么必须使用子智能体？
单一长对话会话会随着代码生成迅速膨胀。一旦上下文占满，注意力衰减就会出现“幻觉”和“忘记前期约束”。
子智能体拥有**独立的上下文空间、专有 System Prompt、严格裁剪的 Tool 权限以及专属模型级别**。

### 定义专业审计子智能体
文件路径：`.claude/agents/code-reviewer.md`

```markdown
---
name: code-reviewer
description: 专门针对代码风格、业务正确性、安全漏洞和运行性能进行严苛审核。在功能实现完成后调用。
tools: Read, Grep, Glob, Bash
model: claude-opus-4-6
---

你是一名资深 Staff 软件架构师。请针对当前变更的每个文件执行最严苛的代码复审，质疑每一个走捷径的实现：

1. 正确性 (Correctness)：是否满足功能预期的边界行为？
2. 异常边界 (Edge Cases)：什么极端输入会导致运行时崩溃？
3. 安全漏洞 (Security)：是否存在 SQL/命令注入、未转义渲染、鉴权旁路？
4. 性能损耗 (Performance)：是否有 O(n²) 循环、重复数据库 IO 或内存未释放？
5. 可维护性 (Readability)：半年后新成员是否能轻松阅读维护？

请按以下三段输出结构化报告：
- [MUST FIX] 必须立即阻断合并的致命隐患
- [SHOULD FIX] 建议重构的缺陷
- [CONSIDER] 可选架构优化项
```

### 杠杆率最高的技术：双 Claude 审查模式（Dual-Session Review）
1. **会话 A（实现者 Implementer）**：承载业务上下文、权衡推演与快速改动。
2. **会话 B（审查者 Cold Reviewer）**：**新起全新终端会话，零上下文冷读 diff**。
   ```bash
   claude "review the last commit on this branch as a staff engineer. Check correctness, security, and edge cases. Be harsh — this is going to production."
   ```
   *没有历史上下文的会话 B 会像真正的技术审查委员会一样，瞬间揪出会话 A 自以为理所当然的所有妥协与隐患。*

---

## 7. MCP 集成：打通真实研发基础设施与最小权限原则

### 7.1 知识（Skill）与能力（MCP）的清晰界限
- **Skills（Markdown 知识规则）**：告诉 Claude **“怎么做”**（如《K8s 部署规范》、《团队 API 命名风格》），载体是 `.claude/skills/` 下的指令文档。
- **MCP Servers（协议服务接口）**：赋予 Claude **“实时数据与操作能力”**（查询数据库、读取 GitHub PR、查看 Jira 工单），使外部工具成为 Claude 的原生 Tool。
- **选型准则**：
  - 需要约束工作流、编程模式或团队规则时 ── **选 Skill**（透明可审计，零外部黑盒依赖）。
  - 需要读写实时数据、调用云服务或联动外部系统时 ── **选 MCP**。

### 7.2 现成可用优质 MCP 生态清单（拿来即用）

| 场景分类 | MCP 服务名称 | 包名 / 来源 | 核心能力 | 典型应用场景 |
|---|---|---|---|---|
| **代码与协作** | **GitHub** | `@modelcontextprotocol/server-github` | Issues、PR、Commits、CI 状态、代码搜索 | “分析最近 5 次 CI 失败日志并修复”、“提一个 PR 关联 #123” |
| | **GitLab** | `@modelcontextprotocol/server-gitlab` | MR、Pipelines、项目分支与文件操作 | 自建/私有化 GitLab 代码库的完整自动化管理 |
| | **Git** | `mcp-server-git` (Python/uvx) | 本地 Git 仓库底层操作、Diff 审查、Log 追溯 | 深度分析 commit 历史、分支差异比较与回滚推演 |
| | **Sentry** | `mcp-server-sentry` | 线上错误堆栈查询、Issue 状态监控 | “获取最近 1 小时线上报出的 500 错误，在本地定位修复” |
| **数据库与持久化** | **PostgreSQL** | `@modelcontextprotocol/server-postgres` | Schema 读取、只读 SQL 查询、表结构推演 | “查看 users 和 orders 表结构，写一个高效的迁移脚本” |
| | **SQLite** | `@modelcontextprotocol/server-sqlite` | 本地 SQLite 文件读写与结构分析 | 本地嵌入式数据分析、轻量级原型验证 |
| | **Redis** | `redis-mcp` | 缓存 Key 检索、TTL 检查、缓存击穿排查 | “检查 `v2:user:1001` 的缓存数据结构是否符合预期” |
| | **Supabase** | `@supabase/mcp-server-supabase` | 数据库表、Edge Functions、向量检索 | 全栈无服务应用的后端数据与逻辑自省 |
| **实时网络与检索** | **Brave Search** | `@modelcontextprotocol/server-brave-search` | 互联网隐私搜索、技术文档实时检索 | 检索最新发布的开源库 API 变更与 Breaking Changes |
| | **Puppeteer** | `@modelcontextprotocol/server-puppeteer` | 无头浏览器渲染、网页截屏、动态内容提取 | 抓取动态 JS 渲染的技术文档、排查前端渲染异样 |
| | **Firecrawl** | `firecrawl-mcp` | 网页爬取并清洗转换为干净 Markdown | 爬取官方文档站整站并作为上下文给 Claude 阅读 |
| **任务与项目协同** | **Linear** | `mcp-server-linear` | Issue 查询、需求分配、状态自动流转 | “根据当前讨论的 bug，自动在 Linear 对应团队下创建 issue” |
| | **Jira / Confluence** | `sooperset/mcp-atlassian` | Jira 工单读写、Confluence 架构文档阅读 | “阅读 Confluence 上的技术设计方案，开始落地对应代码” |
| | **Slack** | `@modelcontextprotocol/server-slack` | 频道消息读取、Bug 讨论上下文提取 | “把刚刚客服在 #bugs 频道反馈的复现步骤整理出来” |
| | **Notion** | `mcp-server-notion` | 知识库检索、产品需求文档 (PRD) 对齐 | “根据 Notion 里的 PRD 规范编写接口校验逻辑” |
| **云原生与容器** | **Docker** | `docker-mcp` | 容器状态、构建日志、镜像 Inspect | “排查为什么本地 docker-compose 服务的健康检查失败” |
| | **Kubernetes** | `k8s-mcp` | Pod/Deployment 状态、Event 诊断、日志查看 | “查看 staging 集群中崩溃 Pod 的日志与 describe 结果” |
| **思维推理强化** | **Sequential Thinking** | `@modelcontextprotocol/server-sequential-thinking` | 动态多步骤拆解、动态回溯与思维反思 | 遇到极其晦涩的底层算法、并发竞态逻辑时的深度推演 |
| | **Memory** | `@modelcontextprotocol/server-memory` | 基于知识图谱的跨会话长期记忆持久化 | 记录团队业务术语、人际关系与跨项目背景知识 |
| **私有系统转接** | **OpenAPI / Swagger** | `@modelcontextprotocol/server-openapi` | 传入 Swagger JSON/YAML 自动转接为 Tools | 公司内部私有微服务或第三方 API 一秒接入 Claude |

> 🔍 **寻找更多 MCP 服务器的权威中心**：
> 1. **GitHub 官方参考库**：[modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
> 2. **Smithery.ai**：[smithery.ai](https://smithery.ai)（最大的 MCP 注册表与一键安装中心，收录数千个 MCP）
> 3. **Glama MCP 目录**：[glama.ai/mcp/servers](https://glama.ai/mcp/servers)（带健康度检测与星标排行的 MCP 发现站）
> 4. **PulseMCP**：[pulsemcp.com](https://www.pulsemcp.com)（精选 MCP 生态导航）

---

### 7.3 MCP 安装与配置实战

#### 前置运行环境准备
大多数 MCP 采用 Node.js 或 Python 编写，建议备妥免安装执行工具：
- **Node.js**：自带 `npx`（验证：`node -v && npx -v`）
- **Python uv**：自带 `uvx`，运行 Python MCP 极快（安装：`brew install uv`）

#### 方式一：CLI 命令行快速添加（适合快速试用）
```bash
# 语法结构
claude mcp add <服务名称> <执行命令> [参数...] [--env KEY=VALUE...]

# 1. 添加 Sequential Thinking 推理增强（无需 API Key）
claude mcp add sequential-thinking npx -y @modelcontextprotocol/server-sequential-thinking

# 2. 添加 GitHub MCP
claude mcp add github npx -y @modelcontextprotocol/server-github \
  --env GITHUB_TOKEN="ghp_你的GitHubToken"

# 3. 添加 PostgreSQL 只读查询
claude mcp add postgres npx -y @modelcontextprotocol/server-postgres \
  "postgresql://readonly_user:password@localhost:5432/mydb"

# 4. 使用 Python / uvx 添加本地 Git 深度分析
claude mcp add git uvx mcp-server-git --repository /path/to/repo

# 5. 添加 Brave 网络搜索
claude mcp add brave-search npx -y @modelcontextprotocol/server-brave-search \
  --env BRAVE_API_KEY="你的BraveKey"
```

#### 方式二：配置文件管理（推荐，适合团队工程化）

根据作用域将配置放置在对应位置：
- **项目公共配置（提交到 Git）**：`.claude/settings.json`（仅放无需密钥或公共配置的服务）
- **个人本地配置（敏感信息，加入 .gitignore）**：`.claude/settings.local.json`
- **本机全局配置（所有项目共享）**：`~/.claude/settings.json`

**配置文件标准结构示例 (`.claude/settings.json`)**：
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "local-git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "."]
    }
  }
}
```

---

### 7.4 避坑指南：敏感信息防泄露与最小权限原则

1. **分层密钥隔离**：
   切勿将包含 `GITHUB_TOKEN` 或生产数据库连接串的配置直接提交到 Git。应将其分离至 `.claude/settings.local.json`：
   ```json
   // .claude/settings.local.json (必须写入 .gitignore)
   {
     "mcpServers": {
       "github": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-github"],
         "env": {
           "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxx"
         }
       },
       "postgres-readonly": {
         "command": "npx",
         "args": [
           "-y",
           "@modelcontextprotocol/server-postgres",
           "postgresql://readonly_user:pass123@localhost:5432/my_db"
         ]
       }
     }
   }
   ```
2. **永远默认只读（Least Privilege Principle）**：
   - 绝不将生产环境的写权限交给任何自动化 Agent！
   - 为 Claude 创建专用的只读数据库从库账号（Read-Only User）。
   - 针对有写权限的子智能体（如 `implementer`），仅允许连接本地 Docker 或 Dev 临时数据库。

---

### 7.5 MCP 验证与日常运维

#### 终端运维命令
```bash
# 查看当前已配置的所有 MCP 服务列表及状态
claude mcp list

# 查看指定服务的详细启动参数与环境变量
claude mcp get github

# 移除不再需要的 MCP 服务
claude mcp remove brave-search
```

#### 会话中验证与自然语言调用
在终端进入 `claude` 会话后：
1. **输入 `/mcp`**：实时查看已连接服务及其注册的 Tool 清单与状态。
2. **自然语言调用范例**：
   - *“用 sequential-thinking 帮我深度推演这个高并发死锁场景的所有可能路径。”*
   - *“通过 github mcp 列出最近 3 个待审查的 PR 及改动简述。”*
   - *“查询 postgres 只读库中的 orders 表字段，生成对应的 TypeScript 类型定义。”*

---

## 8. 端到端实战：从需求 Interview 到全自动 PR 交付

以构建一个高可用后端端点 `/api/v2/recommendations` 为例（带 Redis 缓存、鉴权、单元测试与架构验证）：

```
[ Step 0: 零配置启动 ]
       │ 自动装载 CLAUDE.md / settings.json
       ▼
[ Step 1: 面试模式确立 Spec ]
       │ 使用 AskUserQuestion 逐项对齐鉴权/缓存/返回格式，生成 SPEC.md
       ▼
[ Step 2: 核心功能编码与自动测试闭环 ]
       │ 编写代码 -> 运行测试 -> 读取失败日志 -> 自动修复 -> PostToolUse Hook 自动 Lint
       ▼
[ Step 3: 并发调用子智能体冷审查 ]
       │ code-reviewer 发现：Redis 连接未释放、中间件顺序错误
       ▼
[ Step 4: 针对性自愈修复 ]
       │ 回到主会话提示修复，重新测试全部通过
       ▼
[ Step 5: 安全专用智能体审计 ]
       │ security-auditor 出具安全合规声明
       ▼
[ Step 6: 自动化创建标准化 PR ]
       │ 通过 GitHub MCP 自动生成包含测试报告、Spec 对齐情况的 Pull Request
```

**效率对比**：传统手工流耗时约 2～3 小时，且容易遗漏防御性审查；整套智能体流水线在 25 分钟内高质量交付，安全门禁与质量审计均 100% 自动执行。

---

## 9. 进阶模式与工程落地模板

### 1. 上下文主动紧缩法则
- 绝不等到上下文 100% 触发系统强行压缩（容易丢失关键变量与状态）。
- **当上下文消耗达到 ~50% 时，主动输入 `/compact`**。
- 在 `CLAUDE.md` 中硬性规定：*“When compacting, always preserve: the list of modified files, current test status, and any unresolved issues.”*

### 2. 后台异步监控：`/loop` 定时轮询
```bash
# 后台每隔 5 分钟检查一次特性分支 CI 运行情况
/loop 5m check if the CI pipeline on branch feat/recommendations passed and report back

# 每隔 30 分钟扫描一次主干新出现的失败用例
/loop 30m check for any new failing tests on main
```

### 3. 模型分级路由（Cost & Capability Balancing）
```bash
claude --model claude-sonnet-4-6     # 默认选择：日常绝大多数编码、重构与测试
claude --model claude-opus-4-6       # 极复杂任务：跨系统底层架构重构、难题攻坚
claude --model claude-haiku-4-5      # 高频轻量级：快速信息检索、格式化、单行报错分析
```

### 4. 生产级项目标准工程目录树
```text
your-project/
├── CLAUDE.md                    ← 项目永久技术与规范记忆（必须纳入 Git）
├── CLAUDE.local.md              ← 本地个人覆盖配置（加入 .gitignore）
├── .claude/
│   ├── settings.json            ← Hooks 门禁、MCP 配置与全局权限
│   ├── agents/                  ← 专职子智能体定义
│   │   ├── code-reviewer.md     ← 代码复审智能体
│   │   ├── test-writer.md       ← 单元测试与 E2E 编写智能体
│   │   ├── security-auditor.md  ← 安全风险审计智能体
│   │   └── pm-spec.md           ← 需求工程与 Spec 生成智能体
│   ├── skills/                  ← 领域工程知识库 (Markdown)
│   │   ├── deploy.md            ← 部署规范与流水线指引
│   │   ├── database-patterns.md ← 数据库操作规范
│   │   └── api-design.md        ← RESTful/GraphQL 风格指南
│   ├── commands/                ← 自定义斜杠命令
│   │   ├── review-pr.md         ← /review-pr 快捷审查脚本
│   │   ├── ship.md              ← /ship 交付流水线
│   │   └── diagnose.md          ← /diagnose 问题排查
│   └── hooks/                   ← 确定性生命周期执行脚本
│       ├── block_dangerous.py   ← 危险命令拦截网关
│       ├── auto_format.sh       ← 格式化与静态检查
│       └── session_summary.py   ← 会话结束报告生成
```

### 5. 最小可行性（MVP）CLAUDE.md 示范模板
```markdown
# Project: MyApp Backend

## Tech Stack
- Node.js 22, TypeScript 5.4, Fastify 4
- PostgreSQL 16 + Drizzle ORM, Redis 7
- Jest for testing
See @package.json for dependencies; See @docs/architecture.md for system design.

## Verification Commands
- Run all tests: `npm test`
- Run single test: `npm test -- --testPathPattern=<pattern>`
- Type check: `npm run typecheck`
- Lint: `npm run lint`

## Critical Rules (Things to get right)
- Always use ESM imports (never CommonJS require).
- Redis keys must have environment & version prefix: `v2:user:{id}:...`.
- Auth middleware must be registered BEFORE rate limiter in router setup.
- All database queries must go through the repository/service layer, never directly in route handlers.

## Git Protocol
- Never commit directly to main.
- Branch prefix: `feat/`, `fix/`, `chore/`.
- Conventional Commits standard required.
```

---

## 10. 这周行动计划：5 天阶梯式落地指南

| 日程 | 主题 | 落地实操任务 | 预期收益 |
|---|---|---|---|
| **Day 1** | **CLAUDE.md 极简化精简** | 在项目根目录执行 `/init`，剔除 70% 显而易见的废话，仅保留团队高频错误与测试校验命令，行数控制在 50 行内。 | 指令遵循率立即提升 80% |
| **Day 2** | **落地第 1 个 Hook** | 在 `.claude/settings.json` 中配置 `PostToolUse`（针对 `Write` 工具自动触发 linter 与 formatter）。 | 彻底终结格式与语法琐碎纠纷 |
| **Day 3** | **实践双会话审查** | 在下一个特性开发完成后，新开无上下文终端运行 Review 提示词进行冷读 diff。 | 提前捕获 90% 潜在边缘漏洞 |
| **Day 4** | **部署第 1 个子智能体** | 创建 `.claude/agents/code-reviewer.md`，限定只读工具与更高级别思考模型。 | 主会话上下文寿命延长 3 倍 |
| **Day 5** | **集成第 1 个 MCP 服务** | 配置只读 GitHub MCP 或只读数据库 MCP，实现 issue/schema 免复制自动对齐。 | 跨工具交互链路彻底打通 |
| **Week 2+**| **复利演进与持续迭代** | 根据日常开发出现的错漏持续更新 `CLAUDE.md`，追加常用流水线命令。 | 搭建真正自主可控的专属工程团队 |
