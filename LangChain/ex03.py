from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain


# 多个LLM实例和工具模块组成一个多步骤的序练


llm_summary =Ollama(model="deepseek-r1:14b", temperature=0.5)
llm_detail = Ollama(model="deepseek-r1:14b", temperature=0.7)


prompt_summary = PromptTemplate(template="简要介绍{topic}定义。")
prompt_api = PromptTemplate(template="基于以下内容描述{api_data}在{topic}中的作用。")
prompt_detail = PromptTemplate(template="结合概述和API描述,详细描述{topic}的行业应用：{summary}")


chain_summary = LLMChain(llm=llm_summary, prompt=prompt_summary)
chain_api = LLMChain(llm=llm_detail, prompt=prompt_api)
chain_detail = LLMChain(llm=llm_detail, prompt=prompt_detail)


def fetch_data(topic):
    # 模拟获取API数据
    return f"{topic}的最新应用数据"

def multi_step_chain(topic):
    # 第一步：获取概述
    summary = chain_summary.invoke({"topic": topic})['text']
    
    # 第二步：获取API数据描述
    api_data = fetch_data(topic)
    api_description = chain_api.invoke({"api_data": api_data, "topic": topic})['text']
    
    # 第三步：详细描述行业应用
    detailed_description = chain_detail.invoke({
        "topic": topic,
        "summary": summary
    })['text']
    
    return detailed_description



# 运行多步骤链
topic = "人工智能"
result = multi_step_chain(topic)
print(result)
