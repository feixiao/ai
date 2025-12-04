"""
Autogen 版本：轻量 ReAct 示例（决策 -> 可选工具 -> 汇总回答）

说明：参考 `langchain/chap05.py`。
- 在模型不支持原生 function/tool calling 的情况下，使用两段提示链：
  1) 决策提示：让 LLM 输出 JSON（{\"decision\": "use_tool|answer", \"tool_input\": "..."}）
  2) 汇总提示：将工具结果与原问题合并，输出最终回答

实现细节：
- 使用 `autogen_ext.models.ollama.OllamaChatCompletionClient` 调用本地 Ollama 模型；
- 若模型返回无法解析的 JSON，会回退为简单的文本匹配（包含 `use_tool` 则选择调用工具）；
- 本地工具 `search_information` 用于模拟检索；调用在 Python 端进行（避免依赖模型的 function-calling）。

运行：
```bash
export LLM_MODEL=deepseek-r1:8b
python3 autogen/chap05.py
```
"""

import os
import asyncio
import json
from typing import Optional

from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient


def search_information(query: str) -> str:
    """模拟的本地信息检索工具。

    参数：
    - query: 查询字符串（建议简洁英文短语以匹配预置结果）
    返回：字符串结果
    """
    print(f"\n--- 工具已调用: search_information，查询: '{query}' ---")
    simulated_results = {
        "weather in london": "伦敦目前多云，气温约15°C。",
        "capital of france": "法国的首都是巴黎。",
        "population of earth": "地球的估计人口约80亿。",
        "tallest mountain": "世界最高的山为珠穆朗玛峰。",
    }
    return simulated_results.get(query.lower(), f"(模拟搜索) 未找到有关：{query} 的确切信息。")


def extract_text_from_resp(resp) -> str:
    """从模型返回的不同结构中提取文本内容（兼容性处理）。"""
    try:
        if hasattr(resp, "choices"):
            return resp.choices[0].message.content
        if isinstance(resp, dict) and "choices" in resp:
            return resp["choices"][0]["message"]["content"]
    except Exception:
        pass
    return str(resp)


async def decision_and_answer_flow(client: OllamaChatCompletionClient, question: str) -> None:
    """执行一次完整的决策 -> 可选工具 -> 汇总流程并打印最终回答。"""
    print(f"\n--- 处理问题：{question} ---")

    # 决策提示，要求模型只输出一个 JSON
    decision_prompt = (
        "你是决策器。判断用户问题是否需要调用名为 'search_information' 的工具。"
        "只输出一个 JSON 对象，格式：{\"decision\": \"use_tool|answer\", \"tool_input\": \"...\"}。"
        "如果需要检索事实类信息（例如天气、首都、人口、最高山等），请给出 use_tool 并把查询翻译为简洁英文；否则输出 answer 并将 tool_input 设为空字符串。"
        f"\n用户问题：{question}"
    )

    try:
        dec_resp = await client.create([UserMessage(content=decision_prompt, source="user")])
        raw = extract_text_from_resp(dec_resp).strip()
    except Exception as e:
        print(f"调用决策模型时出错: {e}")
        raw = ""

    # 解析 JSON 决策，容错处理
    decision = {"decision": "answer", "tool_input": ""}
    try:
        decision = json.loads(raw)
    except Exception:
        # 回退：若文本包含 use_tool 则认为需要调用工具
        if "use_tool" in raw.lower():
            decision["decision"] = "use_tool"

    tool_result = ""
    if decision.get("decision") == "use_tool":
        ti = (decision.get("tool_input") or question).strip()
        # 若模型给的是自然语言查询，尽量使用其值，否则使用原问题
        try:
            tool_result = search_information(ti)
        except Exception:
            tool_result = "(工具调用失败)"

    # 汇总提示：把工具结果与问题传入模型，要求简洁中文回答
    final_prompt = (
        "你是个助理，请用中文简洁回答用户问题。\n"
        f"原始问题：{question}\n工具检索结果：{tool_result}\n"
        "如果工具结果为空，则只基于模型知识直接回答。"
    )

    try:
        final_resp = await client.create([UserMessage(content=final_prompt, source="user")])
        final_text = extract_text_from_resp(final_resp)
    except Exception as e:
        final_text = f"(生成最终回答失败：{e})"

    print("\n--- ✅ 最终回答 ---\n" + final_text)


async def main():
    model_name = os.getenv("LLM_MODEL", "deepseek-r1:8b")
    print(f"使用模型: {model_name}")

    client = OllamaChatCompletionClient(model=model_name)
    try:
        # 并发运行多个示例以观察不同路径（使用工具/直接回答）
        tasks = [
            decision_and_answer_flow(client, "法国的首都是什么？"),
            decision_and_answer_flow(client, "伦敦天气怎么样？"),
            decision_and_answer_flow(client, "告诉我一些关于狗的事情。"),
        ]
        await asyncio.gather(*tasks)
    finally:
        try:
            await client.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
