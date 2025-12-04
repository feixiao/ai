from typing import Optional
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch


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

llm = None
try:
    llm = build_model("ollama")
    print(f"语言模型已初始化: {llm.model}")
except Exception as e:
    print(f"语言模型初始化失败: {e}")
    llm = None


# --- 定义模拟的子代理处理程序（相当于 ADK 的 sub_agents） ---
def booking_handler(request: str) -> str:
   """模拟预订代理处理请求"""
   print("\n--- 委派至预订处理程序 ---")
   return f"预订处理程序已处理请求: '{request}'。结果：模拟的预订操作。"

def info_handler(request: str) -> str:
   """模拟信息查询代理处理请求"""
   print("\n--- 委派至信息处理程序 ---")
   return f"信息处理程序已处理请求: '{request}'。结果：模拟的信息检索操作。"

def unclear_handler(request: str) -> str:
   """处理无法识别或不明确的请求"""
   print("\n--- 处理不明确的请求 ---")
   return f"协调器无法委派该请求: '{request}'。请进一步说明。"

# --- 定义协调器路由链（相当于 ADK 协调器的指令） ---
# 该链用于决定将请求委派给哪个处理程序。
coordinator_router_prompt = ChatPromptTemplate.from_messages([
   ("system", """分析用户请求并确定应由哪个专业处理程序负责。
    - 若请求涉及预订航班或酒店，请输出 'booker'；
    - 若请求为一般信息查询，请输出 'info'；
    - 若请求不清晰或不属于上述类别，请输出 'unclear'。
    仅输出一个单词：'booker'、'info' 或 'unclear'。"""),
   ("user", "{request}")
])

if llm:
   coordinator_router_chain = coordinator_router_prompt | llm | StrOutputParser()

# --- 定义委派逻辑（相当于 ADK 的自动流程，根据 sub_agents 分派） ---
# 使用 RunnableBranch 根据路由结果将任务分派至对应处理程序。

# 定义各个分支逻辑
branches = {
   "booker": RunnablePassthrough.assign(output=lambda x: booking_handler(x['request']['request'])),
   "info": RunnablePassthrough.assign(output=lambda x: info_handler(x['request']['request'])),
   "unclear": RunnablePassthrough.assign(output=lambda x: unclear_handler(x['request']['request'])),
}

# 创建 RunnableBranch。
# 它接收路由链的输出，并根据分类结果将原始请求转发给对应的处理函数。
delegation_branch = RunnableBranch(
   (lambda x: x['decision'].strip() == 'booker', branches["booker"]), # 增加 .strip() 防止多余空格
   (lambda x: x['decision'].strip() == 'info', branches["info"]),     # 同上
   branches["unclear"] # 默认分支，处理“不明确”或其他输出
)

# 将路由链与委派分支组合为一个完整的可运行单元
# 路由链的输出（decision）与原始输入（request）一并传递给委派逻辑
coordinator_agent = {
   "decision": coordinator_router_chain,
   "request": RunnablePassthrough()
} | delegation_branch | (lambda x: x['output'])  # 提取最终输出

# --- 示例运行 ---
def main():

   if not llm:
       print("\n由于语言模型初始化失败，跳过执行。")
       return

   print("--- 运行预订请求示例 ---")
   request_a = "帮我订一张去伦敦的机票。"
   result_a = coordinator_agent.invoke({"request": request_a})
   print(f"最终结果 A: {result_a}")

   print("\n--- 运行信息查询请求示例 ---")
   request_b = "意大利的首都是哪里？"
   result_b = coordinator_agent.invoke({"request": request_b})
   print(f"最终结果 B: {result_b}")

   print("\n--- 运行不明确请求示例 ---")
   request_c = "告诉我关于量子物理的事情。"
   result_c = coordinator_agent.invoke({"request": request_c})
   print(f"最终结果 C: {result_c}")

if __name__ == "__main__":
   main()