# 智能座舱 Agent 架构与落地指南

> 将 Agentic Design Patterns（Prompt Chaining、Routing、Parallelization、Reflection、Tool Calling、Planning、Multi-Agent Collaboration、Memory Management）应用于车载智能座舱场景的系统性拆解。
>
> 内容整理自两份行业岗位深度分析：**Agent 产品经理（智能座舱）** 与 **座舱智能体应用负责人**。

---

## 一、核心架构：MasterAgent + N 个垂类 Sub-Agent

### 1.1 分层协同架构

```
┌─────────────────────────────────────────────────────┐
│                   MasterAgent（中枢调度）              │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ 意图路由  │  │ 冲突仲裁  │  │ 上下文/状态池管理  │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
└───────┬──────────┬──────────┬──────────┬────────────┘
        │          │          │          │
   ┌────▼───┐ ┌───▼────┐ ┌──▼───┐ ┌───▼─────┐
   │车控 Agent│ │导航 Agent│ │娱乐   │ │健康安全  │  ...
   │空调/车窗 │ │通勤/充电 │ │音乐播客│ │DMS/疲劳  │
   └────────┘ └────────┘ └──────┘ └────────┘
```

- **MasterAgent**：全局意图中台，负责任务分解（DAG 任务流）、优先级仲裁、上下文传递
- **Sub-Agent**：垂类场景执行器（车控、导航、娱乐、健康安全、儿童陪伴、通勤秘书等）
- **核心原则**：提炼跨场景通用复用模式，避免烟囱式技能插件

### 1.2 与设计模式的映射

| 设计模式 | 座舱场景映射 |
|:---|:---|
| **Routing（路由）** | MasterAgent 将用户意图分发给正确的垂类 Sub-Agent |
| **Parallelization（并行化）** | 复合指令拆解为 DAG，多个 Sub-Agent 并行执行 |
| **Planning（规划）** | 复杂多步任务的分解、排序与依赖管理 |
| **Multi-Agent Collaboration** | Supervisor + Sub-Agent 分层架构，Handoff 交接机制 |
| **Tool Calling** | Sub-Agent 通过 Function Calling 对接车控 API（VHAL） |
| **Memory Management** | 全局共享状态池（Blackboard）+ 车主画像长期记忆 |
| **Reflection（反思）** | Bad Case 归因 → Prompt/模型迭代闭环 |
| **Prompt Chaining** | ASR → 意图预判 → LLM 推理 → TTS/车控的流式链路 |

---

## 二、关键机制设计

### 2.1 任务分解与合并（Task Decomposition & Merging）

复合指令示例：*"我有点累了，帮我找个最近的充电站，顺便把座椅调成半躺、放点轻音乐"*

- MasterAgent 拆解为 DAG 任务流，并行/串行分发给健康/车控、导航、娱乐 Agent
- 执行结果合并为一句自然语音反馈（避免多个 Agent 各自播报）

### 2.2 优先级仲裁与冲突消解

**打断优先级矩阵**：`安全 > 导航 > 车控 > 闲聊娱乐`

- **跨域资源抢占**：儿童陪伴 Agent 占用音响时，健康安全 Agent 检测到疲劳预警 → Audio Ducking + 打断后上下文恢复
- **执行指令冲突**：通勤助手建议关空调省电 vs 车控管家开启空调预冷 → 基于当前最高优先级目标（如剩余电量红线）消解

### 2.3 上下文传递与共享状态池（Shared Blackboard）

垂类 Agent 之间切换时的指代消解与记忆共享：

> 先在通勤 Agent 查了去公司的路况，接着对娱乐 Agent 说"那给我放个能听一路的播客"——娱乐 Agent 必须能从全局上下文读取到"去公司耗时 45 分钟"的路线时长参数。

### 2.4 快慢双通道路由（System 1 & System 2）

解决多 Agent 协同的延迟叠加问题（三次 LLM 调用 → 3~5s 不可用）：

- **System 1（快通道）**：90% 高频单意图明确指令 → 端侧毫秒级分类小模型直接 Bypass MasterAgent → 直达垂类 Agent
- **System 2（慢通道）**：复合长尾指令 → MasterAgent 编排
- **先行安抚**：识别复杂任务时立即触发语音/音效反馈（"正在为您规划充电路线并调整座椅…"），掩盖后台调度耗时

---

## 三、端云协同任务切分策略（Edge-Cloud Routing）

### 3.1 静态切分 + 动态路由矩阵

| 切分层级 | 场景特征 | 典型任务 |
|:---|:---|:---|
| **纯端侧闭环**（<300ms / 强隐私 / 无网可用） | 极低延迟、隐私敏感 | 唤醒词检测、DMS/OMS 视觉特征提取、确定性单步车控（车窗/空调/座椅/灯光） |
| **云端重度推理**（高算力 / 实时联网 / 复杂推理） | 复杂逻辑、联网数据 | 多轮模糊意图澄清、通勤规划（路况+日程+充电桩）、个性化推荐、儿童伴聊+内容安全过滤 |
| **弱网/断网优雅降级** | 隧道、地库 | 云端超时 >1.5s 未返回时，端侧兜底话术 / 自动降级为本地基础功能 |

