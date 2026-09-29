# antirez/h3.c 本地部署测试与极简技术速查手册实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在独立环境拉取并本地编译测试 antirez/h3.c（Apple Silicon 原生 MiniMax-H3 推理引擎），并在本仓库中编写一份精炼、权威的全中文技术速查手册 `docs/h3-quickstart.md`。

**Architecture:** 采用“独立沙箱构建验证 + 真实日志捕获 + 结构化速查手册沉淀”的工作流。在 `/tmp/h3.c` 执行原生多核 Clang 编译与 Metal 运行时加载，运行确定性宿主测试套件与 Metal 算子对齐测试，将真实测试数据与核心原理沉淀为单文件控制在 500 行以内的极简技术速查手册。

**Tech Stack:** C (C11), Objective-C, Metal / Metal 4 TensorOps, MPSGraph, Accelerate, Apple Clang, Make, ffmpeg, ffprobe, macOS (Apple Silicon M4 Max).

**Spec:** `docs/superpowers/specs/2026-09-30-h3-deployment-design.md`

## Global Constraints

- **代码与文档行数控制**：单个文档文件严格不超过 500 行（目标 300~380 行）。
- **纯中文文档规则**：遵循用户长期偏好（MEMORY.md），仅保留全中文技术文档，不生成伴随英文版。
- **真实性第一**：所有编译步骤、测试输出与参数说明基于本地 M4 Max 机器真实运行结果，杜绝脑补。
- **Git 提交规范**：英文 commit message，格式 `type: description`，无 `Co-Authored-By`。
- **无敏感信息**：严禁硬编码 API Keys、Token 或任何私密信息。

## Review Focus

1. **环境前置缺失**：当目标机器未安装 `ffmpeg` 或 `ffprobe` 时，推理与封包会静默失败或在管线末端崩溃；文档必须包含环境自检命令与明确修复指引。
2. **分辨率与帧数几何约束**：MiniMax-H3 要求长宽必须为 32 的倍数且不能超过 768p 面积，帧数必须符合 `5 + 17*n`；文档必须以显要表格强调此类非法参数边界。
3. **互斥参数陷阱**：`--reuse` 与 `--core-reuse` 互斥，`--ssd-streaming` 与 `--use-int8-row-fc2` 不兼容，Ref2VA 与 FL2VA 无法混用；文档必须明确列出互斥矩阵。
4. **Metal 着色器动态编译路径**：`h3_shaders.metal` 必须位于可执行文件同级目录或特定查找路径；文档必须指出运行时着色器动态加载机理。
5. **内存越界与量化硬件限制**：INT8 动态量化算子在不同世代 Apple Silicon（M3/M4/M5）上的支持差异；文档必须提供降级兼容标志（如 `--use-slower-bf16-mlp`）。

---

### Task 1: 独立测试环境准备与源码克隆

**Files:**
- Create: `/tmp/h3.c/` (外部独立临时目录，不污染当前 git 仓库)

**Interfaces:**
- Consumes: git CLI, network access to `https://github.com/antirez/h3.c.git`
- Produces: 完整的 `antirez/h3.c` 最新源码树与 Makefile

- [ ] **Step 1: 检查清理既有临时路径并克隆最新源码**

```bash
rm -rf /tmp/h3.c
git clone --depth 1 https://github.com/antirez/h3.c.git /tmp/h3.c
```

- [ ] **Step 2: 验证源码树完整性**

```bash
ls -la /tmp/h3.c
test -f /tmp/h3.c/Makefile && test -f /tmp/h3.c/main.c && test -f /tmp/h3.c/h3_shaders.metal && echo "SOURCE_OK"
```
Expected output: `SOURCE_OK`

---

### Task 2: 本地编译构建与产物校验

**Files:**
- Modify: `/tmp/h3.c/`
- Build artifacts: `/tmp/h3.c/h3`, `/tmp/h3.c/libh3.a`

**Interfaces:**
- Consumes: `clang`, `make`, Apple frameworks (Metal, Accelerate, MPSGraph, Foundation)
- Produces: `./h3` 可执行文件与 `libh3.a` 静态库

- [ ] **Step 1: 执行多核编译**

```bash
cd /tmp/h3.c && make -j8
```

- [ ] **Step 2: 验证编译生成物与可执行文件基本响应**

```bash
cd /tmp/h3.c && ./h3 --help
```
Expected output: 打印出完整的 h3 命令行用法与参数列表，返回码 0。

- [ ] **Step 3: 验证设备探测功能**

```bash
cd /tmp/h3.c && ./h3 --info
```
Expected output: 检测并打印出当前系统的 Metal 硬件设备名称（如 Apple M4 Max）。

---

### Task 3: 自动化测试套件执行与指标采集

**Files:**
- Modify: `/tmp/h3.c/`
- Output log: `/tmp/h3.c/test_output.log`

**Interfaces:**
- Consumes: `make test` test runner in `/tmp/h3.c`
- Produces: 真实通过的测试用例列表、耗时及断言结果

- [ ] **Step 1: 运行自动化测试套件**

```bash
cd /tmp/h3.c && make test 2>&1 | tee /tmp/h3.c/test_output.log
```

- [ ] **Step 2: 分析测试覆盖项与结果**

检查测试日志中的：
1. 宿主端纯 C 基础测试（BF16 转换、Safetensors 解析、分块与调度算法）；
2. Metal 4 GPU 初始化与 MPSGraph 算子调度测试；
3. 记录通过数、耗时与警告信息。

---

### Task 4: 编写全中文极简技术速查手册 (`docs/h3-quickstart.md`)

**Files:**
- Create: `docs/h3-quickstart.md`

**Interfaces:**
- Consumes: Task 1-3 产生的真实编译输出、测试日志、硬件探测信息与 spec 文档
- Produces: 结构完整、格式精炼、严格小于 500 行的全中文速查手册

- [ ] **Step 1: 编写 `docs/h3-quickstart.md` 内容**
涵盖六大模块：
1. 项目定位与纯 C/Metal 架构核心优势；
2. 系统与前置依赖自检（M系列芯片、ffmpeg 等）；
3. 源码构建与编译产物说明；
4. 本地测试套件实测（含真实测试日志分析）；
5. 模型结构与 CLI / REPL 常用命令实操（T2V、FL2VA、Ref2VA、终端预览 `--show`）；
6. 核心参数速查与显存/速度优化矩阵（--ssd-streaming, --token-reduction, 互斥规则表）。

- [ ] **Step 2: 检查文件行数与规范约束**

```bash
wc -l docs/h3-quickstart.md
```
Expected output: 行数在 250~450 行之间（严格 < 500 行）。

- [ ] **Step 3: 检查 Markdown 链接与排版渲染**
确保标题层级规范、代码块语法高亮标记准确、无反问句。

---

### Task 5: 仓库审查与代码提交

**Files:**
- Modify: git staging
- Target: `docs/h3-quickstart.md`, `docs/superpowers/plans/2026-09-30-h3-deployment-quickstart.md`

**Interfaces:**
- Consumes: git CLI
- Produces: 干净的 git commit

- [ ] **Step 1: 检查工作区状态**

```bash
git status
```

- [ ] **Step 2: 提交文档与实施计划**

```bash
git add docs/h3-quickstart.md docs/superpowers/plans/2026-09-30-h3-deployment-quickstart.md
git commit -m "docs: add antirez h3.c deployment and quickstart guide"
```
Ensure no `Co-Authored-By` line is added.
