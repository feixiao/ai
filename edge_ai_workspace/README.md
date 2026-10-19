# 2026 工业级端侧与边缘计算全景实战体系

> 本工作区基于工业级端侧 AI 部署架构规范，分为三大互补协同的边缘计算落地体系：
> 1. **Mac Studio 端**：工业边缘计算中心节点 / 工作站（Edge Server / MEC）
> 2. **Android (Pixel 10) 端**：移动现场传感器级智能边缘节点（Sensor Edge）
> 3. **NVIDIA Jetson / 嵌入式 Linux 端**：工业智能现场与具身机器人实时边缘计算节点（Robotics / Embedded Edge）

---

## 一、 三大边缘体系核心对比矩阵

| 维度 | 模块 1：Mac Studio 边缘中心节点 | 模块 2：Android (Pixel 10) 移动边缘节点 | 模块 3：NVIDIA Jetson 工业与具身计算节点 |
| :--- | :--- | :--- | :--- |
| **物理定位** | 桌面边缘工作站 / 机房边缘分析中心 | 现场便携手持终端 / 智能巡检仪 / 车载终端 | 工业现场边缘工控机 / 具身机器人主控 / 自主移动设备 (AGV/AMR) |
| **硬件架构** | Apple Silicon M 系列（UMA 统一内存架构） | Google Pixel 10（移动 SoC 架构） | NVIDIA Jetson Orin Nano / Orin NX / AGX Orin (Tegra 统一内存架构) |
| **算力底盘** | Apple GPU / Neural Engine；大显存带宽 | Android CPU / GPU / NPU；受电池功耗严苛约束 | Ampere / Blackwell GPU + Deep Learning Accelerator (DLA) + Arm Cortex CPU |
| **功耗与散热** | 主动散热桌面级（40W ~ 150W） | 被动散热便携级（3W ~ 8W） | 工业级可调功耗档位（7W ~ 60W），支持宽温与无风扇工控设计 |
| **典型传感器** | 多路 RTSP/GB28181 网络流摄像头 | CameraX 手机相机模组、AAudio 麦克风阵列 | 工业面阵/线阵相机 (GigE/USB3 Vision)、LiDAR、IMU、CAN 总线设备 |
| **实时性与调度** | 用户态通用进程调度，关注高吞吐 | Android 框架与应用生命周期，关注低功耗保活 | Linux `PREEMPT_RT` / `SCHED_FIFO` 硬实时线程调度、硬件中断亲和性绑定 |
| **模型分层策略** | 轻量检测 (Core ML/ANE) + 大模型 (MLX/Metal) | 端侧轻量模型 (LiteRT) + 系统级辅助模型 | 工业级 TensorRT INT8/FP16 优化引擎、NVIDIA DeepStream 流媒体管线 |
| **核心零拷贝机制**| VideoToolbox/CVPixelBuffer 到 Core ML/Metal | `ImageProxy` stride 转换、Surface/AHardwareBuffer | V4L2 DMA-BUF 直通 CUDA 外部内存 (`cudaImportExternalMemory`) |
---

## 二、文档导航

### [Mac Studio](MAC_STUDIO.md)
Mac Studio 作为独立边缘计算节点：音视频硬解、Core ML/Metal、MLX、多模态模型和可验证 Demo。

### [Android / Pixel 10](ANDROID_PIXEL.md)
Android 作为移动端边缘节点：CameraX、YUV stride、Surface/AHardwareBuffer、AAudio/Oboe、端侧运行时和可验证 Demo。
### [NVIDIA Jetson / 嵌入式 Linux](EMBEDDED_JETSON.md)
NVIDIA Jetson 工业与具身机器人边缘节点：设备接入 (GigE/U3V/GenICam)、网络高吞吐优化 (Jumbo Frame/AF_XDP/无锁队列)、多设备硬件时序同步 (PTP 1588/PPS)、DMA-BUF 零拷贝直通与 TensorRT C++ 生产级部署。

三大文档各自独立针对特定物理场景，可根据工程定位按需查阅。
