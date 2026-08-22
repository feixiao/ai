# antirez/ds4 (DwarfStar) Mac Studio 本地部署与运行指南

本项目文档针对 **Mac Studio (Apple M4 Max, 128GB 统一内存, macOS)** 环境，提供 Salvatore Sanfilippo（Redis 创始人 antirez）开源的专有原生推理引擎 [**ds4 (DwarfStar)**](https://github.com/antirez/ds4) 的完整编译、模型下载、CLI 交互、HTTP 服务与 Agent 接入指南。

---

## 1. 项目简介与硬件匹配分析

**DwarfStar (ds4)** 是 antirez 为 **DeepSeek V4 Flash / PRO** 以及 **GLM 5.2** 定制研发的原生 C/Metal 高性能推理引擎（不直接依赖 GGML 库，但借鉴了 llama.cpp 的 GGUF 格式与内核理念）。

### 硬件与模型适配策略 (M4 Max 128GB)

| 模型版本 | 显存/内存占用 | 运行模式 | 在 M4 Max (128GB) 上的建议 |
| :--- | :--- | :--- | :--- |
| **DeepSeek V4 Flash (ds4f-q2)** | ~81 GB | **全显存常驻 (Metal Resident)** | **🔥 最佳主力选择**。可全量装入 128GB 统一内存，留出充足空间支持 100k~300k 超长上下文 KV Cache。生成速度约 35~40+ t/s，Prefill 达 600~800 t/s。 |
| **DeepSeek V4 Flash (ds4f-q2-q4)** | ~95 GB | **全显存常驻** | 提升后 6 层 MoE 精度，适合高精度需求，需控制上下文在 64k~100k 以内。 |
| **DSpark 投机采样 (ds4f-dspark)** | ~5.6 GB 辅助显存 | **投机加速** | 搭配 `ds4f-q2` 启用，最高可提速代码与结构化输出生成。 |
| **DeepSeek V4 PRO (pro-q2-imatrix)** | >200 GB | **SSD 专家流式加载 (SSD Streaming)** | 体验 PRO 模型时使用。共享/Dense 权重常驻内存，MoE 专家从高速 SSD 动态缓存加载（建议分配 48~64GB 动态专家缓存）。 |

---

## 2. 环境准备与源码编译

macOS 预装的 Clang / Make 工具链和 Metal 驱动已原生支持 ds4。

### 2.1 克隆仓库

```bash
cd /Users/frank/wk/github/ai/ds4
git clone https://github.com/antirez/ds4.git
cd ds4
```

### 2.2 编译 Metal 原生版本

```bash
# 默认编译 macOS Metal 高性能后端
make
```

编译成功后，将在当前目录生成 5 个二进制可执行程序：
- `ds4`：交互式命令行与单次 Prompt 推理工具。
- `ds4-server`：兼容 OpenAI / Anthropic / Codex Responses 协议的 HTTP 本地服务。
- `ds4-agent`：基于本地 KV Cache 直读的原生编码智能体。
- `ds4-bench`：首字延迟 (TTFT)、Prefill 与 Decode 吞吐量阶梯基准测试工具。
- `ds4-eval`：92 道 GPQA/AIME/安全代码能力回归评测工具。

---

## 3. 模型权重下载

ds4 提供了自动化下载脚本 `download_model.sh`，支持断点续传（下载到 `./gguf/` 目录），并自动将 `./ds4flash.gguf` 软链接至当前选中的主力模型。

### 3.1 下载主力模型（推荐 ds4f-q2）

```bash
# 适用于 96GB/128GB 机器的主力模型 (DeepSeek V4 Flash 2-bit MoE)
./download_model.sh ds4f-q2

# （可选）下载 DSpark 辅助草稿模型（加速生成）
./download_model.sh ds4f-dspark
```

*(可选其它模型代号：`ds4f-q2-q4`、`ds4f-q4`、`pro-q2-imatrix`、`glm-antirez-iq2xxs`)*

---

## 4. 运行与使用方式

### 4.1 CLI 交互对话与一问一答

#### 单次提问 (One-shot)
```bash
./ds4 -p "请用简练的语言解释 Redis Streams 的核心设计思想。"
```

#### 进入多轮对话交互界面 (带思考过程)
```bash
./ds4 -m ds4flash.gguf
```
- 交互界面提示符为 `ds4>`。
- 快捷指令：
  - `/think`：开启深度思考（DeepSeek 思考模式）。
  - `/nothink`：关闭深度思考，直接输出答案。
  - `/ctx 100000`：调整当前会话上下文上限。
  - `/read <file_path>`：将本地文件内容载入上下文。
  - `/quit`：退出会话。

#### 启用 DSpark 投机加速 (贪婪采样模式)
```bash
./ds4 -m ds4flash.gguf \
  --mtp gguf/DeepSeek-V4-Flash-DSpark-support-0731.gguf \
  --dspark --temp 0
```

---

### 4.2 启动本地 HTTP 服务 (OpenAI / Anthropic 双兼容)

`ds4-server` 提供了标准 API 服务，支持 SSE 流式传输、DSML 工具调用精确重放与磁盘 KV 缓存复用。

由于全量加载模型会占用约 **81 GB 显存/内存**，推荐采用 **按需后台启停** 方案，用时秒级启动，不用时一键释放内存。

#### 💡 推荐：一键按需管理脚本

```bash
cd /Users/frank/wk/github/ai/ds4

# 1. 后台静默启动（推荐日常使用，日志自动写入 server.log）
./start_server.sh -d

# 2. 停止服务并立即释放 81GB 内存
./stop_server.sh

# （可选）查看运行日志
tail -f server.log

# （可选）前台启动（用于调试，按 Ctrl+C 退出）
./start_server.sh
```

#### 手动启动完整命令（供自定义调试参考）：
```bash
./ds4-server \
  -m ds4flash.gguf \
  --host 127.0.0.1 \
  --port 8400 \
  --ctx 100000 \
  --kv-disk-dir ~/.ds4/kvcache \
  --kv-disk-space-mb 16384 \
  --cors
```

#### 关键启动参数说明：
- `--port 8400`：服务端口（默认为 8400，避开常见的 8000 端口冲突）。
- `--ctx 100000`：分配 100k 上下文窗口（在 128GB M4 Max 上既保证长文本又不会触发显存换页压力）。
- `--kv-disk-dir ~/.ds4/kvcache`：启用磁盘 KV Cache 持久化，同一会话历史不需要重复 Prefill。
- `--batched-session N`：多会话并发批处理（在单机多客户端调用时可开启，如 `--batched-session 4`）。
- `--power 70`：（可选）降低满载发热与风扇转速，通过在层间与 Token 间插入微休眠实现 70% 功率控制。

#### 支持的 API 端点：
- `POST /v1/chat/completions` (OpenAI 协议)
- `POST /v1/messages` (Anthropic Claude 协议)
- `POST /v1/responses` (OpenAI Responses / Codex 协议)
- `GET /v1/models`

#### 测试 OpenAI 兼容端点：
```bash
curl http://127.0.0.1:8400/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "你好，请自我介绍一下。"}],
    "stream": true
  }'
```

---

### 4.3 接入 Claude Code / OpenCode / 外部工具

#### 接入 Claude Code (作为本地模型后端)
在终端中设置环境变量即可将 Claude Code 指向本地 ds4-server：

```bash
export ANTHROPIC_BASE_URL="http://127.0.0.1:8400"
export ANTHROPIC_AUTH_TOKEN="dsv4-local"
export ANTHROPIC_MODEL="deepseek-v4-flash"

claude
```

#### 接入 OpenCode (`~/.config/opencode/opencode.json`)
```json
{
  "provider": {
    "ds4": {
      "name": "ds4.c (local M4 Max)",
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "http://127.0.0.1:8400/v1",
        "apiKey": "dsv4-local"
      },
      "models": {
        "deepseek-v4-flash": {
          "name": "DeepSeek V4 Flash",
          "limit": {
            "context": 100000,
            "output": 384000
          }
        }
      }
    }
  }
}
```

---

### 4.4 原生编码智能体 (ds4-agent)

ds4 内置了深度结合底层 KV 缓存的原生 Coding Agent，无需 API 转换层，直接与底层推理核心联动，具有极高的首字响应速度：

```bash
./ds4-agent -m ds4flash.gguf --ctx 100000
```
- 会话会自动保存到 `~/.ds4/kvcache`。
- 在 Agent 中可通过 `/list` 查看历史会话，`/switch <sha>` 秒级恢复历史会话（无需重新 Prefill）。

---

### 4.5 体验超大模型：DeepSeek V4 PRO (SSD Streaming 模式)

如果在 128GB 内存上想测试参数量更大的 **DeepSeek V4 PRO**：

```bash
# 1. 下载 PRO 2-bit imatrix 模型
./download_model.sh pro-q2-imatrix

# 2. 以 SSD 流式专家加载模式启动（动态分配 56GB 显存作为专家缓存）
./ds4 \
  -m gguf/DeepSeek-V4-Pro-IQ2XXS-w2Q2K-AProjQ8-SExpQ8-OutQ8-Instruct-imatrix.gguf \
  --ssd-streaming \
  --ssd-streaming-cache-experts 56GB \
  --ctx 32768 \
  --nothink
```

---

## 5. 性能基准测试与质量评估

### 5.1 吞吐量基准测试 (`ds4-bench`)

测试在不同上下文长度下的 Prefill 与生成速率：

```bash
./ds4-bench \
  -m ds4flash.gguf \
  --prompt-file speed-bench/promessi_sposi.txt \
  --ctx-start 2048 \
  --ctx-max 32768 \
  --step-incr 4096 \
  --gen-tokens 128
```

### 5.2 能力回归评测 (`ds4-eval`)

运行 92 道数学、推理与代码漏洞定位评测题：

```bash
./ds4-eval -m ds4flash.gguf --trace /tmp/ds4-eval.txt
```

---

## 6. 常见问题与调优建议

1. **显存限制与 OS 锁定限制**：
   macOS 默认单个进程最多使用约 75% 统一内存。若要在极端情况下分配更多显存，可临时提高限制：
   ```bash
   sudo sysctl iogpu.wired_limit_mb=120000
   ```
2. **长上下文内存规划**：
   - 128GB 内存配置下，`ds4f-q2` 权重占用约 81GB。
   - 100k 上下文 KV Cache 约需 6~8GB 额外内存，总占用控制在 90GB 左右，处于极佳的安全区间。
3. **静音 / 低发热运行**：
   如果长时间运行批处理任务，加上 `--power 70` 或 `--power 50` 可以在保持合理速度的同时显著降低机身温度。
