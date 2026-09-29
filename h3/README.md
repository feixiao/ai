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

## 3. 模型权重下载

MiniMax-H3 模型权重（包含 Transformer DiT、Text Encoder、Audio VAE、Video VAE 及 Tokenizer）体积较大。推荐在 `/Users/frank/wk/github/ai/h3` 目录下直接调用自动化脚本下载：

### 3.1 极速下载主力模型（国内推荐 ModelScope）

```bash
cd /Users/frank/wk/github/ai/h3

# 使用阿里魔搭社区镜像高速下载（国内首选）
./download_model.sh /Users/frank/forbuild/h3/models/MiniMax-H3 modelscope

# 或者使用 HuggingFace 镜像源下载
./download_model.sh /Users/frank/forbuild/h3/models/MiniMax-H3 hf-mirror
```

下载完成后，脚本会自动建立软链接至 `/Users/frank/forbuild/h3/MiniMax-H3`，以供推理引擎直接加载。

---

## 4. 运行与使用方式

在 `/Users/frank/wk/github/ai/h3` 目录下，提供了一系列开箱即用的快捷代理脚本，自动衔接底层运行环境与 Metal 显存配额调优。

### 4.1 一键生成视频 (T2V)

#### 基础文本生成视频
```bash
./generate.sh "A cute cyber kitten walking through neon rain at night, cinematic lighting"
```

#### 极速预览档（Fast Preset）
去噪采样 14 步，启用 2 阶速度外推与 Token 合并：
```bash
./generate.sh "A futuristic sports car drifting on a mountain road" --fast
```

#### 电影画质档（Quality Preset）
去噪采样 24 步，DiT 50 层全量运算：
```bash
./generate.sh "A majestic ancient dragon flying through sunset clouds, 4k resolution" --quality
```

#### 显存极简流式档（SSD Preset）
采用双缓冲流式加载，适合后台并发展开其他任务时使用：
```bash
./generate.sh "Drone view of a tropical island, turquoise water" --ssd
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

## 8. 参数速查表与避坑指南

### 常用命令行选项速查

| 参数 | 默认值 | 说明与约束 |
| :--- | :--- | :--- |
| `-d, --model-dir <PATH>` | 必选 | MiniMax-H3 权重所在目录 |
| `-p, --prompt <TEXT>` | 缺省进入 REPL | 文本提示词 |
| `-o, --output <PATH>` | `outputs/h3_<ts>.mp4` | 目标视频生成路径 |
| `--width`, `--height` | `864x480` | 分辨率，**必须为 32 的整数倍** |
| `--frames <N>` | `56` | 视频帧数，**必须符合 $5 + 17 \times n$ 公式** |
| `--seconds <N>` | 互斥 | 按秒指定时长，自动换算帧数公式 |
| `--steps <N>` | `20` | 去噪步数（12~24 推荐） |
| `--show` | 开启 | 启用终端实时视觉预览 |
| `--zoom <N>` | `2` | 视网膜屏图像缩放因子 |

### 关键互斥与规则避坑

1. **分辨率与时长限制**：宽度与高度非 32 的倍数会报错拒绝启动；帧数公式不满足 $5 + 17 \times n$ 会被向上对齐。
2. **加速参数互斥**：
   * `--reuse` 与 `--core-reuse` **不可同时开启**；
   * `--ssd-streaming` 与 `--use-int8-row-fc2` **不可同时开启**；
   * 首尾帧控制（`--first-frame` / `--last-frame`）与多模态参考（`--ref-*`）**不可混用**。
3. **音频参考输入规范**：
   * `--ref-audio` 仅能挂载 2~15 秒的音频文件，且总长不得超过 15 秒；
   * 音频参考必须配合图片或视频同时输入，不可单独作为唯一的参考条件。
