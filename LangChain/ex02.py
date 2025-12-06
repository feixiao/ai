from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain


prompt_step_1 = PromptTemplate(template="简要介绍机器学习的基本概念。")
prompt_step_2 = PromptTemplate(template="给予以下内容介绍，描述机器学习的应用领域：{intro}")
prompt_step_3 = PromptTemplate(template="基于应用领域，提供机器学习在金融行业的一个实例：{applications}")



llm = Ollama(model="deepseek-r1:8b", temperature=0.5)

chain_step_1 = LLMChain(llm=llm, prompt=prompt_step_1)
chain_step_2 = LLMChain(llm=llm, prompt=prompt_step_2)
chain_step_3 = LLMChain(llm=llm, prompt=prompt_step_3)


# 初始化一个顺序链，将三个步骤连接起来
sequential_chain = chain_step_1 | chain_step_2 | chain_step_3


input_dict = {
    # No input variables needed for the first step
    "intro":"机器学习是一种通过数据训练模型，使其能够自动识别模式并进行预测的技术。",
    "applications":"机器学习在金融、医疗和教育等多个领域有广泛应用。"
}

# 运行顺序链
result = sequential_chain.invoke(input_dict)

print(result)