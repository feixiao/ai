# Wan 2.2 ComfyUI Mac Studio 安装与测试指南

为了让用户更顺畅地在 Mac Studio 上跑通 Wan 2.2，本指南优先推荐直接使用社区已有的 GGUF 工作流，然后再介绍如何通过官方模板手动进行适配。

---

## 1. 环境准备

- **硬件建议**：Mac Studio (M1/M2/M3 Max 或 Ultra)，建议 64GB 以上统一内存。
- **系统要求**：macOS 14.0+ (建议使用最新系统以获得最佳 Metal 支持)。
- **软件基础**：
  - 系统需已安装 Python（建议 3.10+）。
  - 建议已安装 Homebrew（用于快速安装依赖）。

## 2. 安装 ComfyUI

### 方法一：Homebrew 安装（推荐）
```bash
brew install comfyui
```

### 方法二：官网下载
- 访问 [ComfyUI 官方文档](https://docs.comfy.org/installation/desktop/macos#comfyui-desktop-macos-download) 下载 Mac 安装包，并按照引导完成安装。

## 3. 基础配置 (针对 Mac)

由于 Mac 使用统一内存架构（Unified Memory），模型运行时会占用大量系统内存。
- **内存限制**：Wan 2.2 14B 模型在 FP16 精度下需要约 30GB 显存，加上 VAE 运算，极易触碰 Mac 的显存分配阈值导致系统重启或 ComfyUI 卡死。
- **推荐方案**：**务必使用 GGUF 量化版本**。

### 3.1 模型准备与角色说明

在 Mac Studio 上运行 Wan 2.2，模型选择对性能至关重要。你通常可以从工作流发布页面获取下载地址，以下是各模型在文档结构中的存放要求及其作用：

```bash
# 确保基础目录已就绪
mkdir -p ~/ComfyUI/models/{clip,vae,unet,loras}
```

#### 1. 文本编码器 (T5 Encoder)
- **作用**：解析提示词（Prompt）。它是生成过程的基础，决定了模型对指令的理解程度。
- **Mac 建议**：务必使用 **GGUF 版**（如 `umt5-xxl`）。相比 FP16 原版，GGUF 版能节省大量显存，让 14B 模型在 32GB/64GB 内存的 Mac 上也能跑通。
- **存放路径**：`~/ComfyUI/models/clip/`

#### 2. VAE 模型
- **作用**：图像/视频解码器。负责将生成的潜空间数据转换为人眼可见的像素画面。
- **核心提示**：使用 Wan 2.2 专用的 VAE 才能获得正确的色彩和清晰度。
- **存放路径**：`~/ComfyUI/models/vae/`

#### 3. 主推理模型 (UNET / GGUF)
- **作用**：视频生成的核心“大脑”。
- **Mac 建议**：**必须使用 GGUF 格式**。Apple Silicon 的统一内存架构对量化模型非常友好，Q4 或 Q5 量化能在保持极高画质的同时，避免系统因显存过载而崩溃。
- **存放路径**：`~/ComfyUI/models/unet/`

#### 4. Lightning LoRA (推荐)
- **作用**：极速插件。能将推理步数从 50 步压缩到 4-8 步，生成耗时缩短 10 倍以上。
- **存放路径**：`~/ComfyUI/models/loras/`

### 3.2 配置文件优化 (ComfyUI Desktop 版)

为了确保 ComfyUI 在 Mac Studio 上以最佳性能启动，建议预先配置 `config.json` 文件以启用 MPS 加速并禁用不兼容的优化。

```bash
cat > ~/Library/Application\ Support/ComfyUI/config.json << 'EOF'
{
    "installState": "installed",
    "detectedGpu": "mps",
    "basePath": "/Users/frank/ComfyUI",
    "versionConsentedMetrics": "0.8.28",
    "selectedDevice": "mps",
    "args": ["--force-fp32-unet", "--force-fp32-vae", "--use-split-cross-attention", "--disable-torch-compile"]
}
EOF
```


## 4. 快速跑通：直接使用社区 GGUF 工作流 (推荐)

这是针对 Mac 用户最省时、成功率最高的方式。社区工作流通常已预配置好 Tiled VAE 和 GGUF 节点，减少了手动连线的错误。

### 4.1 寻找资源
- **Civitai (C站)**：访问 [Civitai](https://civitai.com/search/models?sortBy=models_v9&query=Wan%202.2%20%28GGUF%29) 搜索 "Wan 2.2 GGUF Workflow"。
- **GitHub**：搜索 `ComfyUI-Wan2.2-workflow`，寻找标注有 "Low VRAM" 或 "Mac Optimized" 的项目。

### 4.2 导入与使用
1. 下载 `.json` 工作流文件。
2. 将 JSON 文件直接拖入 ComfyUI 界面。
3. 如果加载后出现红色警告（提示缺少节点），请使用 `ComfyUI-Manager` 自动安装缺失节点。

---

## 5. 进阶：使用 ComfyUI 官方内置模板

如果你希望使用官方标准模板进行深度定制，可以尝试加载内置模板，但需注意在 Mac 上直接运行 FP16 版通常会失败。

### 5.1 加载模板
1. 在右侧菜单点击 **Templates -> Video**。
2. 选择 **Wan 2.2 14B Image to Video**。

### 5.2 为什么直接运行会失败？
- **内存/FP16 限制**：Mac 的 MPS (Metal Performance Shaders) 在处理 14B 模型的 FP16 精度时，显存压倒性过载。
- **缺乏 Tiled VAE**：官方模板默认的 VAE 解码器极其消耗显存，需要适配。

---

## 6. 手动适配指南：将官方模板改为 GGUF 版

### 第一步：安装 GGUF 必要节点
1. 进入 `custom_nodes` 目录：
   ```bash
   cd ~/ComfyUI/custom_nodes
   git clone https://github.com/city96/ComfyUI-GGUF
   ```
2. 重启 ComfyUI。

### 第二步：下载 GGUF 格式模型
1. 访问 [HuggingFace (QuantStack)](https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF/tree/main) 下载模型。
2. **推荐规格**：`Q5_K_M` (画质与性能的最佳平衡) 或 `Q4_K_M` (极速测试)。
3. 将下载的 `.gguf` 文件放入 `ComfyUI/models/unet/` 目录。

### 第三步：节点替换与连线逻辑
1. **替换加载器**：
   - 在官方模板中，删除原本的 `UNETLoader` 或 `Load Diffusion Model` 节点。
   - 右键添加 `Unet Loader (GGUF)` 节点。
   - 在 `unet_name` 中选择刚下载的 GGUF 模型。
2. **连接 MODEL**：
   - 将 `Unet Loader (GGUF)` 的 `MODEL` 输出连接到原本 `UNETLoader` 接出的地方（通常是 `KSampler` 或 `LoraLoader`）。
3. **适配 VAE (关键)**：
   - 右键添加 `VAE Decode (Tiled)`。
   - 将 `KSampler` 的 `samples` 和官方 VAE 模型的 `vae` 分别接入。
   - 这样可以分块解码图像，避免高分辨率下的内存溢出。

---

## 7. 生成与性能参考 (Mac Studio)

| 参数配置 (M1/M2 Ultra) | 分辨率 | 帧数 | 耗时 |
| :--- | :--- | :--- | :--- |
| **测试级** | 320x320 | 8 帧 | 5 - 15 分钟 |
| **标准级** | 480x480 | 8 帧 | 15 - 30 分钟 |
| **高清级** | 640x640 | 8 帧 | 30 分钟+ |

> [!TIP]
> **显存监控**：生成过程中建议打开“活动监视器”观察 GPU 内存。若峰值超过 40GB，请增加统一内存或降低分辨率。

---

## 8. 故障排查与 Mac 专项优化

### 8.1 故障处理
- **黒屏/像素堆积**：这是显存不足的典型表现，请优先调低分辨率到 320x320。
- **ComfyUI 自动闪退**：尝试在启动 ComfyUI 时添加参数 `--highvram` 或 `--mps`（针对 Mac 的优化启动模式）。
- **KSampler 卡死**：在 ComfyUI 设置中开启 `Run VAE on CPU` 以释放 GPU 压力。

### 8.2 特别配置建议
- **推理精度**：将 Inference 设为 `fp32`。虽然 Mac 支持混合精度，但 `fp32` 在一些 Metal 实现中稳定性更高。
- **VAE 设置**：务必使用 Tiled VAE 节点，避免长视频生成时的 OOM。


### 8.3 FFMPEG
ln -s /opt/homebrew/bin/ffmpeg /Users/$(whoami)/ComfyUI/.venv/bin/ffmpeg
---

## 9. 参考资料

- [ComfyUI Official Video Templates](https://github.com/Comfy-Org/workflow_templates)
- [Civitai Wan 2.2 GGUF Workflows](https://civitai.com/search/models?sortBy=models_v9&query=Wan%202.2%20%28GGUF%29)
- [ComfyUI-GGUF Plugin Repo](https://github.com/city96/ComfyUI-GGUF)
- [HuggingFace GGUF Models](https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF)
