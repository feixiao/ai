

# Models:
# https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/tutorial/models.html
# 抽象接口访问各种服务提供的模型


import os
import asyncio
from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient

async def main():
	model_name = os.getenv("LLM_MODEL", "deepseek-r1:8b")
	ollama_model_client = OllamaChatCompletionClient(model=model_name)

	response = await ollama_model_client.create([UserMessage(content="What is the capital of France?", source="user")])
	print(response)
	await ollama_model_client.close()

if __name__ == "__main__":
	asyncio.run(main())
