### 智能体设计模式


#### 创建环境
```shell
pyenv virtualenv 3.12 llm
pyenv activate llm
pyenv deactivate llm

pip install -r requirements.txt
```

#### 例子说明
+ chap01 	提示链模式
+ chap02    路由模式
+ chap03	并行化模式
+ chap04    反思模式
+ chap05    工具模式
+ chap06	规划模式
+ chap07	多智能体协作模式
+ chap08	内存管理

## 关于 chap05.py：在“不支持 Tools”的模型上实现工具增强

某些本地模型（例如 `registry.ollama.ai/library/deepseek-r1:14b`）当前不支持原生的 function/tool calling。
为兼容此类模型，`chap05.py` 采用了“轻量 ReAct 决策 -> 可选调用 Python 工具 -> 汇总回答”的流程，无需模型原生工具能力也能实现“带工具”的效果。

### 思路概览
- 决策链：让 LLM 只输出一个 JSON，包含 `decision`（`use_tool` 或 `answer`）与 `tool_input`（若用工具则给出英文查询）。
- 工具：使用 LangChain 的 `@tool` 装饰器定义本地 Python 工具（示例为 `search_information`）。
- 汇总链：结合工具结果与原问题，生成最终回答。

该流程的优点是“通用、可移植”，即使模型不支持 tools，也可通过普通对话能力完成“要不要用工具”的判断与调用。

### 运行
```bash
python chap05.py
```

你应能看到三条并发查询的输出：
- “伦敦天气怎么样？”与“法国的首都是什么？”会触发工具（或兜底）并给出答案；
- “告诉我一些关于狗的事情。”则直接由模型作答。

### 依赖说明
- 本目录的 `requirements.txt` 已包含所需依赖（`langchain`, `langchain-core`, `langchain-ollama`, `nest_asyncio` 等）。
- 你可以通过环境变量 `LLM_MODEL` 指定模型名称；默认使用 `deepseek-r1:14b`（Ollama）。

### 与原生 Agents 的区别
- 原生 Agents（如 `create_tool_calling_agent`、`AgentExecutor`、`initialize_agent`）依赖模型的函数/工具调用能力或特定版本的库结构。
- `chap05.py` 不再依赖这些接口，避免了版本差异与工具能力缺失带来的报错。

### 常见问题与排查
1) NameError/ImportError（如 `create_tool_calling_agent` 未定义或不可导入）
	- 说明：依赖的 Agents API 或版本不一致；`chap05.py` 已移除这些强依赖。
2) `StructuredTool object is not callable`
	- 解决：使用 `tool.invoke({"query": ...})` 或回退 `tool.run(...)`。
3) INVALID_PROMPT_INPUT（花括号被当作变量）
	- 解决：在 `ChatPromptTemplate` 中对示例 JSON 使用双花括号转义，如 `{{"decision": ...}}`。

### 如何切换到“支持 Tools”的模型
- 若切换到支持工具调用的模型（如部分 OpenAI 模型），可以改回原生 Agents 流程（`create_tool_calling_agent`/`initialize_agent` 等）。
- 但推荐先验证当前库版本的导入路径与 API 是否匹配，避免再次出现导入错误。


