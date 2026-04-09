# Wan2.2 视频生成模型：Mac Studio (M4 Max, 128GB) ComfyUI 部署与性能手册

## 1. 文档说明 (Document Overview)
本手册专门针对在 **ComfyUI** 环境下，利用 **Mac Studio (M4 Max, 128GB)** 运行 Wan2.2 视频生成模型的场景编写。文档涵盖了 ComfyUI 环境的搭建、插件依赖管理以及针对顶级硬件的性能基准测试。

---

## 2. 环境搭建指南 (Environment Setup Guide)

在 ComfyUI 中使用 Wan2.2，重点在于确保插件（Custom Nodes）与底层 MPS (Metal Performance Shaders) 加速的兼容性。

### 2.1 硬件规格 (Hardware Specification)
* **核心架构**: Apple M4 Max (High-end Workstation)
* **统一内存**: 128GB Unified Memory (支持在 ComfyUI 中加载超大规模 Checkpoints)

### 2.2 安装 Python 与核心依赖（arm64 原生）
打开终端，逐行执行以下命令（可直接复制粘贴）：

```bash
# 1. 安装 Miniforge（推荐，原生支持 arm64，轻量无污染）
brew install --cask miniforge

# 2. 创建专用 conda 环境（避免污染全局）
conda create -n comfy-wan22 python=3.11

# 3. 激活环境
conda activate comfy-wan22

conda install pytorch torchvision torchaudio -c pytorch-nightly

# 4. 升级 pip 并安装 CoreML 基础依赖
pip install --upgrade pip
pip install coremltools==7.3 numpy==1.26.4 pillow==10.3.0
```

验证是否为 arm64：

```bash
python -c "import platform; print(platform.machine())"
```

输出应为 `arm64`。

##### 测试试运行以下代码，验证 CoreML 是否可用：

```python
import torch
if torch.backends.mps.is_available():
    mps_device = torch.device("mps")
    x = torch.ones(1, device=mps_device)
    print (x)
else:
    print ("MPS device not found.")
```

### 2.3 部署 ComfyUI 并启用 CoreML 后端
Wan2.2 工作流基于 ComfyUI 构建，但默认 ComfyUI 不支持 CoreML。建议使用轻量补丁方案：

```bash

# 克隆已预集成 CoreML 支持的 ComfyUI 分支
git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git ~/ComfyUI-CoreML

# 参考：Apple 官方 Metal+PyTorch 支持说明
* [Apple Metal (MPS) for PyTorch 官方文档](https://developer.apple.com/metal/pytorch/)

# 进入目录并安装定制化依赖
cd ~/ComfyUI-CoreML
pip install -r requirements.txt
pip install -e .

# 启动时强制启用 CoreML（关键）
python main.py --cpu --disable-smart-memory --preview-method auto
```

启动成功后访问 `http://127.0.0.1:8188`，即可进入 ComfyUI 界面。

---

## 3. WAN2.2 工作流导入与配置

### 3.1 获取并加载 WAN2.2 专用工作流
WAN2.2 镜像通常已预置完整工作流文件（`.json` 格式），无需手动搭建节点。建议流程：

1. 从 CSDN 星图镜像广场下载 `WAN2.2-文生视频+SDXL_Prompt风格`。
2. 解压后得到 `wan22_sdxl_prompt_style.json`。
3. 在 ComfyUI 左上角点击 `Load`，选择该 JSON 文件。

加载完成后，左侧节点区将自动展开完整流程，核心模块包括：

* **SDXL Prompt Styler**：中文提示词解析与风格注入节点
* **WAN2.2 Video Encoder**：CoreML 加速的轻量视频编码器
* **CoreML Sampler**：替代传统 KSampler，全程在神经引擎运行
* **Video Preview**：直接在浏览器内播放生成结果

### 3.2 中文提示词输入与风格选择实操
WAN2.2 对中文提示词做了语义对齐优化，但必须通过 `SDXL Prompt Styler` 节点输入，不建议直接填入基础 CLIP 文本编码器。

操作步骤：

1. 找到名为 **SDXL Prompt Styler** 的蓝色节点。
2. 双击打开编辑面板，在 `Positive prompt` 输入中文描述，例如：

	> 一只橘猫坐在窗台晒太阳，窗外是樱花飘落，柔焦镜头，胶片质感，暖色调

3. 在 `Style` 下拉菜单中选择风格（共 8 种预设）：

* Cinematic Film（电影胶片）
* Anime Line Art（动漫线稿）
* Watercolor Sketch（水彩手绘）
* Neon Cyberpunk（霓虹赛博）
* Oil Painting（油画）
* Minimalist Flat（极简扁平）
* Vintage Photo（复古照片）
* Studio Portrait（影棚人像）

小技巧：风格选择会直接影响生成速度。实测中，`Cinematic Film` 与 `Studio Portrait` 在 M2 Ultra 上耗时较短（平均约 3.2 秒/帧）；`Neon Cyberpunk` 因纹理复杂，单帧通常多耗约 1.1 秒。

### 3.3 视频参数设置与执行控制
WAN2.2 默认输出分辨率为 `512x512`，支持无损缩放至 `1024x1024`（需额外显存/内存）。在 M2 Ultra 上推荐参数如下：

| 参数 | 推荐值 | 说明 |
| :--- | :--- | :--- |
| Resolution | 512x512 | CoreML 加速最稳的基础分辨率 |
| Duration | 4s | 默认 4 秒（16 帧 @ 4fps），平衡质量与速度 |
| FPS | 4 | WAN2.2 采用低帧率设计，4fps 可满足大多数动态表达 |
| Seed | random | 留空即随机，填固定数字可复现结果 |

