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
├── opencode.json      # 符合 opencode.ai/config.json 规范的核心配置文件
├── install.sh         # 一键安装、服务连通性自检与平滑合并脚本
├── remote-connect.sh  # 手机端与内网穿透直连管理脚本 (支持自有服务器/局域网/临时穿透)
└── ReadMe.md          # 本部署、移动端接入与使用指南文档
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

---

## 7. 手机端与远程访问指南 (内网穿透 / 自有云服务器)

OpenCode 原生内置了 **Web 控制台** 与 **安全扫码配对机制（Pairing）**，支持手机端浏览器直接访问，亦可一键“添加到主屏幕”作为独立 PWA App 使用。

为满足您在**无公网域名、仅有公网云服务器 IP** 或**局域网环境**下的手机直连需求，本目录提供了自动化运维脚本 [`remote-connect.sh`](./remote-connect.sh)。

### 7.1 方案 A：自有公网云服务器（SSH 反向隧道，纯 IP 访问，首选推荐）

此方案无需购买或配置任何域名，直接利用 Mac 自带的 SSH 建立反向加密隧道，手机直接通过 `http://<云服务器IP>:<端口>` 访问，100% 走私有链路。

#### 步骤一：云服务器 1 分钟基础配置
云服务器 SSH 默认仅允许本地绑定，需开启网关端口转发（`GatewayPorts`）：
```bash
# 登录您的公网云服务器执行以下命令开启 GatewayPorts 并重启 sshd：
sudo sed -i 's/^#*GatewayPorts.*/GatewayPorts yes/' /etc/ssh/sshd_config
grep -q "^GatewayPorts yes" /etc/ssh/sshd_config || echo "GatewayPorts yes" | sudo tee -a /etc/ssh/sshd_config
sudo systemctl restart sshd || sudo service ssh restart
```
并在云服务商控制台（阿里云/腾讯云/华为云/AWS 等）的安全组规则中，放行对应的入方向端口（推荐 `8888` 或 `9000` 等常用 Web 端口）。

#### 步骤二：Mac 本地一键启动并配对
若云服务器的 `8080` 端口已被其他服务占用，可指定任意放行端口（如 `8888`）：
```bash
# 基本用法（映射到云服务器 8888 端口）：
./remote-connect.sh --server <您的服务器公网IP> --port 8888

# 首次指定并保存配置（下次直接执行 ./remote-connect.sh 即可免参秒连）：
./remote-connect.sh --server 43.163.244.203 --user ubuntu --port 8888 --save
```

脚本将自动：
1. 确保本地 OpenCode 服务处于就绪状态。
2. 建立稳定的 SSH 远程端口转发通道。
3. 在终端即时绘制**专属二维码**与**带安全 Token 的登录链接**。
4. 手机微信或自带相机扫码直接打开使用；在终端按 `Ctrl + C` 可随时安全终止隧道。

---

### 7.2 方案 B：局域网 Wi-Fi 快速配对

当手机与 Mac 处于同一 Wi-Fi 或内网时，无需经过任何公网服务器：

```bash
./remote-connect.sh --lan
```

脚本会自动获取 Mac 当前 Wi-Fi 局域网 IP（如 `192.168.2.138`），输出配对二维码，手机在同一网络下扫码秒连。

---

### 7.3 方案 C：免配置临时穿透 (Cloudflare Quick Tunnel)

在外出且临时无法访问自建服务器时，可使用免配置临时隧道：

```bash
./remote-connect.sh --quick
```

脚本会自动启动临时隧道并获取官方免费分配的安全 HTTPS 域名（如 `https://xxxx.trycloudflare.com`），生成扫码二维码。完全免注册、免自备域名。

---

### 7.4 手机端交互体验最佳实践

1. **一键添加为独立 App (PWA)**：
   - **iOS (Safari)**：点击底部“分享”按钮 -> 选择“添加到主屏幕”（Add to Home Screen）。
   - **Android (Chrome)**：点击右上角菜单 -> 选择“安装应用”或“添加到主屏幕”。
   - 此时 OpenCode 将以全屏、无地址栏的沉浸式原生 App 形态运行。
2. **多设备鉴权隔离**：
   - 扫码链接自带 OpenCode 原生 Hash 鉴权凭据，外网未授权用户无法随意访问。
3. **远程会话无缝接续**：
   - 手机端创建或正在运行的任务，回到电脑端打开 `opencode` 可直接无缝继续协作。

