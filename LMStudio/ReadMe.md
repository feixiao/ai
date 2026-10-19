# LM Studio 跨网络远程访问与稳定连接指南 (Tailscale / 穿透方案)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Engine: LM Studio](https://img.shields.io/badge/Engine-LM%20Studio-green.svg)](https://lmstudio.ai/)
[![Protocol: Tailscale](https://img.shields.io/badge/Network-Tailscale-blue.svg)](https://tailscale.com/)

本指南针对 LM Studio 官方 **LM Link 经常掉线、超时无法连接**的问题，提供工业级稳定的跨网络（蜂窝网络、外网 Wi-Fi、异地出行）直连替代方案。核心采用 **Tailscale (WireGuard 点对点加密专网)** 作为主力传输层，并提供 Cloudflare Tunnel 与 SSH 反向隧道作为备选方案。

---

## 1. 痛点分析：为什么 LM Link 经常连不上？

LM Studio 官方的 LM Link 机制主要依赖其部署在海外的信令（Signaling）服务器与 STUN/TURN 中继节点：
1. **海外中继网络抖动**：信令服务器与中继节点位于海外，国内移动蜂窝网络（4G/5G）或家庭宽带对其连接存在丢包与高延迟。
2. **移动端 IP 频繁漂移**：手机切换基站、从 Wi-Fi 切到蜂窝网络时，公共 IP 会发生变化，LM Link 的长连接极易假死且无法自动重连。
3. **宿主机休眠与节电拦截**：电脑锁屏或空闲时，网卡进入节能低功耗状态，导致 LM Link 心跳握手丢失。

---

## 2. 替代方案选型矩阵

| 方案 | 传输技术 | 移动端门槛 | 稳定性 | 安全性 | 适用场景 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tailscale (推荐首选)** | WireGuard P2P 虚拟专网 | 需装 App，开箱自启 | **极高**（断网秒级重连） | **极高**（端到端加密，零公网暴露） | 手机/笔记本异地远程调用主力设备算力 |
| **Cloudflare Tunnel** | 边缘反向代理 | **免客户端**（浏览器直接打开） | 中等（受 CF 海外出口速度影响） | 中等（需配置 Access 鉴权防盗刷） | 他人临时借用、未装客户端的设备访问 |
| **自有云服务器 (SSH/frp)** | TCP 反向端口映射 | 需有 VPS 节点 | 高（国内 BGP 延迟极低） | 高（依赖 SSH Key 或 Token 鉴权） | 拥有国内公网服务器且具备 Linux 运维基础 |

---

## 3. 方案实操：Tailscale 极速落地配置

### 步骤一：LM Studio 开启全网卡服务监听

默认状态下，LM Studio 仅监听本机回环地址（`127.0.0.1`），外部及 Tailscale 虚拟网卡请求会被系统直接丢弃。

1. 打开 **LM Studio**。
2. 点击左侧工具栏的 **Developer**（开发者模式，带有 `<>` 图标）或 **Local Server** 页面。
3. 在右侧面板配置服务参数：
   - **Port**：保持默认 `1234`（或按需修改）。
   - **Serve on Local Network**：切换为 **开启（ON）**；或确保 Host 绑定为 **`0.0.0.0`**（允许所有网卡流量访问）。
   - **Enable CORS**：勾选启用（允许跨域请求，便于 WebUI 与移动端前端调用）。
4. 点击 **Start Server** 并加载目标模型（如 `qwen3.8-27b` 或 `gemma-4-26b`）。

---

### 步骤二：安装并配对 Tailscale

Tailscale 基于 WireGuard 构建虚拟局域网，两端直接点对点打洞，流量不经任何第三方中心服务器。

1. **宿主机（运行 LM Studio 的电脑）**：
   - macOS：在 Mac App Store 或 [官网下载](https://tailscale.com/download/mac) 安装。
   - Windows：在 [官网下载](https://tailscale.com/download/windows) 安装。
   - 启动并使用您的账号（支持 Google、GitHub、Microsoft）登录。
2. **远程终端（手机 / iPad / 外出笔记本）**：
   - 移动端在 App Store / Google Play / 各大应用市场安装 **Tailscale**。
   - 打开 App 并**使用与宿主机完全相同的账号登录**。
   - 点击连接开关，授权系统创建 VPN 虚拟网卡配置。

---

### 步骤三：获取虚拟 IP 与连通性校验

1. 在宿主机或手机端 Tailscale 列表中，找到宿主机设备名对应的 **`100.x.y.z`** 地址（例如 `100.86.120.35`）。
2. **手机端断开局域网 Wi-Fi，切换至纯 4G/5G 蜂窝网络**。
3. 打开手机端浏览器或终端，访问以下接口进行健康检查：
   ```text
   http://100.x.y.z:1234/v1/models
   ```
   *若能正常返回包含当前加载模型标识的 JSON 数据（`"object": "list"`），即证明跨网通道完全建立成功。*

---

### 步骤四：移动端与第三方客户端接入

在任意支持 OpenAI-Compatible 协议的客户端中填入以下配置：

```text
API Base URL : http://100.x.y.z:1234/v1
API Key      : lm-studio (LM Studio 默认不校验，不可留空，填任意字符串即可)
Model Name   : 当前在 LM Studio 中加载的模型 Identifier (可通过 /v1/models 自动拉取)
```

#### 常见客户端推荐：
- **iOS / Android 原生 App**：**Chatbox**、**Cherry Studio**、**OpenCat**。
- **Web 端 / PWA**：**NextChat (ChatGPT-Next-Web)**、**LobeChat**。
- **代码智能体终端**：**OpenCode**、**PiAgent**、**Claude Code**。

---

## 4. 生产级高可用与防掉线设置

为了保证人在外地或长时间离开电脑时连接不中断，必须在宿主机完成以下两项防断连配置：

### 1. 禁用 Tailscale 设备密钥过期（防止 90 天静默掉线）
Tailscale 默认对每台接入设备开启 90 天认证密钥过期保护：
1. 登录 [Tailscale 控制台 (Admin Console)](https://login.tailscale.com/admin/machines)。
2. 在机器列表中找到运行 LM Studio 的电脑设备。
3. 点击右侧操作菜单 `...` -> 选择 **Disable Key Expiry**。

### 2. 宿主机阻止系统深度休眠
电脑进入锁屏睡眠后，网络芯片会降低时钟频率或断开网络连接，造成 API 超时。

- **macOS（推荐命令行常驻）**：
  在后台执行 `caffeinate` 阻止休眠：
  ```bash
  # 阻止系统休眠、屏幕休眠与空闲超时
  caffeinate -dis &
  ```
  *或者安装开源应用 **Amphetamine**，设置触发器为“当 LM Studio 运行时始终保持系统唤醒”。*
- **Windows**：
  1. 打开 `控制面板 -> 电源选项`，将当前电源计划的“使计算机进入睡眠状态”设置为 **从不**。
  2. 打开 `设备管理器 -> 网络适配器 -> 右键网卡属性 -> 电源管理`，取消勾选 **“允许计算机关闭此设备以节约电源”**。

---

## 5. 备用穿透方案：Cloudflare Tunnel（免客户端模式）

若遇到临时无法安装 Tailscale 客户端的设备（如借用他人电脑、公共浏览器），可使用 Cloudflare Quick Tunnel 建立临时公共 HTTPS 访问点：

```bash
# 1. 安装 cloudflared (以 macOS 为例)
brew install cloudflared

# 2. 一键启动向本地 1234 端口的反向穿透
cloudflared tunnel --url http://127.0.0.1:1234
```

终端将打印公网临时访问 URL（如 `https://xxxx-xxxx-xxxx.trycloudflare.com`），直接将其作为 Base URL（加上 `/v1`）即可在任意公网终端进行调用。

---

## 6. 常见故障排查 (Troubleshooting)

| 症状 | 根本原因 | 解决办法 |
| :--- | :--- | :--- |
| **手机 ping 不通 100.x.y.z** | 双方未在同一账号或未打开 Tailscale | 检查两端 Tailscale 客户端的连接开关是否处于 Connected 状态，确认账号一致。 |
| **能 ping 通但 1234 端口被拒绝 (Connection Refused)** | LM Studio 仅监听了 `127.0.0.1` | 进入 LM Studio 的 Server 选项，勾选 `Serve on Local Network`，将 Host 改为 `0.0.0.0`。 |
| **请求超时 (Connection Timed Out)** | 系统防火墙拦截了 1234 端口传入 | **macOS**：在“系统设置 -> 网络 -> 防火墙”中允许 LM Studio 传入连接。<br>**Windows**：在 Windows Defender 防火墙添加入站规则放行 TCP 1234 端口。 |
| **生成长文本时中途截断** | 宿主机在模型推理中途进入睡眠 | 执行 `caffeinate -dis` 或检查电脑电源休眠设置。 |
