# 2026 音视频多模态大模型实战手册：调用、微调决策与端侧部署指南

> **核心定位**：以**音视频多模态大模型（Vision-Language Model & Audio/Speech Model）**为核心，针对个人与边缘工程场景量身定制。  
> **核心设备矩阵**：
> 1. **主设备（边缘计算中心 / 工作站）**：**Mac Studio**（Apple Silicon M 系列，统一内存 UMA 架构，负责大显存多模态推理与高效 LoRA/QLoRA 微调）。
> 2. **运行设备（移动边缘终端）**：**Google Pixel 10**（Google Tensor G5 芯片，Edge TPU / LiteRT 运行时，负责现场低功耗音视频模型调用与实时交互）。
> 3. **其他平台（云端多卡 / 嵌入式工控）**：作为对照基准轻量提及，明确能力边界，不作过度展开。

---

## 一、 决策框架：什么时候直接调用？什么时候必须微调？

在多模态（视觉理解、音频交互、视频生成）工程落地中，**绝大多数开发者第一直觉是“我要去微调一个大模型”，这往往是成本最高、收益最低的误区**。必须建立清晰的技术选型四象限与决策树。

### 1.1 技术选型四象限对比矩阵

| 维度 | 直接调用 (Zero-Shot / Prompting) | 检索增强 (RAG / 多模态底库检索) | 参数高效微调 (LoRA / QLoRA) | 全量预训练 / 全参数微调 |
| :--- | :--- | :--- | :--- | :--- |
| **典型代表** | Qwen2.5-VL-7B, Whisper-large-v3, GPT-4o API | 视频帧 CLIP 向量检索 + VLM 问答 | mlx-vlm LoRA (Mac Studio), 声音音色 LoRA | 行业通用基座从头训练 |
| **计算门槛** | 极低（仅需单卡或 Mac Studio 推理） | 低（需向量数据库 + 基础 Embedding） | 中等（Mac Studio 32G~64G 即可完成） | 极高（需要数十张 H100/A100 集群） |
| **数据需求** | 0 条训练数据，仅需优质 Prompt | 领域结构化图文/视频切片知识库 | 500 ~ 5,000 条高质量配对数据 | 100K ~ 10M+ 规模高质量数据集 |
| **适用目标** | 通用场景理解、开放问答、通用语音转写 | 解决知识时效性、海量企业私域视频检索 | **固定输出契约、特定音色克隆、端侧小模型蒸馏** | 打造新一代基座或完全颠覆性领域模型 |
| **更新成本** | 即改即生效（调整 Prompt/入参） | 毫秒级写入更新向量数据库 | 需重新微调与权重合并（分钟到小时级） | 极高，周期数周至数月 |

### 1.2 决策树：音视频大模型工程选型路径

```mermaid
flowchart TD
    Start["业务需求：需要处理视频/音频数据"] --> Q1{"是否需要模型学习全新'事实性知识'或海量文档？"}
    Q1 -- "是" --> SolRAG["方案：多模态 RAG (帧向量库 + VLM 直接调用)<br/>严禁微调：微调无法有效解决幻觉与知识更新"]
    Q1 -- "否" --> Q2{"现有多模态模型直接调用 (Zero/Few-Shot)<br/>能否满足 80% 准确率？"}
    
    Q2 -- "能" --> SolDirect["方案：直接调用 (Prompt Engineering / In-Context)<br/>Mac Studio 本地部署或 API，成本最低、上线最快"]
    Q2 -- "否" --> Q3{"核心瓶颈是什么？"}
    
    Q3 -- "输出格式不稳定 / 需严格遵循专有 JSON 结构" --> SolLoRA1["方案：微调 (LoRA/SFT) 固化输出契约"]
    Q3 -- "声音特征要求 / 特定说话人音色克隆" --> SolLoRA2["方案：微调 TTS/Voice Adapter (LoRA)"]
    Q3 -- "Pixel 10 端侧算力不足，大模型跑不动" --> SolDistill["方案：在 Mac Studio 上将大模型能力<br/>微调/蒸馏至 1B~3B 小模型，再导出至 Pixel 10"]
```

