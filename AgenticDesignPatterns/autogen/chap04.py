"""
Autogen 版本：反思循环示例（多步骤改进 Python 代码）

该脚本参考 `langchain/chap04.py` 的逻辑：
- 任务：生成并改进一个名为 `calculate_factorial` 的 Python 函数；
- 通过多轮生成 + 代码审查（反思）循环，逐步改进代码；
- 当审查返回 `CODE_IS_PERFECT` 时停止。

实现说明：
- 使用 `autogen_ext.models.ollama.OllamaChatCompletionClient` 与模型交互；
- 为兼容不同返回格式，对响应做兼容性解析；
- 所有提示均使用中文，结果也以中文输出。

运行：
```bash
export LLM_MODEL=deepseek-r1:8b
python3 autogen/chap04.py
```
"""

import os
import asyncio
from typing import Optional

from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient


def extract_text_from_resp(resp) -> str:
	"""从不同返回结构中安全提取模型文本响应。"""
	try:
		if hasattr(resp, "choices"):
			return resp.choices[0].message.content
		if isinstance(resp, dict) and "choices" in resp:
			return resp["choices"][0]["message"]["content"]
	except Exception:
		pass
	return str(resp)


async def run_reflection_loop(model_name: Optional[str] = None):
	"""
	运行反思循环：生成 -> 代码审查 -> 根据审查改进，最多迭代若干次。
	"""
	model_name = model_name or os.getenv("LLM_MODEL", "deepseek-r1:8b")
	client = OllamaChatCompletionClient(model=model_name)

	task_prompt = (
		"你的任务是创建一个名为 `calculate_factorial` 的 Python 函数。\n"
		"该函数应满足以下要求：\n"
		"1. 接受一个整数参数 `n`。\n"
		"2. 返回 n 的阶乘（n!）。\n"
		"3. 包含清晰的文档字符串，解释函数用途和参数。\n"
		"4. 处理边界情况：0 的阶乘为 1。\n"
		"5. 对于负数输入应抛出 `ValueError`。\n"
	)

	max_iterations = 3
	current_code = ""

	# 把任务提示作为消息历史的第一条
	message_history = [UserMessage(content=task_prompt, source="user")]

	try:
		for i in range(max_iterations):
			print("\n" + "=" * 20 + f" 反思循环：第 {i+1} 次迭代 " + "=" * 20)

			# 生成或改进代码
			if i == 0:
				print("\n>>> 阶段 1：生成初始代码...")
				resp = await client.create(message_history)
				current_code = extract_text_from_resp(resp)
			else:
				print("\n>>> 阶段 1：根据上次批评改进代码...")
				# 将上次生成的代码加入上下文，要求模型改进
				message_history.append(UserMessage(content=f"上次生成的代码:\n{current_code}", source="user"))
				message_history.append(UserMessage(content="请根据上次的批评意见改进代码。", source="user"))
				resp = await client.create(message_history)
				current_code = extract_text_from_resp(resp)

			print("\n--- 生成的代码（版本 " + str(i + 1) + ") ---\n")
			print(current_code)

			# 反思/审查阶段
			print("\n>>> 阶段 2：对生成的代码进行反思（代码审查）...")
			reflector_system = (
				"你是一名资深软件工程师，精通 Python。\n"
				"你的任务是对给定的 Python 代码进行严格审查，基于原始任务要求判断是否存在错误或改进空间。\n"
				"如果代码完全符合要求，请仅回复 CODE_IS_PERFECT；否则，请以条目形式列出具体批评意见。"
			)

			# 合并 task_prompt 与当前代码并发送给“审稿人”模型
			reflect_prompt = f"SYSTEM:\n{reflector_system}\n\nTASK:\n{task_prompt}\n\nCODE_TO_REVIEW:\n{current_code}"
			critique_resp = await client.create([UserMessage(content=reflect_prompt, source="user")])
			critique = extract_text_from_resp(critique_resp)

			if critique is None:
				critique = "未能获取审查结果。"

			# 停止条件
			if "CODE_IS_PERFECT" in critique:
				print("\n--- 批评结果 ---\n未发现进一步问题，代码被认为是完善的。")
				break

			print("\n--- 批评结果 ---\n" + critique)
			# 将批评加入消息历史，用于下一轮改进
			message_history.append(UserMessage(content=f"上次代码的批评意见:\n{critique}", source="user"))

		print("\n" + "=" * 30 + " 最终结果 " + "=" * 30)
		print("\n反思过程结束后得到的最终优化代码：\n")
		print(current_code)

	except Exception as e:
		print(f"执行反思循环时出错: {e}")
	finally:
		try:
			await client.close()
		except Exception:
			pass


async def main():
	model_name = os.getenv("LLM_MODEL", "deepseek-r1:8b")
	print(f"使用模型: {model_name}")
	await run_reflection_loop(model_name=model_name)


if __name__ == "__main__":
	asyncio.run(main())

