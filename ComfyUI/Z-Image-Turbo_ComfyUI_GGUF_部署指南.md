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
| **图生图 (I2I)** | `Load Image` + `VAEEncodeTiled` | 建议开启 Tiled 模式以避免 Mac 显存爆满 |

---

## 7. 进阶篇：Z-Image Power Nodes (深度掌控)

对于追求极致效果的用户，推荐安装 **[ComfyUI-ZImagePowerNodes](https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes)**。这是一套专门为 Z-Image 优化的增强节点，能够大幅提升生成效率与可控性。

### 7.1 安装与必备模型 (Mac 完全兼容)

该插件虽然在 GitHub 上较多提及 Windows，但经测试在 **Apple Silicon (M1/M2/M3)** 平台上运行完全稳定。

#### A. 安装步骤
- **Manager 安装 (推荐)**: 
    1. 点击 ComfyUI 界面右侧的 **Manager** -> **Custom Nodes Manager**。
    2. 搜索 `Z-Image Power Nodes`。
    3. 点击 **Install** 并根据提示点击 **Restart** 重启 ComfyUI。
- **手动安装 (命令行)**: 
    ```bash
    cd custom_nodes
    git clone https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes.git
    ```

#### B. 必备模型组合 (GGUF)
- **UNet**: `z_image_turbo-Q5_K_S.gguf` 或 `Q8_0` 版本。
- **Clip**: `Qwen3-4B-Q8_0.gguf` (目前对 Power Nodes 支持最佳)。

### 7.2 核心增强功能

#### A. 视觉风格引擎 (`⚡Style Prompt Encoder`)
内置 **100+ 预设风格**（电影、二次元、写实、赛博朋克等）。
- **优势**: 无需编写复杂的提示词描述风格，只需选择 Thumbnail 预览图，即可将极简提示词转化为高质量成品。
- **动态注入**: 使用 `Style String Injector` 可以将风格描述灵活嵌入现有的提示词模板。

#### B. 专业版采样器 (`⚡Z-Sampler Turbo`)
相比原生采样器，提供了更细致的微调参数：
- **Intensity (对比度调节)**:
    - 正值 (>0): 提高画面对比度与边缘清晰度，适合插画与原画。
    - 负值 (<0): 画面更柔和、具有“氛围感”，适合人像摄影。
- **Turbo Creativity (创意发散)**:
    - 通过潜空间微扰增加画面的随机性，解决 Z-Image Turbo 在相同 Seed 下构图过于固定的问题。
- **极致步数**: 此采样器在 **3 - 5 步** 即可产生具有参考价值的预览图。

#### C. 局部重绘增强 (`⚡VAE Encode for Soft Inpainting`)
专为 Z-Image 设计的 VAE 编码节点。它能更自然地处理 Mask 边缘，支持“软掩码”效果，使重绘区域与原图无缝融合。

---

## 8. 全能型旗舰工作流：Amazing Z-Image Workflow

