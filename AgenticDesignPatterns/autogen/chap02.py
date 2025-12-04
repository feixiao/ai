"""
Autogen 版本的协调器示例（路由 -> 委派）

功能：
- 使用 Ollama（通过 autogen_ext 的客户端）向模型发送路由提示，要求模型只返回一个单词：
  'booker'、'info' 或 'unclear'。
- 根据模型返回的路由结果，在 Python 端把请求分派给不同的本地处理函数（模拟子代理处理程序）。

说明：该实现参考 `AgenticDesignPatterns/langchain/chap02.py` 的逻辑，
但使用更直接的 Autogen 客户端调用方式，避免对 Autogen 内部 runnable API 的依赖，便于在不同环境中运行。

运行：
```bash
export LLM_MODEL=deepseek-r1:8b
python3 autogen/chap02.py
```
"""

import os
import asyncio
from typing import Any

from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient


def booking_handler(request: str) -> str:
    """模拟处理预订请求的子代理逻辑。"""
    print("\n--- 委派至预订处理程序 ---")
    # 这里可以接入真实的订票系统或调用其他服务；当前为模拟返回。
    return f"预订处理程序已处理请求: '{request}'。结果：模拟的预订操作。"


def info_handler(request: str) -> str:
    """模拟处理信息查询的子代理逻辑。"""
    print("\n--- 委派至信息处理程序 ---")
    # 模拟信息检索结果
    return f"信息处理程序已处理请求: '{request}'。结果：模拟的信息检索操作。"


def unclear_handler(request: str) -> str:
    """处理无法识别或不明确的请求的回退逻辑。"""
    print("\n--- 处理不明确的请求 ---")
    return f"协调器无法委派该请求: '{request}'。请进一步说明。"


async def route_request(model_client: OllamaChatCompletionClient, request: str) -> str:
    """向模型询问路由决策，并将请求分派给对应的处理程序。

    模型应仅返回一个词：'booker'、'info' 或 'unclear'。
    如果返回不明确，则采用默认分支 unclear。
    """
    # 路由提示：明确要求只输出单词，便于解析
    system = (
        "分析用户请求并确定应由哪个专业处理程序负责。\n"
        "- 若请求涉及预订航班或酒店，请输出 'booker'；\n"
        "- 若请求为一般信息查询，请输出 'info'；\n"
        "- 若请求不清晰或不属于上述类别，请输出 'unclear'；\n"
        "仅输出一个单词：'booker'、'info' 或 'unclear'。"
    )

    # 构造用户消息，把 system 与 user 拼接为一次调用的文本
    user_prompt = f"SYSTEM:\n{system}\n\nUSER REQUEST:\n{request}\n\nOnly respond with one word."
    resp = await model_client.create([UserMessage(content=user_prompt, source="user")])

    # 从响应中提取文本（兼容不同返回结构）
    text = None
    try:
        if hasattr(resp, "choices"):
            # OpenAI-like shape
            text = resp.choices[0].message.content
        elif isinstance(resp, dict) and "choices" in resp:
            text = resp["choices"][0]["message"]["content"]
        else:
            text = str(resp)
    except Exception:
        text = str(resp)

    decision = (text or "").strip().lower()
    # 仅保留字母与下划线部分，防止模型包含注释或多余解释
    if decision.startswith("book"):
        return booking_handler(request)
    if decision.startswith("info"):
        return info_handler(request)
    # 其他情况走回退
    return unclear_handler(request)


async def main():
    model_name = os.getenv("LLM_MODEL", "deepseek-r1:8b")
    print(f"使用模型: {model_name}")

    # 使用 Autogen 的 Ollama 客户端
    client = OllamaChatCompletionClient(model=model_name)

    try:
        print("--- 运行预订请求示例 ---")
        request_a = "帮我订一张去伦敦的机票。"
        result_a = await route_request(client, request_a)
        print(f"最终结果 A: {result_a}")

        print("\n--- 运行信息查询请求示例 ---")
        request_b = "意大利的首都是哪里？"
        result_b = await route_request(client, request_b)
        print(f"最终结果 B: {result_b}")

        print("\n--- 运行不明确请求示例 ---")
        request_c = "告诉我关于量子物理的事情。"
        result_c = await route_request(client, request_c)
        print(f"最终结果 C: {result_c}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
