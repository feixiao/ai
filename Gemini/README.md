# Gemini 核心特权与高阶实战指南

本项目用于深入研究与系统化运用 Google Gemini 生态的核心能力，涵盖大模型超长上下文、深度自主研究、云端异步编程 Agent、多模态视频生成与私有化知识库等全套技术栈。

---

## 核心特权与能力矩阵

| 核心权益 / 工具 | 关键定位与技术指标 | 全栈开发应用场景 | 个人投资应用场景 |
| :--- | :--- | :--- | :--- |
| **5TB 超大云盘** | Drive / 相册 / Gmail 空间无上限感，支持家庭组共享与资产直连 | 本地大型数据集、依赖包备份、模型权重与 Docker 镜像归档 | 历史研报库、高频交易数据、上市公司年报合集长期存储 |
| **Gemini 3.1 Pro 超大上下文** | 100万 ~ 200万 Token 原生上下文窗口，免切片、零信息丢失检索 | 整个代码仓库工程一键打包，全景架构分析与跨模块重构 | 30+ 份同行公司 10-K/年报打包横向对比，财报会议细颗粒度穿透 |
| **Deep Research (深度研究)** | 多轮自主规划、深度网页递归抓取、交叉验证、生成万字报告 | 技术选型全景对比、前沿架构优劣势调研、复杂技术链路可行性分析 | 行业竞争格局梳理、冷门细分赛道深挖、上市公司财务暴雷红队压力测试 |
| **Gemini Spark (云端 Agent)** | 24 小时云端驻守、定时任务编排、自主轮询与状态监控 | 依赖库安全漏洞轮询、CI/CD 状态告警智能汇总、外部 API 状态监控 | 盘后财报与监管公告抓取、突发宏观快讯结构化过滤、自选股舆情预警 |
| **满血版 NotebookLM** | Source-Grounded 溯源事实约束（零幻觉）、Audio Overview 双人播客 | 官方技术文档/RFC/API Spec 导入，生成随时可溯源的精准开发助手 | 几十万字英文研报/财报一键生成双人对谈播客，边通勤边高效吸收 |
| **Overview & Reports 套件** | 包含 Audio/Video Overview、高管简报、万字研报、时间线与自测题 | 视频架构分享生成带时间戳分镜章节，会议录音自动提炼决策备忘录 | 财报电话会一键转双人对谈播客，批量生成赛道深度研究报告 |
| **Google Flow (每月 1000 积分)** | 官方 Veo / Flow 影视级视频与分镜生成平台，光影与物理一致性 | 软件系统演示动效、技术方案架构动态演化演示 | 投研成果可视化展示、商业计划书动态演示、财经视频分镜制作 |
| **Jules (GitHub 代码助理)** | 异步云端自主编程代理，直接联动 GitHub Repo，自主改代码提 PR | 自动化修 Bug、补全 TypeScript 强类型、批量补单测、依赖跨版本升级 | 个人自动化量化脚本维护、回测代码优化与开源投研数据清洗管道维护 |

---

## 文档目录导航

各模块包含完整的技术原理、最佳实践、提示词模版与避坑指南：

1. **[01. 超大上下文与 Google AI Studio 实战](./01_SUPER_CONTEXT_AND_STUDIO.md)**
   - 告别 RAG 向量检索切片：100万~200万 Token 窗口的技术红利与原理。
   - 全代码库喂入实践：依赖拓扑推演、架构异味扫描与重构方案生成。
   - 财务分析实践：多年度 10-K 与电话会议纪要统一上下文对比。
   - Google AI Studio 参数配置、System Instructions、JSON Schema 约束与 Prompt Caching 技巧。

2. **[02. Deep Research 深度研究实战](./02_DEEP_RESEARCH.md)**
   - 自主多步规划与递归搜索运行机制。
   - 投研万字报告提示词工程：从模糊选题到专业研报的提问范式。
   - 技术调研实操：架构横评、框架演进与性能对比。
   - 报告信源二次审计与事实核查工作流。

3. **[03. 满血版 NotebookLM 知识库构建](./03_NOTEBOOKLM_PRO.md)**
   - 基于来源（Source-Grounded）的无幻觉知识库体系。
   - 赛道与个股研报知识库沉淀：多源资料（PDF、网页、YouTube）管理。
   - Audio Overview（双人播客）生成机制与焦点定制技巧。
   - 从晦涩长文到结构化速读指南（FAQ、时间线、简报）的高效流转。

