# LiveKit Audio Agent (对接远端 LM Studio 本地大模型)

基于 **LiveKit Agents** 架构与部署在 Tailscale 远端内网主机（`100.126.144.68:1234`）上的 **LM Studio** 实现低延迟实时语音通话 Agent。

---

## 1. 探测结果与模型选型

通过 `probe.py` 探测远端 LM Studio 节点（`http://100.126.144.68:1234`）获取的模型清单如下：

| 序号 | 模型 ID | 类型 | 量化/格式 | 状态 | 适用场景 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **`qwen/qwen3-vl-8b`** | VLM / 对话 | GGUF Q4_K_M | **loaded (已就绪)** | **推荐首选（响应极快，语音实时性高）** |
| 2 | `qwen3.8-27b-splash` | VLM | splash 4bit | not-loaded | 适合大参数量复杂推理 |
| 3 | `qwen3-vl-32b-thinking-mlx` | VLM | mlx 4bit | not-loaded | 深度思考模型，语音交互时容易延迟过大 |
| 4 | `google/gemma-4-26b-a4b-qat` | VLM | mlx 4bit | not-loaded | 英文/多模态支持 |
| 5 | `gemma-4-31b-it` | VLM | mlx 4bit | not-loaded | Gemma 4 31B 问答对话 |
| 6 | `gemma-4-26b-a4b-it` | VLM | mlx 4bit | not-loaded | Gemma 4 26B 问答对话 |
| 7 | `text-embedding-nomic-embed-text-v1.5` | Embedding | GGUF | not-loaded | 文本向量嵌入 |

> **选型策略**：系统默认自动探测并选用状态为 `loaded` 且体积轻量响应迅速的 **`qwen/qwen3-vl-8b`**。

---

## 2. 目录结构

```
LiveKit/lmstudio_audio_agent/
├── .env.example       # 环境变量配置模板
├── requirements.txt   # 项目依赖库
├── probe.py           # 远端 LM Studio 模型自动探测与优选模块
├── agent.py           # LiveKit 语音 Agent 核心入口
└── test_agent.py      # 模型探测与 LiveKit 流式推理自动化测试
```

---

## 3. 快速上手

### 步骤 1：激活环境并安装依赖
```bash
### 步骤 2：启动本地 LiveKit Server (无需云端)

本机已内置安装好官方 `livekit-server`，直接一行命令即可启动本地开发服务器：

```bash
livekit-server --dev
```
* 监听地址：`ws://127.0.0.1:7880`
* 默认开发者 Key：`devkey`
* 默认开发者 Secret：`secret`

### 步骤 3：配置环境变量与启动 Agent

```bash
cp .env.example .env
# 配置好 DEEPGRAM_API_KEY（本地 LiveKit 已自动配好 devkey）

python agent.py dev
```

启动后，Agent 会自动注册到本机的 `ws://127.0.0.1:7880`。

### 步骤 4：本地浏览器测试连接

打开浏览器访问 LiveKit 官方开源客户端测试页：
👉 [https://agents-playground.livekit.io/](https://agents-playground.livekit.io/)
* **Server URL**: `ws://localhost:7880`
* **Token**: 在终端生成一个测试 Token：
  ```bash
  lk token create --dev --join --room test-room --identity test-user
  ```
将生成的 Token 粘贴到网页中点击 **Connect**，即可对着麦克风与 LM Studio 大模型实时语音通话！
```
启动后终端将生成 LiveKit Agent Playground 测试链接，点击进入并在浏览器允许麦克风权限即可开始语音对话。