### 3.2 端侧 Router（路由网关）

- 使用极小模型（BERT 级别分类器或 0.5B 模型）毫秒级判断 Query 应分发给"本地规则引擎"、"端侧小模型"还是"云端大模型"
- 参考：`aurelio-labs/semantic-router`（Embedding 向量空间匹配，几十毫秒路由）、`lm-sys/RouteLLM`（成本-质量-延迟权衡）

---

## 四、端侧推理加速与模型部署

### 4.1 模型量化与压缩

- **PTQ**（训练后量化）：AWQ、GPTQ、SmoothQuant
- **QAT**（量化感知训练）
- **知识蒸馏**：云端大模型生成合成数据 → 蒸馏端侧 1.5B~7B 小模型（Qwen2.5-3B/7B、MiniCPM 等）
- **LoRA Swapping**：底座共享一个 INT4 量化模型常驻内存，不同任务通过动态加载 LoRA 权重切换

### 4.2 推理引擎与硬件映射

| 平台 | 芯片 | 推理引擎 | 关键技术 |
|:---|:---|:---|:---|
| NVIDIA | Orin / Thor | TensorRT-LLM | KV Cache 量化、PagedAttention、In-flight Batching |
| Qualcomm | SA8295P / Cockpit Elite | QNN (SNPE) | HTP/NPU 算子支持限制、固定上下文长度、CPU/GPU/NPU 异构执行 |
| 跨平台 | — | ONNX Runtime / llama.cpp / MNN / MLC-LLM | 通用部署 |

### 4.3 端侧性能优化要点

- **首字延迟 (TTFT)**：端到端 ASR→LLM→TTS/车控 需 800ms~1.2s 内响应
- **流式全链路**：ASR 流式识别同时触发意图预判；LLM 输出 Speculative Decoding；TTS 流式分句合成
- **Prompt Cache（前缀缓存）**：System Prompt + 车辆状态 + Tool 列表的 KV Cache 预计算常驻内存，每次仅增量计算 User Query
- **算力隔离**：LLM 绑定特定 NPU 核心或低优先级线程，渲染掉帧时动态限制 Token 生成速率

---

## 五、车控安全与合规

### 5.1 Function Calling 安全

- **Grammar 约束解码**：底层 C++ 推理引擎使用 BNF 语法树强制约束 Token 采样范围，保证 100% 合法的 Function Call JSON 格式（参考 llama.cpp 的 GBNF）
- **结构化输出约束**：Guided Decoding / Grammar-based 采样
- **垂直领域微调**：LoRA/QLoRA 训练专门的 Tool-Use 小模型，车载场景容错率极低

### 5.2 执行层安全护栏（Guardrails）

- LLM **决不直接触碰 CAN 总线**，必须经过 Rule-based 安全校验状态机（结合当前车速、挡位 P/D/R 鉴权）后才放行下发
- 端侧脱敏特征化：舱内视觉/健康原始数据仅在车端处理，转化为结构化标签（如 `fatigue_level: high`）后再送入 Agent 上下文
- 儿童模式：独立的端云敏感词过滤 + 专属知识库白名单

### 5.3 主动服务（Proactive Agent）与骚扰平衡

- **注意力负荷指数网关**：结合车速、方向盘转角、路况复杂度计算驾驶负荷；高速变道/复杂路口严禁非安全类 Agent 主动语音交互
- **多模态渐进式触达**：低优推荐先走 HUD/中控屏静默卡片或氛围灯律动，用户确认后再展开语音交互

---

## 六、数据闭环与评测体系（LLMOps & Evaluation）

### 6.1 北极星指标

- 任务端到端完成率（Task Success Rate）
- 意图分发准确率
- 用户主动打断/接管率（语音没听懂 → 用户被迫手动操作中控屏 = 一次失败接管）
- 多轮对话收敛轮次

### 6.2 Bad Case 归因漏斗

```
ASR 识别错误 ──→ 补充车载专有名词热词库
         │
意图路由分发错误 ──→ 补充 Hard Negative 样本，微调端侧小模型分类器（BERT / 0.5B~1.5B Router）
         │
垂类 Agent 规划/参数提取错误 ──→ 优化大模型 System Prompt、Few-shot 示例及 Function Schema 描述
```

### 6.3 可观测性工具

- **Langfuse** / **Arize Phoenix**：全链路追踪 MasterAgent → Sub-Agent 每次调用耗时、Token 消耗、中间状态传递
- 内置工作流：生产日志筛选 Bad Case → 标注修正 → 转化为评测数据集 → 回归测试 Prompt/小模型

---

## 七、跨场景复用：标准化 Agent 底座协议

将所有垂类 Agent 统一抽象为四个标准配置模块，通过配置化/工作流编排快速孵化新场景（健康 → 儿童陪伴 → 露营模式）：

