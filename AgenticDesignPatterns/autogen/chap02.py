"""
AssistantAgent 版本的路由示例（无回退）

需求：参考 langchain/chap02.py，实现路由 -> 委派逻辑，但仅使用
`autogen_agentchat.AssistantAgent`。如果环境未安装 `autogen-agentchat`
或无法构造 AssistantAgent，将直接抛出 ImportError/TypeError 以提示安装或调整。

运行示例：
```bash
export LLM_MODEL=deepseek-r1:8b
python3 autogen/chap02.py
```
"""

import os
import asyncio
from typing import Any

try:
    # AssistantAgent 位于 autogen_agentchat.agents 模块内
    from autogen_agentchat.agents import AssistantAgent  # type: ignore
except Exception as exc:  # 明确失败原因，直接抛出
    raise ImportError(
        "缺少 autogen-agentchat（或版本不含 AssistantAgent），请安装/升级：pip install autogen-agentchat"
    ) from exc


def booking_handler(request: str) -> str:
    print("\n--- 委派至预订处理程序 ---")
    return f"预订处理程序已处理请求: '{request}'。结果：模拟的预订操作。"


def info_handler(request: str) -> str:
    print("\n--- 委派至信息处理程序 ---")
    return f"信息处理程序已处理请求: '{request}'。结果：模拟的信息检索操作。"


def unclear_handler(request: str) -> str:
    print("\n--- 处理不明确的请求 ---")
    return f"协调器无法委派该请求: '{request}'。请进一步说明。"


async def run_agent(agent: Any, prompt: str) -> str:
    """调用 AssistantAgent.run 并提取文本结果。

    AssistantAgent.run(task=...) 返回 TaskResult，包含 messages 序列。
    我们取最后一个带 content 属性的消息内容作为决策文本。
    """
    out = agent.run(task=prompt)
    if asyncio.iscoroutine(out):
        out = await out

    # 尝试解析 TaskResult.messages
    messages = getattr(out, "messages", None) or []
    content = None
    for msg in reversed(messages):
        if hasattr(msg, "content"):
            content = getattr(msg, "content", None)
            if content:
                break
    if content is None:
        content = str(out)
    return str(content)


async def route_request_with_agent(agent: Any, request: str) -> str:
    prompt = (
        "分析用户请求并确定应由哪个专业处理程序负责。\n"
        "- 若请求涉及预订航班或酒店，请输出 'booker'；\n"
        "- 若请求为一般信息查询，请输出 'info'；\n"
        "- 若请求不清晰或不属于上述类别，请输出 'unclear'；\n"
        "仅输出一个单词：'booker'、'info' 或 'unclear'。\n\n"
        f"用户请求：{request}\n"
    )
    decision_text = await run_agent(agent, prompt)
    decision = (decision_text or "").strip().lower()
    if decision.startswith("book"):
        return booking_handler(request)
    if decision.startswith("info"):
        return info_handler(request)
    return unclear_handler(request)


async def main():
    model_name = os.getenv("LLM_MODEL", "deepseek-r1:8b")
    print(f"使用模型: {model_name}")

    # 构造 AssistantAgent：该版本需要显式传入 model_client
    from autogen_ext.models.ollama import OllamaChatCompletionClient

    agent_client = OllamaChatCompletionClient(model=model_name)
    agent = AssistantAgent(
        name="router",
        model_client=agent_client,
        system_message="你是路由器，只输出 booker/info/unclear 三选一。",
    )

    for label, req in [
        ("A", "帮我订一张去伦敦的机票。"),
        ("B", "意大利的首都是哪里？"),
        ("C", "告诉我关于量子物理的事情。"),
    ]:
        result = await route_request_with_agent(agent, req)
        print(f"最终结果 {label}: {result}")

    try:
        await agent_client.close()
    except Exception:
        pass


if __name__ == "__main__":
    asyncio.run(main())
