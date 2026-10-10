# AI 探索与实战工坊 (AI Practice & Engineering)

> 本仓库是一套面向开发者与创作者的 AI 工程化实战知识库与代码工作台，深度聚焦于 **Mac Studio (Apple M4 Max · 128GB 统一内存)** 极限生产力环境下的本地大模型推理、多模态音视频生成 (ComfyUI / DiT)、智能体设计模式 (Agentic Design Patterns) 以及现代编码助手生态 (Coding Agent CLI)。

---

## 🖥️ 核心实验环境：Mac Studio (M4 Max · 128GB Unified Memory)

仓库内所有本地端侧模型、量化工程、DiT 图像/视频生成工作流，均以 **Apple Silicon (M4 Max, 128GB 统一内存)** 为标杆基准进行极限调优：

- **统一内存优势**：128GB 统一内存彻底打破了传统消费级 GPU 显存墙（24GB/32GB VRAM），可单机全量加载并常驻大参数量模型（Wan 2.2 14B、HunyuanVideo 1.5、Qwen-Image-2.1、DeepSeek-R1 量化版及 70B+ MoE）。
- **Metal / MPS 深度调优**：集成 Tiled VAE、分块切片编码、量化 GGUF/ExLlama 加速与原生 C/Metal 推理引擎（ds4, h3），保障高吞吐与零显存溢出（OOM）。
- **音视频短剧全自动化生产**：首创“脚本扩写 ➔ 参考图首帧生成 ➔ Wan 2.2 / Hunyuan I2V 镜头切片 ➔ 后期合成”的 Mac Studio 独占极速流水线。

---

## 目录索引

