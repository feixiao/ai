"""
Lightweight tool-augmented flow using autogen-agentchat for models without native tool calling.

Flow:
1) decision_agent emits JSON {"decision": "use_tool|answer", "tool_input": "..."}.
2) Optional Python tool execution (search_information) for simple factual lookup.
3) final_agent produces the final answer combining tool output if present.

Works with Ollama models like deepseek-r1 that lack tool-calling support; if using a model
that can call tools (e.g., qwen3:8b) and the SDK exposes Tool, tool schemas are attached
while keeping the manual fallback.
"""

import asyncio
import json
import os
from typing import Iterable, List, Tuple

from autogen_agentchat.agents import AssistantAgent
try:
	# Some SDK versions expose a Tool helper; keep optional to avoid import errors.
	from autogen_agentchat.tools import Tool  # type: ignore
except Exception:  # pragma: no cover
	Tool = None  # type: ignore

from autogen_ext.models.ollama import OllamaChatCompletionClient


def _extract_text(messages: Iterable) -> str:
	"""Flatten TaskResult.messages into plain text across SDK variants."""
	parts: List[str] = []
	for message in messages:
		content = getattr(message, "content", None)
		if isinstance(content, str):
			parts.append(content)
			continue
		if isinstance(content, list):
			for item in content:
				if isinstance(item, str):
					parts.append(item)
					continue
				if isinstance(item, dict):
					txt = item.get("text") or item.get("content")
					if isinstance(txt, str):
						parts.append(txt)
						continue
				txt_attr = getattr(item, "text", None)
				if isinstance(txt_attr, str):
					parts.append(txt_attr)
					continue
				content_attr = getattr(item, "content", None)
				if isinstance(content_attr, str):
					parts.append(content_attr)
					continue
				parts.append(str(item))
	return "\n".join(filter(None, parts)).strip()


def _build_client() -> OllamaChatCompletionClient:
	model_name = os.getenv("LLM_MODEL", "deepseek-r1:14b")
	return OllamaChatCompletionClient(model=model_name, temperature=0.2)


def search_information(query: str) -> str:
	"""Simulated search tool returning canned answers."""
	print(f"\n--- 工具已调用: search_information，查询: '{query}' ---")
	simulated = {
		"weather in london": "伦敦目前多云，气温15°C。",
		"capital of france": "法国的首都是巴黎。",
		"population of earth": "地球的估计人口约为80亿。",
		"tallest mountain": "珠穆朗玛峰是地球上最高的山峰（海拔）。",
	}
	result = simulated.get(query.lower(), f"“{query}”的模拟搜索结果: 未找到具体信息，但该主题似乎很有趣。")
	print(f"--- 工具结果: {result} ---")
	return result


def _parse_decision(raw: str, fallback_query: str) -> Tuple[str, str]:
	"""Parse JSON decision; fallback to simple heuristics."""
	decision = "answer"
	tool_input = ""
	try:
		obj = json.loads(raw.strip())
		decision = obj.get("decision", decision)
		tool_input = obj.get("tool_input", tool_input)
	except Exception:
		lowered = raw.lower()
		if "use_tool" in lowered:
			decision = "use_tool"
	if decision == "use_tool" and not tool_input:
		tool_input = fallback_query
	return decision, tool_input


async def run_agent_with_tool(question: str, decision_agent: AssistantAgent, final_agent: AssistantAgent) -> None:
	print(f"\n--- 正在处理查询: '{question}' ---")

	decision_prompt = (
		"你是一个决策器。判断用户问题是否需要使用提供的工具 search_information。\n"
		"只输出一个JSON对象，不要多余文本。键为 decision 与 tool_input。示例：\n"
		"{\"decision\": \"use_tool|answer\", \"tool_input\": \"weather in London\"}\n"
		"若问题涉及地理事实/天气/人口/最高山等，选择 use_tool，并将查询翻译为简洁英文；"
		"否则输出 answer 并将 tool_input 设为空字符串。\n"
		f"用户问题：{question}"
	)

	decision_result = await decision_agent.run(task=decision_prompt)
	decision_text = _extract_text(decision_result.messages)
	choice, tool_input = _parse_decision(decision_text, question)

	tool_result = ""
	if choice == "use_tool":
		tool_result = search_information(tool_input or question)

	final_prompt = (
		"你是一个乐于助人的助手，尽量简洁、准确，用中文回答。\n"
		f"原始问题：{question}\n"
		f"工具检索结果：{tool_result}\n"
		"请结合工具结果给出最终回答。若工具结果为空，则直接回答。"
	)

	final_result = await final_agent.run(task=final_prompt)
	final_text = _extract_text(final_result.messages)
	print("\n--- ✅ 最终回答 ---\n" + final_text)


async def main() -> None:
	client = _build_client()

	# If the backend model supports tool-calling (e.g., qwen3:8b), attach the tool schema so the
	# model can invoke it directly. The manual path remains as a fallback.
	search_tool = None
	if Tool is not None:
		try:
			search_tool = Tool(
				name="search_information",
				description="Simple factual lookup returning short facts.",
				func=search_information,
			)
		except Exception:
			search_tool = None

	decision_agent = AssistantAgent(
		name="decision_agent",
		model_client=client,
		system_message="你是一个仅输出 JSON 决策的助手。不要输出除 JSON 外的任何内容。",
		tools=[search_tool] if search_tool else None,
	)

	final_agent = AssistantAgent(
		name="final_agent",
		model_client=client,
		system_message="你是一个乐于助人的助手，回答要准确、简洁，用中文输出。",
		tools=[search_tool] if search_tool else None,
	)

	queries = [
		"法国的首都是什么？",
		"伦敦天气怎么样？",
		"告诉我一些关于狗的事情。",
	]

	await asyncio.gather(*(run_agent_with_tool(q, decision_agent, final_agent) for q in queries))


if __name__ == "__main__":
	asyncio.run(main())
