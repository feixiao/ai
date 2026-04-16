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
- **模型加载**: 使用 `Unet Loader (GGUF)` 节点加载 `z_image_turbo_q4_k_m.gguf`。
- **编码器加载**: 使用 `GGUF Clip Loader` 节点加载对应的文本编码器。
- **VAE 加载**: 选择标准的 `ae.safetensors` (Flux VAE)。

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

- **Q: 为什么生成的图片是全黑或全噪点？**
  - A: 检查 CFG 是否设置为 1.0。大于 1.0 的值通常是主要诱因。
- **Q: 模型加载非常慢？**
  - A: 首次在 MPS 上运行 DiT 模型时，系统会进行 Shader 编译。后续运行会恢复正常速度。
- **Q: 是否支持 LoRA？**
  - A: 目前 Z-Image 的 LoRA 生态仍在发展中，建议关注 ComfyUI-Z-Image 插件的更新以获取兼容性支持。

---
> **关联文档**:
> - [Flux.1 ComfyUI Mac 部署指南](file:///Users/frank/wk/github/ai/ComfyUI/FLUX_ComfyUI_Apple_Silicon_%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97.md)
> - [Wan2.2 安装测试指南](file:///Users/frank/wk/github/ai/ComfyUI/Wan2.2_ComfyUI_MacStudio_%E5%AE%89%E8%A3%85%E6%B5%8B%E8%AF%95%E6%8C%87%E5%8D%97.md)
