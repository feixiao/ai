
# 提示链

from openai import OpenAI
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 使用 Ollama 本地部署的 deepseek-chat 模型 
# pip install langchain langchain-community langchain-openai langgraph
# ollama run  deepseek-r1:32b


# 为了更好的安全性，从 .env 文件加载环境变量
# from dotenv import load_dotenv
# load_dotenv()
# 请确保在 .env 文件中设置了 OPENAI_API_KEY

# 创建 API 客户端
dpApiKey="ollama" #随便写的，没有生成apikey
llm = OpenAI(api_key=dpApiKey, base_url="http://localhost:11434/v1")

# --- 提示 1：提取信息 ---
prompt_extract = ChatPromptTemplate.from_template(
   "Extract the technical specifications from the following text:\n\n{text_input}"
)


# --- 提示 2：转换为 JSON ---
prompt_transform = ChatPromptTemplate.from_template(
   "Transform the following specifications into a JSON object with 'cpu', 'memory', and 'storage' as keys:\n\n{specifications}"
)

# --- 使用 LCEL 构建提示链 ---
# StrOutputParser() 用于将 LLM 的消息输出转换为简单字符串。
extraction_chain = prompt_extract | llm | StrOutputParser()

# 完整的提示链将提取链的输出作为变量 'specifications' 传入转换提示。
full_chain = (
   {"specifications": extraction_chain}
   | prompt_transform
   | llm
   | StrOutputParser()
)

# --- 运行提示链 ---
input_text = "The new laptop model features a 3.5 GHz octa-core processor, 16GB of RAM, and a 1TB NVMe SSD."

# 使用输入文本字典执行整个提示链。
final_result = full_chain.invoke({"text_input": input_text})

print("\n--- 最终 JSON 输出 ---")
print(final_result)