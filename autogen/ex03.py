# Teams
# A team is a group of agents that work together to achieve a common goal.
import os
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.ollama import OllamaChatCompletionClient

# RoundRobinGroupChat(轮询群聊)
# 策略：​ 这是最简单、最直接的策略。它严格按照成员列表 (agents参数) 中智能体的顺序来选择下一个发言者。

# SelectorGroupChat(选择器群聊)
# 策略：​ 引入了发言者选择器 (speaker_selection_method)​ 的概念。
# 这个选择器是一个函数，它接收当前的群聊状态（包括消息历史、候选智能体列表、最后发言者等）作为输入，并返回应该被选择的下一个发言者。

# MagenticOneGroupChat(磁性一号群聊)
# 策略：​ 这是 SelectorGroupChat的一个特定实现。它提供了一个预设的、基于 LLM 的​ speaker_selection_method函数。
async def main():
	# Create an OpenAI model client.
    model_name = "qwen3:8b"
    model_client = OllamaChatCompletionClient(model=model_name)

    # Create the primary agent. 
    primary_agent = AssistantAgent(
        "primary",
        model_client=model_client,
        system_message="You are a helpful AI assistant.",
    )

    # Create the critic agent.
    critic_agent = AssistantAgent(  
        "critic",
        model_client=model_client,
        system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
    )

    # Define a termination condition that stops the task if the critic approves.
    text_termination = TextMentionTermination("APPROVE")

    # Create a team with the primary and critic agents.
    team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=text_termination)

    # Use `asyncio.run(...)` when running in a script.
    result = await team.run(task="Write a short poem about the fall season.")
    print(result)

if __name__ == "__main__":
	asyncio.run(main())