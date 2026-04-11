# LatentSync ComfyUI Mac Studio 使用指南

LatentSync 是一款强大的唇形同步（Lip-sync）模型，可以在现有视频基础上根据音频调整口型。在 Mac Studio 上运行它的关键在于处理 **FFmpeg** 依赖以及 **MPS 加速** 兼容性。

---

## 1. 系统依赖准备

LatentSync 涉及大量的视频与音频流处理，必须先安装系统级工具。

### 1.1 安装 FFmpeg
如果你的 Mac 尚未安装 FFmpeg，请使用 Homebrew 安装：
```bash
brew install ffmpeg
```

### 1.2 Python 环境建议
建议使用 **Python 3.10 或 3.11**。
> [!WARNING]
> 不要使用 Python 3.12+，因为 LatentSync 依赖的 `mediapipe` 库在 3.12 上安装极不稳定，会导致节点导入失败。

---

## 2. 安装自定义节点

推荐使用由 [ShmuelRonen](https://github.com/ShmuelRonen/ComfyUI-LatentSyncWrapper) 维护的封装版，它对 ComfyUI 的集成度最高。

### 2.1 自动安装（推荐）
1. 打开 ComfyUI 界面，进入 **Manager**。
2. 点击 **Install Custom Nodes**。
3. 搜索 `LatentSync` 并点击安装。
4. 重启 ComfyUI。

### 2.2 手动安装（如果 Manager 失败）
```bash
cd ~/ComfyUI/custom_nodes
git clone https://github.com/ShmuelRonen/ComfyUI-LatentSyncWrapper.git
cd ComfyUI-LatentSyncWrapper
# 确保在 ComfyUI 的 Python 环境下运行
pip install -r requirements.txt
```

---

## 3. 模型下载与存放

LatentSync 需要特定的权重模型（约 5GB），部分节点会自动下载，但由于网络环境原因，建议手动下载：

1. 从 [HuggingFace - LatentSync](https://huggingface.co/chunyu-li/LatentSync/tree/main) 下载以下文件：
   - `latentsync_v2.pt`
   - `whisper/tiny.pt` (或指定版本)
2. 存放到以下目录（视插件版本而定，通常在如下路径）：
   - `ComfyUI/models/checkpoints/latentsync/` 
   - 或插件目录下的 `checkpoints/` 文件夹。

---

## 4. Mac Studio 专项优化配置

由于 LatentSync 的部分底层算子（如特定的音频处理）在 Metal (MPS) 上可能未完全实现，建议进行以下环境变量配置。

### 4.1 开启 MPS 回退模式
在启动 ComfyUI 前，在 Terminal 中设置环境变量，强制 MPS 在遇到不支持的算子时使用 CPU 代替，防止崩溃：
```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
python main.py
```

### 4.2 内存建议
由于 Mac Studio 是统一内存，LatentSync 在处理长视频时会占用较多内存进行图像序列缓存。
- **推荐策略**：生成视频长度建议控制在 **10秒以内**。
- **配置**：在节点中将 `face_detection_threshold` 设为 `0.5` 以平衡速度与精度。

---

## 5. 工作流建议逻辑

LatentSync 在 ComfyUI 中的典型用法：
1. **Load Video**: 加载你生成的 Wan 2.2 视频。
2. **Load Audio**: 加载对应的音频配音（建议 `.wav` 格式）。
3. **LatentSync Node**: 
   - `seed`: 固定种子以保证稳定性。
   - `guidance_scale`: 建议 `1.5` - `2.5`。
   - `num_inference_steps`: 建议 `20` 步左右。
4. **Output Video**: 使用 `VideoCombine` 合成带声轨的最终视频。

---

## 6. 常见故障处理

*   **Import Failed (Mediapipe)**: 如果终端报错找不到 `mediapipe`，请尝试手动安装适配版本 `pip install mediapipe==0.10.11`。
*   **Audio/Video Align Error**: 确保输入的视频帧率与音频长度匹配。如果视频是 24fps，计算好对应的总帧数，避免口型与声音错位。
*   **Out of Memory**: 虽然 128G 内存很充裕，但如果遇到卡顿，请检查是否在后台同时运行了多个大模型采样任务。

---
*关联文档：[Wan 2.2 Mac 安装指南](file:///Users/frank/wk/github/ai/ComfyUI/Wan2.2_ComfyUI_MacStudio_%E5%AE%89%E8%A3%85%E6%B5%8B%E8%AF%95%E6%8C%87%E5%8D%97.md)*
