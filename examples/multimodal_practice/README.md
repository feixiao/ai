# 2026 音视频多模态大模型实操练习套件 (Hands-on Practice Labs)

> 针对 **Mac Studio（桌面边缘中心）** 与 **Google Pixel 10（移动端边缘节点）** 打造的 4 套端到端、零门槛、零外部三方依赖的音视频大模型实战练习。  
> 理论与完整指南请参阅：[`docs/AUDIO_VIDEO_MULTIMODAL_HANDBOOK.md`](../../docs/AUDIO_VIDEO_MULTIMODAL_HANDBOOK.md)。

---

## 快速开始

### 方式一：一键运行全部 4 套练习
```bash
bash run_all_labs.sh
```
*自动完成环境探测（Apple Silicon 芯片检测、统一内存 UMA 探测、可选工具检查），并依次执行 4 套实操练习流水线。*

### 方式二：交互式终端控制台菜单
```bash
bash run_all_labs.sh --menu
# 或直接运行
python3 interactive_menu.py
```
*提供 TUI 数字菜单，支持按需单选练习 1~4、环境探测或算力预算估算器。*

### 方式三：真机环境就绪检查与 Pixel 10 ADB 模型推送
```bash
# 检查 Mac Studio 与 Pixel 10 工具链 (Python, Metal, FFmpeg, ADB 在线设备)
bash setup_environment.sh --check

# 一键安装 Apple Silicon 原生 MLX 多模态组件
bash setup_environment.sh --install-mac-mlx

# 将量化导出的模型通过 ADB 推送至在线的 Pixel 10 手机端
bash setup_environment.sh --push-pixel10 /path/to/qwen2.5_vl_3b_w4a16.task
```

---

## 4 套实操练习详解

### 练习 1：Mac Studio 视频抽帧与视觉语言模型 (VLM) 批处理
* **脚本文件**：`01_video_vlm_inference.py`
* **功能**：
  1. 纯 Python 原生无外部包依赖生成 BMP 格式连续视频抽帧切片；
  2. 构造兼容 Qwen2.5-VL / MLX / Ollama 的标准多模态 Payload；
  3. 执行视觉时序推理，识别工业场景违章状态变化与安全复位；
  4. 支持指定 `--dump-frames /path` 将抽帧图片保存到本地硬盘查看；
  5. 支持指定 `--endpoint http://localhost:11434/v1/chat/completions` 对接本地真实运行的 Ollama 或 LM Studio。
* **命令示例**：
  ```bash
  # 基础确定性实操
  python3 01_video_vlm_inference.py --demo

  # 导出抽帧图像到本地查看
  python3 01_video_vlm_inference.py --demo --dump-frames /tmp/vlm_frames

  # 挂接本地运行的真实 Ollama 服务
  python3 01_video_vlm_inference.py --endpoint http://localhost:11434/v1/chat/completions --model qwen2.5-vl:7b
  ```

---

### 练习 2：Mac Studio 音频大模型 (Whisper ASR + TTS) 语音交互闭环
* **脚本文件**：`02_audio_whisper_tts.py`
* **功能**：
  1. 纯 Python 原生生成 16kHz PCM 单声道测试音频波形；
  2. 模拟端侧低功耗语音活动检测 (VAD)，滤除静音区间；
  3. 模拟 ANE 硬件加速的 Whisper-large-v3-turbo 极速语音转写；
  4. 触发本地语音合成 (TTS) 反馈（在 macOS 上加 `--play` 可调用系统语音合成引擎直接发音朗读）。
* **命令示例**：
  ```bash
  # 基础实操
  python3 02_audio_whisper_tts.py --demo

  # 在 Mac 扬声器中播放合成的回复语音
  python3 02_audio_whisper_tts.py --demo --play

  # 传入自己录制的真实 WAV 音频文件
  python3 02_audio_whisper_tts.py --audio /path/to/my_record.wav
  ```

---

### 练习 3：Mac Studio 多模态大模型 LoRA 微调与数学梯度下降
* **脚本文件**：`03_vlm_lora_dataset_and_train.py`
* **功能**：
  1. 自动生成标准 ShareGPT 多模态图文对数据集（`train.jsonl` 与 `valid.jsonl`）；
  2. 严格校验助手输出是否 100% 满足工业级 JSON Schema；
  3. 规划并输出真实的 MLX LoRA 训练命令；
  4. **原生数学级 LoRA 仿真**：使用原生 Python 完整计算 $W + \frac{\alpha}{r}BA$ 的前向传播与反向传播，演示在冻结基座权重前提下仅更新低秩适配器使 Loss 降低 87% 的过程。
* **命令示例**：
  ```bash
  python3 03_vlm_lora_dataset_and_train.py --demo
  ```

---

### 练习 4：W4A16 4-bit 量化导出与 Pixel 10 端侧部署
* **脚本文件**：`04_export_to_pixel10.py`
* **功能**：
  1. 精确测算 3.0B 视觉模型从 FP16 (6.0GB) 到 W4A16 INT4 (1.8GB) 的压缩比与显存开销；
  2. 对标 Google Pixel 10 硬件约束（<= 4.5GB 可用内存上限），校验部署安全性；
  3. 自动生成包含 LiteRT、llama.cpp GGUF、ExecuTorch 三大端侧运行时的标准转换命令矩阵；
  4. 生成直接可贴入 Android Studio 的 CameraX 零拷贝 HardwareBuffer 调用模板代码。
* **命令示例**：
  ```bash
  python3 04_export_to_pixel10.py --demo
  ```