- [1. 多模态生成与音视频落地 (Mac Studio 128G 实战)](#1-多模态生成与音视频落地-mac-studio-128g-实战)
- [2. 智能体设计模式与多 Agent 框架 (Agentic Workflows)](#2-智能体设计模式与多-agent-框架-agentic-workflows)
- [3. 智能编码助手与 CLI 演进生态 (Coding Agent CLI Ecosystem)](#3-智能编码助手与-cli-演进生态-coding-agent-cli-ecosystem)
- [4. 高性能端侧与本地推理引擎 (Local LLM & Native Inference)](#4-高性能端侧与本地推理引擎-local-llm--native-inference)
- [5. Prompt 工程、评估与协议规范 (Prompt & MCP)](#5-prompt-工程评估与协议规范-prompt--mcp)
- [6. 经典机器学习与深度学习基础](#6-经典机器学习与深度学习基础)

---

### 1. 多模态生成与音视频落地 (Mac Studio 128G 实战)

依托 128GB 统一内存的大容量与高带宽特性，沉淀端到端生图、生视频与数字人流水线：

- **[短剧/短视频 Mac Studio 落地方案](./ComfyUI/短剧短视频_MacStudio_落地方案.md)**：利用 Wan 2.2 I2V + T2V 分镜式镜头生成，结合 Lightning LoRA 与 Tiled VAE 解码，构建 15~30s 商业短剧全流程。
- **[HunyuanVideo 1.5 腾讯混元视频生成](./ComfyUI/hunyuan_video_1.5/README.md)**：针对 M4 Max 128GB 调优的原生 ComfyUI 节点链与 API 自动化调用测试。
- **[Wan 2.2 ComfyUI Mac Studio 部署与测试](./ComfyUI/Wan2.2_ComfyUI_MacStudio_安装测试指南.md)**：Wan 2.2 14B GGUF 高低噪分段架构与统一内存防溢出配置。
- **[Qwen-Image-2.1 高画质生图](./ComfyUI/qwen_image_2.1/README.md)**：阿里通义文生图/图生图原生架构，黄金档与顶配超精度档部署指南。
- **[Z-Image-Turbo GGUF 极速出图](./ComfyUI/Z-Image-Turbo_ComfyUI_GGUF_部署指南.md)**：超低步数出图与双流工作流设计。
- **[Flux.1 on Apple Silicon 部署](./ComfyUI/FLUX_ComfyUI_Apple_Silicon_部署指南.md)**：Mac 平台 MPS 硬件加速下的 Flux.1 最佳实践。
- **[ComfyUI 工作流合集与性能 Benchmark](./ComfyUI/工作流.md)**：含基准跑分脚本 `comfyui_benchmark.py`。
- **[多媒体处理工具集](./media/readme.md)**：包含 [TTS 语音合成](./media/TTS.md)、[SadTalker 唇形同步数字人](./media/sadtalker.md) 以及音频分轨 [Spleeter](./spleeter/ReadMe.md)。

---

### 2. 智能体设计模式与多 Agent 框架 (Agentic Workflows)

- **[《智能体设计模式》实战源码](./AgenticDesignPatterns/ReadMe.md)**
  - **[LangChain & LCEL 实现](./AgenticDesignPatterns/langchain/)**：Prompt 链（Chaining）、动态路由（Routing）、并行分发（Parallelization）、反思调优（Reflection）、工具调用（Tool Calling/ReAct）、结构化规划（Planning）、多 Agent 协同（Multi-Agent Collaboration）与记忆管理（Memory）。
  - **[Microsoft AutoGen 实现](./AgenticDesignPatterns/autogen/)**：基于多 Agent 对话拓扑的 Agentic Pattern 完整映射。
- **[helloagents](./helloagent/ReadMe.md)**：基于 [hello-agents](https://github.com/datawhalechina/hello-agents) 的轻量级核心智能体原理与实践。
- **[AutoGen & AutoGenBench](./autogen/ReadMe.md)**：多智能体协作、AutoGen Studio 原型调试及 [性能基准测试](./autogenbench/ReadMe.md)。
- **[CrewAI](./crewai/ReadMe.md)**：基于角色设定（Role-playing）与团队协作的自动化 Agent 工作流。
- **[LangChain 进阶范例](./LangChain/ReadMe.md)**：从基础问答（ex01）到复杂并行执行与结构化输出解析（ex06）。
- **[Go 语言 Agent 生态]**：[adk-go](https://github.com/google/adk-go) 现代化代码优先 Go Agent 工具包。

---

### 3. 智能编码助手与 CLI 演进生态 (Coding Agent CLI Ecosystem)

涵盖主流 AI 辅助编程命令行、Agent 技能（Skills）一键迁移与配置集成：

- **[Pi Agent (`pi` / `pi-coding-agent`)](./PiAgent/ReadMe.md)**：极简灵活的 Coding Agent 架构，支持多 Provider、反向代理/中转网关及 Google Gemini Pro 深度集成。
- **[Claude Code 本地强化指南](./ClaudeCode/ReadMe.md)**：Anthropic 官方 CLI 架构、LM Studio / 本地大模型桥接脚本与 Session 跨端同步。
- **[OpenCode CLI 指南](./OpenCode/ReadMe.md)**：开源终极 Coding Agent，一键部署并无缝对接本地大模型。
- **[CodeBuddy Skills & Agents 体系](./CodeBuddy/ReadMe.md)**：腾讯 CodeBuddy CLI 的技能系统对齐与角色配置一键部署。
- **[Google Antigravity (`agy`) 实践](./Antigravity/ReadMe.md)**：对齐 Gemini 体系的前沿 Coding CLI 与 Agent 运行环境。
- **[Google Gemini 生态实战矩阵](./Gemini/README.md)**：覆盖百万 Token 超长上下文、Deep Research、NotebookLM Pro、Jules 代码 Agent 与 Veo 视频生成。

---

### 4. 高性能端侧与本地推理引擎 (Local LLM & Native Inference)

在 128GB 内存上实现极速纯端侧模型吞吐与调度：

- **[ds4 (DwarfStar)](./ds4/README.md)**：antirez 开源的高性能原生 C 推理引擎与 Coding Agent，支持 DeepSeek V4 Flash/PRO、GLM 5.2 等长上下文模型。
- **[h3 (MiniMax-H3)](./h3/README.md)**：antirez 开源的原生 C/Metal 音视频 DiT 推理引擎，专为 Mac 统一内存优化。
- **[Ollama 本地模型矩阵与部署](./ollama/ReadMe.md)**：DeepSeek-R1 系列、Qwen2.5 部署优化及 ModelScope 国内镜像加速。
- **[Intel 独立显卡 (Arc / IPEX-LLM) 推理指南](./intel/ReadMe.md)**：Intel GPU 驱动安装、IPEX-LLM 部署与 llama.cpp 异构计算。
- **[硬件选购与性能横向评测](./机器选购.md)**：汇总 M4 Max、M4 Pro、M1 Pro、DGX SPARK 及云端 API 的 Token 生成速率与内存吞吐比。

---

### 5. Prompt 工程、评估与协议规范 (Prompt & MCP)

- **Prompt Engineering & Context**：[Prompt 设计指南](./prompt/ReadMe.md) 与 [DeepSeek 专项 Prompting](./prompt/deepseek.md)。
- **MCP (Model Context Protocol)**：
  - [MCP 中文入门指南](https://github.com/feixiao/MCP-Chinese-Getting-Started-Guide)
  - [FastMCP (Pythonic 构建)](https://github.com/jlowin/fastmcp)
  - [mcp-zero (Go-Zero 框架)](https://github.com/zeromicro/mcp-zero)
  - [modelcontextprotocol/go-sdk](https://github.com/modelcontextprotocol/go-sdk)
- **评测与可观测性**：
  - [Promptfoo](https://github.com/promptfoo/promptfoo)：基于 YAML 的自动化 Prompt/模型对比与评估。
  - [DeepEval](https://github.com/confident-ai/deepeval)：单元测试级 LLM 应用评估框架。
  - [Ragas](https://github.com/vibrantlabsai/ragas)：RAG 应用全面评估体系。

---

### 6. 经典机器学习与深度学习基础

- **基础框架与代码**：[PyTorch 实验](./PyTorch/ReadMe.md)、[TensorFlow Lite 端侧推理](./TensorFlowLite/ReadMe.md)、[Keras 实践](./keras/ReadMe.md)。
- **精选教程与练习**：
  - [《AI FOR EVERYONE》课程笔记](https://www.bilibili.com/video/BV1yC4y127uj/)
  - [《机器学习实战：基于 Scikit-Learn、Keras 和 TensorFlow (第2版)》配套代码](https://github.com/feixiao/handson-ml2)
  - [吴恩达机器学习课程精选课后题](https://github.com/feixiao/deeplearning_ai_books)