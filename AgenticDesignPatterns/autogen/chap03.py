"""
Autogen-AgentChat 版本：并行示例（总结 / 问题 / 关键术语 -> 综合）

参考 `langchain/chap03.py`，使用 `autogen_agentchat.agents.AssistantAgent`
和本地 Ollama 模型并行完成三项子任务后再综合输出。

运行示例：
```bash
export LLM_MODEL=deepseek-r1:8b
python3 autogen/chap03.py
```

依赖：autogen-agentchat、autogen-core、autogen-ext 已安装并可用。
"""

import os
import asyncio
from typing import Any

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient


def extract_text(task_result: Any) -> str:
    """从 TaskResult 中提取最后一条带 content 的消息文本。"""
    messages = getattr(task_result, "messages", None) or []
    for msg in reversed(messages):
        if hasattr(msg, "content") and getattr(msg, "content"):
            return str(getattr(msg, "content"))
    return str(task_result)


async def run_agent(agent: AssistantAgent, prompt: str) -> str:
    out = agent.run(task=prompt)
    if asyncio.iscoroutine(out):
        out = await out
    return extract_text(out)


async def run_parallel_example(topic: str) -> None:
    model_name = os.getenv("LLM_MODEL", "deepseek-r1:14b")
    print(f"使用模型: {model_name}")

    client = OllamaChatCompletionClient(model=model_name)

    def make_agent(name: str, system_prompt: str) -> AssistantAgent:
        return AssistantAgent(
            name=name,
            model_client=client,
            system_message=system_prompt,
        )

    # 四个 agent：总结、提问、术语、综合
    summarizer = make_agent(
        "summarizer", "简要总结以下话题，用中文输出。"
    )
    questioner = make_agent(
        "questioner", "为给定话题生成三个有趣的问题，用中文输出，每行一个。"
    )
    term_agent = make_agent(
        "term_agent", "识别话题中的 5-10 个关键术语，输出逗号分隔列表。"
    )
    synth = make_agent(
        "synthesizer",
        "根据提供的总结、问题、关键术语与原始话题，给出条理清晰的中文综合回答。",
    )

    summarize_prompt = f"话题：{topic}\n请给出简要总结。"
    questions_prompt = f"话题：{topic}\n生成三个有趣的问题，每行一个。"
    terms_prompt = f"话题：{topic}\n识别 5-10 个关键术语，输出逗号分隔列表。"

    print("\n--- 并行生成 summary / questions / key_terms ---")
    summary, questions, key_terms = await asyncio.gather(
        run_agent(summarizer, summarize_prompt),
        run_agent(questioner, questions_prompt),
        run_agent(term_agent, terms_prompt),
    )

    print("\nSummary:\n", summary)
    print("\nQuestions:\n", questions)
    print("\nKey Terms:\n", key_terms)

    synthesis_prompt = (
        "根据以下信息给出综合回答（中文，条理清晰）：\n"
        f"总结: {summary}\n"
        f"相关问题: {questions}\n"
        f"关键术语: {key_terms}\n"
        f"原始话题: {topic}\n"
    )

    final_answer = await run_agent(synth, synthesis_prompt)
    print("\n--- 最终综合回答 ---\n", final_answer)

    try:
        await client.close()
    except Exception:
        pass


async def main():
    await run_parallel_example("太空探索的历史")


if __name__ == "__main__":
    asyncio.run(main())
