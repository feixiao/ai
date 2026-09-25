# OpenCode 本地模型接入指南 (LM Studio)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: Shell](https://img.shields.io/badge/Language-Shell-blue.svg)](https://www.gnu.org/software/bash/)
[![Engine: LM Studio](https://img.shields.io/badge/Engine-LM%20Studio-green.svg)](https://lmstudio.ai/)

本目录提供 OpenCode 接入本地大模型推理引擎（以 Apple Silicon / Mac Studio 上的 LM Studio 为基准）的完整配置规范与一键部署方案。模型定义与分工策略直接对标 [`ClaudeCode/claude-lm.sh`](../ClaudeCode/claude-lm.sh:1)。

---

## 1. 架构定位与模型选型

在代码智能体（Coding Agent）工作流中，单一模型难以同时兼顾长文本架构推演与极速子任务分发。本配置采用与 `ClaudeCode/claude-lm.sh` 完全一致的双梯队分工架构：

| 角色梯队 | 模型标识 | 参数与架构 | 核心职责 | 对标 Claude Code 层级 |
| :--- | :--- | :--- | :--- | :--- |
| **主力编码 (Primary)** | `qwen3.8-27b-splash` | 27B Dense，高精度量化 | 负责复杂逻辑重构、完整功能实现与底层架构推演 | Sonnet / Opus / Fable |
| **极速轻量 (Fast / Subagent)** | `google/gemma-4-26b-a4b-qat` | 26B 总量 / 4B 激活 MoE | 负责文件索引、高并发代码检索、单测快速校验与轻量检查 | Haiku / Subagent |

### 核心特性

- **100K 严控上下文**：两款模型均配置 100,000 上下文上限，确保本地显存稳定，防止长会话溢出。
- **原生工具调用**：全面开启 `tool_call: true` 与必要推理标记，适配 OpenCode 代码编辑、Bash 执行与文件检索等工具链。
- **协议兼容**：采用 `@ai-sdk/openai-compatible` 标准协议，直连 LM Studio 本地服务（`http://127.0.0.1:1234/v1`）。

---

## 2. 目录文件结构

```text
OpenCode/
├── opencode.json     # 符合 opencode.ai/config.json 规范的核心配置文件
├── install.sh        # 一键安装、服务连通性自检与平滑合并脚本
└── ReadMe.md         # 本部署与使用指南文档
```

---

## 3. 配置文件解析 (`opencode.json`)

配置文件直接遵循 [OpenCode 官方配置协议](https://opencode.ai/config.json)：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "lmstudio/qwen3.8-27b-splash",
  "small_model": "lmstudio/google/gemma-4-26b-a4b-qat",
  "provider": {
    "lmstudio": {
      "name": "LM Studio (Local M4 Max)",
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "http://127.0.0.1:1234/v1",
        "apiKey": "lmstudio"
      },
      "models": {
        "qwen3.8-27b-splash": {
          "name": "Qwen 3.8 27B Splash (Primary Coder)",
          "tool_call": true,
          "reasoning": true,
          "limit": {
            "context": 100000,
            "output": 32768
          }
        },
        "google/gemma-4-26b-a4b-qat": {
          "name": "Gemma 4 26B A4B QAT (Fast Subagent)",
          "tool_call": true,
          "reasoning": false,
          "limit": {
            "context": 100000,
            "output": 16384
          }
        }
      }
    }
  },
  "agent": {
    "coder": {
      "description": "核心编码智能体：负责架构设计、深度推理、核心功能实现与复杂重构",
      "model": "lmstudio/qwen3.8-27b-splash",
      "mode": "primary",
      "temperature": 0.2
    },
    "fast": {
      "description": "极速扫描智能体：负责快速文件扫描、轻量级检查与子任务分发",
      "model": "lmstudio/google/gemma-4-26b-a4b-qat",
      "mode": "subagent",
      "temperature": 0.1
    }
  }
}
```

---

## 4. 快速安装与使用

### 4.1 连通性自检

在安装配置前，可先行检测本地 LM Studio 是否已在 1234 端口启动并加载目标模型：

```bash
cd OpenCode
./install.sh --check
```

输出示例：
```text
[INFO] 正在检测 LM Studio 服务状态 (http://127.0.0.1:1234/v1/models)...
[OK] LM Studio 服务运行正常！

核心模型加载自检：
  [+] 主力编码模型 (qwen3.8-27b-splash): 已就绪
  [+] 极速子代理模型 (google/gemma-4-26b-a4b-qat): 已就绪
```

### 4.2 部署为全局配置（推荐）

运行部署命令，脚本将自动处理配置目录创建与平滑合并：

```bash
./install.sh
```

- 目标路径为 `~/.config/opencode/opencode.json`。
- 若目标已存在旧配置，脚本会自动创建时间戳备份，并将 `lmstudio` Provider、模型与 Agent 规则安全合并，保留原有的 plugins 和 permissions 配置。

### 4.3 部署为单一工作区专属配置

如需仅对当前代码库或特定项目生效：

```bash
./install.sh --project .
```

该命令将在指定的项目根目录下生成 `./opencode.json`。

---

## 5. 日常使用方式

### 5.1 启动 OpenCode

配置完成后，直接在终端启动 OpenCode，系统将默认采用 `lmstudio/qwen3.8-27b-splash` 驱动主交互：

```bash
opencode
```

### 5.2 智能体角色调度

在 OpenCode 会话中，可通过 `@` 快捷指令选择专属智能体：

- **调用主力开发角色**：输入 `@coder 请重构该模块并实现并发控制`。
- **调用极速扫描角色**：输入 `@fast 检查当前目录所有 TypeScript 文件的类型定义`。

---

## 6. 排查与注意事项

1. **服务端口冲突**：LM Studio 默认端口为 `1234`，若在设置中更改了端口（例如改为 `8000`），可通过 `./install.sh --port 8000` 进行部署，或直接修改 `opencode.json` 中的 `baseURL`。
2. **JIT 模型加载**：确保 LM Studio 设置中开启了 "Keep in Memory" 或自动加载功能，避免并发请求时发生模型切换延迟。
3. **网络代理旁路**：本地推理请求必须旁路系统代理，确保 `127.0.0.1` 和 `localhost` 不走外部 HTTP 代理。
