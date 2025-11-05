from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser


model = Ollama(model="deepseek-r1:14b", temperature=0.5)

# 定义任务提示词模版
search_prompt = ChatPromptTemplate.from_template("请帮我找到关于{topic}的相关信息。")
summarize_prompt = ChatPromptTemplate.from_template("请总结以下内容：{content}")


def search_for_info(topic):
    # 模拟搜索信息的函数
    return f"{topic}的相关信息内容"

class SimpleAgent(Agent):
    