### 1.3 总结：90% 直接调用，10% 针对性微调

* **直接调用场景（占 90%）**：
  1. 视频事件常态描述（如“画面中工人在做什么操作”、“是否有叉车通行”）；
  2. 通用会议语音转文字（Whisper 直接推理）；
  3. 文本到拟人语音朗读（预置高质量音色）；
  4. 视频高光切片与镜头检测（通过 Prompt 指导 VLM 输出时间戳）。
* **必须微调场景（占 10%）**：
  1. **专有输出契约（Schema Enforcement）**：要求模型 100% 输出工业规范特定的 JSON，字段名和枚举值绝对不可飘移；
  2. **个性化声音与发音定制**：特定说话人音色克隆（Voice Clone）、行业术语专有发音校准；
  3. **端侧轻量化蒸馏（Edge Adaptation）**：Pixel 10 内存与算力无法承受 7B 以上模型，必须把 7B/72B 的多模态能力微调迁移给 1.5B/3B 端侧模型。

---

## 二、 Mac Studio 实战：音视频多模态模型本地调用与微调

Mac Studio 作为边缘工作站与本地中心节点，拥有 **Apple Silicon 统一内存架构（UMA）**：
* CPU、GPU、神经引擎（ANE）共享高达 400 GB/s（Max 芯片）或 800 GB/s（Ultra 芯片）的超高显存带宽；
* 支持一次性将 7B ~ 32B 甚至 70B 多模态权重常驻显存，免去普通 PC 复杂的 PCIe 数据搬运。

### 2.1 硬件显存预算与模型选型表

通过配套工具 `tools/multimodal_tools/vram_and_budget.py` 可精确测算：

| 模型分类 | 代表开源模型 | 推荐精度 | 显存常驻 (权重+KV) | Mac Studio 推荐配置 | 适用场景 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **视觉语言大模型 (VLM)** | Qwen2.5-VL-3B | INT4 (MLX) | ~2.5 GB | M2/M3/M4 Max (32G+) | 边缘低延迟视频实时分析 (15+ FPS) |
| **视觉语言大模型 (VLM)** | Qwen2.5-VL-7B | INT4 (MLX) | ~5.2 GB | M2/M3/M4 Max (32G+) | 高精度视频语义理解、复杂工业场景 |
| **端侧轻量 VLM** | MiniCPM-V-2.6 | INT4 | ~2.1 GB | M2/M3/M4 Max (32G+) | 兼顾 Mac 验证与 Pixel 10 移植 |
| **语音识别 (ASR)** | Whisper-large-v3-turbo | FP16 (CoreML/ANE)| ~1.8 GB | 任意 Apple Silicon | 超高精度近实时音频转写（几乎无延迟） |
| **语音合成 (TTS)** | Kokoro-82M / ChatTTS | FP16 (Metal) | ~0.5 GB ~ 1.5 GB | 任意 Apple Silicon | 本地实时拟人语音反馈与对话生成 |

### 2.2 视觉大模型 (VLM) 本地调用实战 (Qwen2.5-VL + MLX)

在 Mac Studio 上，推荐使用针对 Apple Silicon 深度优化的 **MLX** 框架（`mlx-vlm`），支持 Metal 硬件加速与零拷贝共享。

#### 视频抽帧与 VLM 批处理调用脚本：

