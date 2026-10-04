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
├── models.json      # 核心模型与反代 Provider 定义 (覆盖 Google/Anthropic/OpenAI/本地)
├── settings.json    # Agent 行为偏好、默认模型及思考预算配置
├── install.sh       # 一键检查环境、测试服务连通性并部署到 ~/.pi/agent/
└── ReadMe.md        # 本使用与反向代理接入指南
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

# 2. 如果本机未安装 Pi CLI，一键安装 CLI + 部署配置 + 安装自动发现扩展
./PiAgent/install.sh -i -e

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

## 7. 动态模型自动发现（进阶）

如果你的反代网关（如 One-API）经常增删模型，可以安装官方社区的自动发现扩展：

```bash
pi install npm:pi-models-discovery
```

然后在 `~/.pi/agent/models.json` 的对应 Provider 中添加 `"discoverModels": true`，Pi 将在每次启动时自动拉取网关的 `GET /v1/models`，无需手动频繁修改配置文件。
