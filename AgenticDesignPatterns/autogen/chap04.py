"""
Reflection loop using autogen-agentchat AssistantAgent.
Creates a simple coder/reviewer pair that iterates until the code passes review
or the maximum number of rounds is reached.
"""

import asyncio
import os
from typing import Iterable, List

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient


def _extract_text_contents(messages: Iterable) -> str:
    """Flatten TaskResult.messages into a single text string without depending on SDK internals."""
    chunks: List[str] = []
    for message in messages:
        content = getattr(message, "content", None)
        if isinstance(content, str):
            chunks.append(content)
            continue

        if isinstance(content, list):
            for part in content:
                if isinstance(part, str):
                    chunks.append(part)
                    continue

                if isinstance(part, dict):
                    text = part.get("text") or part.get("content")
                    if isinstance(text, str):
                        chunks.append(text)
                    continue

                text_attr = getattr(part, "text", None)
                if isinstance(text_attr, str):
                    chunks.append(text_attr)
                    continue

                content_attr = getattr(part, "content", None)
                if isinstance(content_attr, str):
                    chunks.append(content_attr)
                    continue

                # Fallback to string conversion for unknown types.
                chunks.append(str(part))
    return "\n".join(filter(None, chunks)).strip()


def _build_client() -> OllamaChatCompletionClient:
    model_name = os.getenv("LLM_MODEL", "deepseek-r1:8b")
    # Keep temperature conservative for deterministic improvements.
    return OllamaChatCompletionClient(model=model_name, temperature=0.2)


async def run_reflection_loop() -> None:
    task_prompt = (
        "你的任务是创建一个名为 `calculate_factorial` 的 Python 函数。\n"
        "必须满足：\n"
        "1) 接受整数参数 n；\n"
        "2) 计算阶乘 n!；\n"
        "3) 包含清晰的文档字符串；\n"
        "4) 0 的阶乘为 1；\n"
        "5) 负数输入抛出 ValueError。"
    )

    client = _build_client()

    coder = AssistantAgent(
        name="coder",
        model_client=client,
        system_message=(
            "你是资深 Python 开发者。请直接给出可运行的完整函数实现，"
            "必要时给出最简测试示例。不要长篇解释。"
        ),
    )

    reviewer = AssistantAgent(
        name="reviewer",
        model_client=client,
        system_message=(
            "你是代码审查专家，严格按任务检查代码。\n"
            "若完全符合要求，只回复 CODE_IS_PERFECT；否则用项目符号列出问题。"
        ),
    )

    max_iterations = 3
    current_code = ""
    last_critique = ""

    for idx in range(max_iterations):
        print("\n" + "=" * 25 + f" 反思循环：第 {idx + 1} 次迭代 " + "=" * 25)

        if idx == 0:
            print("\n>>> 阶段 1：生成初始代码...")
            coder_prompt = (
                f"任务:\n{task_prompt}\n\n"
                "请直接输出满足要求的完整 Python 代码，不要解释。"
            )
        else:
            print("\n>>> 阶段 1：根据上次批评改进代码...")
            coder_prompt = (
                f"任务:\n{task_prompt}\n\n"
                "以下是上一版代码与批评意见，请按批评改进：\n"
                f"[上一版代码]\n{current_code}\n\n"
                f"[批评]\n{last_critique}\n"
                "请给出改进后的完整 Python 代码。"
            )

        code_result = await coder.run(task=coder_prompt)
        current_code = _extract_text_contents(code_result.messages)
        print("\n--- 生成的代码 ---\n" + current_code)

        print("\n>>> 阶段 2：对生成的代码进行反思...")
        reviewer_prompt = (
            "请审查下述代码：\n"
            f"[任务]\n{task_prompt}\n\n"
            f"[代码]\n{current_code}\n\n"
            "如满足要求，仅回复 CODE_IS_PERFECT；否则用项目符号列出问题。"
        )
        critique_result = await reviewer.run(task=reviewer_prompt)
        critique_text = _extract_text_contents(critique_result.messages)

        if "CODE_IS_PERFECT" in critique_text.upper():
            print("\n--- 批评结果 ---\n未发现进一步问题，代码已令人满意。")
            break

        last_critique = critique_text
        print("\n--- 批评结果 ---\n" + critique_text)

    print("\n" + "=" * 30 + " 最终结果 " + "=" * 30)
    print("\n反思过程结束后得到的最终优化代码：\n")
    print(current_code)


def main() -> None:
    asyncio.run(run_reflection_loop())


if __name__ == "__main__":
    main()