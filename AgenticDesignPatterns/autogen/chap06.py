"""
Autogen 版本：规划 + 撰写 代理示例（参考 crewai/chap06.py）

功能简介：
- 使用本地 Ollama 模型（通过 autogen_ext 的 Ollama 客户端）模拟一个“规划者-撰写人”流程：
  1) 根据主题生成一个要点式的写作计划；
  2) 根据计划撰写一段 200 字左右的摘要；
  3) 输出结构化结果（计划 + 摘要）。

说明：此脚本并不依赖 CrewAI。它用更轻量的 Autogen 调用来复现 `langchain/chap06.py` 的意图，
避免对 CrewAI / LiteLLM 的额外依赖，同时能直接在本地 Ollama 上运行（若已安装并启动模型）。

运行示例：
```bash
export LLM_MODEL=deepseek-r1:8b
export OLLAMA_HOST=http://localhost:11434
python3 autogen/chap06.py
```
"""

import os
import asyncio
from typing import Optional

from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient


def extract_text_from_resp(resp) -> str:
    """兼容不同返回结构，提取模型的文本答案。"""
    try:
        if hasattr(resp, "choices"):
            return resp.choices[0].message.content
        if isinstance(resp, dict) and "choices" in resp:
            return resp["choices"][0]["message"]["content"]
    except Exception:
        pass
    return str(resp)


async def plan_and_write(client: OllamaChatCompletionClient, topic: str) -> str:
    """根据主题先生成写作计划，再根据计划写摘要，返回格式化的输出字符串。"""
    # 1) 生成计划（要点列表）
    plan_prompt = (
        "你是一位经验丰富的科技写作规划师。\n"
        f"任务：为主题 '{topic}' 制定一个清晰的要点计划（4-6 个要点），用短句列出每个要点。\n"
        "仅输出要点列表，每行一项，无需多余解释。"
    )
    resp_plan = await client.create([UserMessage(content=plan_prompt, source="user")])
    plan_text = extract_text_from_resp(resp_plan)

    # 2) 根据计划撰写摘要（约200字）
    write_prompt = (
        "你是一位专业撰稿人，请根据下面的要点计划撰写一段约200字的摘要，要求语言简洁、逻辑清晰，适合技术读者阅读。\n\n"
        f"计划:\n{plan_text}\n\n请输出最终摘要文本（中文）。"
    )
    resp_write = await client.create([UserMessage(content=write_prompt, source="user")])
    summary_text = extract_text_from_resp(resp_write)

    # 3) 组合结果并返回
    output = (
        "=== 计划 (要点) ===\n"
        f"{plan_text}\n\n"
        "=== 摘要 ===\n"
        f"{summary_text}\n"
    )
    return output


async def main():
    model_name = os.getenv("LLM_MODEL", "deepseek-r1:8b")
    ollama_host = os.getenv("OLLAMA_HOST")
    print(f"使用模型: {model_name}")
    if ollama_host:
        print(f"OLLAMA_HOST: {ollama_host}")

    client = OllamaChatCompletionClient(model=model_name)
    try:
        print("\n## 运行示例任务：规划并撰写摘要 ##")
        topic = "强化学习在人工智能中的重要性"
        result = await plan_and_write(client, topic)
        print("\n--- 任务结果 ---\n")
        print(result)
    except Exception as e:
        print(f"执行时出错: {e}")
    finally:
        try:
            await client.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
