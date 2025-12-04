
import os 
import asyncio
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage
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

llm = build_model("ollama")

def run_reflection_loop():
   """
   演示一个多步骤的 AI 反思循环，用于逐步改进一个 Python 函数。
   """
   # --- 核心任务 ---
   task_prompt = """
   你的任务是创建一个名为 `calculate_factorial` 的 Python 函数。
   该函数应满足以下要求：
   1. 接受一个整数参数 `n`。
   2. 计算它的阶乘（n!）。
   3. 包含一个清晰的文档字符串，说明函数的功能。
   4. 处理边界情况：0 的阶乘应为 1。
   5. 处理无效输入：若输入为负数，应抛出 ValueError。
   """

   # --- 反思循环 ---
   max_iterations = 3
   current_code = ""

   # 构建消息历史，以便在每一步提供上下文信息
   message_history = [HumanMessage(content=task_prompt)]

   for i in range(max_iterations):
       print("\n" + "="*25 + f" 反思循环：第 {i + 1} 次迭代 " + "="*25)

       # --- 1. 生成 / 优化阶段 ---
       # 第一次迭代生成代码，之后的迭代基于反馈进行优化
       if i == 0:
           print("\n>>> 阶段 1：生成初始代码...")
           # 第一次只需要任务提示
           response = llm.invoke(message_history)
           current_code = response.content
       else:
           print("\n>>> 阶段 1：根据上次批评意见改进代码...")
           # 消息历史中包含任务、上次的代码及其批评
           # 我们要求模型根据批评进行改进
           message_history.append(HumanMessage(content="请根据提供的批评意见改进代码。"))
           response = llm.invoke(message_history)
           current_code = response.content

       print("\n--- 生成的代码 (版本 " + str(i + 1) + ") ---\n" + current_code)
       message_history.append(response)  # 将生成的代码加入历史记录

       # --- 2. 反思阶段 ---
       print("\n>>> 阶段 2：对生成的代码进行反思...")

       # 为“反思代理”创建专用提示
       # 模型将在此阶段扮演高级代码审查工程师
       reflector_prompt = [
           SystemMessage(content="""
               你是一名资深软件工程师，精通 Python。
               你的任务是对给定的 Python 代码进行细致的代码审查。
               请根据原始任务要求，严格检查以下内容：
               - 是否存在错误；
               - 是否符合代码风格；
               - 是否处理了边界情况；
               - 是否有改进空间。
               如果代码完全符合要求，请仅回复 "CODE_IS_PERFECT"。
               否则，请以项目符号（•）形式列出你的批评意见。
           """),
           HumanMessage(content=f"原始任务:\n{task_prompt}\n\n待审查代码:\n{current_code}")
       ]

       critique_response = llm.invoke(reflector_prompt)
       critique = critique_response.content

       # --- 3. 停止条件 ---
       if"CODE_IS_PERFECT"in critique:
           print("\n--- 批评结果 ---\n未发现进一步问题，代码已令人满意。")
           break

       print("\n--- 批评结果 ---\n" + critique)
       # 将批评内容添加到历史中，用于下一轮改进
       message_history.append(HumanMessage(content=f"上次代码的批评意见:\n{critique}"))

   print("\n" + "="*30 + " 最终结果 " + "="*30)
   print("\n反思过程结束后得到的最终优化代码：\n")
   print(current_code)

if __name__ == "__main__":
   run_reflection_loop()
