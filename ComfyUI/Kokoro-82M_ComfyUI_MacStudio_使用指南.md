# Kokoro-82M ComfyUI Mac Studio 使用指南

Kokoro-82M 是目前最强的轻量级文本转语音（TTS）模型之一，仅 8200 万参数就能达到媲美大模型的音质。它在 Mac Studio 上的运行速度极快，是视频配音的绝佳选择。

---

## 1. 系统依赖准备 (Mac 专项)

Kokoro 依赖于 `espeak-ng` 进行音素处理，这是 Mac 上最容易报错的一步。

### 1.1 安装系统级音素库
打开终端，通过 Homebrew 安装：
```bash
brew install espeak-ng
```

### 1.2 解决 Mac 路径识别问题
由于 Mac 的 Homebrew 路径（`/opt/homebrew`）与 Python 插件默认查找路径可能不一致，如果后续运行报错“找不到 espeak 库”，你可能需要建立一个软连接（通常不需要，除非报错）：
```bash
# 只有在报错找不到库时执行
sudo ln -s /opt/homebrew/lib/libespeak-ng.dylib /usr/local/lib/libespeak-ng.dylib
```

---

## 2. 安装自定义节点

推荐使用目前社区维护最活跃的版本：[comfyui-kokoro](https://github.com/stavsap/comfyui-kokoro)。

### 2.1 通过 Manager 安装 (推荐)
1. 在 ComfyUI Manager 中点击 **Install Custom Nodes**。
2. 搜索 `Kokoro`。
3. 选择 **`comfyui-kokoro`** 并点击 Install。
4. 重启 ComfyUI。

### 2.2 手动安装
```bash
cd ~/ComfyUI/custom_nodes
git clone https://github.com/stavsap/comfyui-kokoro.git
cd comfyui-kokoro
~/ComfyUI/.venv/bin/pip3 install -r requirements.txt
```

---

## 3. 模型下载与存放

该插件通常会自动下载模型，但如果你想手动管理或遇到下载慢的问题：

1. **核心模型**: 下载 `kokoro-v0_19.onnx` (或最新版本)。
2. **存放位置**: 
   - `~/ComfyUI/custom_nodes/comfyui-kokoro/models/`
3. **声音配置 (Voices)**: 存放于插件目录下的 `voices/` 文件夹（插件通常自带了一些，如 `af_heart`, `am_fenrir` 等）。

---

## 4. Mac Studio 性能优化

Kokoro 非常轻量，即使在 CPU 上运行也接近实时。

*   **设备选择**: 在 ComfyUI 节点中，`device` 选项建议选 `cpu` 或 `auto`。
*   **并发建议**: 由于 Mac Studio 核心数极多，你可以同时运行多个 TTS 任务而不会感到卡顿。
*   **采样率**: 默认为 24000Hz。如果你需要更高音质，可以在节点后连接重采样节点，但原声 24k 已经足够清晰。

---

## 5. 典型配音工作流逻辑

在 ComfyUI 中你可以构建如下链路：
1. **Primitive (Text)**: 输入你想要朗读的台词。
2. **Kokoro TTS 节点**: 
   - `text`: 接上面的文本。
   - `voice`: 选择音色（推荐 `af_heart`，非常自然）。
   - `speed`: 语速调节。
3. **Save Audio**: 保存生成的 `.wav` 文件。
4. **(进阶)**: 将此音频直接接入上一步学的 **LatentSync** 节点，实现“音频驱动口型”。

---

## 6. 常见故障处理

*   **报错 `Phonemizer not found`**: 确保你已经在虚拟环境下安装了 `phonemizer`：
    `~/ComfyUI/.venv/bin/pip3 install phonemizer`
*   **声音断断续续**: 检查文本中是否有特殊的无法识别的字符。
*   **Mac 环境环境变量**: 建议在 `.zshrc` 中加入 `export PATH="/opt/homebrew/bin:$PATH"` 确保环境变量正确。