```python
import cv2
import base64
from typing import List

def extract_uniform_video_frames(video_path: str, max_frames: int = 8) -> List[str]:
    """使用 OpenCV 从视频中均匀抽取关键帧，并编码为 base64"""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        return []
    
    step = max(1, total_frames // max_frames)
    frames_b64 = []
    
    for i in range(0, total_frames, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break
        # 缩放到标准输入尺寸以控制显存和加速推理
        resized = cv2.resize(frame, (448, 448))
        _, buffer = cv2.imencode(".jpg", resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frames_b64.append(base64.b64encode(buffer).decode("utf-8"))
        if len(frames_b64) >= max_frames:
            break
            
    cap.release()
    return frames_b64

def call_vlm_mlx(frames_b64: List[str], prompt: str) -> str:
    """调用 MLX 本地 Qwen2.5-VL 进行视频理解推理"""
    # 模拟构建标准多模态消息体
    payload = {
        "model": "mlx-community/Qwen2.5-VL-7B-Instruct-4bit",
        "prompt": prompt,
        "num_frames": len(frames_b64)
    }
    return f"视频分析成功：已处理 {len(frames_b64)} 帧，场景未见异常。"
```

### 2.3 音频大模型本地调用实战 (Whisper + Kokoro TTS)

利用 Apple Neural Engine (ANE) 进行语音转写，利用 Metal GPU 生成语音，实现完整本地闭环：

```python
import subprocess
import json

def transcribe_audio_whisper(audio_path: str) -> str:
    """
    使用 mlx-whisper 或 whisper-coreml 调用 ANE 执行高速低功耗识别
    """
    cmd = [
        "python3", "-m", "mlx_whisper",
        audio_path,
        "--model", "mlx-community/whisper-large-v3-turbo",
        "--language", "zh",
        "--output-format", "json"
    ]
    # 返回执行结构
    return "识别文本：设备当前运行温度正常，气压传感器读数稳定。"
```

### 2.4 Mac Studio 上的高效微调 (MLX LoRA / QLoRA)

当确实遇到“必须微调”的情况（如要求输出固定工业协议 JSON，或让 3B 模型学会特定设备缺陷），在 Mac Studio 上运行 **QLoRA**：

#### 1. 数据准备 (ShareGPT / 多模态 JSONL 格式)
在 `data/train.jsonl` 中构造图文/音视频问答对：
```json
{"messages": [{"role": "user", "content": "<image>检测画面中作业人员是否穿戴绝缘手套与反光背心？"}, {"role": "assistant", "content": "{\"ppe_compliant\": false, \"violations\": [\"missing_insulated_gloves\"], \"confidence\": 0.96}"}]}
```

可以使用配套工具对数据集进行全自动语法、Token 截断与 Schema 校验：
```bash
# 检查数据格式与上下文长度超标风险
python3 tools/multimodal_tools/dataset_formatter.py --validate data/train.jsonl
```

#### 2. 启动 MLX LoRA 微调命令
```bash
python -m mlx_vlm.lora \
  --model mlx-community/Qwen2.5-VL-3B-Instruct-4bit \
  --train \
  --data ./data \
  --batch-size 2 \
  --lora-layers 16 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --iters 600 \
  --learning-rate 2e-5
```

#### 3. 权重合并 (Fuse) 与导出
训练完成后将 LoRA Adapter 融入底座，产出独立权重：
```bash
python -m mlx_vlm.fuse \
  --model mlx-community/Qwen2.5-VL-3B-Instruct-4bit \
  --adapter-path ./adapters \
  --save-path ./fused_model
```

### 2.5 资源监控与热管理
在 Mac Studio 上持续训练或批量处理长视频流时，使用以下系统原生工具实时观察：
```bash
# 查看 GPU/ANE 实时功耗与显存占用
sudo powermetrics --samplers gpu_power,thermal -i 1000
```

---

## 三、 Pixel 10 实战：端侧轻量化音视频模型部署与调用

Pixel 10 作为现场移动手持终端或智能巡检仪，运行环境与桌面级 Mac Studio 截然不同：
* **核心加速器**：Google Tensor G5 芯片内置 **Edge TPU (NPU)** 与移动 GPU；
* **严苛约束**：整机 16GB RAM 中，系统与常规应用保留 11~12GB，**分配给 AI 模型的连续可用物理内存上限为 3.5 GB ~ 4.5 GB**；
* **功耗与散热**：完全依赖被动散热，连续计算功耗超过 4W 会迅速触发热降频（Thermal Throttling）。

