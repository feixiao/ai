# antirez/h3 (MiniMax-H3) Apple Silicon 本地部署与运行指南

本项目文档针对 **Mac Studio / MacBook Pro (Apple M4 Max, 128GB 统一内存, macOS)** 环境，提供 Salvatore Sanfilippo（Redis 创始人 antirez）开源的原生专有推理引擎 [**h3.c**](https://github.com/antirez/h3.c) 的完整编译、模型下载、一键生成、交互式 REPL 与进阶优化指南。

---

## 1. 项目简介与硬件匹配分析

**h3.c** 是 antirez 为 **MiniMax-H3（Hailuo）** 视音频生成大模型定制研发的原生 C/Objective-C/Metal 端侧推理引擎。该引擎彻底剥离了 Python 解释器、PyTorch、HuggingFace Diffusers、MLX 等任何重型外部运行时，直接基于 Apple Metal 4 TensorOps 与 MPSGraph 实现毫秒级冷启动与极低显存占用。

### 硬件与模型适配策略 (M4 Max 128GB)

| 运行模式 | 统一内存占用 | 适用场景 | 在 M4 Max (128GB) 上的建议 |
| :--- | :--- | :--- | :--- |
| **全显存常驻 (Metal Resident)** | ~40GB - 60GB | **常规默认模式** | **🔥 最佳主力选择**。可全量装入 128GB 统一内存，极速前向推理，无磁盘 I/O 开销。 |
| **快速预览加速 (`--fast`)** | ~40GB - 50GB | **快速构图与 Prompt 验证** | 启用 14 步采样、速度外推 (`--reuse 2`) 与空间 Token 缩减，生成提速约 2.5x。 |
| **高质量影视档 (`--quality`)** | ~60GB | **终稿成品渲染** | 启用 24 步充分降噪，50 全层 DiT 精细计算，呈现最佳画面细节。 |
| **SSD 流式加载 (`--ssd`)** | ≤ 24GB | **低显存设备体验 / 显存超限保护** | 仅保留 2 个 DiT 块槽位，权重从 SSD 动态双缓冲流式加载。 |

---

## 2. 环境准备与源码编译

macOS 预装的 Clang / Make 工具链和 Metal 驱动已原生支持 h3。

### 2.1 克隆仓库

源码统一放置于 `/Users/frank/wk/github/h3`：

```bash
cd /Users/frank/wk/github
git clone --depth 1 https://github.com/antirez/h3.c.git h3
cd h3
```

### 2.2 编译 Metal 原生版本

```bash
# 并行多核编译
make -j8
```

编译成功后，将在当前目录生成核心组件：
* `h3`：交互式命令行与视频生成主程序。
* `libh3.a`：封装完整 DiT 采样、文本/视觉编码、VAE 与 Metal 调度的静态库。
* `h3_shaders.metal`：运行时由 Metal API 动态编译注入的 GPU 计算着色器。

---

## 3. 模型权重下载与体积优化

MiniMax-H3 是一个原生视音频超大多模态系统，官方全量仓库（包含首尾帧核心模式 FL2VA 与多参考模式 Ref2VA）高达 **~260 GB**。

而在日常创作与工程实践中，文生视频与首尾帧图生视频仅需核心的 **FL2VA** 权重（**约 134 GB**），即可获得完整的音视频生成能力。当前下载脚本已全面优化为**按需精简下载**：

### 3.1 极速下载主力模型 (FL2VA 核心)

```bash
cd /Users/frank/wk/github/ai/h3

# 推荐：使用 ModelScope 阿里魔搭国内源（REST API 直连，零 git-lfs，默认仅下 FL2VA 核心，省 ~125GB）
./download_model.sh

# 一键增量补充下载 Ref2VA 多模态参考权重 (~125GB)
./download_model.sh --ref2va

# 一键清理多余的 Ref2VA 目录与临时缓存以释放磁盘空间 (~64GB)
./download_model.sh --clean

# 或者使用 HuggingFace 官方源下载 Ref2VA
./download_model.sh --ref2va --source huggingface
```

下载完成后，脚本会自动建立软链接至 `/Users/frank/forbuild/h3/MiniMax-H3`，以供推理引擎直接加载。可以通过 `./h3 --info -d ./MiniMax-H3` 验证权重完整性。

---

## 4. 视频生成参数详解与场景化调优

MiniMax-H3 是高参数量的视音频 Diffusion Transformer 模型。在 Apple Silicon (Metal) 环境下，生成速度与画质细节受去噪步数、时序外推、层数剪枝、空间 Token 规模及分辨率多重维度的共同影响。

### 4.1 核心参数深度剖析

1. **去噪步数 (`--steps N`)**：默认 20 步。
   * **原理**：控制 DiT 逆向扩散求解微分方程的离散步数。
   * **调优策略**：
     * `10 ~ 12 步`：快速勾勒主体与动态轮廓，耗时减半；
     * `14 ~ 18 步`：平衡档位，日常出片主体轮廓与动态连贯；
     * `24 ~ 28 步`：高保真档位，呈现丰富光影、微表情与复杂纹理；
     * `> 32 步`：细节收益递减，耗时线性增加。
2. **时序速度外推 (`--reuse N` 与 `--core-reuse N`)**：
   * **原理**：antirez 为端侧定制的时序外推算法（Velocity Extrapolation）。在扩散去噪相邻时间步之间，导数向量变化连续平滑；开启外推后，引擎仅在基准步执行完整 Transformer 前向传播，其余步通过导数外推预测，直接跳过重型计算。
   * `--reuse 1`：精确逐步前向计算，无外推；
   * `--reuse 2`：隔步计算并外推，整体推理速度提升约 **2.0x ~ 2.5x**，画面质感保留度达 95% 以上，**日常最高性价比提速选项**；
   * `--reuse 3`：激进外推，极速预览专用；
   * `--core-reuse N`：残差核心刷新（1 精确，4 快速，6 激进），与 `--reuse` 互斥。
3. **DiT 活跃层数剪枝 (`--layers N`)**：默认 50 层（全量无损）。
   * **原理**：MiniMax-H3 主干 Transformer 共包含 50 个 DiT Block。
   * `--layers 50`：50 层全量运算，保持最大建模能力与细节精度；
   * `--layers 45`：跳过尾部 5 个微调 Block，提速约 10%~15%，人眼视觉几乎无感；
   * `--layers 40`：激进剪枝 10 层，计算量直接减少 20%，生成耗时大幅降低。
4. **空间 Token 缩减 (`--token-reduction`)**：
   * **原理**：在 DiT 中间计算块中，对空间横向相邻的视频 Token 进行成对合并计算，直接将中间层的 Token 序列减半，计算吞吐提升约 25%。
5. **渲染分辨率与内部超分 (`--width`, `--height`, `--render-width`, `--render-height`)**：
   * **原理**：DiT 注意力计算量与空间分辨率呈平方级增长。
   * **超分策略**：指定较低的内部渲染分辨率（如 `--render-width 640 --render-height 384`），DiT 完成轻量计算后，由 macOS 硬件加速的 Apple vImage 高精度滤镜动态上采样至目标输出尺寸（如 `--width 864 --height 480`），成倍提升生成效率。
   * **硬性约束**：所有宽、高数值必须为 **32 的整数倍**。
6. **视频时长与帧数公式 (`--frames N`, `--seconds N`)**：
   * **约束**：帧数必须严格符合 **$5 + 17 \times n$**（如 22 帧、39 帧、56 帧、73 帧）。
   * `22 帧`（n=1，约 0.9 秒）：极致速度验证 Prompt 首选；
   * `56 帧`（n=3，约 2.3 秒）：默认标准镜头长度；
   * `73 帧`（n=4，约 3.0 秒）：完整动态运镜。
7. **硬件级 INT8 加速 (`--use-int8-row-fc2`)**：
   * 在 Apple Silicon M4/M5 芯片上启用硬件级单缩放 INT8 矩阵乘加速 FC2 全连接层，减轻显存带宽与计算压力。

---

### 4.2 场景化黄金参数配置方案

根据实际创作场景，提供四组针对性调优配置：

#### ⚡ 方案 1：极致速度档（如何最快出片）

* **适用场景**：Prompt 构图验证、镜头调度摸索、短镜头秒级试错。
* **核心参数组合**：
  * 去噪步数：`--steps 10`
  * 速度外推：`--reuse 2`
  * 层数剪枝：`--layers 40`
  * Token 缩减：`--token-reduction`
  * 视频帧数：`--frames 22`（约 1 秒短镜头）
  * 内部超分：`--render-width 640 --render-height 384 --width 864 --height 480`
  * 硬件加速：`--use-int8-row-fc2`
* **性能表现**：综合生成耗时缩短至默认全量生成的 **1/4 ~ 1/5**，实现秒级快速产出。
* **一键运行命令**：
  ```bash
  cd /Users/frank/wk/github/ai/h3
  ./generate.sh "A cute cyber kitten walking through neon rain" --lightning
  ```

#### 🎬 方案 2：极致画质档（如何生成最高质量视频）

* **适用场景**：终稿成品输出、高清 4K 放大底片、角色微表情与复杂光影质感。
* **核心参数组合**：
  * 去噪步数：`--steps 28`（或 24~30 步充分去噪）
  * 活跃层数：`--layers 50`（全量 50 层无损运算）
  * 速度外推：不启用 `--reuse`（全步数真实前向求解，避免外推插值微小残差）
  * Token 规模：禁用 `--token-reduction`（全稠密空间 Token，保留发丝级细节）
  * 原生分辨率：`--width 864 --height 480`（原生无插值直出）
  * 视频帧数：`--frames 56` 或 `--frames 73`（标准流畅运镜）
* **性能表现**：耗时相对最长，但发丝细节、材质反光、水流与火焰动态物理规律最为真实完整。
* **一键运行命令**：
  ```bash
  cd /Users/frank/wk/github/ai/h3
  ./generate.sh "A majestic ancient dragon flying through sunset clouds, 4k cinematic" --ultra
  ```

#### ⚖️ 方案 3：平衡日常档（日常主力出片，兼顾画质与效率）

* **适用场景**：日常创意生成、自媒体视音频素材、动态镜头产出。
* **核心参数组合**：
  * 去噪步数：`--steps 14`
  * 速度外推：`--reuse 2`
  * 层数剪枝：`--layers 45`
  * Token 缩减：`--token-reduction`
  * 视频帧数：`--frames 56`（约 2.3 秒）
* **性能表现**：推理速度提速约 **2.5x**，人眼画质保留度达 95% 以上，兼顾效率与画面表现力。
* **一键运行命令**：
  ```bash
  cd /Users/frank/wk/github/ai/h3
  ./generate.sh "A futuristic sports car drifting on a mountain road" --fast
  ```

#### 💾 方案 4：极简显存 / 后台静默档（SSD 双缓冲流式）

* **适用场景**：后台无感运行、并发其他高显存负载任务、显存受限机型。
* **核心参数组合**：
  * 流式加载：`--ssd-streaming`（仅驻留 2 个 DiT 块槽位，显存控制在 ≤24GB）
  * 去噪步数：`--steps 16`
  * 速度外推：`--reuse 2`
* **一键运行命令**：
  ```bash
  cd /Users/frank/wk/github/ai/h3
  ./generate.sh "Drone view of a tropical island, turquoise water" --ssd
  ```

---

### 4.3 基础运行与原生命令行调用

除预设快捷指令外，所有原生 CLI 参数均可自由透传组合：

```bash
# 基础生成命令
./generate.sh "A cute cyber kitten walking through neon rain at night, cinematic lighting"

# 自定义高清长镜头渲染
./generate.sh -p "Sunset over Tokyo skyline with flying cars" \
              -o outputs/tokyo_sunset.mp4 \
              --width 864 --height 480 \
              --frames 73 \
              --steps 24 \
              --layers 50
```

---

## 5. 交互式 REPL 与终端实时预览

不传入提示词时，`h3.c` 会启动基于 `linenoise` 的交互式控制台，支持指令补全与历史记录；若终端支持图形渲染协议（Kitty, Ghostty, iTerm2, WezTerm），则每一步降噪均可在终端中直观呈现画面演化：

```bash
./start_interactive.sh
```

在交互式界面中，可直接输入提示词生成，或通过 `!` 语法动态指定首尾帧与参考素材：
* `!ref-image path/to/image.png`：添加参考图像；
* `!first-frame path/to/start.png`：锚定首帧；
* `!last-frame path/to/end.png`：锚定尾帧；
* `!seed 1234`：切换随机种子。

---

## 6. 进阶生成控制模式

### 6.1 首尾帧过渡动画 (FL2VA)
给定起始帧与终止帧，让模型自动插值推演中间平滑运镜与动态：
```bash
./generate.sh -p "The blooming process of a golden lotus flower" \
              --first-frame assets/lotus_bud.png \
              --last-frame assets/lotus_full.png \
              -o outputs/blooming.mp4
```

### 6.2 多模态参考生视音频 (Ref2VA)
结合角色立绘与背景音频生成动态对话片段：
```bash
./generate.sh -p "The character is talking expressively and smiling" \
              --ref-image assets/character.png \
              --ref-audio assets/dialogue.wav \
              -o outputs/talking_character.mp4
```

---

## 7. 自动化测试与硬件自检

引擎内置了确定性宿主测试套件与 Metal 算子对齐测试，无需挂载真实权重即可全面验证本地 Apple Silicon 硬件加速的完备性：

```bash
./run_tests.sh
```

**实测指标（Apple M4 Max 128GB）**：
* 宿主端纯 C 基础与数学测试：`ok: 1768 checks` 全部通过。
* AudioVAE Metal 算子精度验证：`Conv1d`, `ConvTranspose1d`, `SnakeBeta` 与 Host 参考实现误差保持在 $10^{-7} \sim 10^{-8}$ 级别。
* FFmpeg 并发管道封装：自动完成原始流无损封装生成有效 MP4（H.264+AAC）。

---

## 8. 参数速查表与调优矩阵

### 8.1 速度与画质调优权衡矩阵表

| 核心参数 | 默认值 | 极致速度推荐 | 极致画质推荐 | 对生成速度的影响 | 对画面质量的影响 | 核心调优说明 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`--steps`** | `20` | `10 ~ 12` | `24 ~ 28` | **强正比线性影响** | 步数越高，光影纹理与微动态越细腻 | 10 步成型；14 步平衡；28 步极致；>32 步收益饱和 |
| **`--reuse`** | `1` (关闭) | `2` 或 `3` | 不启用 (或 `1`) | **提速 2.0x ~ 2.5x** | `2` 画面保留度 >95%，`3` 偶有轻微外推残差 | 日常性价比最高的加速开关，与 `--core-reuse` 互斥 |
| **`--layers`** | `50` | `40` | `50` | `40` 提速约 20%，`45` 提速 10% | 剪枝仅略微影响超深层高频细节 | 推荐 45 层作为平衡档，40 层作为极速档 |
| **`--token-reduction`** | 关闭 | 开启 | 关闭 | **提速约 25%** | 中间层 Token 合并，大动态下画面略微软化 | 构图验证与日常推荐开启，终稿关闭 |
| **`--render-width/height`** | 同 output | `640x384` | 不使用 (原生渲染) | **提速约 30% ~ 40%** | 低分辨率渲染后经 Apple vImage 硬件超分 | 输出分辨率保持 864x480，内部降分辨率大幅减负 |
| **`--frames`** | `56` | `22` (约 0.9s) | `56` 或 `73` (约 3s) | 帧数越少，3D 注意力越快 | 决定视频总时长与运镜跨度 | 必须严格符合公式 $5 + 17 \times n$ |
| **`--use-int8-row-fc2`** | 关闭 | 开启 (M4/M5 Max) | 开启 | 提速 5% ~ 10% | 硬件级单缩放量化，精度损失几近无感 | 仅支持 Apple M4 / M5 Max 系列 Metal 硬件 |
| **`--ssd-streaming`** | 关闭 | 关闭 (全显存最快) | 关闭 | 引入 NVMe SSD 双缓冲 I/O 延迟 | 无任何算法画质损失 | 将统一内存占用严格压至 ≤24GB，低显存保底 |
| **`--show`** | 开启 | 关闭 (后台批处理) | 开启 (终端实时监看) | 终端 ANSI 图形绘制占用少量 I/O | 不影响生成视频文件质量 | 在 Kitty/Ghostty/iTerm2 下提供单步渐进预览 |

### 8.2 常用命令行选项速查

| 参数 | 默认值 | 说明与约束 |
| :--- | :--- | :--- |
| `-d, --model-dir <PATH>` | 必选 | MiniMax-H3 权重所在目录 |
| `-p, --prompt <TEXT>` | 缺省进入 REPL | 文本提示词 |
| `-o, --output <PATH>` | `outputs/h3_<ts>.mp4` | 目标视频生成路径 |
| `--width`, `--height` | `864x480` | 分辨率，**必须为 32 的整数倍** |
| `--render-width`, `--render-height` | 缺省同 output | 内部 DiT 计算分辨率，由 vImage 超分 |
| `--frames <N>` | `56` | 视频帧数，**必须符合 $5 + 17 \times n$ 公式** |
| `--seconds <N>` | 互斥 | 按秒指定时长，自动换算帧数公式 |
| `--steps <N>` | `20` | 去噪步数（12~24 推荐） |
| `--reuse <N>` | `1` | 速度外推（1: 精确, 2: 推荐, 3: 激进） |
| `--layers <N>` | `50` | DiT 计算层数（50: 全量, 45: 快速, 40: 极速） |
| `--token-reduction` | 关闭 | 中间计算块空间 Token 成对合并 |
| `--show` | 开启 | 启用终端实时视觉预览 |
| `--zoom <N>` | `2` | 视网膜屏图像缩放因子 |

### 8.3 关键互斥与规则避坑

1. **分辨率与时长限制**：宽度与高度非 32 的倍数会报错拒绝启动；帧数公式不满足 $5 + 17 \times n$ 会被向上对齐。
2. **加速参数互斥**：
   * `--reuse` 与 `--core-reuse` **不可同时开启**；
   * `--ssd-streaming` 与 `--use-int8-row-fc2` **不可同时开启**；
   * 首尾帧控制（`--first-frame` / `--last-frame`）与多模态参考（`--ref-*`）**不可混用**。
3. **音频参考输入规范**：
   * `--ref-audio` 仅能挂载 2~15 秒的音频文件，且总长不得超过 15 秒；
   * 音频参考必须配合图片或视频同时输入，不可单独作为唯一的参考条件。
