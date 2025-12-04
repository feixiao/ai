"""
Autogen 版本：多智能体协作示例（研究员 -> 撰稿人）

说明：参考 `langchain/chap07.py`。
此实现使用 Autogen 的 Ollama 客户端实现一个顺序执行的“团队”：
- 研究员先生成排名前3的新兴 AI 趋势（包含要点与简短来源说明）；
- 撰稿人接收研究结果并撰写一篇约500字的博客文章；

该脚本不依赖 CrewAI，而是用更轻量的方式展示多 Agent 协作的逻辑。

运行示例：
```bash
export LLM_MODEL=deepseek-r1:8b
python3 autogen/chap07.py
```
"""

import os
import asyncio
from typing import Optional

from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient


def extract_text_from_resp(resp) -> str:
    try:
        if hasattr(resp, "choices"):
            return resp.choices[0].message.content
        if isinstance(resp, dict) and "choices" in resp:
            return resp["choices"][0]["message"]["content"]
    except Exception:
        pass
    return str(resp)


async def researcher_task(client: OllamaChatCompletionClient, topic: str) -> str:
    """研究员：生成排名前3的新兴趋势，每个趋势包含要点和简短来源说明。"""
    prompt = (
        "你是一位高级研究分析师，擅长发现 AI 领域的新兴趋势。\n"
        f"任务：为主题 '{topic}' 列出排名前3的新兴趋势。每个趋势包含：标题、1-2 行的解释、以及简短的潜在来源或证据。\n"
        "请用中文输出，按数字 1-3 列出，每项之间空一行。"
    )
    resp = await client.create([UserMessage(content=prompt, source="user")])
    return extract_text_from_resp(resp)


async def writer_task(client: OllamaChatCompletionClient, research: str) -> str:
    """撰稿人：根据研究输出撰写约500字的博客文章。"""
    prompt = (
        "你是一名擅长将技术内容转化为普通读者可读文本的技术撰稿人。\n"
        "根据下面的研究结果，撰写一篇约500字的博客文章，语言引人入胜、条理清晰，适合非专业读者。\n\n"
        f"研究结果:\n{research}\n\n请只输出最终文章正文（中文），不需要额外的说明。"
    )
    resp = await client.create([UserMessage(content=prompt, source="user")])
    return extract_text_from_resp(resp)


async def main():
    model_name = os.getenv("LLM_MODEL", "deepseek-r1:8b")
    print(f"使用模型: {model_name}")

    client = OllamaChatCompletionClient(model=model_name)
    try:
        topic = "强化学习在人工智能中的重要性"
        print("\n== 研究员任务: 生成趋势 ==")
        research = await researcher_task(client, topic)
        print("\n研究员输出:\n")
        print(research)

        print("\n== 撰稿人任务: 根据研究撰写博客 ==")
        article = await writer_task(client, research)
        print("\n撰稿人输出（博客文章）:\n")
        print(article)

    except Exception as e:
        print(f"执行时出错: {e}")
    finally:
        try:
            await client.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