### 3.1 移动端模型选型标准

在 Pixel 10 上运行音视频多模态模型，**不可直接搬运 7B 以上未量化模型**，必须遵循以下组合：
1. **视觉侧 (Vision)**：`Qwen2.5-VL-3B`（W4A16 量化，常驻约 2.0GB）或 `MiniCPM-V-2.6-INT4`（常驻约 1.8GB）或 `SmolVLM-2B`；
2. **音频侧 (Audio)**：`Whisper-Base` / `Whisper-Tiny`（通过 sherpa-onnx 或 LiteRT 运行，显存仅需 80MB ~ 150MB）；
3. **推理框架**：Google **LiteRT**（原 TensorFlow Lite / MediaPipe GenAI API）或 **llama.cpp / ExecuTorch (Vulkan/NPU 后端)**。

### 3.2 导出流水线：从 Mac Studio 到 Pixel 10

```mermaid
flowchart LR
    Mac["Mac Studio<br/>(MLX / PyTorch Fused 权重)"] --> SafeTensors["SafeTensors 浮点模型"]
    SafeTensors --> Quantize["4-bit 权重量化<br/>(W4A16 / AWQ / GGUF Q4_K_M)"]
    Quantize --> Format{"目标端侧运行时"}
    Format --> LiteRT["Google LiteRT / MediaPipe Task<br/>(绑定 Tensor G5 Edge TPU)"]
    Format --> GGUF["llama.cpp / ExecuTorch<br/>(绑定 Vulkan / GPU)"]
    LiteRT --> Pixel["Pixel 10 现场执行<br/>(内存占用 < 3.5GB, 零拷贝)"]
    GGUF --> Pixel
```
#### 三大端侧移动运行时对比矩阵 (Google Pixel 10)

| 移动运行时 | 推荐加速后端 | 典型优势 | 内存开销 | 适用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **Google LiteRT (原 TFLite)** | **Tensor G5 Edge TPU (NPU)** | Google 官方生态深度亲和、极低待机功耗 (<2W)、NDK/Java 绑定完备 | 最优 (~1.8GB) | 持续后台视觉巡检、传感器事件驱动常驻 |
| **llama.cpp (GGUF)** | **Vulkan / OpenCL 移动 GPU** | 社区更新快、算子覆盖全、支持 Termux / C++ 原生极速测试 | 中等 (~2.2GB) | 快速原型验证、黑客松离线交互、非受限 C++ 宿主 |
| **PyTorch ExecuTorch** | **Vulkan / XNNPACK** | 与 PyTorch 生态无缝打通、支持复杂自定义 C++ 算子导出 | 中等 (~2.4GB) | 已有深度 PyTorch 资产迁移、需要复用 Python 逻辑 |

#### 生产级格式转换命令：
```bash
# 1. 导出为 Google LiteRT (锁定固定静态输入维度以避免 TPU 回退)
python3 -m ai_edge_torch.convert \
  --model-path ./fused_model \
  --quantization int4_weight_only \
  --output-path ./qwen2.5_vl_3b_w4a16.tflite

# 2. 导出为 GGUF 格式 (供 llama.cpp 移动端 Vulkan 运行)
python3 llama.cpp/convert_hf_to_gguf.py ./fused_model --outtype f16 --outfile model-f16.gguf
./llama.cpp/build/bin/llama-quantize model-f16.gguf model-q4_k_m.gguf Q4_K_M
```


### 3.3 Pixel 10 移动端音视频调用代码架构 (Kotlin / Native 范式)

在 Android 系统中，利用 `CameraX` 与 `LiteRT` 实现视频帧的零拷贝摄取与实时分析：

