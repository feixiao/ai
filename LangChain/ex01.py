from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

# 创建 Ollama LLM 实例
llm = Ollama(model="deepseek-r1:8b")

# 提示词模版
prompt_template = """
请你简明扼的语言描述企业创新的重要性，并说明如何影响企业的长远发展。
"""

# 构建提示词对象
prompt = PromptTemplate(
    input_variables=[],
    template=prompt_template
)


chain = LLMChain(llm=llm, prompt=prompt)

# 运行链（无输入变量）
result = chain.invoke({})

print(result)