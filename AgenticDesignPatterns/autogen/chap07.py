"""
Autogen 版本：多智能体协作（研究员 -> 撰稿人），参考 `langchain/chap07.py`。

这里使用 RoundRobinGroupChat 组织对话：
- researcher 先给出前3大 AI 趋势（含要点与来源线索）；
- writer 基于研究结果撰写约500字中文博客，并在末行追加终止标记；
- TextMentionTermination 负责在看到终止标记后收束对话。

默认模型 qwen3:8b，可通过环境变量 LLM_MODEL 覆盖。
"""

import asyncio
import os
from typing import Iterable, List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat  # type: ignore
from autogen_ext.models.ollama import OllamaChatCompletionClient


def _extract_text(messages: Iterable) -> str:
    """Flatten TaskResult.messages content into plain text."""
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
    return OllamaChatCompletionClient(model=model_name, temperature=0.3)


async def main() -> None:
    client = _build_client()

    researcher = AssistantAgent(
        name="researcher",
        model_client=client,
        system_message=(
            "你是高级研究分析师，擅长发现 AI 新兴趋势，输出简洁要点与来源线索。"
        ),
    )

    writer = AssistantAgent(
        name="writer",
        model_client=client,
        system_message=(
            "你是技术内容撰稿人，能将研究要点转写为约500字的中文博客，"
            "结构清晰，语气亲和，便于普通读者理解。文章末行必须写终止标记 END_OF_ARTICLE。"
        ),
    )

    topic = "2024-2025 年人工智能新兴趋势"

    termination = TextMentionTermination("END_OF_ARTICLE")
    team = RoundRobinGroupChat(
        participants=[researcher, writer],
        termination_condition=termination
    )

    task = (
        "团队协作写作：\n"
        "1) researcher 先列出排名前3的新兴 AI 趋势，每项含标题、1-2 行解释、简短来源线索，中文输出。\n"
        "2) writer 基于研究结果写一篇约500字的中文博客，结构清晰、语气亲和。\n"
        "3) writer 在文章最后一行追加终止标记 END_OF_ARTICLE，完成后停止对话。\n"
        f"主题：{topic}"
    )

    result = await team.run(task=task)
    text = _extract_text(result.messages)

    print(f"使用模型: {os.getenv('LLM_MODEL', 'qwen3:8b')}")
    print("\n== 对话输出 ==\n")
    print(text)


if __name__ == "__main__":
    asyncio.run(main())