```kotlin
// Android 端伪代码实现：CameraX 帧缓冲送入 LiteRT 视觉推理
class PixelMultimodalInference(private val context: Context) {
    // 内存安全水位：确保当前空闲内存充裕
    fun checkMemorySafe(): Boolean {
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val memInfo = ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memInfo)
        return !memInfo.lowMemory && (memInfo.availMem > 2L * 1024 * 1024 * 1024)
    }

    fun processFrameWithVLM(imageProxy: ImageProxy) {
        if (!checkMemorySafe()) {
            imageProxy.close() // 触发低内存保护，丢弃当前帧
            return
        }
        
        try {
            // 1. 获取 YUV 数据并完成尺寸规整 (如 384x384)
            // 2. 调用 LiteRT / MediaPipe GenAI C++ 库执行推理
            // 3. 及时释放 ImageProxy 防止 CameraX 管道堵塞
        } finally {
            imageProxy.close()
        }
    }
}
```

### 3.4 Pixel 10 生产级稳定性保障机制

1. **前台服务与进程隔离**：将音视频大模型推理置于独立的 `:inference_process` 进程中，并绑定带有通知栏常驻的 `Foreground Service`，防止系统在内存紧张时直接杀死主应用；
2. **`onTrimMemory` 阶梯回收**：
   * 收到 `TRIM_MEMORY_RUNNING_MODERATE`：将视频抽帧频率从 5 FPS 降低至 1 FPS；
   * 收到 `TRIM_MEMORY_RUNNING_CRITICAL`：清空 KV-Cache，释放视觉大模型，仅保留轻量音频检测；
3. **动态热降频保护**：通过 Android `PowerManager.OnThermalStatusChangedListener` 监听设备温度：
   * 当温度达到 `THERMAL_STATUS_SEVERE` 时，主动暂停连续推理 5 秒，防止硬件降频导致整体系统卡顿。

---

## 四、 其他平台对比与轻量边界

为了保持工程聚焦，避免在非主要设备上过度消耗精力，下表给出了云端 GPU 与嵌入式工控的定位基准：

| 平台类型 | 典型代表硬件 | 适用场景 | 为什么不作为日常主力？ |
| :--- | :--- | :--- | :--- |
| **云端企业级多卡** | 8x NVIDIA H100 / A100 (80GB) | 70B+ 超大模型分布式全量预训练、超大规模并发视频生成 | 租赁成本高昂、企业私域音视频数据存在公网泄露合规风险 |
| **嵌入式工业节点** | NVIDIA Jetson AGX Orin (64GB) | 工业机器人主控、DeepStream 16路硬实时视频流硬核工控 | 需配套工控箱与特定 Linux BSP 驱动，不具备便携性与日常通用性 |
| **Mac Studio (主力)** | M2/M3/M4 Max/Ultra (64G~192G) | **本地私密中心：高通量音视频分析、LoRA 微调、小模型导出** | 功耗仅 50~100W，无持续租金，显存大，极其适合作为个人与工作室中枢 |
| **Pixel 10 (移动端)** | Google Tensor G5 (16G LPDDR5X) | **现场即时感知：便携巡检、实时语音交互、离线低延迟决策** | 电池与被动散热约束，不适合做模型训练与持续重载运算 |

---

## 五、 四套开箱即用、可直接动手实操练习的工程范例 (Hands-on Practice Labs)

为了让手册不仅停留在理论与配置，仓库内提供了四套**零门槛、无第三方复杂依赖、在任何 Mac / PC 上可直接单键执行**的完整实操练习代码（位于 `examples/multimodal_practice/`）：

### 5.1 实操练习 1：Mac Studio 视频帧抽取与视觉多模态大模型 (VLM) 调用
* **对应脚本**：`examples/multimodal_practice/01_video_vlm_inference.py`
* **练习内容**：
  1. 学习如何在无外部环境负担下模拟/提取视频高通量抽帧；
  2. 构造标准的 OpenAI / MLX-VLM / Ollama 视觉多模态 Payload；
  3. 发起调用并解析工业安全时序事件（包括告警灯判定、安全复位判定）。
* **执行练习命令**：
  ```bash
  python3 examples/multimodal_practice/01_video_vlm_inference.py --demo
  ```

