# 并行化

import os 
import asyncio
from typing import Optional


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableParallel, RunnablePassthrough

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

# --- 配置 --- 
# 确保已设置 API 密钥环境变量（例如，OPENAI_API_KEY）
try:
   llm = build_model("ollama")
except Exception as e:
   print(f"初始化语言模型时出错: {e}")
   llm = None

# --- 定义独立的链 --- 
# 这三条链表示可以并行执行的不同任务。

summarize_chain: Runnable = (
   ChatPromptTemplate.from_messages([
       ("system", "简要总结以下话题："),
       ("user", "{topic}")
   ])
   | llm
   | StrOutputParser()
)

questions_chain: Runnable = (
   ChatPromptTemplate.from_messages([
       ("system", "生成三个有趣的问题，关于以下话题："),
       ("user", "{topic}")
   ])
   | llm
   | StrOutputParser()
)

terms_chain: Runnable = (
   ChatPromptTemplate.from_messages([
       ("system", "识别以下话题中的 5-10 个关键术语，用逗号分隔："),
       ("user", "{topic}")
   ])
   | llm
   | StrOutputParser()
)

# --- 构建并行 + 综合链 --- 

# 1. 定义并行执行的任务块。它们的结果与原始话题一起被传递到下一步。
map_chain = RunnableParallel(
   {
       "summary": summarize_chain,  # 话题总结
       "questions": questions_chain,  # 相关问题
       "key_terms": terms_chain,  # 关键术语
       "topic": RunnablePassthrough(),  # 原始话题传递
   }
)

# 2. 定义最终的综合提示模板，将并行结果合并。
synthesis_prompt = ChatPromptTemplate.from_messages([
   ("system", """根据以下信息：
    总结: {summary}
    相关问题: {questions}
    关键术语: {key_terms}
    综合给出一个答案。"""),
   ("user", "原始话题: {topic}")
])

# 3. 构建完整的链，将并行结果直接传入综合提示，再由语言模型和输出解析器处理。
full_parallel_chain = map_chain | synthesis_prompt | llm | StrOutputParser()

# --- 运行链 --- 
async def run_parallel_example(topic: str) -> None:
   """
   异步调用并行处理链，处理指定话题并打印综合结果。

   参数：
       topic: 要处理的输入话题。
   """
   if not llm:
       print("语言模型未初始化，无法运行示例。")
       return

   print(f"\n--- 正在运行并行 LangChain 示例，话题: '{topic}' ---")
   try:
       # `ainvoke` 的输入是单个 'topic' 字符串，
       # 然后将其传递给 `map_chain` 中的每个可执行组件。
       response = await full_parallel_chain.ainvoke(topic)
       print("\n--- 最终响应 ---")
       print(response)
   except Exception as e:
       print(f"\n执行链时发生错误: {e}")

if __name__ == "__main__":
   test_topic = "太空探索的历史"
   # 在 Python 3.7+ 中，使用 asyncio.run 是运行异步函数的标准方法。
   asyncio.run(run_parallel_example(test_topic))