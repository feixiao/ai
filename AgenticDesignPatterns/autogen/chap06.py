"""
Planning + writing via autogen-agentchat (qwen3:8b by default).

The SDK lacks Team, but RoundRobinGroupChat exists. We implement a manual
round-robin loop using planner -> writer across a few rounds, driven by
RoundRobinGroupChat.max_round.
"""

import asyncio
import os
from typing import Iterable, List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat  # type: ignore
from autogen_ext.models.ollama import OllamaChatCompletionClient

# Termination keyword: if seen in any agent reply, stop early.
TERMINATION_KEYWORD = os.getenv("TERMINATION_KEYWORD", "APPROVE")


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
    model_name = os.getenv("LLM_MODEL", "qwen3:8b")
    return OllamaChatCompletionClient(model=model_name, temperature=0.4)


async def _run_round_robin(topic: str) -> str:
    client = _build_client()

    # RoundRobinGroupChat requires participants; build with actual agents so max_round is derived consistently.
    planner = AssistantAgent(
        name="planner",
        model_client=client,
        system_message=(
            "你是科技写作规划师。生成4-6个要点计划，中文，每行一个要点，"
            "精炼可执行，无额外解释。"
        ),
    )

    writer = AssistantAgent(
        name="writer",
        model_client=client,
        system_message=(
            "你是专业撰稿人。基于给定或已有计划撰写约200字中文摘要，"
            "结构清晰、信息密度高，适合技术读者。"
        ),
    )

    termination = TextMentionTermination(TERMINATION_KEYWORD)
    team = RoundRobinGroupChat(
        participants=[planner, writer],
        termination_condition=termination,
    )

    task = (
        "团队协作完成写作：\n"
        "1) planner 先给出写作要点计划（4-6条，每行一个），以`=== 计划 (要点) ===`开头；\n"
        "2) writer 根据计划写约200字中文摘要，以`=== 摘要 ===`开头；\n"
        f"3) writer 最后一行追加终止词 `{TERMINATION_KEYWORD}` 以结束对话。\n"
        f"主题：{topic}"
    )

    result = await team.run(task=task)
    return _extract_text(result.messages)


# async def _run_single_pass(topic: str) -> str:
#     client = _build_client()

#     planner = AssistantAgent(
#         name="planner",
#         model_client=client,
#         system_message=(
#             "你是科技写作规划师。生成4-6个要点计划，中文，每行一个要点，"
#             "精炼可执行，无额外解释。"
#         ),
#     )

#     writer = AssistantAgent(
#         name="writer",
#         model_client=client,
#         system_message=(
#             "你是专业撰稿人。基于给定计划撰写约200字中文摘要，"
#             "结构清晰、信息密度高，适合技术读者。"
#         ),
#     )

#     plan_prompt = (
#         "为以下主题生成写作要点计划（4-6条，中文，每行一个要点）：\n"
#         f"主题：{topic}"
#     )
#     plan_result = await planner.run(task=plan_prompt)
#     plan_text = _extract_text(plan_result.messages)

#     write_prompt = (
#         "根据下述计划撰写约200字的中文摘要，保持结构清晰、信息密度高：\n"
#         f"[计划]\n{plan_text}"
#     )
#     summary_result = await writer.run(task=write_prompt)
#     summary_text = _extract_text(summary_result.messages)

#     return "=== 计划 (要点) ===\n" + plan_text + "\n\n=== 摘要 ===\n" + summary_text


async def main() -> None:
    topic = "强化学习在人工智能中的重要性"
    print(f"使用模型: {os.getenv('LLM_MODEL', 'qwen3:8b')}")
    output = await _run_round_robin(topic)
    print("\n=== RoundRobin 轮询输出 ===\n" + output)


if __name__ == "__main__":
    asyncio.run(main())
