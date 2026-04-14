# GPT-SoVITS ComfyUI Mac Studio 使用指南

GPT-SoVITS 是目前最强大的开源 Few-shot 语音克隆与文本转语音（TTS）模型之一。它仅需 1 分钟甚至更短的参考音频，就能实现极高相似度的声音克隆。在 Mac Studio (Apple Silicon) 上，配合 MPS 加速，可以获得非常流畅的推理体验。

---

## 1. 系统依赖准备 (Mac 专项)

GPT-SoVITS 在音频处理环节高度依赖 `ffmpeg`。

### 1.1 安装 FFmpeg
打开终端，通过 Homebrew 安装：
```bash
brew install ffmpeg
```

### 1.2 环境验证
确保你的 ComfyUI 运行在支持 MPS (Metal Performance Shaders) 的环境中。你可以在 ComfyUI 启动日志中确认是否识别到 Apple GPU。

---

## 2. 安装自定义节点

推荐使用兼容性较好的版本：[ComfyUI-GPT_SoVITS](https://github.com/AIFSH/ComfyUI-GPT_SoVITS) (by AIFSH)。

### 2.1 通过 Manager 安装 (推荐)
1. 在 ComfyUI Manager 中点击 **Install Custom Nodes**。
2. 搜索 `GPT-SoVITS`。
3. 选择 **`ComfyUI-GPT_SoVITS`** 并点击 Install。
4. 重启 ComfyUI。

### 2.2 手动安装
```bash
cd ~/ComfyUI/custom_nodes
git clone https://github.com/AIFSH/ComfyUI-GPT_SoVITS.git
cd ComfyUI-GPT_SoVITS
# 使用 ComfyUI 的虚拟环境安装依赖
~/ComfyUI/.venv/bin/pip3 install -r requirements.txt
```

---

## 3. 模型下载与存放

GPT-SoVITS 需要两部分核心权重：**GPT 权重** 和 **SoVITS 权重**。

### 3.1 预训练权重存放路径
插件通常会自动尝试从 Hugging Face 下载，但建议手动放置以确保速度：
- **路径**: `~/ComfyUI/models/gpt_sovits/` (如果文件夹不存在请手动创建)
- **必备文件**:
  - `pretrained_models/gsv-v2final-pretrainted/s2G488k.pth` (SoVITS 权重)
  - `pretrained_models/gsv-v2final-pretrainted/s1bert25hz-2kh-longer-epoch=12-step=369668.ckpt` (GPT 权重)
  - 以及对应的配置文件 `chinese-roberta-wwm-ext` 等。

> [!TIP]
> 推荐直接从 [GPT-SoVITS 官方 Release](https://github.com/RVC-Boss/GPT-SoVITS/releases) 下载最新版本的权重。
> ComfyUI也会自动下载，启动时候
---

## 4. 参考音频准备 (关键)

GPT-SoVITS 的效果 80% 取决于参考音频的质量。

*   **时长**: 建议 3-10 秒。过短相似度不足，过长可能导致推理变慢。
*   **内容**: 参考音频中的说话内容必须清晰，背景音乐需通过 Spleeter (你已安装) 等工具剥离。
*   **格式**: 默认推荐 `.wav` 格式，采样率 32k 或 48k。
*   **对应文本**: 节点中需要输入该参考音频所说的 **原始文本**（用于对齐音素）。

---

## 5. Mac Studio 性能优化

*   **MPS 加速**: 在节点设置中，`device` 务必选择 `cuda:0` (ComfyUI 会自动映射到 MPS) 或 `auto`。
*   **内存管理**: GPT-SoVITS 在加载模型时会占用数 GB 的统一内存。Mac Studio 拥有大容量统一内存，通常无需担心，但如果在生成长文本时变慢，请尝试将长句拆分为短句。
*   **并行推理**: Mac Studio 的多核性能可以让多个 TTS 任务同时进行，建议单个节点处理短句。

---

## 6. 典型数字人配音流

配合你已有的工作流，可以实现全流程自动化：
1. **ChatTTS / Kokoro**: 用于快速生成基础配音（如果不需要特定人声）。
2. **GPT-SoVITS**: 用于高精度克隆特定人物的声音。
3. **Save Audio**: 将生成的音频保存。
4. **LatentSync**: 将此音频连接至 `LatentSync` 的音频输入端，驱动 Wan 2.2 或 FLUX 生成的人物视频。

---

## 7. 常见故障处理

*   **报错 `RuntimeError: Placeholder storage has not been allocated`**: 通常是显存/内存瞬间不足导致的 MPS 错误。尝试重启 ComfyUI。
*   **报错 `Missing ffmpeg`**: 确认 `brew install ffmpeg` 已成功，并且在终端输入 `ffmpeg -version` 有输出。
*   **音质有杂音**: 检查参考音频的噪声水平，或降低 `top_k` / `top_p` 参数尝试。
*   **遇到 "Unknown pack" 或节点缺失**: 
    如果你是通过加载他人的 JSON 工作流（如 `gsv_tts_workflow.json`）发现节点全红，最快捷的方法是：
    > **使用 ComfyUI Manager 自动修复**:
    > 1. 点击 Manager 按钮 → **Install Missing Custom Nodes**。
    > 2. 它会自动识别工作流所需的特定 GPT-SoVITS 版本并提供安装。
    > 3. 安装完成后重启 ComfyUI。
