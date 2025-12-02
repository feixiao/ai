

# Models:
# https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/tutorial/models.html
# 抽象接口访问各种服务提供的模型


import os
import asyncio
from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient
import logging

# AutoGen uses standard Python logging module to log events like model calls and responses
from autogen_core import EVENT_LOGGER_NAME

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(EVENT_LOGGER_NAME)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

async def main():
	model_name = os.getenv("LLM_MODEL", "deepseek-r1:8b")
	ollama_model_client = OllamaChatCompletionClient(model=model_name)

	response = await ollama_model_client.create([UserMessage(content="What is the capital of France?", source="user")])
	logging.info(response)
	await ollama_model_client.close()

if __name__ == "__main__":
	asyncio.run(main())