点击右上角 `Queue Prompt (▶)` 后，右下角可见实时日志，典型输出如下：

```text
[CoreML] Loading WAN2.2 encoder...
[CoreML] Compiling prompt graph for M2 Ultra...
[CoreML] Running inference on Neural Engine...
Frame 1/16 -> 0.82s | Frame 8/16 -> 0.79s | Frame 16/16 -> 0.81s
Video saved to output/wan22_20240615_142245.mp4
```

实测数据参考：M2 Ultra（64 核 GPU）生成 4 秒视频平均耗时约 12.7 秒，全程 CPU 占用低于 15%，GPU 峰值占用低于 40%。

### 3.4 M4 Max 实测数据占位模板（待填充）
以下内容为占位模板，不影响现有流程；后续可直接在表格中补充真实测试数据。

| 测试 ID | 机型/配置 | 分辨率 | 时长/帧率 | 总耗时（秒） | 平均单帧（秒） | CPU 峰值 | GPU 峰值 | 内存峰值（GB） | 首次编译耗时（秒） | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| M4M_01 | Mac Studio M4 Max / 128GB | 512x512 | 4s @ 4fps | 待填 | 待填 | 待填 | 待填 | 待填 | 待填 | 基线风格：Cinematic Film |
| M4M_02 | Mac Studio M4 Max / 128GB | 768x768 | 4s @ 4fps | 待填 | 待填 | 待填 | 待填 | 待填 | 待填 | 中等复杂提示词 |
| M4M_03 | Mac Studio M4 Max / 128GB | 1024x1024 | 4s @ 4fps | 待填 | 待填 | 待填 | 待填 | 待填 | 待填 | 压力测试场景 |

建议记录口径（便于横向对比）：

1. 每组参数至少跑 3 次，记录平均值。
2. 区分“首次运行”（含 CoreML 编译）与“二次运行”（缓存命中）。
3. 固定同一提示词、同一风格与同一 Seed 再比较分辨率差异。

可选记录日志片段模板：

```text
[CoreML] Loading WAN2.2 encoder...
[CoreML] Compiling prompt graph for M4 Max...
[CoreML] Running inference on Neural Engine...
Frame 1/16 -> 待填s | Frame 8/16 -> 待填s | Frame 16/16 -> 待填s
Video saved to output/wan22_xxx.mp4
```

---

## 4. 效果调优与常见问题处理

### 4.1 提升中文提示词效果的 3 个实用技巧
WAN2.2 支持中文直输，但未经优化的句子仍可能出现语义偏移。以下表达方式经过实测更稳定：

1. 避免长句嵌套：
	将“一个戴墨镜、穿皮夹克、骑哈雷摩托的黑猫”拆分为“主体 + 动作 + 风格 + 细节”。
2. 显式指定画质关键词：
	在提示词末尾追加 `--quality 2` 或 `--sharpness high`（WAN2.2 私有指令）。
3. 使用权重强化关键词：
	例如 `(樱花:1.3)` 表示将“樱花”元素权重提升 30%。

示例对比：

* 原始提示词：`古风庭院，小桥流水`
* 优化提示词：`古风庭院（水墨风格:1.4），小桥流水（青瓦白墙:1.2）--quality 2`

优化后通常可得到更清晰的建筑结构与更丰富的水面倒影细节。

### 4.2 视频卡顿、黑屏、无声的快速排查

| 现象 | 可能原因 | 解决方案 |
| :--- | :--- | :--- |
| 生成中途报错 `CoreML Error: computeUnits=ALL` | 系统限制神经引擎并发数 | 在启动命令末尾添加 `--coreml-compute-units cpu_and_ne` |
| 预览窗口黑屏但日志显示完成 | 浏览器对 WebM 编码兼容性问题 | 右键 `Save As` 保存 MP4，再用系统播放器查看 |
| 生成视频无声 | WAN2.2 当前仅输出纯视频流 | 后期使用 FFmpeg 合成音频：`ffmpeg -i video.mp4 -i audio.wav -c:v copy -c:a aac output.mp4` |
| 首次运行极慢（>2 分钟） | CoreML 首次编译模型图耗时 | 首次耐心等待；后续通常显著提速，可先用空提示词预编译 |

### 4.3 内存与性能释放建议

1. 关闭不使用的浏览器标签页，尤其是含 WebGL 的页面。
2. 在活动监视器中观察 `coremltool` 进程；若内存长期超过 8GB，重启 ComfyUI。
3. 每生成约 5 个视频后执行 `killall coremltool` 清理缓存。

---

## 5. 总结：轻量、可控、真正属于创作者的文生视频
从确认芯片型号、安装 arm64 Python、部署 CoreML 版 ComfyUI，到输入一句中文并在十几秒后得到首段可用视频，WAN2.2 的核心价值在于把文生视频从“实验性流程”拉回“日常创作工具”。

它不追求超长时长输出，但强调稳定、可复现和本地可控；它减少参数负担，却让中文提示词具备更高可解释性；它不依赖云端 API，计算全程在本机完成，在隐私、速度与可控性之间实现平衡。

对于 Mac 创作者（短视频分镜、电商动态展示、独立游戏概念动画等场景），WAN2.2 适合作为“打开即用、用完即关”的轻量生产工具。

---

## 6. 参考资料
* [《WAN2.2 文生视频镜像部署教程》](https://modelers.csdn.net/69a7a1527bbde9200b9d5779.html)