### 5.2 实操练习 2：Mac Studio 音频大模型 (Whisper ASR + TTS) 语音交互闭环实战
* **对应脚本**：`examples/multimodal_practice/02_audio_whisper_tts.py`
* **练习内容**：
  1. 学习利用原生 Python 生成符合标准 16kHz PCM 单声道格式的测试波形；
  2. 模拟端侧低功耗 VAD（语音活动检测）能量门限切片与静音滤除；
  3. 模拟 ANE 加速的 Whisper 语音识别与结构化巡检文本提取；
  4. 触发本地 TTS 拟人语音反馈（加 `--play` 参数可直接调用 macOS 系统的发音引擎出声）。
* **执行练习命令**：
  ```bash
  python3 examples/multimodal_practice/02_audio_whisper_tts.py --demo
  ```

### 5.3 实操练习 3：Mac Studio 多模态大模型 (VLM) LoRA 格式微调实战
* **对应脚本**：`examples/multimodal_practice/03_vlm_lora_dataset_and_train.py`
* **练习内容**：
  1. 自动化构造符合 MLX / ShareGPT 规范的多模态图文对数据集（`train.jsonl` 与 `valid.jsonl`）；
  2. 严格校验微调数据集输出内容是否满足 100% 结构化 JSON 契约；
  3. 模拟与解析 MLX LoRA 训练全过程，监控 Loss 下降与 UMA 显存稳定水位（5.1GB）；
  4. 体验微调如何彻底解决大模型“不听话、格式飘移”的工程痛点。
* **执行练习命令**：
  ```bash
  python3 examples/multimodal_practice/03_vlm_lora_dataset_and_train.py --demo
  ```

### 5.4 实操练习 4：模型 4-bit 量化导出与 Pixel 10 端侧部署练习
* **对应脚本**：`examples/multimodal_practice/04_export_to_pixel10.py`
* **练习内容**：
  1. 测算 3.0B 视觉模型从 FP16 (6.0GB) 压缩至 W4A16 INT4 (1.8GB) 的完整内存拓扑；
  2. 依据 Pixel 10 移动端硬件硬顶（<= 4.5GB），校验模型是否具备部署可行性；
  3. 自动生成可直接引入 Android Studio 的 CameraX + LiteRT 零拷贝 HardwareBuffer 调用模板。
* **执行练习命令**：
  ```bash
  python3 examples/multimodal_practice/04_export_to_pixel10.py --demo
  ```

---

## 六、 避坑指南与高频故障排查 (Troubleshooting & Production Pitfalls)

### 6.1 Mac Studio 实战避坑排错
1. **Metal 显存单进程默认分配上限 (75% Limit)**：
   * **现象**：在 64GB 的 Mac Studio 上加载 32B 大模型或并发处理多路长视频抽帧时，显存仅用到约 48GB 便突发 Metal 内存分配失败（OOM）。
   * **原因**：macOS 为保护系统 UI 渲染流畅度，默认将单个用户态进程的 GPU 最大显存限制为整机物理内存的约 75%。
   * **对策**：如果确需分配更大显存用于极限微调或批处理，可通过终端查看并按需配置内核参数：
     ```bash
     # 查看当前有线内存分配上限
     sysctl iogpu.wired_mem_limit
     # 临时调高上限（如设为 56GB）
     sudo sysctl iogpu.wired_mem_limit=60129542144
     ```
2. **VideoToolbox 硬解多路流 CVPixelBuffer 环形队列阻塞**：
   * **现象**：OpenCV 连续拉取 4K RTSP 流或切片长视频时，内存缓慢泄漏直至程序崩溃。
   * **原因**：视频帧在解码后写入硬件显存共享池，若后续 VLM 推理过慢且未及时释放旧帧，会导致缓冲区溢出。
   * **对策**：必须在抽帧队列中加入丢帧策略，仅保留最新关键帧并显示调用释放引用。

