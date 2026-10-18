# 2026 工业级端侧与边缘计算全景实战体系

> 本工作区基于工业级端侧 AI 部署架构规范，分为两大完全独立的边缘计算落地体系：
> 1. **Mac Studio 端**：工业边缘计算中心节点 / 工作站（Edge Server / MEC）
> 2. **Android (Pixel 10) 端**：移动现场传感器级智能边缘节点（Sensor Edge）

---

## 一、 两大边缘体系核心对比矩阵

| 维度 | 模块 1：Mac Studio 边缘中心节点 | 模块 2：Android (Pixel 10) 移动边缘节点 |
| :--- | :--- | :--- |
| **物理定位** | 桌面边缘工作站 / 机房边缘分析中心 | 现场便携手持终端 / 智能巡检仪 / 车载终端 |
| **硬件架构** | Apple Silicon M 系列 (UMA 统一内存架构) | Google Tensor G5 SoC (移动芯片) |
| **算力底盘** | **400 ~ 800 GB/s** 显存带宽 + 16 核 ANE + 30~76 核 GPU | **Google Edge TPU** + ARMv9 核心集群 + Immortalis GPU |
| **功耗与散热** | 30W ~ 150W（主动散热，支持 7×24 小时长稳运行）| 3W ~ 12W（被动均热板散热，极度敏感于发热与降频）|
| **接入路数** | 并发硬解拉取 **16 ~ 32 路 4K/1080P** RTSP 网络流 | 单路手机摄像头（**CameraX 60fps** 局部视场）|
| **模型分层策略**| **两级混合架构**：<br/>- 一级：16 核 ANE 跑 YOLO（毫秒级超低功耗常驻）<br/>- 二级：Metal GPU 跑 7B~32B 多模态大模型 (Qwen2-VL) | **双轨并行架构**：<br/>- 轨 A (BYOM)：LiteRT INT8 专有视觉感知<br/>- 轨 B (OS Level)：Android AICore (Gemini Nano) 共享大模型 |
| **核心零拷贝机制**| **VideoToolbox $\to$ CVPixelBuffer $\to$ Core ML / Metal 零拷贝**| **CameraX ImageProxy $\to$ JNI DirectByteBuffer $\to$ C++ 零拷贝**|

---

## 二、 文档与立即可看效果的 Demo 指引

### 1. [模块 1：Mac Studio 边缘中心节点落地指南与实时 Demo](01_MAC_STUDIO_EDGE_GUIDE_AND_DEMO.md)
* **包含理论**：Apple Silicon 统一内存（UMA）破解 Memory-Bound、VideoToolbox 多路硬件解码零拷贝、16 核 ANE 神经引擎 100% 卸载三大军规。
* **包含 3 大可直观体验效果的 Demo**：
  1. **Scrypted**：流媒体多路硬解 + ANE 16核实时人/车检测（Web 界面多路实时画框）；
  2. **Ultralytics 实时检测**：Mac 原生窗口调用本地摄像头，实时弹窗画框，标注 60 FPS 与 5ms 硬件延迟；
  3. **Apple MLX 多模态大模型**：本地纯离线运行 Qwen2-VL-7B (4-bit)，300ms 完成工业图像多模态质检查看。

### 2. [模块 2：Android (Pixel 10) 移动边缘计算落地指南与实时 Demo](02_ANDROID_PIXEL_EDGE_GUIDE_AND_DEMO.md)
* **包含理论**：Google Tensor G5 芯片异构硬件拓扑、移动端 LMK 防 OOM 规范（`mmap` 权重映射）、CameraX YUV_420 零拷贝与 NDK 大核绑定技术（CPU Core Affinity）。
* **包含 3 大可直观体验效果的 Demo**：
  1. **Google 官方 MediaPipe 目标检测 App**：手机摄像头实时画框，底部抽屉支持实时切换 **CPU vs GPU vs Edge TPU**，直观见证延迟从 35ms 暴跌至 3ms；
  2. **llama.cpp Android 纯 C++ 离线大模型**：手机开启飞行模式脱网运行 Qwen2.5-0.5B，打字机流式输出体验端侧 SLM 算力；
  3. **MLC-LLM Android GPU 加速应用**：基于 TVM Vulkan Compute 的端侧大模型性能基准应用，实时监测显存与发热。