如果你想跳过碎片的节点搭建，直接使用成熟的成品，推荐 **[Amazing Z-Image Workflow](https://github.com/martin-rizzo/AmazingZImageWorkflow)**。这是目前社区公认的最强 Z-Image 全能型工作流。

### 8.1 核心特色
- **内置精修 (Refiner)**: 自动进行二次采样，显著提升人像细节与背景自然度。
- **内置放大 (Upscaler)**: 支持 1.5 倍 - 2 倍的无损放大，解决 DiT 模型原生分辨率不足的问题。
- **场景化适配**: 提供针对 `Photo` (摄影)、`Comics` (漫画)、`Art` (艺术) 独立优化的专用版本。
- **快捷控制面板**: 预置了横竖屏、分辨率、步数（7 步/12 步）的逻辑开关，操作极简。

### 8.2 新增依赖安装
运行此工作流除了上述插件外，还必须安装：
- **[rgthree-comfy](https://github.com/rgthree/rgthree-comfy)**: 提供逻辑控制面板和布局管理能力。

### 8.3 下载链接 (GGUF 专版)
直接下载以下 `.json` 文件并拖入 ComfyUI：
- **[通用全能版-A](https://github.com/martin-rizzo/AmazingZImageWorkflow/blob/master/amazing-z-image-a_GGUF.json)**: 复盖 18+ 种常用风格。
- **[大师摄影版-P](https://github.com/martin-rizzo/AmazingZImageWorkflow/blob/master/amazing-z-photo_GGUF.json)**: 极致的真实感，由于 Mac 内存大，建议开启其中的 Refiner。
- **[致郁/唯美漫画版-C](https://github.com/martin-rizzo/AmazingZImageWorkflow/blob/master/amazing-z-comics_GGUF.json)**: 包含赛博朋克、像素画、二次元等。

---

## 9. 专项参考工作流 (分步验证版)

如果你希望从基础开始，或者仅需要特定的功能测试，可以使用我们整理的单路工作流：

- **文生图 (T2I) 测试**: [z-image-turbo-t2i.json](./z-image-turbo-t2i.json)
- **图生图 (I2I) 测试**: [z-image-turbo-i2i.json](./z-image-turbo-i2i.json)
- **局部重绘 (进阶版)**: [z-image-turbo__inpainting.json](https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes/blob/master/workflows/GGUF/z-image-turbo__inpainting.json)

---

## 10. Mac Studio (Apple Silicon) 专项优化

### 10.1 解决 MPSGraph INT_MAX 报错
在进行高分辨率图生图或使用 Amazing Workflow 的 Upscaler 时，Mac 的 Metal 后台可能会报错。
- **解决方案**: 确保工作流中使用的是 **`VAEEncodeTiled`**。在 Amazing 工作流中，请在相关的 VAE 节点开启 `tiled` 选项。

### 10.2 显存与启动建议
- **低显存模式**: 对于 32GB 内存机型，启动参数 `--lowvram` 是保障不闪退的前提。
- **预览优化**: 将预览模式设置为 `TAESD`。

---

## 11. 常见问题 (FAQ)

- **Q: 报错 Required input is missing: negative？**
  - A: 即使不写内容，也需要连接一个空的 `CLIP Text Encode` 节点。
- **Q: 是否支持 LoRA？**
  - A: 支持。Amazing Workflow 内置了 `Power Lora Loader`，可以同时加载多个 LoRA。建议将 LoRA 放入 `models/loras` 并在面板中开启。
- **Q: 为什么生成的图片是灰色的？**
  - A: 通常是 VAE 加载错误。请检查 `ae.safetensors` 是否正确连接，且 Loader 的路径指向正确。

---

## 12. 选型建议：我该使用哪一个？

针对 Mac Studio 用户，建议根据你的使用场景进行选择：

### 🏆 首选：[Amazing Z-Image Workflow](https://github.com/martin-rizzo/AmazingZImageWorkflow) (全能旗舰型)
**适用场景**: 正式创作、**自媒体封面/配图**、追求极致画质、高清大图。
- **自媒体优化专项建议**:
    - **视频封面/头图**: 使用 **Photo-P (摄影版)** 并开启 **Refiner**，配合 `Cinematic` 风格可产出具有影院质感的封面。
    - **内容配图**: 使用 **Comics-C (漫画版)** 并开启 **Upscaler**，可产出细腻的 2K/4K 级商业插画。
- **优点**: 内置 **Refiner (精修)** 和 **Upscaler (放大)**，能充分利用 Mac Studio 的大内存优势；支持一键切换风格和构图，极大提升出片效率。
- **要求**: 必须安装 `rgthree-comfy` 和 `Z-Image Power Nodes` 插件。

### 🥈 次选：[Power Nodes 官方示例](https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes/tree/master/workflows/GGUF) (轻量功能型)
**适用场景**: 局部重绘 (Inpainting)、功能调试、极速出草图。
- **优点**: 结构简单，加载速度极快；其中的 `Inpainting` 工作流是目前处理 Z-Image 局部修改的最优选。
- **要求**: 仅需安装 `Z-Image Power Nodes` 插件。

---
> [!TIP]
> **总结建议**: 日常生成图片请无脑选择 **Amazing Z-Image Photo-P (摄影版)** 并开启 Refiner。
