# Flux.1 ComfyUI Apple Silicon 部署指南 (硬件加速优化)

本指南基于 [Flux ComfyUI on Apple Silicon with hardware acceleration (2024)](https://medium.com/@tchpnk/flux-comfyui-on-apple-silicon-with-hardware-acceleration-2024-4d44ed437179) 编写，旨在为 Mac 用户提供在 ComfyUI 中运行 Flux.1 模型的最优配置方案。

---

## 1. 环境准备：PyTorch Nightly

为了获得最佳的 MPS (Metal Performance Shaders) 支持，建议使用最新的 PyTorch Nightly 版本，而不是传统的稳定版。这对于 Flux 使用的 Diffusion Transformer (DiT) 架构至关重要。

### 更新 PyTorch
在 ComfyUI 的虚拟环境中运行：
```bash
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
```
*注：虽然链接包含 cpu，但 macOS 上会自动包含 MPS 加速支持。*

---

## 2. 模型下载与存放路径 (推荐 GGUF 方案)

对于 Apple Silicon，**GGUF 格式**比 FP8 具有更好的兼容性和响应速度。请将下载的模型按以下路径存放：

| 模型类型 | 推荐文件名 | 存放路径 (ComfyUI 根目录下) | 说明 |
| :--- | :--- | :--- | :--- |
| **主模型 (UNet)** | `flux1-dev-Q4_1.gguf` | `models/unet/` | 推荐 (16-32GB RAM)，兼顾速度与画质 |
| **主模型 (UNet)** | `flux1-dev-Q8.gguf` | `models/unet/` | 高质量 (32GB+ RAM) |
| **文本编码器 (Clip)** | `clip_l.safetensors` | `models/clip/` | 官方标准编码器 |
| **文本编码器 (T5)** | `t5xxl_fp16.safetensors` | `models/clip/` | 高精度，占用内存较大 |
| **文本编码器 (T5)** | `t5xxl_fp8_e4m3fn.safetensors`| `models/clip/` | **推荐**，更轻量，适合 Mac |
| **VAE** | `ae.safetensors` | `models/vae/` | Flux 专用 VAE，必下 |

---

---

## 3. 必备自定义节点

必须安装以下节点以支持 GGUF 模型和优化采样：

1. **[ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF)**: 用于加载 GGUF 格式的 Flux 模型。
2. **[XLabs-AI/x-flux-comfyui](https://github.com/XLabs-AI/x-flux-comfyui)** (可选): 如果需要使用 Flux ControlNet 或 IP-Adapter。
3. **[ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)**: 用于方便地安装上述节点。

---

## 4. 工作流配置策略

### 4.1 核心参数设置
- **Sampler (采样器)**: `euler`
- **Scheduler (调度器)**: `simple` 或 `beta`
- **Steps (步数)**: 
  - **20-25 步**: 适合大多数场景，能生成干净的画面。
  - **40+ 步**: 仅在需要极高背景复杂度时使用，对主体提升不明显。
- **Guidance Scale (指令引导)**:
  - 使用 GGUF 模型时建议设置在 **2.0 - 3.5** 之间。
  - 设置过高可能会导致画面出现伪影。

### 4.2 节点连接注意
- 使用 **Unet Loader (GGUF)** 节点加载 `.gguf` 文件。
- 确保 VAE 选择正确的 `ae.safetensors`。

---

## 5. 常见问题与优化

- **显存缓解**: 如果遇到 `Out of Memory`，启动 ComfyUI 时添加参数 `--lowvram` 或 `--novram`。
- **第一次运行慢**: 首次加载模型时 MPS 会进行着色器编译，属于正常现象。
- **预览图像**: 建议将 `Preview Method` 设置为 `TAESD` (需下载对应的 `flux_vae_approx` 权重) 以获得更流畅的生成体验。

---
> **参考资料**: [Medium 原文](https://medium.com/@tchpnk/flux-comfyui-on-apple-silicon-with-hardware-acceleration-2024-4d44ed437179) 
