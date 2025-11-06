import os
from typing import Optional
from crewai import Agent, Task, Crew, Process, LLM

# 规划使代理能够将复杂目标分解为可操作的顺序步骤。 
# 它对于处理多步骤任务、工作流自动化和驾驭复杂环境至关重要。
# LLM 可以根据任务描述生成分步方法来执行规划。
# 明确提示或设计需要规划步骤的任务会鼓励代理框架中的这种行为。
# Google Deep Research 是一个代理，它使用 Google Search 作为工具分析获取的来源，并进行反思、规划和执行。

"""
使用 CrewAI 原生 LLM 适配本地 Ollama
------------------------------------
CrewAI 的 Agent 接受 CrewAI 自带的 LLM 实例。
要使用本地 Ollama，直接通过 crewai.LLM(model="ollama/<模型名>") 构造即可，
无需 OPENAI_API_KEY。

可选环境变量：
- LLM_MODEL: 指定 Ollama 模型名（默认 deepseek-r1:14b）。
- OLLAMA_HOST: Ollama 服务地址（默认 http://localhost:11434）。

注意：CrewAI 通过 LiteLLM 适配各 Provider，请确保当前 Python 环境已安装 litellm。
"""

# 1) 使用 CrewAI 原生 LLM 直接连接本地 Ollama
_model_name = os.getenv("LLM_MODEL") or "deepseek-r1:14b"
_ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
llm = LLM(
  model=f"ollama/{_model_name}",
  base_url=_ollama_host,
  temperature=0.7,
)

# 2. 定义一个清晰且专注的代理
planner_writer_agent = Agent(
    role='文章规划师和撰写人',
    goal='规划并撰写关于指定主题的简洁、引人入胜的摘要。',
    backstory=(
        '你是一位专业的科技作家和内容策略师。 '
        '你的优势在于在撰写前制定清晰、可行的计划， '
        '确保最终的摘要既信息丰富又易于理解。'
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm # 将特定的LLM分配给代理
 )

# 3. 定义一个具有更结构化和具体预期输出的任务
topic = "强化学习在人工智能中的重要性"
high_level_task = Task(
    description=(
        f"1. 为主题“{topic}”的摘要创建一个要点计划。\n"
        f"2. 根据你的计划撰写摘要，保持在200字左右。"
    ),
    expected_output=(
        "一份包含两个独立部分的最终报告：\n\n"
        "### 计划\n"
        "- 一个要点列表，概述摘要的主要内容。\n\n"
        "### 摘要\n"
        "- 对主题的简洁且结构良好的摘要。"
    ),
    agent=planner_writer_agent,
 )

# 创建一个具有明确流程的团队
crew = Crew(
    agents=[planner_writer_agent],
    tasks=[high_level_task],
    process=Process.sequential,
 )

# 执行任务
print("## 正在运行规划和撰写任务 ##")
result = crew.kickoff()

print("\n\n---\n## 任务结果 ##\n---")
print(result)
