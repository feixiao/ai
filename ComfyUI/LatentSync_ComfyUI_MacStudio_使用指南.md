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

1. **第一步：建立本地文件夹**
   由于模型文件比较散碎，建议你先在桌面上（或任意方便的地方）新建一个名为 `latentsync` 的文件夹。

2. **第二步：下载并在这个新建文件夹内组织结构**
   从 [HuggingFace - LatentSync](https://huggingface.co/chunyu-li/LatentSync/tree/main) 挑选下载以下核心模块，并将它们分门别类地放进你刚建好的 `latentsync` 文件夹中：

   - **放在 `latentsync` 的根目录下**：
     - `latentsync_unet.pt` (**必下**：核心生成模型，负责绘制唇形)
     - `latentsync_syncnet.pt` (选下：同步判别模型，推理过程通常用不到)
   
   - **放在 `latentsync/whisper/` 文件夹内** (需手动新建)：
     - `tiny.pt` (**必下**：音频特征提取，必须能听懂你录音在说什么)
   
   - **放在 `latentsync/auxiliary/` 文件夹内** (需手动新建)：
     - `s3fd-619a316812.pth` 或 `sfd_face.pth` (**必下**：用于脸部精确抓取防报错)
     - `vgg16-397923af.pth` (选下：除非插件特别要求，否则可以不装)
     - `vit_g...` (纯评测打分用，**千万别下**，白占极多硬盘！)

3. **第三步：将整个文件夹放入系统指定位置（关键！）**

   根据实测发现，LatentSync 在 Mac 环境下并不会直接去 ComfyUI 的 models 目录下寻找模型，而是默认读取用户家目录下的特定隐藏文件夹：`~/.latentsync16_models`。

   请将你刚才整理好的、内含所有子路径的这个 `latentsync` 文件夹，重命名并移动到正确位置：

   ```bash
   # 在终端中执行（假设你的 latentsync 文件夹在当前目录下）
   mv latentsync ~/.latentsync16_models
   ```

   **最终路径检查：**
   - 核心模型：`~/.latentsync16_models/latentsync_unet.pt`
   - 音频模型：`~/.latentsync16_models/whisper/tiny.pt`
   - 人脸模型：`~/.latentsync16_models/auxiliary/s3fd-619a316812.pth`

   > [!IMPORTANT]
   > 如果你之前放在 `models/checkpoints` 发现插件报错或不断在终端重新下载，请务必迁移到此目录。



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
*   **TorchCodec / MPS Compatibility Issues**: 如果你在运行过程中遇到 `torchcodec` 报错或显存/加速异常，建议重装一套稳定的 Mac 专项 Torch 环境。请在终端执行：
    ```bash
    cd ~/ComfyUI
    source .venv/bin/activate

    # 1. 卸载当前的 torch 相关包
    pip uninstall torch torchvision torchaudio torchcodec -y

    # 2. 安装官方最新的 macOS 稳定版 (原生支持 MPS 加速)
    pip install torch torchvision torchaudio

    # 3. 重新安装匹配的 TorchCodec
    pip install torchcodec

    # 4. 验证安装是否成功
    python -c "import torch; print(f'Torch version: {torch.__version__}')"
    python -c "import torchcodec; print('torchcodec OK')"
    ```
*   **Audio/Video Align Error**: 确保输入的视频帧率与音频长度匹配。如果视频是 24fps，计算好对应的总帧数，避免口型与声音错位。
*   **Out of Memory**: 虽然 128G 内存很充裕，但如果遇到卡顿，请检查是否在后台同时运行了多个大模型采样任务。


