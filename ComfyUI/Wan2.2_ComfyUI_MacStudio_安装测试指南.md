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
   curl -L -o Wan2.2-I2V-A14B-HighNoise-Q5_K_M.gguf "https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF/resolve/main/HighNoise/Wan2.2-I2V-A14B-HighNoise-Q5_K_M.gguf"
   curl -L -o Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf "https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF/resolve/main/LowNoise/Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf"
   ```

3. 或者使用 wget（需先安装 `brew install wget`）：
   ```bash
   wget https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF/resolve/main/HighNoise/Wan2.2-I2V-A14B-HighNoise-Q5_K_M.gguf
   wget https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF/resolve/main/LowNoise/Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf
   ```

4. 如果下载慢，可使用国内镜像或代理加速。


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

## 10. 故障排查与优化建议

- **黑屏视频**：将分辨率从 640x640 降低到 320x320。
- **KSampler 卡死**：优先降低分辨率和帧数，确认内存充足。
- **VAE Decode 像素化**：可尝试 Node Library 里的 VAE DECODE (Tiled) 节点，并适当降低参数。
- **模型下载慢**：可用国内镜像或提前下载。

## 11. 进阶探索

- 可尝试其他视频生成工作流、模型或参数，提升画质与表现力。
- 关注 ComfyUI、Wan 2.2 相关社区，获取最新优化和模型。

## 12. 参考资料
+ [workflow_templates](https://github.com/Comfy-Org/workflow_templates/tree/main/templates) 