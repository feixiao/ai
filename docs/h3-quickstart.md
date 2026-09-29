# antirez/h3.c 本地部署与技术速查手册

`antirez/h3.c` 是 Redis 创始人 Salvatore Sanfilippo（antirez）为 Apple Silicon 芯片（特别优化 M3/M4/M5 系列）研发的原生端侧 MiniMax-H3（Hailuo）视音频生成推理引擎。该引擎完全采用纯 C（C11）、Objective-C 与 Apple Metal 语言编写，彻底剥离了 Python 解释器、PyTorch、HuggingFace Diffusers、MLX 等任何重型外部运行时，实现了极简、高效、秒级冷启动的原生 DiT（Diffusion Transformer）推理。

---

## 1. 核心设计亮点

* **纯 C/Metal 原生架构**：单二进制文件（`./h3`）配合动态 Metal 着色器驱动，无 Python 运行时依赖与环境冲突。
* **分阶段显存调度**：文本编码、Diffusion 去噪采样、视频/音频 VAE 解码分时复用显存，避免模型组件同时常驻统一内存。
* **Metal 4 与 MPSGraph 硬件加速**：针对 Apple Silicon 原生优化 BF16 矩阵乘法、AdaLN 自适应层归一化、RoPE 旋转位置编码融合算子；在支持的硬件上支持 INT8 动态行量化。
* **SSD 双缓冲流式加载（`--ssd-streaming`）**：仅在统一内存中保留 2 个活跃 DiT 块的显存槽位，其余权重直接从高速 NVMe SSD 异步预取，极大降低超大模型常驻内存门槛。
* **时序速度外推（`--reuse` / `--core-reuse`）**：间隔计算去噪速度并进行中间步外推插值，大幅降低 Transformer 前向计算量。
* **终端原生视觉预览**：借助终端图形协议（Kitty、Ghostty、iTerm2、WezTerm），在去噪采样步进中向终端直接绘制实时视频帧。

---

## 2. 系统环境与前置依赖

### 2.1 硬件要求
* **芯片架构**：Apple Silicon（M3 Max / M4 Max / M5 Max 最佳实测推荐）。
* **统一内存**：
  * 全权重常驻模式：建议 64GB 或 128GB Unified Memory；
  * SSD 流式加载模式（`--ssd-streaming`）：32GB~48GB 统一内存即可启动推理。

### 2.2 基础工具链检测
构建与多媒体封包依赖系统编译器与 FFmpeg 套件：

```bash
# 检查 Clang 与 Make
clang --version
make --version

# 检查 FFmpeg 与 FFprobe（用于原始 PCM 音频与 YUV420P 视频实时无损封装）
ffmpeg -version
ffprobe -version
```

若缺失工具，可通过 Homebrew 安装：
```bash
brew install ffmpeg make
xcode-select --install
```

---

## 3. 本地编译与构建流程

### 3.1 获取源码
```bash
git clone --depth 1 https://github.com/antirez/h3.c.git
cd h3.c
```

### 3.2 编译可执行程序与静态库
项目 `Makefile` 自动链接 Apple 系统底层框架（`Metal`, `Accelerate`, `MetalPerformanceShaders`, `MetalPerformanceShadersGraph`, `Foundation`, `icucore`, `libm`）：

```bash
# 并行多核编译
make -j8
```

编译生成核心产物：
* `./h3`：主命令行与交互式 REPL 推理程序；
* `libh3.a`：封装完整 DiT 采样、文本/视觉编码、VAE 与 Metal 调度的静态库；
* `h3_shaders.metal`：运行时由 Metal API 动态编译加载的 GPU 计算着色器（必须与可执行程序保持相对路径可用）。

### 3.3 验证基础命令
```bash
./h3 --help
```

---

## 4. 自动化测试套件与算子实测

`h3.c` 自带轻量级端到端测试与数值对齐套件，用于在无需下载数十 GB 全量权重的前提下验证本地芯片的硬件算子正确性。