| 模块 | 职责 |
|:---|:---|
| **感知触发器 (Trigger)** | 定义 Agent 被激活的条件（语音唤醒、传感器事件、时间触发等） |
| **场景记忆槽位 (Slot/Memory)** | 该场景需维护的上下文变量与持久化存储 |
| **工具集权限 (Tools)** | 该 Agent 可调用的车控 API、外部服务、知识库 |
| **安全护栏 (Guardrails)** | 该场景的安全约束规则（打断优先级、内容过滤、执行鉴权） |

---

## 八、推荐开源项目参考

### 多智能体编排

| 项目 | 核心价值 |
|:---|:---|
| [`langchain-ai/langgraph`](https://github.com/langchain-ai/langgraph) | Supervisor + Sub-Agents 标准框架；StateGraph 共享状态池、Conditional Edges 条件路由、Human-in-the-loop 打断确认 |
| [`openai/swarm`](https://github.com/openai/swarm) / `openai-agents-python` | 轻量级 Handoff（Agent 间控制权交接与上下文传递）模式 |
| [`microsoft/autogen`](https://github.com/microsoft/autogen) | GroupChatManager 发言优先级选择、任务拆解与终止条件策略 |

### 端云路由与意图分发

| 项目 | 核心价值 |
|:---|:---|
| [`aurelio-labs/semantic-router`](https://github.com/aurelio-labs/semantic-router) | 毫秒级 Embedding 向量空间意图路由，不依赖 LLM 推理 |
| [`lm-sys/RouteLLM`](https://github.com/lm-sys/RouteLLM) | 端云大小模型协同路由，成本-质量-延迟权衡评估体系 |

### 端侧推理引擎

| 项目 | 核心价值 |
|:---|:---|
| [`alibaba/MNN`](https://github.com/alibaba/MNN) | MNN-LLM 端侧推理，原生支持 Android/Linux，高通 NPU 适配 |
| [`ggerganov/llama.cpp`](https://github.com/ggerganov/llama.cpp) | 纯 C/C++，GBNF Grammar 结构化输出，多后端支持 |
| [`NVIDIA/TensorRT-LLM`](https://github.com/NVIDIA/TensorRT-LLM) | Orin 平台必选，KV Cache 量化、PagedAttention |
| [`dusty-nv/NanoLLM`](https://github.com/dusty-nv/NanoLLM) | Jetson Orin 端到端 ASR+VLM/LLM+TTS+Agent Pipeline |
| [`quic/ai-hub-models`](https://github.com/quic/ai-hub-models) | 高通官方 QNN/ONNX 模型导出与 NPU 部署示例 |

### 多模态语音 Agent

| 项目 | 核心价值 |
|:---|:---|
| [`TEN-Framework/TEN-Agent`](https://github.com/TEN-framework/TEN-Agent) / [`pipecat`](https://github.com/pipecat-ai/pipecat) | 实时语音/视觉 Agent 编排，VAD+打断+ASR+LLM+TTS 低延迟流式 Pipeline |
| [`OpenBMB/MiniCPM-o`](https://github.com/OpenBMB/MiniCPM-o) | 端侧全模态模型（语音输入输出+视觉+Function Calling），2B~8B 参数 |

### Function Calling 训练与评测

| 项目 | 核心价值 |
|:---|:---|
| [`ShishirPatil/gorilla`](https://github.com/ShishirPatil/gorilla) | Berkeley Function-Calling 基准，训练数据构建 + AST 评估 |
| [`hiyouga/LLaMA-Factory`](https://github.com/hiyouga/LLaMA-Factory) | LoRA/QLoRA 微调，可构造车载指令集微调端侧小模型 |

### 可观测性与评测

| 项目 | 核心价值 |
|:---|:---|
| [`langfuse/langfuse`](https://github.com/langfuse/langfuse) | LLM/Agent 全链路追踪、Bad Case 标注 → 评测数据集 → 回归测试 |
| [`Arize-ai/phoenix`](https://github.com/Arize-ai/phoenix) | Agent 可观测性平台，生产日志分析与 Prompt 迭代 |

---

## 九、车载系统工程要点

### 车载 OS 与中间件

- **Android Automotive OS (AAOS)**：CarService / VHAL（Vehicle Hardware Abstraction Layer）信号打通
- **跨域通信**：SOME/IP、DDS、Binder IPC、gRPC → 将大模型 JSON 指令转化为底层 CAN/以太网车控信号

### 多模态感知融合

- 舱内 OMS/DMS 摄像头（手势、视线、"那边那个建筑是什么"）→ 视觉 Token 暴增
- 方案：端侧轻量级 VLM（Qwen2-VL-2B / InternVL2-2B）+ Token 压缩/池化，仅特定唤醒词或指向性动作时激活视觉编码器

### 量产交付关键问题

- 冷启动耗时
- 内存占用（OOM）
- 发热降频
- 长尾 Bad Case 收敛
