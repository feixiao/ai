# ComfyUI + Wan 2.2 图生视频（Image-to-Video）Mac Studio 安装与测试指南

## 1. 环境准备

- 推荐设备：Apple Silicon（M1/M2/M3/M4，建议 32GB+ 内存，64GB 更佳）
- 确保磁盘有 50GB 以上剩余空间（模型较大）
- 系统需已安装 Python（建议 3.10+）
- 建议 Homebrew 已安装（用于快速安装软件）

## 2. 安装 ComfyUI

### 方法一：Homebrew 安装（推荐）

```
brew install comfyui
```

### 方法二：官网下载

- 访问 [ComfyUI 官方文档](https://docs.comfy.org/installation/desktop/macos#comfyui-desktop-macos-download) 下载 Mac 安装包，按提示拖入应用程序即可。

### 启动

- 在“应用程序”中找到 ComfyUI，或用 Spotlight（⌘+空格）搜索 ComfyUI 启动。

## 3. 基础配置

- 默认存储路径一般无需更改，但请确保有足够空间存放模型。
- 推荐开启“自动更新”功能，便于获取新特性和修复。
- Apple Silicon 下，ComfyUI 会自动使用 Metal Performance Shaders (MPS) 加速。

## 4. 下载并配置 Wan 2.2 工作流

1. 在 ComfyUI 右侧菜单点击“Templates（模板）”→“Video”→“Wan 2.2 14 Image to Video”。
2. 这会加载官方的 Wan 2.2 图生视频工作流，`video_wan2_2_14B_i2v.json` 是官方仓库中对应的模板文件名，界面里一般只显示“Wan 2.2 14 Image to Video”。
3. 如果你想尝试其它 Wan 2.2 视频生成模式，还可以在同一模板库里选择：
   - `video_wan2_2_14B_i2v.json`：标准图像到视频（Image-to-Video）。
   - `03_video_wan2_2_14B_i2v_subgraphed.json`：同样的图像到视频流程，但封装成子图，可用于组合其它复杂流。
   - `video_wan2_2_14B_animate.json`：已有视频动画增强/迭代，用于对现有短视频做风格化处理。
   - `video_wan2_2_14B_flf2v.json`：起始/结束帧生成视频，适合“首尾帧插值”场景。
   - `video_wan2_2_14B_fun_camera.json`：有趣的相机运动效果，适合带运动镜头的画面生成。
4. 这些模板的模型路径和节点结构一般会自动填好，但如果出现缺少模型提示，可根据本指南第7节下载 GGUF 模型并手动加载。


## 5. 常见问题与解决

### 1. 缺少模型

- ComfyUI 会提示缺少模型，直接点击 Download 按钮自动下载。
- 有些模型需手动下载，见下文“新模型”部分。

### 2. OOM/内存溢出（PYTORCH_MPS_HIGH_WATERMARK_RATIO）

- 可参考[官方说明](https://substack.com/@papayabytes/note/c-149839263)。
- 建议初次测试将分辨率调低（如 320x320），减少帧数。

### 3. LoadImage 节点报错

- 需手动上传一张图片（如龙的图片，或任意你喜欢的图），在 Load Image 节点点击“choose file to upload”选择本地图片。

### 4. KSamplerAdvanced 报错

- 默认 Diffusion Model 不适配 Mac，需要更换为 GGUF 格式模型，见下文。

## 6. 安装 Unet Loader (GGUF) 节点

1. 打开终端，进入 ComfyUI 的 custom_nodes 目录：

   ```bash
   cd ~/Documents/ComfyUI/custom_nodes
   git clone https://github.com/city96/ComfyUI-GGUF
   ```

2. 重启 ComfyUI（Manager → Restart）。
3. 在 Node Library 搜索“gguf”，添加 bootleg→Unet Loader (GGUF) 节点，替换掉原有的 Diffusion Model 节点。

## 7. 下载新模型（GGUF 格式）
Wan 2.2 图生视频工作流需要两个 GGUF 模型：
### 下载方法

由于模型文件较大（约10GB+），建议使用终端命令下载，避免浏览器中断：

1. 打开终端，进入目标目录：
   ```bash
   cd ~/Documents/ComfyUI/models/unet/
   ```

2. 使用 curl 下载（Mac 自带）：
   ```bash
   # 14B
   curl -L -o Wan2.2-I2V-A14B-HighNoise-Q5_K_M.gguf "https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF/resolve/main/HighNoise/Wan2.2-I2V-A14B-HighNoise-Q5_K_M.gguf"
   curl -L -o Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf "https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF/resolve/main/LowNoise/Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf"
   ```

## 8. 工作流节点调整

- 用两个 Unet Loader (GGUF) 节点分别加载 HighNoise 和 LowNoise 模型。
- 上方节点选 HighNoise，连接到 LoraLoaderModelOnly。
- 下方节点选 LowNoise，连接到下方的 LoraLoaderModelOnly。

## 9. 生成视频

- 点击“Run”运行工作流，等待生成。
- 生成的 MP4 文件位于：

```
~/Documents/ComfyUI/output/video/
```

- ComfyUI 界面也会有预览。

### 性能参考（Mac Studio）

Wan 2.2 是大型视频生成模型，推理速度取决于硬件配置、分辨率、帧数等因素。以下是基于社区反馈的粗略估计（实际速度因具体配置和优化而异）：

- **设备配置**：Mac Studio (M1/M2 Ultra, 32GB+ RAM)
- **低分辨率测试** (320x320, 4秒视频, 8帧)：约 5-15 分钟
- **中等分辨率** (480x480, 4秒视频, 8帧)：约 15-30 分钟  
- **高分辨率** (640x640, 4秒视频, 8帧)：约 30-60 分钟或更长
- **内存使用**：峰值约 20-40GB RAM，建议 64GB+ 内存避免 OOM

**优化建议**：
- 初次测试从低分辨率开始，逐步调高
- 减少帧数（从 16 帧降到 8 帧）可显著加速
- 确保系统温度控制良好，避免热节流
- 使用 GGUF 量化模型可提升速度，但可能略微影响质量
- 监控 Activity Monitor 中的 CPU/GPU 使用率

如果速度过慢，可考虑云端 GPU 实例或等待未来优化。


## 10. 故障排查与优化建议

- **黑屏视频**：将分辨率从 640x640 降低到 320x320。
- **KSampler 卡死**：优先降低分辨率和帧数，确认内存充足。
- **VAE Decode 像素化**：可尝试 Node Library 里的 VAE DECODE (Tiled) 节点，并适当降低参数。
- **模型下载慢**：可用国内镜像或提前下载。

## 11. 寻找与优化 Mac 工作流

### 推荐资源来源

为了获得最佳性能，建议寻找那些**针对 GGUF 量化模型优化**或**标注了"低显存/低功耗"**的工作流版本：

#### 1. Civitai (C站) —— 社区资源最全
- **推荐搜索词**：Wan 2.2 (GGUF) Workflow
- **寻找特征**：关注那些文件名中带有 GGUF 字样的模型关联工作流，通常会有作者专门标注"适用于 Mac"或"低显存优化"。

#### 2. ComfyUI 官方模板 —— 最稳定、最纯净
- **操作方法**：在 ComfyUI 界面左侧点击 Templates (模板) → Video → Wan 2.2 14B Image to Video
- **Mac 适配建议**：加载官方模板后，手动将 UNETLoader 节点替换为 Unet-GGUF 节点即可（需安装 ComfyUI-GGUF 插件）

#### 3. GitHub 专项仓库 —— 针对低显存优化的技术流
- **推荐搜索**：ComfyUI-Wan2.2-workflow（例如 Cordux 开发的版本）
- **优点**：这些工作流通常已经配置好了针对 GGUF 模型、GGUF 文本编码器 (umt5) 以及 Tiled VAE 解码的节点连接

### Mac 用户特别配置建议

在寻找和使用工作流时，务必检查以下设置以匹配 Apple Silicon 性能：

#### 模型选择
- 避开 FP16，优先下载 Q4_K_M 或 Q5_K 版本的 GGUF 模型
- 使用量化工作流能让速度从"几分钟一帧"提升到"秒级生成"

#### 服务器配置
- 将 Inference (推理) 设为 fp32（Apple MPS 后端对 fp32 兼容性更好）
- 开启 highvram 模式（虽然听起来反直觉，但 Mac 的统一内存管理在 highvram 模式下表现更优）

#### VAE 设置
- 务必在设置中开启 Run VAE on CPU 或在工作流中使用 VAE Decode (Tiled)
- 这能释放大量显存，避免生成长视频时系统卡死


## 12. 进阶探索

- 可尝试其他视频生成工作流、模型或参数，提升画质与表现力。
- 关注 ComfyUI、Wan 2.2 相关社区，获取最新优化和模型。

## 13. 参考资料
+ [workflow_templates](https://github.com/Comfy-Org/workflow_templates/tree/main/templates) 