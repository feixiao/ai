"""
Autogen 版本并行示例：并行生成总结、问题和关键术语，然后综合回答

思路：使用 Autogen 的 Ollama 客户端并行调用模型（asyncio.gather），
分别生成 summary、questions、key_terms，随后将三者与原始话题一起
传入一次综合提示，再次调用模型输出最终答案。

使用方法：
```bash
export LLM_MODEL=deepseek-r1:8b
python3 autogen/chap03.py
```
"""

import os
import asyncio
from typing import Optional

from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient


async def call_model(client: OllamaChatCompletionClient, prompt: str) -> str:
    """调用 Ollama 客户端并提取文本响应，兼容不同返回结构。"""
    resp = await client.create([UserMessage(content=prompt, source="user")])
    try:
        if hasattr(resp, "choices"):
            return resp.choices[0].message.content
        if isinstance(resp, dict) and "choices" in resp:
            return resp["choices"][0]["message"]["content"]
    except Exception:
        pass
    return str(resp)


async def run_parallel_example(topic: str, model_name: Optional[str] = None) -> None:
    """
    并行执行三条子任务（summary/questions/key_terms），再综合生成最终回答。

    参数：
    - topic: 输入的话题文本
    - model_name: Ollama 模型名，若为空则从环境变量读取
    """
    model_name = model_name or os.getenv("LLM_MODEL", "deepseek-r1:8b")
    client = OllamaChatCompletionClient(model=model_name)

    # 为每个子任务构造提示
    summarize_prompt = f"简要总结以下话题：\n\n{topic}\n\n请用中文简洁回答。"
    questions_prompt = f"生成三个关于以下话题的有趣问题：\n\n{topic}\n\n每行一个问题。"
    terms_prompt = f"识别以下话题中的 5-10 个关键术语，用逗号分隔：\n\n{topic}\n\n只返回术语列表。"

    print(f"\n--- 并行调用模型生成 summary/questions/key_terms（模型: {model_name}）---")
    try:
        # 并发运行三个调用
        summary_task = call_model(client, summarize_prompt)
        questions_task = call_model(client, questions_prompt)
        terms_task = call_model(client, terms_prompt)

        summary, questions, key_terms = await asyncio.gather(
            summary_task, questions_task, terms_task
        )

        print("\n--- 子任务输出（并行结果）---")
        print("Summary:\n", summary)
        print("Questions:\n", questions)
        print("Key Terms:\n", key_terms)

        # 构造综合提示，将并行生成的结果传入
        synthesis_prompt = (
            "根据以下信息对话题给出一个综合且简洁的回答：\n\n"
            f"总结: {summary}\n\n"
            f"相关问题: {questions}\n\n"
            f"关键术语: {key_terms}\n\n"
            f"原始话题: {topic}\n\n请用中文给出最终回答，保持条理清晰。"
        )

        final = await call_model(client, synthesis_prompt)
        print("\n--- 最终综合回答 ---")
        print(final)

    except Exception as e:
        print(f"执行并行示例时出错: {e}")
    finally:
        try:
            await client.close()
        except Exception:
            pass


if __name__ == "__main__":
    test_topic = "太空探索的历史"
    asyncio.run(run_parallel_example(test_topic))
