
# 提示链
from typing import Optional
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 使用 Ollama 本地部署的 deepseek-chat 模型 
# pip install langchain langchain-community langchain-openai langgraph
# ollama run  deepseek-r1:14b

def build_model(provider: str, model_name: Optional[str] = None):
	provider = provider.lower()

	if provider == "openai":
		# 延迟导入，避免未安装依赖或本地无用时报错
		from langchain_openai import ChatOpenAI

		name = model_name or os.getenv("LLM_MODEL") or "gpt-4o-mini"
		return ChatOpenAI(model=name)

	if provider == "ollama":
		# 延迟导入，避免未安装依赖或本地无用时报错
		from langchain_ollama import ChatOllama

		name = model_name or os.getenv("LLM_MODEL") or "deepseek-r1:14b"
		return ChatOllama(model=name)

	raise ValueError(
		f"Unsupported provider: {provider}. Use 'openai' or 'ollama'."
	)

llm = build_model("ollama")

# --- 提示 1：提取信息 ---
# 第一个用于从输入字符串中提取技术规格信息
prompt_extract = ChatPromptTemplate.from_template(
   "Extract the technical specifications from the following text:\n\n{text_input}"
)


# --- 提示 2：转换为 JSON ---
# 第二个用于将这些规格信息格式化为一个 JSON 对象。
prompt_transform = ChatPromptTemplate.from_template(
   "Transform the following specifications into a JSON object with 'cpu', 'memory', and 'storage' as keys:\n\n{specifications}"
)

# --- 使用 LCEL 构建提示链 ---
# StrOutputParser() 用于将 LLM 的消息输出转换为简单字符串。
# 第一个链extraction_chain用于提取规格信息。
extraction_chain = prompt_extract | llm | StrOutputParser()

# 完整的提示链将提取链的输出作为变量 'specifications' 传入转换提示。
# 完整链full_chain将提取结果作为输入传递给转换提示prompt_transform。
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