### 4.1 运行测试
```bash
make test
```

### 4.2 本地真实测试指标（Apple M4 Max 实测）
在 Apple M4 Max (128GB RAM, macOS Darwin 27.0.0) 环境下实测结果如下：

```text
./h3_tests
ok: 1768 checks

./h3_audio_gpu_tests
audio primitive weight norm      max abs 5.960464e-08
audio primitive Conv1d           max abs 5.960464e-08
audio primitive ConvTranspose1d  max abs 2.980232e-08
audio primitive SnakeBeta        max abs 1.192093e-07
audio primitive scaled add       max abs 0
audio primitive clip             max abs 0
ok: native AudioVAE Metal primitives match host references

ok: concurrent FFmpeg video/PCM pipes created /tmp/h3-av-mux-test.mp4 (51751 bytes)
```

### 4.3 测试覆盖核心点
1. **宿主确定性与数学逻辑（1768 项检查全部通过）**：
   * 时间轴对齐与画布倍数约束检测；
   * Euler 步进算法与随机数发生器一致性；
   * DiT 速度外推插值算法调度（Reuse Schedule）；
   * Safetensors 头部解析与零拷贝虚拟内存映射；
   * BF16 / FP32 动态精度转换与行排布。
2. **Metal GPU 算子精度验证**：
   * AudioVAE 核心算子（Conv1d, ConvTranspose1d, SnakeBeta 激活函数）实测误差处于 $10^{-7} \sim 10^{-8}$ 级别，完全契合硬件加速标准。
3. **多媒体管道并发封装验证**：
   * 自动调用后台并发 FFmpeg 管道，将原始视频帧流与 PCM 音频流直接复用生成 H.264+AAC 格式的 MP4 容器，无中间临时文件解压损耗。

---

## 5. 模型准备与 CLI 推理实战

### 5.1 模型权重目录布局
从官方或镜像平台下载 MiniMax-H3 safetensors 权重后，其目录结构应符合：
```text
MiniMax-H3/
├── FL2VA/
│   ├── transformer/
│   │   ├── config.json
│   │   └── diffusion_pytorch_model*.safetensors
│   ├── text_encoder/
│   └── audio_vae/
└── tokenizer/
    └── tokenizer.json
```

### 5.2 常用推理模式命令

#### 模式 1：设备与模型信息快速探查
在不加载映射几十 GB 权重的状态下快速校验目录结构与 Metal 设备：
```bash
./h3 -d /path/to/MiniMax-H3 --info
```

#### 模式 2：基础文生视音频（T2V）
根据纯文本提示词生成同步包含视频与音频的 MP4 文件：
```bash
./h3 -d /path/to/MiniMax-H3 \
     -p "A cinematic drone shot of a futuristic cyberpunk city in rain, neon reflections, 4k" \
     -o outputs/cyberpunk.mp4 \
     --width 864 --height 480 \
     --steps 20
```

#### 模式 3：首尾帧锚定过渡生成（FL2VA）
给定起始画面与终止画面，生成平滑过渡的动态视频：
```bash
./h3 -d /path/to/MiniMax-H3 \
     -p "A cat transforms into a robotic panther" \
     --first-frame assets/cat_start.png \
     --last-frame assets/panther_end.png \
     -o outputs/cat_morph.mp4
```

#### 模式 4：多模态参考生视音频（Ref2VA）
指定参考图像、静音视频或指定音轨进行条件引导合成：
```bash
./h3 -d /path/to/MiniMax-H3 \
     -p "Camera pans around the character talking enthusiastically" \
     --ref-image assets/character.png \
     --ref-audio assets/voice.wav \
     -o outputs/dialogue.mp4
```

