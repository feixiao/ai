# LatentSync ComfyUI Mac Studio 使用指南

LatentSync 是一款强大的唇形同步（Lip-sync）模型，可以在现有视频基础上根据音频调整口型。在 Mac Studio 上运行它的关键在于处理 **FFmpeg** 依赖以及 **MPS 加速** 兼容性。

---

## 1. 基础环境准备

有关在 Mac Studio 上运行 ComfyUI 的所有基础环境配置（包括 Python 版本要求、Homebrew 及 FFmpeg 安装），以及**防止花屏的 `config.json` 专项优化**，请完全参考：
👉 [Wan 2.2 Mac 安装测试指南](file:///Users/frank/wk/github/ai/ComfyUI/Wan2.2_ComfyUI_MacStudio_%E5%AE%89%E8%A3%85%E6%B5%8B%E8%AF%95%E6%8C%87%E5%8D%97.md)

请确保你已经按照上述指南完成了基础环境配置。

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
~/ComfyUI/.venv/bin/pip3 install -r requirements.txt
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

## 4. 工作流建议逻辑

LatentSync 在 ComfyUI 中的典型用法：
1. **Load Video**: 加载你生成的 Wan 2.2 视频。
2. **Load Audio**: 加载对应的音频配音（建议 `.wav` 格式）。
3. **LatentSync Node**: 
   - `seed`: 固定种子以保证稳定性。
   - `guidance_scale`: 建议 `1.5` - `2.5`。
   - `num_inference_steps`: 建议 `20` 步左右。
4. **Output Video**: 使用 `VideoCombine` 合成带声轨的最终视频。

---

## 5. 常见故障处理

*   **Import Failed (Mediapipe)**: 如果终端报错找不到 `mediapipe`，请尝试手动安装适配版本 `pip install mediapipe==0.10.11`。
*   **Install Failed (No matching distribution found for decord) 或编译报错 (no member named 'channel_layout')**: 
    这是因为官方未提供 Mac 预编译包，且源码与系统默认的 FFmpeg 最新版 API (7.x 及以上彻底移除了 `channel_layout`) 严重不兼容。我们需要使用老版本 `ffmpeg@4` 并强行指定编译路径（**无需卸载你现有的 ffmpeg 版本**）。请执行：
    ```bash
    # 1. 安装 FFmpeg 4 (它会独立存在于 /opt/homebrew/opt/ffmpeg@4)
    brew install cmake ffmpeg@4
    
    # 2. 拉取底层源码
    git clone --recursive https://github.com/dmlc/decord
    cd decord
    mkdir build && cd build
    
    # 3. 设置临时环境变量指向 FFmpeg 4
    export PKG_CONFIG_PATH="/opt/homebrew/opt/ffmpeg@4/lib/pkgconfig:$PKG_CONFIG_PATH"
    
    # 4. 强制指定 CMake 路径进行编译
    cmake .. -DUSE_CUDA=0 -DCMAKE_BUILD_TYPE=Release \
        -DFFMPEG_DIR="$(brew --prefix ffmpeg@4)" \
        -DCMAKE_C_COMPILER="/usr/bin/clang" -DCMAKE_CXX_COMPILER="/usr/bin/clang++"
        
    make -j4
    
    # 5. 安装进 ComfyUI 独立环境
    cd ../python
    ~/ComfyUI/.venv/bin/python3 setup.py install
    ```
    完成后，在插件的 `requirements.txt` 中将 `decord` 这一行删掉或注释掉，再次运行 `~/ComfyUI/.venv/bin/pip3 install -r requirements.txt` 补齐剩下的包即可。
*   **Audio/Video Align Error**: 确保输入的视频帧率与音频长度匹配。如果视频是 24fps，计算好对应的总帧数，避免口型与声音错位。
*   **Out of Memory**: 虽然 128G 内存很充裕，但如果遇到卡顿，请检查是否在后台同时运行了多个大模型采样任务。


