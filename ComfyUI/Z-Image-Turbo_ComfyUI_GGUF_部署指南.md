# Z-Image Turbo GGUF ComfyUI 部署指南 (Mac Studio 优化)

Z-Image Turbo 是由阿里巴巴通义实验室 (Tongyi-MAI) 开发的 60 亿参数 DiT (Diffusion Transformer) 文本生成图像模型。它专为极速生成优化，通常只需 8 步即可产出高质量、摄影级效果的图片。

本指南针对 Apple Silicon (M1/M2/M3 Max/Ultra) 环境，推荐使用 GGUF 量化方案以平衡性能与显存占用。

---

## 1. 资源准备与配置分档 (高/低配选择)

根据您的 Mac Studio 硬件配置（如 M2 Max 64G vs M2 Ultra 128G），您可以选择不同的量化档位以达到速度与画质的最优平衡。

### 配置分档表

| 档位 | 适用硬件 | 推荐模型组合 (GGUF) | 启动参数建议 |
| :--- | :--- | :--- | :--- |
| **极致性能 (低配/省显存)** | Max 系列 (32G/64G RAM) | 主模型: `Q4_K_M`<br>编码器: `Q4_K_M` | `--lowvram` |
| **均衡模式 (推荐)** | Max/Ultra 系列 (64G+ RAM) | 主模型: `Q6_K`<br>编码器: `Q6_K` 或 `Q8_0` | `--normalvram` |
| **大师品质 (高配/追求细节)** | Ultra 系列 (128G+ RAM) | 主模型: `Q8_0` 或 `BF16`<br>编码器: `BF16` | `--normalvram` |

> [!TIP]
> **资源获取**: 推荐访问 [Jayn7/Z-Image-Turbo-GGUF](https://huggingface.co/Jayn7/Z-Image-Turbo-GGUF) 页面，其中的 `Files and versions` 提供了从 Q3 到 Q8 的全系列下载。

---

## 2. 文件存放路径 (ComfyUI/)

在开始之前，请确保通过 **ComfyUI Manager** 安装了以下插件：

1.  **[ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF)**: 必须安装。它提供了加载 `.gguf` 格式 Diffusion 模型和 Text Encoder 的核心能力。
2.  **[ComfyUI-Z-Image](https://github.com/Gleetholiday/ComfyUI-Z-Image)** (可选): 如果需要更原生的 Prompt 处理（支持 Chat 模版），可以安装此插件，但标准 GGUF 流程通常也足够高效。

---

## 3. 工作流配置详解

### 3.1 核心节点设置
> [!CAUTION]
> **文本编码器注意**: Z-Image Turbo (Lumina) **不兼容** T5-XXL (Flux/Wan 版)。
> 它必须使用 **Qwen-based** 编码器（维度 2560）。

- **编码器加载**: 使用 `CLIPLoaderGGUF` 节点加载对应的 Qwen 编码器。
    - **Type 设置**: 请将其设置为 **`qwen_image`**。
- **VAE 加载**: 选择标准的 `ae.safetensors` (Flux VAE)。
    - *注：若本地缺失，请从 [HuggingFace](https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors) 下载并放入 `models/vae`。*

### 3.2 采样关键参数 (**非常重要**)
Z-Image Turbo 属于蒸馏加速模型，其采样参数与传统模型差异较大：

- **Steps (步数)**: **8 - 12 步**。超过 20 步可能导致画面质量反而下降。
- **CFG (配置尺度)**: **必须设置为 1.0**。超过 1.0 会导致画面过度饱和或伪影。
- **Sampler (采样器)**: `euler`
- **Scheduler (调度器)**: `simple` 或 `beta`
- **Resolution (分辨率)**: 建议从 **1024x1024** 开始，模型对该尺寸有原生优化。

---

## 4. Mac Studio (Apple Silicon) 优化建议

### 4.1 启动参数优化
在 Mac 上运行大型 DiT 模型时，显存管理至关重要。建议启动 ComfyUI 时使用：
```bash
python main.py --lowvram
```
*如果 RAM 充足 (64GB+)，可以使用 `--normalvram` 获取更快切换速度。*

### 4.2 设置预览方法
在 ComfyUI 设置中，将 `Preview Method` 设置为 `TAESD`。这可以让你在 8 步采年的过程中实时看到画面变化，由于生成极快，这种反馈感非常出色。

### 4.3 显存监测
建议配合 `Activity Monitor` (活动监视器) 的 "Window > GPU History" 查看。如果在加载过程中出现严重的 Swap 交换，建议降低 Text Encoder 的量化精度（例如使用 Q4 版本）。

---

## 5. 常见问题 (FAQ)

- **Q: 报错 Required input is missing: negative？**
  - A: 较新版本的采样器要求必须连接负向提示词节点。即使你不写内容，也需要连接一个空的 `CLIP Text Encode` 节点。目前工作流已默认补全。
- **Q: 报错 Value not in list: type？**
  - A: 插件更新后 `flux` 可能被改名为了 `flux2`。请在 `CLIPLoaderGGUF` 节点的 `type` 下拉菜单中选择正确的模型族。
- **Q: 是否支持 LoRA？**
  - A: 目前 Z-Image 的 LoRA 生态仍在发展中，建议关注 ComfyUI-Z-Image 插件的更新以获取兼容性支持。

---

## 6. 测试预设工作流 (分步验证)

为了方便排查问题，我们将双路工作流拆分为两个独立的文件，分别用于测试**文生图**和**图生图**。

### 6.1 文生图 (T2I) 测试
最基础的生成测试。如果此工作流报错，请检查 Unet/Clip 加载是否正常。
- **工作流下载**: [z-image-turbo-t2i.json](./z-image-turbo-t2i.json)

### 6.2 图生图 (I2I) 测试
在文生图正常的基础上测试。如果此工作流报错，请重点检查 VAE Encode 和图片加载。
- **工作流下载**: [z-image-turbo-i2i.json](./z-image-turbo-i2i.json)

> [!TIP]
> **双路合一版**: 如果你已经熟悉流程，可以使用 [z-image-turbo-dual-workflow.json](./z-image-turbo-dual-workflow.json) 在一个页面内切换测试。

### 6.3 节点配置清单

| 区域 | 关键设置项 / 节点 | 说明 |
| :--- | :--- | :--- |
| **Unet Loader (GGUF)** | `z_image_turbo_Q4_K_M.gguf` | 输出 MODEL 到 Sampler |
| **CLIPLoaderGGUF** | `t5xxl_Q4_K_M.gguf` | 输出 CLIP 到 Text Encode |
| **文生图 (T2I)** | `Empty Latent Image`<br>`KSampler` (Steps: 8, CFG: 1.0) | 标准 1024x1024 生成 |
| **图生图 (I2I)** | `Load Image` + `VAE Encode`<br>`KSampler` (Denoise: 0.6) | 保持原图结构进行 Turbo 风格化 |

---

## 7. 高级技巧

- **提示词建议**: 由于使用 T5XXL 编码器，模型对自然语言理解极佳。建议直接用短句描述场景。
- **显存回退**: 如果您的 Mac 只有 32G 内存，且在运行 I2I 时报错，请在启动时务必带上 `--lowvram`，并考虑将 Clip 模型降级为 `Q4_K` 版本。

> [!CAUTION]
> **请注意**: 点击生成前，请确保您的模型文件名（如 `z_image_turbo_q4_k_m.gguf`）与 Loader 节点中的值完全一致。


