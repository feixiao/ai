# Pi Agent (pi-coding-agent) 全面配置与反向代理部署指南

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: Shell](https://img.shields.io/badge/Language-Shell-blue.svg)](https://www.gnu.org/software/bash/)
[![Engine: Pi Agent](https://img.shields.io/badge/Engine-Pi%20Agent-purple.svg)](https://pi.dev)
[![Ecosystem: Gemini Pro](https://img.shields.io/badge/Model-Gemini%20Pro%201M-blue.svg)](https://deepmind.google/technologies/gemini/)

本目录提供 **Pi Agent**（由 Mario Zechner 发起的下一代开源极简 AI 终端 Coding Agent，官网 [pi.dev](https://pi.dev)，包名 `@earendil-works/pi-coding-agent`）的完整环境初始化、大模型多梯队选型、**Google Gemini Pro 专项接入**以及**反向代理（Reverse Proxy）/ 聚合网关**落地规范。

---

## 1. 架构定位与核心哲学

Pi Agent 秉持 **"极简 Harness + 自由可塑"** 的哲学，与臃肿笨重的代码助手不同，它底层基于模块化解耦的 `pi-ai` 引擎，具备四大核心优势：

```text
┌─────────────────────────────────────────────────────────────┐
│                    Pi Coding Agent (pi)                     │
├──────────────┬──────────────┬───────────────┬───────────────┤
│ 交互 TUI 模式 │ 命令行 Print │  RPC 守护进程 │  嵌入式 SDK   │
└──────────────┴──────────────┴───────────────┴───────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
     ┌───────────────────┐           ┌───────────────────┐
     │   pi-agent-core   │           │       pi-ai       │
     │ 循环/工具调用/会话 │           │ 多厂商协议统合抽象 │
     └───────────────────┘           └───────────────────┘
                                               │
       ┌──────────────────┬────────────────────┼───────────────────┐
       ▼                  ▼                    ▼                   ▼
  [Anthropic API]    [OpenAI API]       [Google GenAI]       [反向代理/中转]
  (Claude 3.5/Opus)  (GPT-4o/o1/o3)    (Gemini 1.5/2.0 Pro) (One-API/硅基流动)
```

1. **协议层高度自由**：原生支持 `openai-completions`、`anthropic-messages`、`google-generative-ai` 等多种协议，支持直接覆盖 `baseUrl`。
2. **零门槛接入反向代理**：无论自建 Nginx、Cloudflare AI Gateway，还是 One-API、New-API、LiteLLM，均能作为标准 Provider 接入并驱动 Agent 工具链。
3. **运行时无缝切模**：在交互终端输入 `/model` 或快捷键 `Ctrl+P` 即可实时跨厂商、跨代理切换上下文。
4. **渐进思考深度支持**：针对 DeepSeek-R1、o3-mini、Gemini 2.0 / Claude 思考模型，原生支持 `/thinking` 调节思维预算。

---

## 2. 目录文件结构

```text
PiAgent/
├── models.json             # 核心模型与反代 Provider 定义 (覆盖 Google/Anthropic/OpenAI/本地)
├── settings.json           # Agent 行为偏好、默认模型及思考预算配置
├── install.sh              # 一键检查环境、测试服务连通性、部署配置并安装可选扩展/Skills
├── RECOMMENDED_SKILLS.md   # 高质量 Skill 选型、部署与三大角色实操指南
└── ReadMe.md               # 本使用与反向代理接入指南
```

---

## 3. Google Gemini Pro 接入专题：怎么给 Pi 配 Gemini Pro？

**Gemini 1.5 Pro / Gemini 2.0 Pro** 拥有 **1,000,000 ~ 2,000,000 Tokens 的超长上下文窗口**，对于需要一次性扫描数十万行代码的大型项目重构，是当前最具性价比且推理能力极强的大模型。

Pi Agent 对 Gemini 系列提供了官方一等公民支持。接入主要有以下三种路径：

### 路径 A：官方原生直连（海外节点或直连网络）

若开发机可直接访问 Google 域名，只需配置 API Key 即可：

1. **设置环境变量**（可写入 `~/.zshrc` 或 `~/.bashrc`）：
   ```bash
   export GEMINI_API_KEY="AIzaSyYourGoogleApiKey"
   ```
2. **在 Pi 中选用模型**：
   ```bash
   pi -m google-gemini/gemini-1.5-pro
   ```
   或者启动 `pi` 后输入 `/login google` 根据交互提示输入 Key。

---

### 路径 B：Google 官方反向代理通道（国内免代理环境）

如果开发机无法直连 `generativelanguage.googleapis.com`，可以使用自建的反代域名（如通过 Cloudflare Worker 反向代理官方接口）：

在 `models.json` 中配置原生 `google-generative-ai` 协议，并修改 `baseUrl`：

```json
{
  "providers": {
    "reverse-proxy-gemini": {
      "name": "Gemini 自建反向代理通道",
      "baseUrl": "https://gemini-proxy.yourdomain.com/v1beta",
      "apiKey": "$GEMINI_API_KEY",
      "api": "google-generative-ai",
      "models": [
        {
          "id": "gemini-1.5-pro",
          "name": "Gemini 1.5 Pro (自建反代)",
          "contextWindow": 1048576,
          "maxTokens": 8192,
          "supportsTools": true,
          "supportsImages": true
        },
        {
          "id": "gemini-2.0-flash",
          "name": "Gemini 2.0 Flash (自建反代)",
          "contextWindow": 1048576,
          "maxTokens": 8192,
          "supportsTools": true,
          "supportsImages": true
        }
      ]
    }
  }
}
```

---

### 路径 C：通过 OpenAI 兼容聚合网关中转（One-API / New-API / OpenRouter）

如果你的团队统一通过 One-API / New-API 分发 Gemini，网关已将 Gemini 转为 OpenAI 协议（`/v1/chat/completions`）：

```json
{
  "providers": {
    "reverse-proxy-openai": {
      "name": "One-API 聚合网关",
      "baseUrl": "https://api.your-proxy-domain.com/v1",
      "apiKey": "$CUSTOM_PROXY_API_KEY",
      "api": "openai-completions",
      "models": [
        {
          "id": "gemini-1.5-pro",
          "name": "Gemini 1.5 Pro (聚合反代通道)",
          "contextWindow": 1000000,
          "maxTokens": 8192,
          "supportsTools": true,
          "supportsImages": true
        }
      ]
    }
  }
}
```

---

## 4. 全方位反向代理（Reverse Proxy）配置矩阵

在 `PiAgent/models.json` 中，已开箱即用预设了五大反代与本地推演 Provider：

| Provider 标识 | 协议 (`api`) | 典型服务端 | 核心优势 |
| :--- | :--- | :--- | :--- |
| `reverse-proxy-openai` | `openai-completions` | One-API / New-API / LiteLLM | 聚合全球模型，统一计费分发 |
| `reverse-proxy-anthropic` | `anthropic-messages` | Claude 专线反向代理 | 原生 Claude Messages 协议，完美支持 Computer Use & Agent Tools |
| `google-gemini` / `reverse-proxy-gemini` | `google-generative-ai` | 官方端点 / 自建 Worker 反代 | 100万~200万超大上下文，多模态视觉理解 |
| `siliconflow` | `openai-completions` | 硅基流动国内直连 | DeepSeek-V3 / R1 与 Qwen2.5-Coder 极速响应 |
| `lmstudio` / `ollama` | `openai-completions` | 本机/局域网推理引擎 | 离线断网可用，隐私零泄漏 |

---

## 5. 一键安装与配置部署 (`install.sh`)

本目录下的 [`install.sh`](install.sh:1) 提供了开箱即用的自动化部署、服务健康探测与配置合并：

### 快速执行

```bash
# 1. 赋予执行权限并直接运行 (默认部署到 ~/.pi/agent/)
chmod +x PiAgent/install.sh
./PiAgent/install.sh

# 2. 如果本机未安装 Pi CLI，一键安装 CLI + 部署配置 + 自动发现扩展 + 基础 Skills
./PiAgent/install.sh -i -e -s

# 3. 仅测试各推理后端与反向代理网关连通性
./PiAgent/install.sh --check

# 4. 为当前项目独立生成工程级配置 (.pi/)
./PiAgent/install.sh --project .
```

### 常用环境变量设置（推荐放入 `~/.zshrc`）

```bash
# 反向代理 / 聚合网关 Key
export CUSTOM_PROXY_API_KEY="sk-xxxxxx"

# Google Gemini API Key
export GEMINI_API_KEY="AIzaSyxxxxxx"

# 硅基流动国内反代 Key
export SILICONFLOW_API_KEY="sk-xxxxxx"

# Claude 专线反代 Key
export ANTHROPIC_PROXY_KEY="sk-xxxxxx"
```

---

## 6. Pi Agent 常用命令与交互技巧

启动 Pi 进入交互式 TUI：
```bash
pi
```

### 核心快捷键与斜杠指令

| 指令 / 快捷键 | 功能说明 | 适用场景 |
| :--- | :--- | :--- |
| `Ctrl+P` 或 `/model` | 唤起模型选择器 | 随时在 Gemini Pro、Claude 3.5、DeepSeek-V3 之间切换 |
| `/thinking` | 调节推理思考等级 (`off`, `low`, `medium`, `high`, `max`) | 针对 DeepSeek-R1 或 Gemini Thinking 调节推理算力 |
| `pi -m <provider/model>` | 命令行快速启动 | 例如 `pi -m google-gemini/gemini-1.5-pro` |
| `/login [provider]` | 交互式录入指定 Provider 的 API Key | 快速更新凭据并安全写入 `~/.pi/agent/auth.json` |
| `/logout` | 清理已保存凭据 | 撤销过期的 Key |

---

## 7. 高质量 Skills 选型与角色化安装（对齐 RECOMMENDED_SKILLS.md）

Pi 原生实现 [Agent Skills 规范](https://agentskills.io/specification)：一个 Skill 是包含 `SKILL.md` 及配套脚本/提示词模板的独立目录。启动时 Pi 只轻量加载各 Skill 的元数据与描述；任务执行命中时才动态拉取完整实操指南，兼顾上下文 Token 节约与提示词缓存利用率。

本目录安装脚本与 [`ClaudeCode/RECOMMENDED_SKILLS.md`](../ClaudeCode/RECOMMENDED_SKILLS.md) 的权威选型**保持 100% 对齐**，提供面向**全栈工程师**、**产品经理 (PM)** 与**个人投资者**三大核心角色的技能画像矩阵，并通过本地 Claude 插件缓存优先同步 + 上游 Git 直下机制实现秒级部署。

> 💡 **详细指南**: 各角色技能清单拆解、深入工作流调用范例与最佳实践请参见专属指南：**[`PiAgent/RECOMMENDED_SKILLS.md`](./RECOMMENDED_SKILLS.md)**。

### 7.1 核心角色技能矩阵

| 角色 Profile | 核心目标与定位 | 包含技能数量 | 核心包含的 Skills 清单 |
| :--- | :--- | :--- | :--- |
| **`minimal`**<br>(默认核心档) | 个人投资者、全栈与 PM 共同交集 | 18 个核心技能 | • 文档三剑客: `xlsx`, `pdf`, `docx`, `pptx`<br>• 工程规范: `systematic-debugging`, `test-driven-development`, `brainstorming`, `using-superpowers`, `using-git-worktrees`, `verification-before-completion`<br>• 质询与建模: `grilling`, `domain-modeling`, `codebase-design`<br>• 前端设计: `ui-ux-pro-max`, `design-system`, `ui-styling`<br>• 跨会话规划: `planning-with-files`<br>• 自定义 MCP: `mcp-builder` |
| **`eng`**<br>(全栈工程师) | 严格工程规范、TDD、DDD 建模与前端设计系统 | 33 个专业技能 | • `superpowers` 14 项完整全家桶 (调试/TDD/Worktree/计划编写与执行/审查/多Agent编排)<br>• `ui-ux-pro-max` 7 项全套设计系统 (design-system, ui-styling, design, brand, banner, slides)<br>• `mattpocock-skills` (domain-modeling, codebase-design, grilling, research, resolving-merge-conflicts, tdd, wizard, diagnosing-bugs)<br>• 扩展与测试: `mcp-builder`, `webapp-testing`, `web-artifacts-builder`<br>• 跨会话规划: `planning-with-files` |
| **`pm`**<br>(产品经理) | 工业级 PRD、严苛对抗质询(砍需求)、SaaS 商业化阶梯定价与敏捷管理 | 36 个专业技能 | • 需求文档: `docx`, `pdf`, `xlsx`, `pptx`<br>• 对抗质询: `grilling`, `brainstorming`<br>• 体验与落地页: `ui-ux-pro-max`, `design`, `design-system`, `ui-styling`, `landing-page-generator`<br>• 商业化增收: `commercial-skills`, `pricing-strategist`, `commercial-policy`, `commercial-forecaster`, `deal-desk`<br>• 产品套件: `product-manager-toolkit`, `product-strategist`, `product-discovery`, `product-analytics`, `competitive-teardown`, `experiment-designer`, `roadmap-communicator`, `spec-to-repo`, `saas-scaffolder`, `ui-design-system`, `ux-researcher-designer`<br>• 敏捷协作: `senior-pm`, `scrum-master`, `jira-expert`, `confluence-expert`, `atlassian-admin`, `atlassian-templates`, `meeting-analyzer`, `team-communications`<br>• 路线图跟踪: `planning-with-files` |
| **`invest`**<br>(个人投资者) | 财报长文表格提取、估值模型联动、红队严苛质询与资产看板可视化 | 13 个专业技能 | • 财报与研报三剑客: `xlsx`, `pdf`, `docx`, `pptx`<br>• 红队反脆弱审查: `grilling`, `grill-me`<br>• 深度事实调研: `research`<br>• 投资论点推演: `brainstorming`<br>• 资产图表与原型: `theme-factory`, `frontend-design`, `canvas-design`, `web-artifacts-builder`<br>• 跨季度日志: `planning-with-files` |
| **`full`**<br>(全量生态档) | 装载本地缓存与来源库中全部可用技能 | 1000+ 个 | 安装包含全部垂类（金融、工程进阶、深度调研、合规、高管顾问等）的所有可用技能 |

---

### 7.2 一键部署与角色安装命令

```bash
# 1. 部署默认精选必备 Skills (minimal: 18 个核心技能，部署到 ~/.pi/agent/skills/)
./PiAgent/install.sh -s

# 2. 为全栈工程师一键部署完整工程技能栈
./PiAgent/install.sh -s --profile eng

# 3. 为产品经理一键部署 PRD/商业化/敏捷协作技能栈
./PiAgent/install.sh -s --profile pm

# 4. 为个人投资者一键部署财报建模/红队质询技能栈
./PiAgent/install.sh -s --profile invest

# 5. 预览指定角色包含的技能清单 (不写盘)
./PiAgent/install.sh --list-skills --profile eng

# 6. 为当前工作区项目生成专属配置及项目级技能目录 (.pi/skills/)
./PiAgent/install.sh --project . -s --profile minimal

# 7. 清理目标目录中未包含在当前 profile 清单内的冗余技能
./PiAgent/install.sh -s --profile minimal --prune-skills

# 8. 若本地无 Claude 插件缓存，允许从上游 Git 直下缺失技能
./PiAgent/install.sh -s --profile eng --fetch-skills
```

---

### 7.3 Pi Agent 技能生效目录与调用方式

Pi 会自动递归扫描并加载以下目录中的 `SKILL.md`：

```text
~/.pi/agent/skills/<skill-name>/SKILL.md  # 用户全局级 Pi Skill [install.sh -g 部署目标]
.pi/skills/<skill-name>/SKILL.md          # 项目工作区级 Pi Skill [install.sh -p 部署目标]
~/.agents/skills/<skill-name>/SKILL.md    # 跨 Agent 规范全局目录
.agents/skills/<skill-name>/SKILL.md      # 跨 Agent 规范项目目录
```

#### 检查与显式调用

启动 Pi 进入交互式会话：

```bash
pi
```

- **语义自主调用**：任务命中技能范围时（如输入“审查某财报 PDF”或“用 TDD 修复并发 Bug”），Pi 会自动识别并加载对应技能；
- **显式定向调用**：在交互输入框中输入 `/skill:<skill-name>` 强制触发，例如：
  ```text
  /skill:grilling 我打算重构用户权限中心，请对我接下来的设计思路进行最严苛的红队质询。
  /skill:xlsx 根据当前财报数据构建 5 年期 DCF 现金流折现估值模型并输出敏感性分析表格。
  /skill:systematic-debugging 接口在高并发下偶现 500，请按根因追踪法排查日志。
  ```
- **重载更新**：如果在外部更新了技能文件，在 Pi 会话中输入 `/reload` 即可实时热重载。

---

## 8. 动态模型自动发现（进阶）

如果你的反代网关（如 One-API）经常增删模型，可以安装官方社区的自动发现扩展：

```bash
pi install npm:pi-models-discovery
```

然后在 `~/.pi/agent/models.json` 的对应 Provider 中添加 `"discoverModels": true`，Pi 将在每次启动时自动拉取网关的 `GET /v1/models`，无需手动频繁修改配置文件。
