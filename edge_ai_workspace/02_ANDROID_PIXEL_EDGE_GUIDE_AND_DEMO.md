# 模块 2：Android (Pixel 10) 移动边缘计算落地指南与实时 Demo

> **核心硬件**：Google Pixel 10（具体 SoC、加速器名称、驱动能力以设备实际规格和运行时枚举为准；本文不假定未公开的内部微架构）。  
> **核心系统能力**：Android CameraX/NDK 音视频管线，以及 LiteRT、厂商 GPU/NPU 后端或其他端侧运行时；系统级生成式 AI 能力是否可用取决于 Android 版本、地区、设备配置与 API。

---

## 一、 系统架构全景 (Android Pixel Edge)

在现场手持巡检仪、移动机器人终端或车载设备中，Android 端负责实时视觉感知与本地大模型交互：

```mermaid
    subgraph Input["1. 现场输入"]
        Cam["CameraX / Camera2（实际帧率取决于设备）"]
        Mic["AAudio / Oboe（低延迟音频采集）"]
    end

    subgraph Native["2. 移动端零拷贝处理与异构推理核心 (Native Layer)"]
        subgraph PipelineCV["CV 视觉感知管道 (BYOM)"]
            YUV["YUV_420_888：处理 rowStride/pixelStride；或 Surface/AHardwareBuffer"]
            LiteRT["LiteRT / 其他端侧运行时"]
            LiteRT_Service["可选硬件后端<br/>厂商 Delegate / GPU / NPU"]
        end

        subgraph PipelineAICore["3. 系统级多模态语义认知 (OS-Level)"]
            AICore["Android AICore 服务 (系统常驻共享内存)"]
            GeminiNano["Gemini Nano (零包体占用 / 共享 TPU)"]
            AICore --> GeminiNano
        end
    end

    subgraph Hardware["4. Google Tensor G5 芯片异构加速分配"]
        TPU["设备可用的 NPU/专用加速器<br/>名称与后端依设备而定"]
        GPU["设备 GPU<br/>Vulkan / OpenGL ES 等后端"]
        CPU["ARM CPU<br/>NEON 与系统调度"]
    end

    LiteRT_Service --> TPU
    LiteRT_Service --> GPU
    GeminiNano --> TPU
```

---

## 二、 音视频处理核心演进与真实工程瓶颈（客观勘误）

在 Android 端做音视频与 AI 结合，过去和现在的核心差异在于**管线调度与内存复用**，但工程落地中存在大量需要避开的隐形深坑：

### 1. 视频管道：CameraX 的真实工程现状与 Stride 陷阱

```
[常见错误做法: 忽视 Stride 导致画面倾斜拉丝/花屏]
ImageAnalysis (YUV_420_888) -> 直接获取 buffer 指针 -> 强行当作紧凑连续数组读入模型 -> 画面几何变形/识别失败

[工业级正确链路 1: CPU 处理 (通用稳妥)]
ImageAnalysis -> 提取各 Plane 的 buffer, rowStride, pixelStride -> 传入 libyuv (使用 Android420ToABGR 抹平步长) -> 紧凑 RGB 张量

[工业级正确链路 2: GPU/Surface 零拷贝 (极限性能)]
CameraX 输出至 Surface / AHardwareBuffer -> 绑定为 OpenGL ES / Vulkan OES 外部纹理 (EGLImageKHR) -> GPU 着色器硬件采样裁剪 -> 显存直接送入推理
```

| 技术点 | 常见误区 / 旧模式 | 真实工程实践 (现代规范) | 避坑与性能收益 |
| :--- | :--- | :--- | :--- |
| **YUV 内存步长 (Stride)** | 误以为各 Plane 是紧凑连续的内存（直接 `memcpy`） | **必须显式处理 `rowStride` 与 `pixelStride`** | 手机相机硬件通常按 16/64 字节对齐，`rowStride > width` 极常见，必须用 `libyuv` 处理，否则会导致画面倾斜拉丝 |
| **预处理加速** | 在 Java/Kotlin 循环中反复转 Bitmap | **GPU 纹理路径或 libyuv/NEON 路径** | 减少 Java 堆对象与 CPU 搬运；具体收益必须在目标设备测量 |
| **硬件 Delegate** | 把 NNAPI 当作默认通用加速入口 | **设备实际支持的 GPU/NPU/Vendor 后端** | NNAPI 已进入弃用/维护过渡状态，不应作为新项目的唯一方案；以当前 LiteRT 与厂商后端文档为准 |

