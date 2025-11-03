from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser


# 多任务并执行
model = Ollama(model="deepseek-r1:14b", temperature=0.5)


prompt1 = ChatPromptTemplate.from_template("请解释机器学习的基本概念。")
prompt2 = ChatPromptTemplate.from_template("深度学习和机器学习有什么区别？")
prompt3 = ChatPromptTemplate.from_template("人工智能有哪些主要应用？")

output_parser = StrOutputParser()


parallel_tasks = RunnableParallel({
    "task1": prompt1 | model | output_parser,
    "task2": prompt2 | model | output_parser,
    "task3": prompt3 | model | output_parser,
})


results = parallel_tasks.invoke({})

for task, result in results.items():
    print(f"{task}结果: {result}")