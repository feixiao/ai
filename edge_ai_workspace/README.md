# 2026 工业级端侧与边缘计算全景实战体系

> 本工作区基于工业级端侧 AI 部署架构规范，分为两大完全独立的边缘计算落地体系：
> 1. **Mac Studio 端**：工业边缘计算中心节点 / 工作站（Edge Server / MEC）
> 2. **Android (Pixel 10) 端**：移动现场传感器级智能边缘节点（Sensor Edge）

---

## 一、 两大边缘体系核心对比矩阵

| 维度 | 模块 1：Mac Studio 边缘中心节点 | 模块 2：Android (Pixel 10) 移动边缘节点 |
| :--- | :--- | :--- |
| **物理定位** | 桌面边缘工作站 / 机房边缘分析中心 | 现场便携手持终端 / 智能巡检仪 / 车载终端 |
| **硬件架构** | Apple Silicon M 系列（UMA 统一内存架构） | Google Pixel 10；具体 SoC、GPU/NPU 能力以设备规格和运行时枚举为准 |
| **算力底盘** | Apple GPU / Neural Engine；带宽与核心数取决于具体 M 系列型号 | Android CPU、GPU、可能存在的 NPU/专用加速器；不可从型号推断未公开微架构 |
| **功耗与散热** | 由具体 Mac Studio 型号、负载和环境决定 | 由具体手机配置、负载、环境和系统调度决定 |
| **接入路数** | 取决于 VideoToolbox、网络、解码格式和应用流水线；必须实测 | 取决于摄像头、CameraX 配置和设备能力；不预设 60fps |
| **模型分层策略** | 轻量视觉模型可评估 Core ML；大模型可评估 MLX/Metal 等后端 | BYOM 使用 LiteRT 或其他运行时；系统级模型能力按设备与 API 可用性确认 |
| **核心零拷贝机制**| VideoToolbox/CVPixelBuffer 到 Core ML/Metal 的零拷贝需由具体 API 与模型验证 | `ImageProxy` 不是紧凑数组；先正确处理 stride，只有 Surface/AHardwareBuffer 路径在设备支持时才谈零拷贝 |

---

## 二、 文档与立即可看效果的 Demo 指引

### 1. [模块 1：Mac Studio 边缘中心节点落地指南与实时 Demo](01_MAC_STUDIO_EDGE_GUIDE_AND_DEMO.md)
* **包含理论**：Apple Silicon 统一内存（UMA）破解 Memory-Bound、VideoToolbox 多路硬件解码零拷贝、16 核 ANE 神经引擎 100% 卸载三大军规。
* **包含 3 大可直观体验效果的 Demo**：
  1. **Scrypted**：流媒体多路硬解 + ANE 16核实时人/车检测（Web 界面多路实时画框）；
  2. **Ultralytics 实时检测**：Mac 原生窗口调用本地摄像头，实时弹窗画框，标注 60 FPS 与 5ms 硬件延迟；
  3. **Apple MLX 多模态大模型**：本地纯离线运行 Qwen2-VL-7B (4-bit)，300ms 完成工业图像多模态质检查看。

* **包含理论**：音视频管线、YUV stride、CameraX/NDK 内存复用、端侧运行时和实测方法。
* **包含 3 大可验证参考 Demo**：
  1. Google AI Edge/MediaPipe Samples 目标检测：对比 CPU 与 GPU 后端，不预设 NNAPI 或固定延迟；
  2. llama.cpp Android：离线 GGUF 文本生成，实际速度和内存以设备实测为准；
  3. MLC-LLM：若目标设备和版本支持，再评估 Vulkan 后端与功耗。