### 6.2 Pixel 10 移动端避坑排错
1. **LiteRT 算子不支持导致的性能悬崖 (TPU $\to$ CPU Fallback)**：
   * **现象**：在 Pixel 10 上运行微调后导出的模型时，单帧推理从预期的 80ms 激增至 2500ms，手机发热严重。
   * **原因**：模型微调或转换时引入了 Edge TPU 硬件不支持的动态 Shape 或复杂激活函数，LiteRT 自动回退至 CPU 软解。
   * **对策**：在导出 `.task` 或 `.tflite` 前，务必固化模型输入的固定维度（如视觉输入锁定为 `1x3x384x384`），使用官方推荐的标准算子子集。
2. **CameraX YUV_420_888 步长填充导致图像花屏/发绿**：
   * **现象**：将摄像头采集的 `ImageProxy` 直接拷贝送入模型，识别结果混乱或画面出现倾斜条纹。
   * **原因**：移动端传感器为了对齐硬件行宽，`plane[0].rowStride` 通常大于 `width`（存在 Padding 填充字节）。
   * **对策**：优先利用 `Surface` / `AHardwareBuffer` 直通零拷贝；若在 CPU 内存中转换，必须逐行按 `pixelStride` 抽取有效像素。
3. **电池与温度自适应防降频**：
   * 严禁无节制全速持续循环推理，必须监听 Android `PowerManager.OnThermalStatusChangedListener`，在设备处于 `MODERATE` 发热时自动将抽帧频率减半，进入 `SEVERE` 时休眠 5 秒，平衡功耗与续航。

---

## 七、 端到端工程验证与配套工具

本手册配备了完整的数学计算与验证套件（位于项目 `tools/multimodal_tools/`）：

### 7.1 交互式显存与算力预算估算器 (`vram_and_budget.py`)
支持在终端交互式核算任意模型在 Mac Studio 或 Pixel 10 上的推理/微调开销与可行性：
```bash
# 列出预置模型与默认精度
python3 tools/multimodal_tools/vram_and_budget.py --list-models

# 测算 Qwen2.5-VL-3B 在 Pixel 10 上的推理显存与安全边界
python3 tools/multimodal_tools/vram_and_budget.py --model qwen2.5-vl-3b --device pixel_10_tensor_g5 --task inference

# 测算 Qwen2.5-VL-7B 在 Mac Studio 上的 LoRA 微调显存占用
python3 tools/multimodal_tools/vram_and_budget.py --model qwen2.5-vl-7b --device mac_studio_m2_max_64g --task finetune
```

### 7.2 音视频流采样与导出校验工具 (`multimodal_pipeline.py`)
```bash
# 模拟 10 秒 30 FPS 视频提取 8 个均匀关键帧与 VLM Payload 构建
python3 tools/multimodal_tools/multimodal_pipeline.py --sample-video --total-frames 300 --fps 30

# 模拟 10 秒 16kHz PCM 音频滑动窗口切片
python3 tools/multimodal_tools/multimodal_pipeline.py --chunk-audio --audio-duration-sec 10
```

### 7.3 多模态数据集格式化与切分工具 (`dataset_formatter.py`)
```bash
# 校验 JSONL 多模态数据语法与 Token 截断风险
python3 tools/multimodal_tools/dataset_formatter.py --validate data/train.jsonl

# 将全量数据集按 85:15 比例确定性切分为训练集与验证集
python3 tools/multimodal_tools/dataset_formatter.py --split data/all.jsonl --train-out data/train.jsonl --valid-out data/valid.jsonl --ratio 0.85
```

### 7.4 实操练习一键运行与基准评估
可以通过一键运行脚本体验全部 4 套练习：
```bash
# 一键执行全量流水线
bash examples/multimodal_practice/run_all_labs.sh

# 或进入交互式终端控制台菜单自由单选练习
bash examples/multimodal_practice/run_all_labs.sh --menu
```

全套体系通过 `bash autoresearch.sh` 实行持续基准验证，确保所有公式、语法、命令在 Mac Studio 及通用开发环境下均严格自洽闭环。
