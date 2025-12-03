

# Agents
# https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/tutorial/agents.html

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import StructuredMessage
from autogen_agentchat.ui import Console
# from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
import os
import asyncio

# Define a tool that searches the web for information.
# For simplicity, we will use a mock function here that returns a static string.
async def web_search(query: str) -> str:
    """Find information on the web"""
    return "AutoGen is a programming framework for building multi-agent applications."

async def main():
    # Create an agent that uses the OpenAI GPT-4o model.
    # model_client = OpenAIChatCompletionClient(
    #     model="gpt-4.1-nano",
    #     # api_key="YOUR_API_KEY",   
    # )

    # Autogen 的 Ollama 客户端会把 model="xxx:8b" 先解析成基名 xxx 再查一张内置的“模型能力表”，决定是否支持工具调用、推理、vision 等。你的 “deepseek-r1-tool-calling” 这个基名不在这张表里，所以报 KeyError。
    # ollama rm deepseek-r1:8b
    # ollama cp deepseek-r1-tool-calling:8b deepseek-r1:8b 
    model_name = "qwen3:8b"
    model_client = OllamaChatCompletionClient(model=model_name)
    
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        tools=[web_search],
        system_message="Use tools to solve tasks.", 
    )

    # Use asyncio.run(agent.run(...)) when running in a script.
    result = await agent.run(task="Find information on AutoGen")
    print(result.messages)

if __name__ == "__main__":
	asyncio.run(main())