"""
说明
----
本示例演示：在“模型不支持原生工具调用（function/tool calling）”的情况下，
如何使用“轻量 ReAct 决策 -> 可选调用 Python 工具 -> 汇总回答”的流程来完成工具增强。

适配背景：
- 例如 Ollama 的 deepseek-r1:14b 模型（registry.ollama.ai/library/deepseek-r1:14b）当前不支持 tools。
- 我们不直接依赖 langchain 的 Agents（如 AgentExecutor、create_tool_calling_agent 等），
  而是通过两个 Prompt 链手动决定是否调用工具，并汇总最终回答，避免对模型原生工具能力的要求。

使用步骤概览：
1) 决策链：让 LLM 输出一个 JSON，说明是否需要使用工具以及工具输入。
2) 若需要，调用本地 Python 工具（search_information）。
3) 汇总链：结合工具结果输出最终回答。
"""

import os
import asyncio
from typing import Optional, List

import nest_asyncio
from langchain_core.tools import tool  # 定义/注册可被 LC 使用的 Python 工具
from langchain_core.prompts import ChatPromptTemplate  # 构造对话提示模版
from langchain_core.output_parsers import StrOutputParser  # 将模型输出解析为纯文本字符串

def build_model(provider: str, model_name: Optional[str] = None):
  """根据提供商构建聊天模型。

  参数：
  - provider: "openai" 或 "ollama"
  - model_name: 可选模型名；不传则读取环境变量 LLM_MODEL；再不传使用合理默认值。

  说明：采用“延迟导入”，避免未安装某些依赖时报 ImportError。
  """
  provider = provider.lower()

  if provider == "openai":
    # OpenAI 聊天模型（需要有效的 OpenAI API Key）
    from langchain_openai import ChatOpenAI

    name = model_name or os.getenv("LLM_MODEL") or "gpt-4o-mini"
    return ChatOpenAI(model=name)

  if provider == "ollama":
    # 本地 Ollama 模型（例如 deepseek-r1:14b）。注意：该模型不支持 tools。
    from langchain_ollama import ChatOllama

    name = model_name or os.getenv("LLM_MODEL") or "deepseek-r1:14b"
    return ChatOllama(model=name)

  raise ValueError(
    f"Unsupported provider: {provider}. Use 'openai' or 'ollama'."
  )

try:
    # 需要一个具有函数/工具调用功能的模型。
    llm = build_model("ollama")
    print(f"✅ 语言模型已初始化: {getattr(llm, 'model', 'unknown')}")
except Exception as e:
    print(f"初始化语言模型时出错: {e}")
    llm = None

# --- 定义一个工具 ---
@tool
def search_information(query: str) -> str:
    """
  简单的“信息检索”工具（模拟）。

  入参：
  - query: 查询字符串，建议用英文关键词，便于检索（此处为模拟字典）。

  返回：
  - 预置字典中的结果字符串；若无匹配，返回默认提示。

  用途：
  - 演示如何在“不支持原生 tools 的模型”场景下，依然能通过 Python 函数作为工具提供事实信息。
    """
    print(f"\n--- ️ 工具已调用: search_information，查询: '{query}' ---")
    # 使用预定义结果的字典模拟一个搜索工具。
    simulated_results = {
      "weather in london": "伦敦目前多云，气温15°C。",
      "capital of france": "法国的首都是巴黎。",
      "population of earth": "地球的估计人口约为80亿。",
      "tallest mountain": "珠穆朗玛峰是地球上最高的山峰（海拔）。",
      "default": f"“{query}”的模拟搜索结果: 未找到具体信息，但该主题似乎很有趣。"
    }
    result = simulated_results.get(query.lower(), simulated_results["default"])
    print(f"--- 工具结果: {result} ---")
    return result

tools = [search_information]  # 工具列表：可扩展更多工具

# --- 基于文本的轻量 ReAct 决策器（无需模型原生 tool-call 支持） ---
# 该 Prompt 要求模型仅输出一个 JSON 且包含键：decision, tool_input
# 注意：使用双花括号转义，避免被 PromptTemplate 误识别为变量
decision_prompt = ChatPromptTemplate.from_messages([
  ("system", (
    "你是一个决策器。判断用户问题是否需要使用提供的工具search_information。\n"
    "只输出一个JSON对象，不要多余文本。键为 decision 与 tool_input。示例：\n"
    "{{\"decision\": \"use_tool|answer\", \"tool_input\": \"weather in London\"}}\n"
    "若问题涉及地理事实/天气/人口/最高山等，选择 use_tool，并将查询翻译为简洁英文；否则输出 answer 并将 tool_input 设为空字符串。"
  )),
    ("human", "{question}")
])

# 用于将工具结果与原问题汇总为最终答案
final_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个乐于助人的助手，尽量简洁、准确，用中文回答。"),
    ("human", (
        "原始问题：{question}\n"
        "工具检索结果：{tool_result}\n"
        "请结合工具结果，给出最终回答。若工具结果为空，则直接回答。"
    )),
])

decision_chain = decision_prompt | llm | StrOutputParser()  # 决策链
answer_chain = final_prompt | llm | StrOutputParser()      # 汇总链

async def run_agent_with_tool(query: str):
  """
  使用“决策 -> 可选工具 -> 汇总”的三步流程生成答案。

  步骤：
  1) 调用 decision_chain：得到是否用工具（decision=use_tool|answer）及工具输入（tool_input）。
  2) 若需要，调用 search_information 工具（通过 .invoke 或 .run）。
  3) 调用 answer_chain：结合工具结果输出最终回答。
  """
  if llm is None:
    print("LLM 未初始化，跳过。")
    return
  print(f"\n---  正在处理查询: '{query}' ---")
  try:
    raw = await decision_chain.ainvoke({"question": query})
    # 解析JSON
    import json
    decision = {"decision": "answer", "tool_input": ""}
    try:
      decision = json.loads(raw.strip())
    except Exception:
      # 简单兜底解析
      text = raw.lower()
      if "use_tool" in text:
        decision["decision"] = "use_tool"
    tool_result = ""
    if decision.get("decision") == "use_tool":
      ti = (decision.get("tool_input") or query).strip()
      # 使用 LangChain 工具的 invoke 接口调用
      try:
        tool_result = search_information.invoke({"query": ti})
      except Exception:
        # 兼容旧接口
        try:
          tool_result = search_information.run(ti)
        except Exception:
          tool_result = f"(工具调用失败，按原问题回答)"
    final = await answer_chain.ainvoke({
      "question": query,
      "tool_result": tool_result,
    })
    print("\n--- ✅ 最终回答 ---\n" + final)
  except Exception as e:
    print(f"\n流程执行期间发生错误: {e}")

async def main():
  """并发运行多个示例查询，便于观察不同路径（用工具/直接回答）。"""
  tasks = [
    run_agent_with_tool("法国的首都是什么？"),
    run_agent_with_tool("伦敦天气怎么样？"),
    run_agent_with_tool("告诉我一些关于狗的事情。"),  # 应该触发默认工具响应
  ]
  await asyncio.gather(*tasks)

nest_asyncio.apply()  # 允许在 Jupyter/交互式环境中再次进入事件循环
asyncio.run(main())   # 运行示例