---

### 2. 音频管道：低功耗常驻与端侧流式模型演进

* **底层 API 的客观事实**：
  * `AAudio`（Android 8.0+）和 `Oboe`（C++ 封装库）是 Android 上获得低延迟（< 10ms）的标准基础设施，而非刚刚出现的技术。
  * 它的核心价值是支持 **独占模式（Exclusive Mode）** 与无锁单生产者单消费者（SPSC RingBuffer），规避系统混音器的重采样缓冲。
* **现代端侧音频 AI 的真实演进点**：
  1. **低功耗 DSP / 硬件孤岛常驻（Low-Power Audio Island / CHRE）**：
     对于唤醒词识别（Wake-word）与关键异响检测，现代方案是将极小模型（如几百 KB 的微型 CNN/RNN）固化在低功耗音频 DSP 上运行，功耗仅几毫瓦，无需唤醒主应用处理器（AP），从而实现 7×24 小时不掉电监听。
  2. **端侧轻量流式语音识别（Streaming ASR）**：
     以往需要上传云端的语音听写，现在通过 **Sherpa-ONNX / Whisper 裁剪版**，配合流式 Conformer 架构，在移动端 ARMv9 CPU 上以 4 线程运行，RTF（实时率）可达到 0.1~0.2（即 1 秒音频仅需 100~200ms 计算）。

---

## 三、 关键工程技术准则与避坑要点

### 1. 内存与资源管理
* 可用内存受设备、应用进程、前台状态和系统压力共同影响，不应写死统一的 LMK 阈值。
* 避免在帧循环中创建大 Bitmap 或重复复制模型权重；是否支持内存映射、是否减少常驻内存，要由具体运行时和设备实测确认。
* 优先采用固定大小缓冲区、明确的帧丢弃策略和及时释放 `ImageProxy`，先控制延迟与峰值内存，再讨论零拷贝。

### 2. 线程调度与性能测量
* 不要硬编码 CPU 核心编号。核心拓扑、频率和调度策略依设备而异；优先使用线程优先级、性能 hint 和运行时 profiling 验证收益。
* 音频回调线程禁止阻塞、分配内存或执行模型推理；将数据写入预分配的无锁环形缓冲区，再由工作线程处理。
* 视觉管线同时记录预处理、推理、后处理、端到端延迟、帧丢弃率和温度。推理毫秒数不等于实时 FPS。

---

## 四、 Android 可验证的经典开源 Demo

以下是三个在 Android 手机上能够直接编译、安装并实测性能的开源标杆 Demo：

### Demo 1：Google 官方 MediaPipe 目标检测应用
* **项目特点**：采用 CameraX 高帧率取流，支持在设置面板中动态切换执行后端。
* **实测观察点**：
  * 打开手机后置摄像头，画面中出现的物体会被实时标注类别与置信度；
  * **核心验证**：
    * 切换 **Delegate: CPU** $\rightarrow$ 观察多线程（2/4线程）下的延迟表现；
    * 切换 **Delegate: GPU** $\rightarrow$ 观察基于 OpenCL / OpenGL ES 的加速效果与发热情况。
* **源码开源仓库**：
  * GitHub 官方仓库：`https://github.com/google-ai-edge/mediapipe-samples`
  * 对应工程路径：`examples/object_detection/android`

---

### Demo 2：llama.cpp Android 离线文本生成
* **看什么**：在断网状态下加载 GGUF 模型，观察本地生成是否可用，以及首 token 延迟、生成速度、内存、温度和长时间运行后的降频。
* **注意**：模型大小、量化格式、设备后端和系统状态都会影响结果，不在文档中预设固定 tokens/s 或内存数值。
* **参考项目**：`https://github.com/ggerganov/llama.cpp`。具体 Android 构建入口和目录以仓库当前版本为准。

---

### Demo 3：MLC-LLM Android GPU 后端评估
* **看什么**：在目标手机上验证 Vulkan 后端是否可用，并记录生成速度、内存占用、电池温度和持续运行时的降频。
* **注意**：预编译 APK、模型覆盖范围和设备支持会随项目版本变化，应以官方仓库当前发布物为准。
* **参考项目**：`https://github.com/mlc-ai/mlc-llm`。

---

