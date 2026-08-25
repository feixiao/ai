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

#### 💡 推荐：一键按需管理脚本 (运行于 `~/forbuild/ds4/`)

为了便于查找与管理，脚本、模型软链接及编译可执行文件均统一收录在 `~/forbuild/ds4/` 目录下。

```bash
# 进入部署运行目录
cd ~/forbuild/ds4

# 1. 后台静默启动（推荐日常使用，日志自动写入 server.log）
./start_server.sh -d

# 2. 停止服务并立即释放 81GB 内存
./stop_server.sh

# （可选）查看运行日志
tail -f server.log

# （可选）前台启动（用于调试，按 Ctrl+C 退出）
./start_server.sh
```

> **💡 说明：** 
> 1. 您也可以在当前 AI 仓库的 `/Users/frank/wk/github/ai/ds4` 目录下直接运行 `./start_server.sh` 和 `./stop_server.sh`，它们会自动路由调用 `~/forbuild/ds4` 下的主逻辑。
> 2. `start_server.sh` 启动时会自动切换工作目录 (`cd`) 到真实的源码仓库，以保证 Metal 渲染文件 (`metal/*.metal`) 被底层正常加载。

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

#### 💡 推荐：使用 `claude-ds4` 一键启动脚本接入 Claude Code

我们为您准备了完整的 Claude Code 包装脚本（已安装至系统命令 `claude-ds4`，同时位于 `~/forbuild/ds4/claude-ds4.sh`）。

它会自动将配置隔离至 `~/.ds4/claude_config`，自动增量双向同步官方会话（支持直接 `--resume <id>` 恢复任何历史会话），清除云端 API Key，并将 Claude Code 内部的 Sonnet、Haiku、Opus 及子 Agent 全部路由映射到本地运行的 `ds4-server`（8400 端口）：

```bash
# 启动本地服务后，在任意目录下直接执行：
claude-ds4

# 恢复历史会话（已实现官方 ~/.claude 与 ds4 会话互通）
claude-ds4 --resume <session-id>
```

##### 独立会话同步工具 (`sync_sessions.sh`)

如果需要手动同步或指定单个 UUID 会话迁移，可直接使用配套同步脚本：

```bash
cd ~/forbuild/ds4

# 1. 默认增量同步所有官方会话到 ds4
./sync_sessions.sh

# 2. 双向同步（两边保持最新）
./sync_sessions.sh -b

# 3. 精准同步单个指定 UUID 会话
./sync_sessions.sh 2ce044f6-9934-4e69-b974-c6881e1764da
```

##### 包装脚本源码详情 (`~/forbuild/ds4/claude-ds4.sh`)：
```bash
#!/bin/sh
# 1. 独立配置目录，避免与官方 Claude Code 登录凭证（Keychain/OAuth）冲突
export CLAUDE_CONFIG_DIR="$HOME/.ds4/claude_config"
mkdir -p "$CLAUDE_CONFIG_DIR"

# 2. 避免代理干扰本地 127.0.0.1 通信
export NO_PROXY="127.0.0.1,localhost,$NO_PROXY"
export no_proxy="127.0.0.1,localhost,$no_proxy"

# 3. 基础端点与本地鉴权配置
unset ANTHROPIC_AUTH_TOKEN
export ANTHROPIC_API_KEY="dsv4-local"
export ANTHROPIC_BASE_URL="http://127.0.0.1:8400"
export ANTHROPIC_MODEL="deepseek-v4-flash"

# 自定义模型名称与展示信息
export ANTHROPIC_CUSTOM_MODEL_OPTION="deepseek-v4-flash"
export ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="DeepSeek V4 Flash local ds4"
export ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION="ds4.c local GGUF"

# 全量将 Sonnet / Haiku / Opus / 子 Agent 路由重定向到本地模型
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-flash"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-flash"
export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"

# 流量与流式超时及未知模型窗口优化
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK=1
export CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1
export CLAUDE_STREAM_IDLE_TIMEOUT_MS=600000

# 4. 自动增量同步会话与共享配置
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync_sessions.sh"
if [ "${CLAUDE_DS4_NO_SYNC:-0}" != "1" ] && [ -f "$SYNC_SCRIPT" ] && [ -x "$SYNC_SCRIPT" ]; then
    "$SYNC_SCRIPT" -b >/dev/null 2>&1 || true
    trap '"$SYNC_SCRIPT" -b >/dev/null 2>&1 || true' EXIT
fi

# 5. 查找并启动 claude
CLAUDE_BIN="$HOME/.local/bin/claude"
[ ! -f "$CLAUDE_BIN" ] && CLAUDE_BIN="$(which claude 2>/dev/null)"
"$CLAUDE_BIN" "$@"
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

### 5.1 吞吐量基准测试与图表一键生成 (`ds4-bench`)

我们已为您配置了自动进行基准测试并自动绘图的自动化脚本。

在 `~/forbuild/ds4/` 目录下运行以下命令（若后台有运行中的 `ds4-server`，脚本会提示是否需要先停止以防止数据干扰）：

```bash
cd ~/forbuild/ds4

# 一键运行测试并自动生成 CSV 数据和 SVG 折线图表（默认测试从 32k 起至 100k，步长 32k 保证快速测试）
./run_bench.sh

# （可选）也可以指定自定义测试上限与步长。例如测试到 64k 上下文，步长 8k：
./run_bench.sh 65536 8192
./run_bench.sh 10240 65536
```

**运行结果说明：**
* 运行结束后，会在 `speed-bench/` 文件夹下生成两个文件：
  * **`speed-bench/m4_max.csv`**（原始评测数据）。
  * **`speed-bench/m4_max_ts.svg`**（走势图表，可以直接在 Finder 中双击使用浏览器查看图表曲线）。

#### 手动分步运行与自定义绘图命令：

1. **手动运行评测并导出 CSV**（例如最大 100k 上下文，32k 起，32k 步长）：
   ```bash
   ./ds4-bench \
     -m ds4flash.gguf \
     --prompt-file speed-bench/promessi_sposi.txt \
     --ctx-start 32768 \
     --ctx-max 102400 \
     --step-incr 32768 \
     --gen-tokens 128 > speed-bench/m4_max.csv
   ```
2. **手动调用绘图脚本生成 SVG 图表**：
   ```bash
   python3 speed-bench/plot_speed.py speed-bench/m4_max.csv --title "M4 Max Benchmark"
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