4. **[04. Jules 异步编程 Agent 实战](./04_JULES_CODE_AGENT.md)**
   - Jules 的运行架构：沙箱克隆、环境准备、自主编辑、测试验证与提交 PR。
   - 与本地 CLI（如 Claude Code）的分工协同：异步托管 vs 本地高频交互。
   - Issue 编写规范：如何让 Jules 准确复现问题并一次性跑通测试。
   - 典型适用任务：TypeScript 类型补全、单元测试覆盖率提升、依赖升级、文档自动化。

5. **[05. Gemini Spark 与云端自动化监控](./05_SPARK_AND_AUTOMATION.md)**
   - 云端 Agent 的常驻运行机制与 Workspace 生态互通。
   - 投资自动化：盘后财报披露自动追踪、重点指标提取、邮件摘要分发。
   - 研发自动化：第三方依赖漏洞监控、前沿开源项目技术雷达追踪。
   - 任务提示词设计与异常处理容错机制。

6. **[06. Google Flow / Veo 视频生成与积分攻略](./06_GOOGLE_FLOW_VEO_VIDEO.md)**
   - Veo 视频生成技术特点与每秒画质/物理模拟表现。
   - 影视级分镜提示词结构：主体 + 场景 + 镜头运动（Pan/Zoom/Orbit）+ 氛围光影。
   - 每月 1000 积分的最佳消费策略：避免废片浪费的高性价比生成路径。
   - 投研成果、技术方案与商业路演演示动效实操。

7. **[07. 5TB 云端存储与 AI 资产中枢](./07_CLOUD_STORAGE_ECOSYSTEM.md)**
   - 存储空间从“存放网盘”升级为“AI 计算直连中枢”。
   - Google Drive 与 AI Studio、Colab、NotebookLM 的免下载联动。
   - 研发素材库、ComfyUI/Wan2.2 视频生成大文件、本地大模型数据集归档规范。
   - 数据隐私安全边界与家庭组资源隔离策略。

8. **[08. Google 多模态概览与智能研报全景指南 (Overview & Reports)](./08_MULTIMODAL_OVERVIEW_AND_REPORTS.md)**
   - 告别传统 ASR+LLM+TTS 繁琐链路：Gemini 原生超长音视频多模态直通架构。
   - Audio Overview 进阶实战：双人播客生成机理、Interactive 实时插话打断与受众定制 Prompt。
   - Video Overview 与音画穿透：免转写原生多模态、秒级时间戳引用与架构白板分镜抽取。
   - Reports 结构化套件：高管简报 (Briefing Doc)、万字深度研报、时序演进表 (Timeline) 与反向盲点审计 (Red Team)。
   - 认知层工具：概念词汇表 (Glossary)、预测型 FAQ 问答库与场景模拟自测题 (Quiz)。
   - 自动化工程流水线：基于最新 `google-genai` SDK 实现一键批量自动化产出。

---

## 辅助工具

- **[上下文打包工具 (`tools/pack_context.py`)](./tools/pack_context.py)**：用于将本地复杂的源码仓库或多个研报/PDF/Markdown 目录扫描并打包为单份带有清晰路径标记的文本文件，便于直接上传至 Google AI Studio 或 Gemini 进行百万级 Token 深度分析。
- **[多模态概览全套自动化生成器 (`tools/auto_overview_generator.py`)](./tools/auto_overview_generator.py)**：基于官方最新 `google-genai` SDK，传入本地 PDF/音视频文件，一键批量并发生成高管简报、深度研报、双人播客脚本、FAQ 题库及精准时间戳导航。

---

## 常用官方入口汇总

- **Gemini Web 交互端**: `https://gemini.google.com/` (支持日常对话、Deep Research、多模态交互)
- **Google AI Studio (核心研发调试台)**: `https://aistudio.google.com/` (支持 Gemini 3.1 Pro/2.5 Pro 原生参数调节、系统提示词、JSON Schema 输出、免费与付费 API Key 管理)
- **NotebookLM**: `https://notebooklm.google.com/` (私有化知识库与 Audio Overview 双人播客生成)
- **Jules (GitHub 代码助理)**: `https://jules.google/` (云端自动化 GitHub 代码仓库连接与 PR 托管)
- **Google Flow / VideoFX**: `https://labs.google/fx/tools/video-fx` / Google Vids (官方视频与分镜生成平台)
- **Google One 存储管理**: `https://one.google.com/` (5TB 存储配额与家庭组共享配置)
