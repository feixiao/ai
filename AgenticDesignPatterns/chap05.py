import os
import asyncio
from typing import Optional, List

import nest_asyncio
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def build_model(provider: str, model_name: Optional[str] = None):
  provider = provider.lower()

  if provider == "openai":
    # 延迟导入，避免未安装依赖或本地无用时报错
    from langchain_openai import ChatOpenAI

    name = model_name or os.getenv("LLM_MODEL") or "gpt-4o-mini"
    return ChatOpenAI(model=name)

  if provider == "ollama":
    # 延迟导入，避免未安装依赖或本地无用时报错
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
    提供给定主题的事实信息。使用此工具来查找诸如“法国的首都”或“伦敦的天气？”等短语的答案。
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

tools = [search_information]

# --- 基于文本的轻量 ReAct 决策器（无需模型原生 tool-call 支持） ---
decision_prompt = ChatPromptTemplate.from_messages([
  ("system", (
    "你是一个决策器。判断用户问题是否需要使用提供的工具search_information。\n"
    "只输出一个JSON对象，不要多余文本。键为 decision 与 tool_input。示例：\n"
    "{{\"decision\": \"use_tool|answer\", \"tool_input\": \"weather in London\"}}\n"
    "若问题涉及地理事实/天气/人口/最高山等，选择 use_tool，并将查询翻译为简洁英文；否则输出 answer 并将 tool_input 设为空字符串。"
  )),
    ("human", "{question}")
])

final_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个乐于助人的助手，尽量简洁、准确，用中文回答。"),
    ("human", (
        "原始问题：{question}\n"
        "工具检索结果：{tool_result}\n"
        "请结合工具结果，给出最终回答。若工具结果为空，则直接回答。"
    )),
])

decision_chain = decision_prompt | llm | StrOutputParser()
answer_chain = final_prompt | llm | StrOutputParser()

async def run_agent_with_tool(query: str):
  """使用轻量决策->工具->汇总流程生成答案。"""
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
    """并发运行所有代理查询。"""
    tasks = [
        run_agent_with_tool("法国的首都是什么？"),
        run_agent_with_tool("伦敦天气怎么样？"),
        run_agent_with_tool("告诉我一些关于狗的事情。"),  # 应该触发默认工具响应
    ]
    await asyncio.gather(*tasks)

nest_asyncio.apply()
asyncio.run(main())