#### 模式 5：交互式 REPL 终端与实时视觉预览
不传递 `-p` 参数时，`h3.c` 会利用内置 `linenoise` 启动交互式控制台，支持指令记忆与快捷重试，配合 `--show` 参数可在支持图形协议的终端内实时显示每一步降噪预览：
```bash
./h3 -d /path/to/MiniMax-H3 --show --zoom 2
```

---

## 6. 参数速查与显存/速度优化矩阵

### 6.1 基础参数与边界约束表

| 参数项 | 说明 | 约束规则与默认值 |
| :--- | :--- | :--- |
| `-d, --model-dir <PATH>` | 模型 Safetensors 所在根目录 | **必选参数** |
| `-p, --prompt <TEXT>` | 生成提示词文本 | 若缺省则自动进入交互式 REPL 终端 |
| `-o, --output <PATH>` | 输出 MP4 路径 | 默认 `outputs/h3.mp4`；传空字符串 `""` 则跳过封装 |
| `--width <N>`, `--height <N>` | 输出视频分辨率 | **必须为 32 的整数倍**，总面积不得超过 $768 \times 1344$ |
| `--render-width`, `--render-height` | 模型内部降分辨率渲染 | 可先以低分辨率计算再通过 Apple vImage 超分 |
| `--frames <N>` | 生成视频总帧数 | 默认 56；**必须符合公式 $5 + 17 \times n$**（如 22, 39, 56, 73...） |
| `--seconds <N>` | 按秒指定时长 | 按照 24 fps 自动对齐帧数公式，与 `--frames` **互斥** |
| `--steps <N>` | 去噪采样步数 | 默认 20 步；日常快速验证推荐 12~16 步 |
| `--seed <N>` | 随机数种子 | 默认 42 |
| `--profile` | 性能分析剖析 | 打印各阶段（Text/DiT/VAE）的 Metal 耗时与显存占用 |

### 6.2 显存与推理速度加速开关

| 优化开关 | 推荐场景 | 加速/节约显存原理 |
| :--- | :--- | :--- |
| `--ssd-streaming` | **显存受限机型（≤36GB）** | 仅保留 2 个 DiT Block 内存槽位，其余权重流式换入，大幅压低常驻内存 |
| `--token-reduction` | 快速原型预览 | 在 DiT 中间计算块中合并横向相邻视频 Token，计算量降低约 25% |
| `--layers <N>` | 快速验证调试 | 剪枝 DiT 活跃层数，默认 50 层（精确），可选 45 层（快速）或 40 层（极速） |
| `--reuse <N>` | 平滑画质加速 | 间隔执行 Denoiser 前向传递，中间步采用时序外推（1: 精确, 2: 推荐, 3: 激进） |
| `--core-reuse <N>` | 细粒度残差加速 | 仅刷新 Patch 与 Head 层，复用 Transformer 核心残差 |
| `--use-int8-row-fc2` | M4/M5 Max 芯片 | 启用硬件级单缩放 INT8 矩阵乘加速 FC2 层 |

### 6.3 关键互斥与防坑指南

1. **几何与时长边界**：宽度与高度不是 32 的倍数会直接报错终止；帧数如果不匹配 $5 + 17 \times n$ 会被底层自动上取整对齐。
2. **加速选项互斥**：
   * `--reuse` 与 `--core-reuse` **不可同时启用**（报错互斥）；
   * `--ssd-streaming` 与 `--use-int8-row-fc2` **不可同时启用**；
   * `--first-frame` / `--last-frame`（FL2VA）与 `--ref-*` 系列多模态参考参数（Ref2VA）**不可混合使用**。
3. **音频参考输入约束**：
   * `--ref-audio` 最多支持挂载 3 段独立音频，单段时长介于 2~15 秒，总时长不得超过 15 秒；
   * 音频参考必须伴随图像或视频参考同时输入，不能作为单一多模态条件提供。
4. **着色器路径依赖**：运行程序时，`h3_shaders.metal` 必须位于 `./h3` 的工作目录下，否则运行时无法完成 GPU 管道装配。
