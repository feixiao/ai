# Qwen-Image-2.1 ComfyUI 本地工作流与智能提示词扩写系统

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![ComfyUI Compatible](https://img.shields.io/badge/ComfyUI-Native%20%2F%20GGUF-green.svg)](https://github.com/comfyanonymous/ComfyUI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

本项目专为阿里开源的 **Qwen-Image-2.1** 图像生成模型打造，提供**本地化极简描述自动扩写、端到端自动化测试脚本、ComfyUI 官方标准画布工作流以及轻量自定义节点**。

---

## 1. Qwen-Image-2.1 核心特性

- **架构创新**：基于 70 亿参数（7B）的 32 层 Single-Stream DiT（单流 Diffusion Transformer）架构，统一了文本到图像生成与多参考图编辑。
- **高维语义理解**：采用 **Qwen3-VL** 作为视觉与文本编码器，相比传统 CLIP/T5 具有质的飞跃，擅长理解自然语言中的空间方位、物理材质及复杂逻辑。
- **原生 2K 与 RGBA**：支持直接原生输出 2048×2048 细节分辨率，且原生支持 RGBA 真实透明通道渲染。
- **专用 VAE**：采用 16 通道专用 VAE 架构（请勿与 SDXL/FLUX/Wan VAE 混用）。

---

## 2. 目录结构

```text
ComfyUI/qwen_image_2.1/
├── README.md                      # 本说明文档
├── prompt_expander.py             # 核心提示词扩写引擎（LM Studio 客户端 + 启发式兜底）
├── qwen_image21_test.py           # 命令行端到端测试主脚本（自动化调用全流程）
├── workflows/
│   ├── qwen_image_2.1_t2i_canvas.json   # ComfyUI Web 画布工作流（直接拖入浏览器）
│   └── qwen_image_2.1_api.json          # ComfyUI API 格式工作流模板（供脚本调用）
├── custom_nodes/
│   └── ComfyUI-LMStudio-Prompt/   # ComfyUI 专用节点：画布中直接连线实时扩写
│       ├── __init__.py
│       └── lmstudio_prompt_node.py
├── tests/                         # 自动化测试用例（覆盖扩写、CLI、工作流与节点）
└── output/                        # 自动生成的图像与测试日志存储目录
```

---

## 3. 模型下载与配置分档 (Apple Silicon / Mac 优化)

请将所需模型放置在您的 ComfyUI 模型目录中（默认路径通常为 `~/ComfyUI/models/` 或共享目录 `/Users/frank/ComfyUI/models/`）：

| 角色分类 | 推荐下载文件名 (首选 GGUF) | 目标存放目录 | Hugging Face 仓库源 | 显存/内存预估 |
| :--- | :--- | :--- | :--- | :--- |
| **Diffusion 主模型 (默认首选)** | `qwen-image-2.1-UC-Q4_K_M.gguf`<br>*(或 `qwen-image-2.1-Q4_K_M.gguf`，高精度可选 `Q8_0`)* | `models/unet/` | [`unsloth/Qwen-Image-2.1-GGUF`](https://huggingface.co/unsloth/Qwen-Image-2.1-GGUF) | ~4.3GB (Q4) / ~8.5GB (Q8) |
| **文本/视觉编码器** | `Qwen3-VL-8B-Instruct-Q4_K_M.gguf`<br>*(极轻量可选 `Qwen3-VL-8B-Instruct-Q3_K_M.gguf`)* | `models/clip/` | [`unsloth/Qwen3-VL-8B-Instruct-GGUF`](https://huggingface.co/unsloth/Qwen3-VL-8B-Instruct-GGUF) | ~5.2GB (Q4) / ~3.8GB (Q3) |
| **专用 VAE 解码器** | `qwen_image_2.1_vae_bf16.safetensors` | `models/vae/` | [`Comfy-Org/Qwen-Image-2.1`](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) | ~335MB |

### 一键下载命令 (终端直接执行)

Mac 系统可直接使用 `hf` (Hugging Face 官方 CLI) 快速并行下载至对应目录：

```bash
# 1.1 下载 Qwen-Image-2.1 GGUF 主模型 - 默认首选轻量级 Q4_K_M (~4.3GB，速度快且画质几乎无损)
hf download unsloth/Qwen-Image-2.1-GGUF qwen-image-2.1-UC-Q4_K_M.gguf --local-dir /Users/frank/ComfyUI/models/unet

# 1.2 下载 Qwen-Image-2.1 GGUF 主模型 - 高精度 Q8_0 (~8.5GB，适合追求极限浮点精度)
hf download unsloth/Qwen-Image-2.1-GGUF qwen-image-2.1-Q8_0.gguf --local-dir /Users/frank/ComfyUI/models/unet

# 2. 下载 Qwen3-VL 编码器 GGUF (存入 models/clip)
hf download unsloth/Qwen3-VL-8B-Instruct-GGUF Qwen3-VL-8B-Instruct-Q4_K_M.gguf --local-dir /Users/frank/ComfyUI/models/clip

# 2.1 兼容性别名软链接 (确保不同工作流命名规范兼容)
ln -sf /Users/frank/ComfyUI/models/clip/Qwen3-VL-8B-Instruct-Q4_K_M.gguf /Users/frank/ComfyUI/models/clip/Qwen3VL-8B-Instruct-Q4_K_M.gguf

# 3. 下载 Qwen-Image-2.1 专用 16 通道 VAE (存入 models/vae)
hf download Comfy-Org/Qwen-Image-2.1 vae/qwen_image_2.1_vae_bf16.safetensors --local-dir /tmp/qwen_vae && \
mv /tmp/qwen_vae/vae/qwen_image_2.1_vae_bf16.safetensors /Users/frank/ComfyUI/models/vae/
```

### 💡 核心答疑：LM Studio 中已下载 Qwen3-VL-8B，能否直接复用？

**答：提示词扩写阶段可以直接用；但 ComfyUI 生图阶段不能直接复用 LM Studio 默认下载的 MLX 分片。**

#### 1. 角色分工与底层机制差异
- **提示词扩写（LLM 生成阶段）**：作为独立 HTTP 接口服务运行。本地 LM Studio 中只要已挂载 `qwen3-vl-8b`（无论 MLX 还是 GGUF 格式），本项目的测试脚本与自定义节点即可直接通过 API 调度进行智能扩写，**无需重复下载**。
- **生图特征提取（ComfyUI 阶段）**：ComfyUI 的 `CLIPLoaderGGUF` 需要将模型权重直接载入计算图，以提取 Cross-Attention 隐层特征向量（Conditioning）。由于 LM Studio 在 Apple Silicon 上默认下载的常为 **MLX 多分片 safetensors 格式**（目录内包含 `model-00001-of-00002.safetensors` 与分片索引等），ComfyUI 无法直接解析该分片结构，必须使用**单一 GGUF 量化文件**。

#### 2. 磁盘空间极致优化方案（统一由 LM Studio 下载 GGUF + 软链映射，立省 ~5.5GB）
LM Studio（基于 llama.cpp 后端）原生支持 GGUF 格式。推荐直接在 LM Studio 中下载 GGUF 变体，再通过**软链接（Symlink）**共享给 ComfyUI，整机仅保留一份约 5.2GB 文件：

##### 步骤 1：在 LM Studio 中获取 GGUF 变体
* **GUI 界面操作**：打开 LM Studio 搜索 `qwen/qwen3-vl-8b`，在版本/量化选项（Variants）下拉列表中选择 **GGUF** 架构（推荐 `Q4_K_M` 量化）点击下载；
* **CLI 命令行操作**（任选其一）：
  ```bash
  ~/.lmstudio/bin/lms get qwen/qwen3-vl-8b --gguf
  ```

##### 步骤 2：建立软链接至 ComfyUI clip 目录
LM Studio 下载完成后，在终端执行以下软链命令，ComfyUI 即可立刻识别并加载：

```bash
# 1. 映射 LM Studio 下载的 GGUF 到 ComfyUI models/clip 目录
ln -sf /Users/Shared/LLM_Models/lmstudio-community/Qwen3-VL-8B-Instruct-GGUF/Qwen3-VL-8B-Instruct-Q4_K_M.gguf /Users/frank/ComfyUI/models/clip/Qwen3-VL-8B-Instruct-Q4_K_M.gguf

# 2. 创建兼容别名软链接（兼容不同工作流引用命名）
ln -sf /Users/frank/ComfyUI/models/clip/Qwen3-VL-8B-Instruct-Q4_K_M.gguf /Users/frank/ComfyUI/models/clip/Qwen3VL-8B-Instruct-Q4_K_M.gguf
```

##### 步骤 3：双向复用与旧文件清理
1. **ComfyUI 端**：直接作为 `clip_name` 文本编码器载入生图；
2. **LM Studio 端**：直接加载该 GGUF 变体模型并开启本地 Server；
3. **安全清理**：若硬盘空间紧张，可在 LM Studio 中删除原先的 `Qwen3-VL-8B-Instruct-MLX-4bit` 目录，全机只保留一份 ~5.2GB 的 GGUF 文件。

> ⚠️ **常见报错说明**：
> 如果在生图时终端打印 `ComfyUI 节点错误 (缺少模型文件或缺少自定义节点): clip_name / unet_name / vae_name ... Value not in list`，即表明上述对应模型文件尚未下载到位，下载对应文件并刷新 ComfyUI 即可解决。

### 资源开销评估与性能优化指南 (显著降低显存/内存峰值与提升生图速度)

运行整套 Qwen-Image-2.1 系统时，涉及**提示词扩写大模型**与**ComfyUI 生图模型**两部分。为充分发挥 Apple Silicon 统一内存架构优势并杜绝掉速，系统支持全链路性能与资源优化：

#### 1. 提示词扩写大模型 (LM Studio 侧)：默认首选 `qwen/qwen3-vl-8b`
- **核心优势（黄金首选 ⭐️）**：Qwen-Image-2.1 的 Cross-Attention 文本编码器正是基于 `Qwen3-VL-8B` 预训练。使用同源多模态大模型扩写，生成的景深虚化、材质反射、镜头焦段等词汇分布与 DiT 神经网络的先验分布**完全对齐**，画质与意图表达最丰富。
- **极速响应**：本地实测单次扩写响应仅需 **2.7 秒**，无思维链（Reasoning）冗余。
- **零额外磁盘负担**：LM Studio 挂载后通过软链接直接共享给 ComfyUI `models/clip/`，全机只保留一份 ~5.2GB 文件，实现双向复用。
- **低显存设备备选**：对于 16GB / 24GB 轻薄设备，若同时运行多个应用显存紧张，可按需降级选用 `Qwen2.5-3B-Instruct`（~2.0GB）或 `Qwen2.5-1.5B-Instruct`（~1.0GB），亦可使用内置启发式规则引擎（0GB 显存，0 毫秒）。

#### 2. Diffusion 骨干模型 (DiT - Unet 侧)：默认首选 `qwen-image-2.1-UC-Q4_K_M.gguf`
- **核心定位**：Qwen-Image-2.1 基础 DiT 参数规模为 7B。
- **量化优势**：默认采用 `qwen-image-2.1-UC-Q4_K_M.gguf`（~4.3GB）。单流 DiT 对 4-bit 量化鲁棒性极高，画质几乎无损，相比 `Q8_0`（~8.5GB）节约近 40% 的内存带宽与 MPS 动态反量化开销，出图速度显著提升。

#### 3. 文本/视觉编码器 (CLIP 侧)：架构锁定但可降量化
- **架构约束**：Qwen-Image-2.1 的 Cross-Attention 交叉注意力层在预训练时深度对齐 `Qwen3-VL-8B` 的 4096 维隐藏层特征，**不可替换为其他尺寸或类型的 CLIP 编码器**（如 CLIP-L、T5 或 Qwen-3B）。
- **量化规格**：推荐使用 `Qwen3-VL-8B-Instruct-Q4_K_M.gguf`（~5.2GB），显存极端紧张设备可选 `Q3_K_M`（~3.8GB）。

#### 4. 分级配置与资源占用对照表

| 配置档位 | 扩写大模型 (LM Studio) | DiT 主模型 (ComfyUI) | Text Encoder (ComfyUI) | 总显存/内存预估 | 推荐设备与场景 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **首选黄金档 ⭐️** | **`qwen/qwen3-vl-8b` (~5.2GB)** | **`qwen-image-2.1-UC-Q4_K_M` (~4.3GB)** | **Qwen3-VL-8B Q4 (~5.2GB)** | **~14GB** | **32GB+ / 64GB / 128GB Mac 首选，原厂同源对齐，实测 2.7s 极速扩写，画质无损且出图快** |
| **顶配超精度档** | `qwen/qwen3-vl-8b` (~5.2GB) | Qwen-Image-2.1 Q8 (~8.5GB) | Qwen3-VL-8B Q4 (~5.2GB) | **~19GB** | 64GB/128GB Mac，追求极限浮点精度与复杂叙事 |
| **16G 显存降级档** | `Qwen2.5-3B` (~2.0GB) 或规则 | `qwen-image-2.1-UC-Q4_K_M` (~4.3GB) | Qwen3-VL-8B Q4 (~5.2GB) | **~11GB** | 16GB/24GB 轻薄设备，防止同时加载爆显存 |

#### 5. 出图性能第一性原理剖析与 1 分钟生图调优 (实测对比)

在 Apple Silicon (MPS 后端) 运行 7B 级 DiT 模型时，生图耗时受三大因素共同支配：
1. **CFG 双前向 vs 单前向开销**：当 `cfg > 1.0` 且输入了负向提示词时，每个采样步需分别执行一次正向和一次负向的 7B DiT 前向传播。18 步需执行 **36 次完整前向**；而将 `cfg` 设为 `1.0`（Flow-Matching 模型的原生单前向模式）时，ComfyUI 自动剪枝负向分支，前向次数直接减半（仅需 18 次），**单步耗时直接腰斩**。
2. **MPS 动态反量化开销**：ComfyUI-GGUF 在 MPS 每次前向计算中动态解包 Q4_K_M 权重为 FP16，32 层 DiT 共有 224 个主要线性层，单次前向需消耗 ~6.7 秒。
3. **Token 序列平方复杂度 ($O(N^2)$)**：Qwen-Image-2.1 下采样倍率为 16x。1024×1024 包含 4096 个图像 token；而适度调整为 **896×896** 时，Token 降至 3136 个（**注意力计算量剧减 41.4%**），画质肉眼几乎无区别。

| 调优策略 | 分辨率 | 步数 | CFG | 实测单步耗时 | 总生图耗时 | 提速比与画质评价 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **初始基准** | 1024×1024 | 18 步 | 4.0 (双前向) | 13.45 秒/步 | **250.57s (4分10秒)** | 基准值，CFG 双前向反量化开销过大 |
| **单前向前向减半** | 1024×1024 | 18 步 | 1.0 (单前向) | 6.79 秒/步 | **~122s (~2分)** | **提速 2.0x**，完全无损，耗时直接减半 |
| **黄金平衡档 ⭐️** | **896×896** | **14 步** | **1.0 (单前向)** | **5.21 秒/步** | **80.18s (1分20秒)** | **提速 3.12x**，微观机械结构与光影依然顶级 |
| **极速草稿档 🚀** | **768×768** | **14 步** | **1.0 (单前向)** | **4.25 秒/步** | **~59s (突破1分钟大关)** | **提速 4.25x**，创意探索与极速原型首选 |

#### 6. 快速操作指引
1. **下载 Q4_K_M 主模型**：
   ```bash
   hf download unsloth/Qwen-Image-2.1-GGUF qwen-image-2.1-UC-Q4_K_M.gguf --local-dir /Users/frank/ComfyUI/models/unet
   ```
2. **生图测试直接执行**（默认选用 16 步 + CFG 1.0 极速单前向模式）：
   ```bash
   # 黄金平衡档 (约 1分20秒，强烈推荐)
   python qwen_image21_test.py --desc "雨夜小巷里的机甲猫" --size 896x896 --steps 14

   # 1 分钟极速出图草稿档 (约 59 秒)
   python qwen_image21_test.py --desc "雨夜小巷里的机甲猫" --size 768x768 --steps 14

   # 默认测试 (1024x1024 + 16 步)
   python qwen_image21_test.py --desc "雨夜小巷里的机甲猫"
   ```
3. **工作流默认集成**：API 模板 `workflows/qwen_image_2.1_api.json` 及画布工作流均已默认配置为 `qwen-image-2.1-UC-Q4_K_M.gguf`，采样器默认配置为 `Steps: 16, CFG: 1.0`。

---

## 4. 本地 LM Studio 提示词扩写引擎

本系统能够将用户的一句极简描述自动扩充为影视级、高细节的结构化英文 Prompt。

### 推荐大模型选型
* **`qwen/qwen3-vl-8b` (极力推荐，原厂同源首选 ⭐️)**：与 Qwen-Image-2.1 同源的多模态文本/视觉理解大模型，词汇与构图先验契合度最高，实测本地单次扩写仅需约 **2.7 秒**，无思维链冗余，且与 ComfyUI 共用一份 GGUF 软链。
* **`qwen/qwen2.5-3b-instruct` / `1.5b` (低显存备选)**：占用显存仅约 1~2GB，专为 16GB 设备显存紧张时降级备用。
* **`qwen3.8-27b-mlx` (复杂叙事)**：27B 强语义大模型，仅建议拥有 64GB+ 统一内存设备运行极其复杂的多主体叙事画面时使用。

### 运行机制
1. 脚本默认请求本地运行在 `1234` 端口的 LM Studio（`http://127.0.0.1:1234/v1`）。
2. **Qwen3-VL 原生智能优先匹配**：引擎会自动读取 LM Studio 已挂载模型，并最高优先级挑选 `qwen3-vl` 同源大模型，用户亦可通过 `--llm-model` 手动指定。
3. 内置 System Prompt 会指导 LLM 补充**主体微观细节、光影体积感、空间构图与镜头焦段**。
4. **自动降级保护**：当 LM Studio 离线或超时，系统自动启用内置的高品质启发式规则库扩写，保证工作流不中断。

---

## 5. 命令行端到端测试 (`qwen_image21_test.py`)

您无需打开浏览器，在终端一条命令即可完成从扩写、组装参数、提交 ComfyUI 到拉取产物全流程：

### 基础测试命令

```bash
# 1. 默认测试（自动调用 Qwen3-VL-8B 同源极速扩写 + Q4_K_M 快速生图，16 步，CFG 1.0）
python qwen_image21_test.py --desc "雨夜小巷里的机甲猫"

# 2. 黄金平衡档（896x896，14 步，约 1 分 20 秒出图，强烈推荐）
python qwen_image21_test.py --desc "雨夜小巷里的机甲猫" --size 896x896 --steps 14

# 3. 极速冲刺档（768x768，14 步，约 59 秒出图）
python qwen_image21_test.py --desc "赛博朋克飞行汽车" --size 768x768 --steps 14

# 4. 指定长宽比与艺术风格
python qwen_image21_test.py --desc "少女华丽晚礼服半身像" --style photorealistic --aspect 3:4

# 5. Dry-Run 模式（仅执行扩写与参数组装校验，无需 ComfyUI 运行）
python qwen_image21_test.py --desc "赛博朋克飞行汽车" --dry-run
```

### 参数一览表
- `--desc`: 用户输入的极简短句。
- `--style`: 风格预设（`cinematic`, `photorealistic`, `anime`, `cyberpunk`, `general`）。
- `--aspect`: 显式指定比例（`1:1`, `16:9`, `9:16`, `4:3`, `3:4`）。
- `--size`: 显式覆盖分辨率（如 `896x896`, `1024x1024`, `768x768`）。
- `--steps`: 迭代步数，默认 16（Flow-Matching 推荐 14-20 步）。
- `--cfg`: 引导系数，默认 1.0（单前向模式，耗时直接减半；>1.0 启用双前向对比引导）。
- `--seed`: 随机种子（默认 `-1` 自动随机生成）。
- `--comfy-host`: ComfyUI 地址（默认 `127.0.0.1:8188`）。
- `--lmstudio-host`: LM Studio 地址（默认 `127.0.0.1:1234`）。
- `--llm-model`: 指定扩写用 LLM 模型名称（默认自动优先选用已挂载的 Qwen 系列）。
- `--dry-run`: 调试模式，生成组装完成的 API JSON 并退出。

---

## 6. ComfyUI Web 画布工作流与自定义节点

### 方式一：直接导入画布工作流
1. 打开 ComfyUI 界面（Comfy Desktop 默认为 `http://127.0.0.1:8188`，源码版为 `http://127.0.0.1:8188`）；
2. 将 `workflows/qwen_image_2.1_t2i_canvas.json` 文件直接拖拽入浏览器画布中；
3. 检查模型加载节点对应的文件名是否匹配本地已下载的模型；
4. 点击 **Queue Prompt** 即可生成。

### 方式二：在画布中启用 LM Studio 扩写节点
若想在 Web 界面中直接输入极简中文并实时扩写生图：
1. 将 `custom_nodes/ComfyUI-LMStudio-Prompt` 目录复制或软链接至 ComfyUI 的插件目录：
   ```bash
   ln -s /Users/frank/wk/github/ai/ComfyUI/qwen_image_2.1/custom_nodes/ComfyUI-LMStudio-Prompt ~/ComfyUI/custom_nodes/
   ```
2. 重启 ComfyUI 服务；
3. 在画布中右键添加节点：`QwenImage/Prompt -> LM Studio Prompt Expander (Qwen-Image)`；
4. 将该节点的 `positive_prompt` 输出引脚连接至 `CLIPTextEncode` 的文本输入，即可在画布中实时享受大模型扩写加持！

---

## 7. 运行单元测试套件

本项目包含完整的回归测试保障：

```bash
# 执行全部单元测试
pytest ComfyUI/qwen_image_2.1/tests/ -v
```
