import os
from typing import Optional

from langchain_core.tools import tool  # 定义/注册可被 LC 使用的 Python 工具
from langchain_core.prompts import PromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableSequence
from langchain_core.runnables.history import RunnableWithMessageHistory


def build_model(provider: str, model_name: Optional[str] = None):
  """根据提供商构建聊天模型。

  参数：
  - provider: "openai" 或 "ollama"
  - model_name: 可选模型名；不传则读取环境变量 LLM_MODEL；再不传使用合理默认值。

  说明：采用“延迟导入”，避免未安装某些依赖时报 ImportError。
  """
  provider = provider.lower()

  if provider == "openai":
    # OpenAI 聊天模型（需要有效的 OpenAI API Key）
    from langchain_openai import ChatOpenAI

    name = model_name or os.getenv("LLM_MODEL") or "gpt-4o-mini"
    return ChatOpenAI(model=name)

  if provider == "ollama":
    # 本地 Ollama 模型（例如 deepseek-r1:8b）。注意：该模型不支持 tools。
    from langchain_ollama import ChatOllama

    name = model_name or os.getenv("LLM_MODEL") or "deepseek-r1:8b"
    return ChatOllama(model=name)

  raise ValueError(
    f"Unsupported provider: {provider}. Use 'openai' or 'ollama'."
  )


try:
    # 需要一个具有函数/工具调用功能的模型。
    llm = build_model("ollama")
    print(f"✅ 语言模型已初始化: {getattr(llm, 'model', 'unknown')}")
except Exception as e:
    print(f"初始化语言模型时出错: {e}")
    llm = None


template = """You are a helpful travel agent.

Previous conversation:
{history}

New question: {question}
Response:"""

prompt = PromptTemplate.from_template(template)

# 2. 配置消息历史存储（按 session_id 隔离）
store = {}

def get_history(session_id: str):
  return store.setdefault(session_id, InMemoryChatMessageHistory())


# 3. 构建链：格式化历史 -> 提示 -> LLM -> 由 RunnableWithMessageHistory 管理历史
def _format_history(inputs: dict):
  msgs = inputs.get("history", []) or []
  history_text = "\n".join(f"{m.type}: {m.content}" for m in msgs)
  return {"question": inputs["question"], "history": history_text}

base_chain = RunnableSequence(_format_history, prompt, llm)

conversation = RunnableWithMessageHistory(
  base_chain,
  get_history,
  input_messages_key="question",
  history_messages_key="history",
)


# 4. 运行对话
def ask(question: str, session_id: str = "demo-session"):
  result = conversation.invoke(
    {"question": question},
    config={"configurable": {"session_id": session_id}},
  )
  print(result)
  return result


ask("I want to book a flight.")
ask("My name is Sam, by theway.")
ask("What was my name again?")