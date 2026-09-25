# Qwen-Image-2.1 ComfyUI 本地工作流与智能提示词扩写系统

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![ComfyUI Compatible](https://img.shields.io/badge/ComfyUI-Native%20%2F%20GGUF-green.svg)](https://github.com/comfyanonymous/ComfyUI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

本项目专为阿里开源的 **Qwen-Image-2.1** 图像生成模型打造，提供**本地化极简描述自动扩写、端到端自动化测试脚本、ComfyUI 官方标准画布工作流以及轻量自定义节点**。

---

## 1. Qwen-Image-2.1 核心特性

- **架构创新**：基于 70 亿参数（7B）的 32 层 Single-Stream DiT（单流 Diffusion Transformer）架构，统一了文本到图像生成与多参考图编辑。
- **高维语义理解**：采用 **Qwen3-VL** 作为视觉与文本编码器，相比传统 CLIP/T5 具有质的飞跃，擅长理解自然语言中的空间方位、物理材质及复杂逻辑。
- **原生 2K 与 RGBA**：支持直接原生输出 2048×2048 细节分辨率，且原生支持 RGBA 真实透明通道渲染。
- **专用 VAE**：采用 16 通道专用 VAE 架构（请勿与 SDXL/FLUX/Wan VAE 混用）。

---

## 2. 目录结构

```text
ComfyUI/qwen_image_2.1/
├── README.md                      # 本说明文档
├── prompt_expander.py             # 核心提示词扩写引擎（LM Studio 客户端 + 启发式兜底）
├── qwen_image21_test.py           # 命令行端到端测试主脚本（自动化调用全流程）
├── workflows/
│   ├── qwen_image_2.1_t2i_canvas.json   # ComfyUI Web 画布工作流（直接拖入浏览器）
│   └── qwen_image_2.1_api.json          # ComfyUI API 格式工作流模板（供脚本调用）
├── custom_nodes/
│   └── ComfyUI-LMStudio-Prompt/   # ComfyUI 专用节点：画布中直接连线实时扩写
│       ├── __init__.py
│       └── lmstudio_prompt_node.py
├── tests/                         # 自动化测试用例（覆盖扩写、CLI、工作流与节点）
└── output/                        # 自动生成的图像与测试日志存储目录
```

---

## 3. 模型下载与配置分档 (Apple Silicon / Mac 优化)

请将所需模型放置在您的 ComfyUI 模型目录中（默认路径通常为 `~/ComfyUI/models/`）：

| 模型分类 | 推荐文件名 (GGUF 方案，首选) | 官方 SafeTensors 方案 | 存放目录 |
| :--- | :--- | :--- | :--- |
| **Diffusion 主模型** | `qwen_image_2.1-Q8_0.gguf` 或 `Q4_K_M` | `qwen_image_2.1_int8_convrot.safetensors` | `models/unet/` 或 `models/diffusion_models/` |
| **文本编码器** | `Qwen3VL-8B-Instruct-Q4_K_M.gguf` | `qwen3vl_8b_fp8_scaled.safetensors` | `models/clip/` 或 `models/text_encoders/` |
| **VAE 解码器** | `qwen_image_2.1_vae_bf16.safetensors` | 官方 safetensors | `models/vae/` |

> 💡 **模型来源**：
> - 官方模型仓库：[Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1)
> - GGUF 社区量化：Hugging Face 搜索 `Qwen-Image-2.1-GGUF`。

---

## 4. 本地 LM Studio 提示词扩写引擎

本系统能够将用户的一句极简描述自动扩充为影视级、高细节的结构化英文 Prompt。

### 运行机制
1. 脚本默认请求本地运行在 `1234` 端口的 LM Studio（`http://127.0.0.1:1234/v1`）。
2. 自动检测 LM Studio 当前挂载的模型（如 `google/gemma-4-26b-a4b-qat`、`qwen3.8-27b` 等）。
3. 内置 System Prompt 会指导 LLM 补充**主体微观细节、光影体积感、空间构图与镜头焦段**。
4. **自动降级保护**：当 LM Studio 离线或超时，系统自动启用内置的高品质启发式规则库扩写，保证工作流不中断。

---

## 5. 命令行端到端测试 (`qwen_image21_test.py`)

您无需打开浏览器，在终端一条命令即可完成从扩写、组装参数、提交 ComfyUI 到拉取产物全流程：

### 基础测试命令

```bash
# 1. 默认测试（极简描述）
python qwen_image21_test.py --desc "雨夜小巷里的机甲猫"

# 2. 选定艺术风格（cinematic / photorealistic / anime / cyberpunk / general）
python qwen_image21_test.py --desc "雪山湖泊日落" --style cinematic

# 3. 指定长宽比与采样步数
python qwen_image21_test.py --desc "少女华丽晚礼服半身像" --style photorealistic --aspect 3:4 --steps 24

# 4. Dry-Run 模式（仅执行扩写与参数组装校验，无需 ComfyUI 运行）
python qwen_image21_test.py --desc "赛博朋克飞行汽车" --dry-run
```

### 参数一览表
- `--desc`: 用户输入的极简短句。
- `--style`: 风格预设（`cinematic`, `photorealistic`, `anime`, `cyberpunk`, `general`）。
- `--aspect`: 显式指定比例（`1:1`, `16:9`, `9:16`, `4:3`, `3:4`）。
- `--steps`: 迭代步数，默认 24（推荐 20-28 步）。
- `--seed`: 随机种子（默认 `-1` 自动随机生成）。
- `--comfy-host`: ComfyUI 地址（默认 `127.0.0.1:8000` 适配 Comfy Desktop；源码版一般为 `127.0.0.1:8188`）。
- `--lmstudio-host`: LM Studio 地址（默认 `127.0.0.1:1234`）。
- `--dry-run`: 调试模式，生成组装完成的 API JSON 并退出。

---

## 6. ComfyUI Web 画布工作流与自定义节点

### 方式一：直接导入画布工作流
1. 打开 ComfyUI 界面（Comfy Desktop 默认为 `http://127.0.0.1:8000`，源码版为 `http://127.0.0.1:8188`）；
2. 将 `workflows/qwen_image_2.1_t2i_canvas.json` 文件直接拖拽入浏览器画布中；
3. 检查模型加载节点对应的文件名是否匹配本地已下载的模型；
4. 点击 **Queue Prompt** 即可生成。

### 方式二：在画布中启用 LM Studio 扩写节点
若想在 Web 界面中直接输入极简中文并实时扩写生图：
1. 将 `custom_nodes/ComfyUI-LMStudio-Prompt` 目录复制或软链接至 ComfyUI 的插件目录：
   ```bash
   ln -s /Users/frank/wk/github/ai/ComfyUI/qwen_image_2.1/custom_nodes/ComfyUI-LMStudio-Prompt ~/ComfyUI/custom_nodes/
   ```
2. 重启 ComfyUI 服务；
3. 在画布中右键添加节点：`QwenImage/Prompt -> LM Studio Prompt Expander (Qwen-Image)`；
4. 将该节点的 `positive_prompt` 输出引脚连接至 `CLIPTextEncode` 的文本输入，即可在画布中实时享受大模型扩写加持！

---

## 7. 运行单元测试套件

本项目包含完整的回归测试保障：

```bash
# 执行全部单元测试
pytest ComfyUI/qwen_image_2.1/tests/ -v
```
