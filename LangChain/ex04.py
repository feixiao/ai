from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser


# 一个简单的链式调用示例
prompt = ChatPromptTemplate.from_template("给我讲一个关于{topic}的笑话。")


# model 选择 Ollama 作为 LLM
llm = Ollama(model="deepseek-r1:8b", temperature=0.5)

# 定义输出解析器
output_parser = StrOutputParser()

# 创建链式调用
chain = prompt | llm | output_parser


# 运行链式调用
result = chain.invoke({"topic": "冰淇淋"})
print(result)