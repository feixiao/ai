# HunyuanVideo 1.5 ComfyUI 本地工作流与端到端自动化测试

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![ComfyUI Compatible](https://img.shields.io/badge/ComfyUI-v0.37.4%20Native-green.svg)](https://github.com/comfyanonymous/ComfyUI)
[![Model](https://img.shields.io/badge/Model-HunyuanVideo%201.5%20(8.3B)-blueviolet.svg)](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5)

本项目为腾讯混元开源的 **HunyuanVideo 1.5** 打造，提供 **ComfyUI 官方原生节点链路**、**API 格式工作流**、**LM Studio 视频提示词智能扩写** 与 **命令行端到端自动化测试脚本**，专门针对 Apple Silicon (Mac Studio / M4 Max) 统一内存架构调优。

> 上游仓库：
> * 原版 13B 模型 —— <https://github.com/Tencent-Hunyuan/HunyuanVideo>
> * 本目录对应的 1.5 版本 —— <https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5>

---

## 1. HunyuanVideo 1.5 核心特性

- **轻量化 DiT 架构**：仅 **8.3B** 参数（相比初代 13B 大幅瘦身），却达到开源视频模型的 SOTA 画质，是本机 (M4 Max / 128GB) 少数**真正跑得动**的高质量视频模型。
- **双任务统一**：同一套框架同时支持**文生视频 (T2V)** 与**图生视频 (I2V)**，图生视频额外引入 SigLIP 视觉编码器做起始帧语义对齐。
- **双文本编码器**：
  - `Qwen2.5-VL-7B` —— 主力多模态语义编码器，负责理解自然语言中的空间、动作与镜头描述；
  - `ByT5-small-glyphXL` —— 字形编码器，专门负责画面中**文字 / 中文字形**的生成与还原。
- **3D VAE**：空间下采样 **16 倍**、时间下采样 **4 倍**，因此分辨率必须是 **16 的整数倍**、帧数必须满足 **length = 4n + 1**。
- **可选 1080P 超分**：官方另有 `1080p_sr_distilled` 扩散模型 + Latent Upsampler，可把 720p 结果二次放大到 1080p（本目录默认未下载，见第 3 节）。
- **MPS 友好**：ComfyUI 内核已声明 `supported_inference_dtypes = [fp16, bf16, fp32]`，fp16 权重可在 Apple Silicon 上原生推理。

---

## 2. 目录结构

```text
ComfyUI/hunyuan_video_1.5/
├── README.md                              # 本说明文档
├── download_models.sh                     # 模型一键下载脚本 (支持 all / t2v / i2v / lite 四种模式)
├── prompt_enhancer.py                     # 视频提示词增强引擎 (LM Studio 客户端 + 规则兜底)
├── hunyuan_video15_test.py                # 命令行端到端测试主脚本
├── workflows/
│   ├── hunyuan_video_1.5_t2v_api.json     # 文生视频 (API 格式, 供脚本直接调用)
│   └── hunyuan_video_1.5_i2v_api.json     # 图生视频 (API 格式)
├── assets/
│   └── i2v_start_sample.png               # 图生视频起始帧示例 (1280x720)
├── tests/                                 # pytest 回归测试 (56 个用例)
│   ├── conftest.py
│   ├── test_workflows.py                  # 工作流结构与连线完整性校验
│   ├── test_cli_runner.py                 # CLI 参数解析 / 参数注入 / 模型前置校验
│   └── test_prompt_enhancer.py            # 帧数换算 / 分辨率对齐 / 扩写降级
└── output/                                # 生成的 mp4、dry-run 工作流与运行报告 (已 gitignore)
```

> 说明：ComfyUI **官方内置模板**中已自带 HunyuanVideo 1.5 的可视化画布工作流（含 1080P 超分分支），
> 位于 ComfyUI 菜单 `Workflows → Browse Templates → Video`，可直接使用；
> 本目录提供的是**可脚本化调用的 API 格式工作流**，二者模型文件完全通用。

---

## 3. 模型下载与配置分档 (Apple Silicon 优化)

所有模型均来自 ComfyUI 官方 repackaged 仓库
[`Comfy-Org/HunyuanVideo_1.5_repackaged`](https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged)，
与 ComfyUI 内置模板引用的权重**完全一致**。

| 角色 | 文件名 | 目标目录 | 体积 |
| :--- | :--- | :--- | ---: |
| **文生视频主模型** | `hunyuanvideo1.5_720p_t2v_fp16.safetensors` | `models/diffusion_models/` | 16.65 GB |
| **图生视频主模型** | `hunyuanvideo1.5_720p_i2v_fp16.safetensors` | `models/diffusion_models/` | 16.65 GB |
| **语义文本编码器** | `qwen_2.5_vl_7b_fp8_scaled.safetensors` | `models/text_encoders/` | 9.38 GB |
| **字形编码器** | `byt5_small_glyphxl_fp16.safetensors` | `models/text_encoders/` | 0.44 GB |
| **专用 VAE** | `hunyuanvideo15_vae_fp16.safetensors` | `models/vae/` | 2.52 GB |
| **视觉编码器 (仅 I2V)** | `sigclip_vision_patch14_384.safetensors` | `models/clip_vision/` | 0.86 GB |
| **合计** | | | **~46.5 GB** |

### 可选：1080P 超分套装（默认不下载）

| 文件名 | 目标目录 | 体积 |
| :--- | :--- | ---: |
| `hunyuanvideo1.5_1080p_sr_distilled_fp8_scaled.safetensors` | `models/diffusion_models/` | 8.34 GB |
| `hunyuanvideo15_latent_upsampler_1080p.safetensors` | `models/latent_upscale_models/` | 0.20 GB |

### 一键下载

```bash
cd ComfyUI/hunyuan_video_1.5

./download_models.sh all     # 完整套装 T2V + I2V (~46.5GB, 默认)
./download_models.sh t2v     # 仅文生视频所需的 4 个文件 (~29GB)
./download_models.sh i2v     # 仅图生视频增量 (CLIP Vision + I2V 主模型, ~17.5GB)
./download_models.sh lite    # 额外补 480p 双档模型, 便于快速迭代

# 自定义模型根目录 (默认 /Users/frank/ComfyUI/models)
COMFY_MODELS=/path/to/ComfyUI/models ./download_models.sh all
```

下载完成后请在 ComfyUI 界面点击右侧菜单的 **刷新** 按钮以识别新模型。

> ⚠️ **不要用 `hf download` CLI 下载本套权重**。本机实测 `hf` CLI 1.9.0 在下载
> `qwen_2.5_vl_7b_fp8_scaled.safetensors` 时会**卡死在 256,000,000 字节**不再前进
> （进程存活但无网络活动），且均速仅约 0.8 MB/s。
> 本脚本改用 `curl` 断点续传 + stall 检测 + safetensors 结构校验后，实测稳定跑到
> **约 6.9 MB/s**，完整 46.5GB 套装预计约 **2 小时**。
>
> 另一个常见陷阱：**只比对文件大小无法发现损坏**。多线程分块下载中断后可能留下
> "大小正确但中间有空洞"的文件，ComfyUI 加载时才会报张量解析错误。
> 本脚本会解析 safetensors 头部 JSON，校验各张量 `data_offsets` 的末端是否与文件
> 实际大小严格吻合，从而可靠识别截断与空洞。

### 已知的链路特性

| 观测项 | 实测值 |
| :--- | :--- |
| `curl` 单流稳态吞吐 | **~6.9 MB/s** |
| `curl` 4 流并发聚合 | ~3.97 MB/s（**并发无收益，说明是链路带宽瓶颈**） |
| `hf-mirror.com` | 1.96 MB/s（**比直连更慢**，本机无需镜像） |
| `hf` CLI 1.9.0 | 0.8 MB/s，且会 stall |

因此脚本默认直连 `huggingface.co`；若你的网络环境直连不稳，可用
`HF_ENDPOINT=https://hf-mirror.com ./download_models.sh t2v` 切换镜像。

### 💡 为什么主模型用 fp16 而不是 fp8 / GGUF？

| 方案 | 体积 | Mac 推理表现 | 结论 |
| :--- | :--- | :--- | :--- |
| **fp16 (本目录默认)** | 16.65 GB | MPS 原生支持，无额外反量化开销 | ✅ **首选**，128GB 统一内存毫无压力 |
| fp8_scaled | 8.34 GB | MPS 不支持 fp8 矩阵乘，每步需动态反量化，**明显变慢** | 仅在内存紧张时降级使用 |
| GGUF | — | HunyuanVideo **1.5 目前无可用 GGUF 转换**（`city96/HunyuanVideo-gguf` 仅覆盖初代 13B） | 不适用 |

> 文本编码器 `Qwen2.5-VL-7B` 官方仅提供 `fp8_scaled` 与全量 fp16 两个版本，
> 本目录沿用官方模板的 `fp8_scaled`（省 7GB 内存），文本编码只执行一次，反量化开销可忽略。

---

## 4. 官方采样参数与档位对照

下表取自 ComfyUI 内置模板中 Hunyuan 官方给出的参数说明：

| 档位 | cfg | shift | 官方步数 | 模板默认步数 |
| :--- | ---: | ---: | ---: | ---: |
| 480p_t2v | 6 | 5 | 50 | 20 |
| 480p_i2v | 6 | 5 | 50 | 20 |
| **720p_t2v** | **6** | **7** | 50 | **20** |
| **720p_i2v** | **6** | **7** | 50 | **20** |
| 1080p_sr_distilled | 1 | 2 | 50 | 8（超分分支） |

- `shift` 通过 `ModelSamplingSD3` 节点注入。ComfyUI 内核中 `HunyuanVideo15.sampling_settings` 已内置 `shift=7.0`，
  因此 `BasicScheduler` 直接读取原始 UNET 输出即可得到正确的 sigma 调度（本目录工作流严格遵循官方连线方式）。
- 官方 50 步在 Apple Silicon 上耗时过长，模板与本目录均默认使用 **20 步**；追求画质可用 `--steps 50`。

---

## 5. 本地 LM Studio 提示词扩写引擎

视频生成对提示词的要求与生图不同：**必须显式描述"动作随时间如何演变"与"镜头怎么运动"**。

`prompt_enhancer.py` 提供两级能力：

1. **LLM 扩写（优先）**：调用本地 LM Studio 的 OpenAI 兼容接口，System Prompt 强制模型输出**单段英文视频提示词**，
   必须覆盖 `主体细节 / 动作时序 / 镜头语言 / 光影氛围` 四个维度，并禁止输出任何前后缀说明。
2. **规则兜底（离线可用）**：LM Studio 不可用时，自动降级到内置风格模板库（`STYLE_PRESETS`），
   把用户描述与风格化的镜头/光照/运动词汇拼装为英文提示词，**零显存、零延迟、不中断流水线**。

### 风格预设

| 预设 | 镜头语言 | 光影与质感 |
| :--- | :--- | :--- |
| `cinematic` | 电影感推轨 + 缓慢环绕，浅景深，24mm 变形宽银幕 | 体积光、金色轮廓光、胶片颗粒、青橙调色 |
| `photorealistic` | 手持纪实镜头，自然微抖，真实焦段 | 自然日光、物理正确的阴影与材质响应 |
| `anime` | 动画式快速横摇，速度线，透视冲击 | 赛璐璐高光、高饱和、锐利线稿 |
| `cyberpunk` | 低角度跟拍，湿地反射滑动 | 霓虹青紫实用光、强泛光、体积雾、色散 |
| `nature` | 航拍缓慢推进，柔和视差 | 大气雾霭、林间暖阳、自然色彩科学 |
| `general` | 稳定中景轻推 | 均衡自然光 |

### 推荐模型

- **`qwen/qwen3-vl-8b`（黄金首选 ⭐）**：本机实测单次扩写约 **2 秒**，词汇分布与 Qwen2.5-VL 文本编码器同源，契合度最高。
- 低显存设备可降级 `qwen2.5-3b-instruct`，或直接用 `--no-enhance` 关闭扩写。

---

## 6. 命令行端到端测试

### 基础用法

```bash
# 1. 文生视频 · 快速验证档 (2.5 秒 / 61 帧 / 8 步)
python hunyuan_video15_test.py --desc "雨夜霓虹街道上, 一只机甲猫抖落雨水后缓步向前" \
       --style cyberpunk --duration 2.5 --steps 8

# 2. 文生视频 · 官方画质档 (5 秒 / 121 帧 / 20 步)
python hunyuan_video15_test.py --desc "纸飞机从摩天大楼顶被抛出, 穿过城市峡谷飞向夕阳" --steps 20

# 3. 竖直构图 (9:16, 720x1280)
python hunyuan_video15_test.py --desc "雪山之巅的日出云海" --aspect 9:16 --style nature

# 4. 图生视频 (起始帧自动上传到 ComfyUI input 目录)
python hunyuan_video15_test.py --mode i2v --image assets/i2v_start_sample.png \
       --desc "霓虹城市中的剪影人物缓缓抬起手臂" --duration 2.5

# 5. 480p 提速档 (需先 ./download_models.sh lite)
python hunyuan_video15_test.py --desc "海浪拍打礁石" --model-size 480p --duration 2.5

# 6. Dry-Run: 仅做扩写与工作流装配校验, 不提交生成 (模型未下载也可运行)
python hunyuan_video15_test.py --desc "赛博朋克飞行汽车" --dry-run
```

### 参数一览表

| 参数 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `--mode` | `t2v` | `t2v` 文生视频 / `i2v` 图生视频 |
| `--desc` | 示例中文短句 | 用户极简描述 |
| `--image` | — | **i2v 必填**，起始帧图片路径（脚本会 POST 到 `/upload/image`） |
| `--style` | `cinematic` | 风格预设（见第 5 节） |
| `--size` | 自动 | 显式分辨率，如 `1280x720`，会向下对齐到 16 的倍数 |
| `--aspect` | `16:9` | 长宽比：`16:9` / `9:16` / `1:1` / `4:3` / `3:4` / `21:9` |
| `--duration` | `5.0` | 时长（秒），自动换算为 `4n+1` 帧 |
| `--fps` | `24` | 帧率 |
| `--model-size` | `720p` | `720p` / `480p` |
| `--steps` | `20` | 采样步数（官方 50） |
| `--cfg` | 官方预设 `6.0` | CFG 引导系数 |
| `--shift` | 官方预设 `7.0` | `ModelSamplingSD3` shift |
| `--seed` | `-1` | 随机种子 |
| `--comfy-host` | `127.0.0.1:8188` | ComfyUI 地址 |
| `--lmstudio-host` | `127.0.0.1:1234` | LM Studio 地址 |
| `--llm-model` | 自动优选 | 指定扩写模型 |
| `--no-enhance` | 关闭 | 直接用 `--desc` 原文，不做扩写 |
| `--comfy-models` | `/Users/frank/ComfyUI/models` | 模型根目录（用于前置校验） |
| `--output` | `./output` | 产物目录 |
| `--dry-run` | 关闭 | 只装配工作流并保存，不提交生成 |
| `--timeout` | `3600` | 等待生成完成的最大秒数 |

### 脚本内置的三道防护

1. **服务连通性检查** —— ComfyUI 离线直接报错并给出启动命令；LM Studio 离线仅告警并自动降级扩写。
2. **模型文件前置校验** —— 生成前逐个检查 6 个权重文件是否就位，缺失时**直接列出文件名与目标目录**，避免浪费一次漫长的排队。
3. **产物落盘 + 运行报告** —— 从 `/history/{prompt_id}` 解析 `SaveVideo` 节点产物并用 `/view` 下载 mp4，
   同时写出 `output/report_<id>.json`（含步数、cfg、shift、种子、耗时、引擎等完整元数据，便于回归对比）。

---

## 7. 在 ComfyUI Web 画布中使用

### 方式一：直接用官方内置模板（推荐）

1. 启动 ComfyUI 后打开 `http://127.0.0.1:8188`；
2. 菜单 `Workflows → Browse Templates → Video`，选择 **Hunyuan Video 1.5 720p T2V / I2V**；
3. 若节点缺模型，工作流内的 Markdown 便签会给出下载链接；
4. `Ctrl+Enter` 排队生成。

内置模板额外包含 **1080P 超分分支**与 **EasyCache 加速节点**（默认处于 Bypass 状态），
选中节点按 `Ctrl+B` 即可启用。

### 方式二：导入本目录的 API 工作流

`workflows/*_api.json` 是 **API 格式**（用于脚本调用），与画布格式不通用。
如需在画布中查看图形化版本，请直接使用内置模板，二者的模型文件与参数完全一致。

---

## 8. Apple Silicon 性能调优要点

在 MPS 后端运行 8.3B 级 DiT 视频模型，耗时由以下因素共同支配：

1. **帧数是线性成本，分辨率是平方成本**
   `EmptyHunyuanVideo15Latent` 中 `1280x720` 的 token 数远高于 `848x480`（后者约 1/2.3），
   注意力计算量为 $O(N^2)$。**先把 `--duration` 降到 2.5 秒（61 帧）、必要时再降分辨率**，收益最直接。
2. **步数直接线性影响总时长**
   官方 50 步 → 默认 20 步可省 60% 时间；快速验证可压到 `--steps 8`。
3. **VAE 解码是独立瓶颈，且是"全帧一次解码"**
   121 帧 720p 的解码本身就可能占用数分钟。工作流中另有 `VAEDecodeTiled` 分支（官方模板默认 Bypass），
   内存吃紧时可改用它。
4. **CFG 双前向**
   `cfg=6` 且提供负向提示词时，每步需执行正向 + 负向**两次**完整 DiT 前向。
   代价换来了明显的画质与指令遵循度，**不建议在 720p 画质档关闭**。
5. **内存占用粗算（128GB 完全够用）**
   主模型 16.65GB + 文本编码器 9.38GB + 字形 0.44GB + VAE 2.52GB ≈ **29GB 常驻**，
   加上注意力激活与 VAE 解码峰值，建议预留 **40–50GB**。
   ComfyUI 默认的智能显存管理会在文本编码后卸载 CLIP，实际峰值更友好。

### 加速手段（按性价比排序）

| 手段 | 效果 | 代价 |
| :--- | :--- | :--- |
| `--duration 2.5`（61 帧） | 耗时约减半 | 视频更短 |
| `--steps 8` | 耗时约 -60% | 细节与运动质量下降 |
| `--model-size 480p` | 显著加速 | 需另下 480p 权重；分辨率上限降低 |
| 启用内置模板的 `EasyCache` | 官方称可提速 | 画质轻微损失 |

---

## 9. 运行单元测试套件

```bash
# 在仓库根目录执行
python3.13 -m pytest ComfyUI/hunyuan_video_1.5/tests/ -v
```

覆盖范围（56 个用例，全部离线，不发起网络请求）：

| 测试文件 | 覆盖内容 |
| :--- | :--- |
| `test_workflows.py` | T2V/I2V 工作流 JSON 可解析、节点连线指向有效、必备节点齐全、帧数满足 4n+1、分辨率满足 16 倍数、shift 为官方值、`VAEDecode → CreateVideo → SaveVideo` 链路完整 |
| `test_cli_runner.py` | 参数解析与覆盖、主机地址归一化、参数注入正确且不污染模板、480p 档位切换、官方预设表完整性、模型文件前置校验（含 I2V 额外依赖 SigLIP） |
| `test_prompt_enhancer.py` | 帧数换算边界、分辨率 16 对齐、长宽比推断、离线时降级为规则扩写、未知风格/长宽比回退、风格预设完整性 |

---

## 10. 实测结果

### 环境

| 项目 | 值 |
| :--- | :--- |
| 硬件 | Mac Studio · Apple M4 Max · 128GB 统一内存 |
| 系统 | Darwin 27.0.0 (macOS 26) |
| ComfyUI | v0.37.4（前端 1.52.7，模板 0.11.69） |
| 后端 | PyTorch MPS，fp16 权重 |
| 扩写模型 | `qwen/qwen3-vl-8b` @ LM Studio (:1234) |

### 端到端耗时

> 状态：**待实跑填充**。模型下载完成后由 `hunyuan_video15_test.py` 实测写入，
> 每次运行同时会落盘 `output/report_<prompt_id>.json`。

| 档位 | 分辨率 | 帧数 | 步数 | cfg | shift | 总耗时 |
| :--- | :--- | ---: | ---: | ---: | ---: | :--- |
| T2V 快速验证 | 1280x720 | 61 | 8 | 6 | 7 | 待测 |
| T2V 官方画质 | 1280x720 | 121 | 20 | 6 | 7 | 待测 |
| I2V 快速验证 | 1280x720 | 61 | 8 | 6 | 7 | 待测 |

---

## 11. 故障排查

| 现象 | 原因与解法 |
| :--- | :--- |
| `value not in list: unet_name / clip_name / vae_name` | 对应模型文件未下载到位或软链接失效 → 执行 `./download_models.sh`，然后在 ComfyUI 点击"刷新" |
| `DualCLIPLoader` 报 `type` 非法 | 必须选择 `hunyuan_video_15`（**不是** `hunyuan_video`，后者是初代 13B 的编码器类型） |
| 帧数报错 / 输出画面闪烁跳帧 | 帧数必须是 `4n+1`（如 61、121）；分辨率必须是 16 的整数倍 |
| OOM / 内存不足 | 降低 `--duration`、改用 `--model-size 480p`，或把 UNETLoader 的 `weight_dtype` 改为 `fp8_e4m3fn` |
| 画面中文字/中文标点糊成一团 | 确认 `byt5_small_glyphxl_fp16.safetensors` 已加载；该字形编码器专治文字渲染 |
| VAE 解码阶段长时间无输出 | 属正常现象，121 帧 720p 解码本身耗时数分钟 |
| i2v 报找不到起始帧 | 确认 `--image` 路径存在；脚本会先 POST `/upload/image` 再回填节点 |
| i2v 生成结果与原图差异过大 | I2V 采用 SigLIP 语义对齐而非逐像素约束，动作幅度大时主体会漂移，属模型特性 |

---

## 12. 与初代 HunyuanVideo (13B) 的关系

你最初提供的 <https://github.com/Tencent-Hunyuan/HunyuanVideo> 是 **2024 年 12 月开源的初代 13B 模型**，
其权重体积与算力需求都远超本机舒适区（fp16 主模型 25.65GB，且为全注意力架构）。
ComfyUI 目前仍然保留它的节点类型（`DualCLIPLoader` 的 `hunyuan_video` 类型、
`EmptyHunyuanLatentVideo` 节点、`hunyuan_video_text_to_video` 内置模板）。

**本目录聚焦 1.5 版本**：参数量减少 36%，画质反而更强，且原生支持 I2V 与 1080P 超分，
是 Apple Silicon 上更现实的选择。若后续确实需要对照初代 13B，可参考
`city96/HunyuanVideo-gguf` 的 Q4_K_M 量化（7.88GB）版本。
