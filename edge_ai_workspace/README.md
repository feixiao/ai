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

## 二、文档导航

### [Mac Studio](MAC_STUDIO.md)
Mac Studio 作为独立边缘计算节点：音视频硬解、Core ML/Metal、MLX、多模态模型和可验证 Demo。

### [Android / Pixel 10](ANDROID_PIXEL.md)
Android 作为移动端边缘节点：CameraX、YUV stride、Surface/AHardwareBuffer、AAudio/Oboe、端侧运行时和可验证 Demo。

两份文档独立阅读，不要求 Mac Studio 与 Pixel 10 联动。性能、硬件后端和系统级 AI 能力均以目标设备实际支持与实测结果为准。
