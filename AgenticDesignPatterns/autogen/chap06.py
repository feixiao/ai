"""
Planning + writing via autogen-agentchat (qwen3:8b by default).

We use RoundRobinGroupChat with a TextMentionTermination keyword. Planner
creates bullet points, writer produces the summary and appends the stop word.
"""

import asyncio
import os
from typing import Iterable, List, Tuple

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat  # type: ignore
from autogen_ext.models.ollama import OllamaChatCompletionClient

# 规划使代理能够将复杂目标分解为可操作的顺序步骤。 
# 它对于处理多步骤任务、工作流自动化和驾驭复杂环境至关重要。

# Termination keyword: use a rare token to avoid accidental early stop.
TERMINATION_KEYWORD = os.getenv("TERMINATION_KEYWORD", "END_OF_SUMMARY")


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


def _split_sections(text: str) -> Tuple[str, str]:
    """Extract plan/summary sections by markers; fall back to whole text."""
    plan, summary = "", ""

    if "=== 计划 (要点) ===" in text:
        _, _, rest = text.partition("=== 计划 (要点) ===")
        if "=== 摘要 ===" in rest:
            plan_part, _, summary_part = rest.partition("=== 摘要 ===")
            plan = plan_part.strip()
            summary = summary_part.strip()
        else:
            plan = rest.strip()

    if not summary and "=== 摘要 ===" in text:
        _, _, summary_part = text.partition("=== 摘要 ===")
        summary = summary_part.strip()

    if not plan:
        plan = text.strip()
    if not summary:
        summary = text.strip()
    return plan, summary


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
            "你是专业撰稿人。基于给定或已有计划撰写180-220字中文摘要，"
            "结构清晰、信息密度高，适合技术读者。全文只能在摘要结束后最后一行写终止标记。"
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
        "2) writer 根据计划写180-220字中文摘要，以`=== 摘要 ===`开头；\n"
        f"3) writer 仅在摘要结束后，最后一行追加终止标记 `{TERMINATION_KEYWORD}`，不要提前使用。\n"
        "4) 没有完成摘要前不要结束对话；若摘要不足180字必须继续补充。\n"
        f"主题：{topic}"
    )

    result = await team.run(task=task)
    text = _extract_text(result.messages)
    plan, summary = _split_sections(text)
    summary_clean = summary.replace(TERMINATION_KEYWORD, "").strip()

    # 如果摘要长度不足，触发兜底重写一次，保证长度要求。
    if len(summary_clean) < 150:
        rewrite_prompt = (
            "补全摘要以满足长度：写一段180-220字中文摘要，以`=== 摘要 ===`开头，"
            f"摘要结束后最后一行写 `{TERMINATION_KEYWORD}`。\n[计划]\n{plan}"
        )
        rewrite = await writer.run(task=rewrite_prompt)
        summary_clean = _extract_text(rewrite.messages).replace(TERMINATION_KEYWORD, "").strip()

    return "=== 计划 (要点) ===\n" + plan + "\n\n=== 摘要 ===\n" + summary_clean


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
