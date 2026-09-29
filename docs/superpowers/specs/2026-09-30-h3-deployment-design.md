# antirez/h3.c 本地部署测试与极简技术速查手册设计

## 1. 概述与目标

`antirez/h3.c` 是 Redis 创始人 Salvatore Sanfilippo（antirez）为 Apple Silicon 芯片（特别是 M3/M4/M5 Max）量身打造的原生 MiniMax-H3 视音频生成推理引擎。该引擎完全由纯 C、Objective-C 和 Metal 编写，摒弃了 Python、PyTorch、HuggingFace Diffusers、MLX 等任何重型外部运行时，直接利用 Metal 4 TensorOps 和 MPSGraph 执行 BF16 算子融合与 INT8 动态量化，并引入了 SSD Streaming 双缓冲流式加载、Euler 时序速度外推等底层创新。

本项目遵循用户的选择（方案 3：纯文档归档与独立外部测试），旨在：
1. **独立外部部署与算子测试**：在独立临时路径（如 `/tmp/h3.c`）中拉取最新源码，基于当前 Apple M4 Max (128GB RAM) 环境执行多核编译，运行完整测试套件 `make test`，抓取实际的宿主确定性与 Metal 算子对齐测试指标。
2. **沉淀高品质中文速查手册**：在仓库 `docs/h3-quickstart.md` 中编写紧凑、严谨、实用的技术速查手册，单文件严格控制在 500 行以内，供后续本地端到端视音频生成参考。

---

## 2. 外部部署与验证方案

### 2.1 源码克隆与构建配置
- **源码拉取路径**：`/tmp/h3.c`（不污染当前工程代码树）
- **编译工具链**：Apple Clang + Make（自动链接 Metal, Accelerate, MetalPerformanceShaders, MetalPerformanceShadersGraph, Foundation, icucore, libm）
- **编译指令**：
  ```bash
  cd /tmp/h3.c
  make clean && make -j8
  ```
- **核心构建产物**：
  - `./h3`：交互式与命令行推理主程序
  - `libh3.a`：包含所有算子与管线的静态库
  - 动态 Metal 着色器：`h3_shaders.metal`（由运行时动态编译注入）

### 2.2 测试套件执行与验证
- **测试指令**：
  ```bash
  make test
  ```
- **关键测试项覆盖**：
  1. `test_host`：宿主确定性、数据排布与 BF16 基础算子逻辑；
  2. `test_metal`：Metal 4 TensorOps/MPSGraph 管道初始化与显存分配验证；
  3. `test_weights` / `test_safetensors`：Safetensors 头部解析与零拷贝内存映射逻辑；
  4. `test_ffmpeg`：AV 多路复用与子进程管道联通性。
- **输出采集**：将实测的测试耗时、算子通过状态以及硬件探测日志完整反哺到文档中。

---

## 3. 文档体系设计 (`docs/h3-quickstart.md`)

文档定位为极简部署与参数速查手册，预计篇幅约 300~380 行（严格低于 500 行规则）。

### 3.1 章节大纲
1. **项目定位与核心特性**
   - 原生 Apple Silicon C/Metal 架构特点
   - 相比传统 Python/Diffusers 生态的工程优势（秒级启动、极低常驻显存、零外部依赖）
2. **环境依赖与前置检查**
   - 芯片与统一内存要求（M3/M4/M5 Max 推荐配置）
   - 系统工具自检：`clang`, `make`, `ffmpeg`, `ffprobe`
3. **源码构建与本地编译**
   - 一键编译与产物验证命令
   - 常见编译标志与平台宏定义（`-D_DARWIN_C_SOURCE`）
4. **测试套件与本地验证实测**
   - `make test` 执行流程与真实测试日志
   - 宿主确定性与 Metal 算子对齐结果
5. **模型准备与 CLI / REPL 运行实战**
   - MiniMax-H3 权重结构与 Safetensors 目录准备
   - 核心模式命令示范：
     - 设备与模型探查：`--info`
     - 基础文生视音频（T2V）：`-p "..." -o output.mp4`
     - 首尾帧约束生成（FL2VA）：`--first-frame` / `--last-frame`
     - 多模态参考生视音频（Ref2VA）：`--ref-image` / `--ref-video`
     - 终端视觉预览与交互 Shell：`--show` + `linenoise` REPL
6. **参数速查与显存/性能优化矩阵**
   - 基础几何与时间参数表（分辨率倍数、帧数公式 `5 + 17*n`）
   - 进阶调优与显存优化开关：
     - `--ssd-streaming`：DiT 块双缓冲流式加载
     - `--token-reduction`：空间 Token 缩减加速
     - `--layers <N>`：层数剪枝
     - `--reuse <N>` / `--core-reuse <N>`：去噪速度外推与残差复用
     - `--use-int8-row-fc2`：动态量化矩阵

---

## 4. 规范与质量自检

1. **单文件行数限制**：`docs/h3-quickstart.md` 控制在 500 行以内。
2. **纯中文文档规则**：依据用户记忆与偏好，仅保留全中文文档，不创建英文副本。
3. **真实性验证**：所有编译命令、测试输出和硬件日志均来自本地真实终端实测，绝不脑补或编造。
4. **Git 规则**：commit message 采用标准英文 `docs: add h3.c deployment and quickstart guide`，无 `Co-Authored-By`。
