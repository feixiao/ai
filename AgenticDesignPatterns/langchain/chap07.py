import os

from crewai import Agent, Task, Crew, Process
from crewai import LLM

# 多智能体协作设计模式
# 要点总结：
# 多智能体协作涉及多个智能体共同努力以实现一个共同目标。
# 这种模式利用专业角色、分布式任务和智能体间通信。
# 协作可以采取顺序交接、并行处理、辩论或分层结构等形式。
# 这种模式非常适合需要多样化专业知识或多个不同阶段的复杂问题。
def main():
    """
    使用最新的 Gemini 模型初始化并运行用于内容创建的 AI 团队。
    """

    # 定义要使用的语言模型。
    # 对于前沿（预览版）功能，您可以使用 "ollama deepseek"。
    # 使用本地 Ollama 模型（确保 Ollama 在本机运行并已拉取 deepseek-r1:14b）
    llm = LLM(
        model="ollama/deepseek-r1:14b",
        base_url="http://localhost:11434",
        temperature=0.3,
    )

    # 定义具有特定角色和目标的代理
    researcher = Agent(
        role='高级研究分析师',
        goal='查找并总结人工智能的最新趋势。',
        backstory="您是一位经验丰富的研究分析师，擅长识别关键趋势并综合信息。",
        verbose=True,
        allow_delegation=False,
        llm=llm # 将特定的LLM分配给代理
    )

    # 定义另一个代理
    writer = Agent(
        role='技术内容撰稿人',
        goal='根据研究结果撰写一篇清晰且引人入胜的博客文章。',
        backstory="您是一位技术娴熟的撰稿人，可以将复杂的技术主题转化为易于理解的内容。",
        verbose=True,
        allow_delegation=False,
        llm=llm # 将特定的LLM分配给代理
    )

    # 为代理定义任务, 绑定到代理
    research_task = Task(
        description="研究2024-2025年人工智能领域排名前3的新兴趋势。重点关注实际应用和潜在影响。",
        expected_output="一份关于排名前3的AI趋势的详细总结，包括要点和来源。",
        agent=researcher, # 将任务分配给研究员代理
    )

    # 为撰稿人定义任务，依赖于研究任务的输出
    writing_task = Task(
        description="根据研究结果撰写一篇500字的博客文章。文章应该引人入胜，并易于普通受众理解。",
        expected_output="一篇关于最新AI趋势的完整500字博客文章。",
        agent=writer,
        context=[research_task], # 依赖于研究任务的输出
    )

    # 创建团队
    blog_creation_crew = Crew(
        agents=[researcher, writer], # 定义团队成员
        tasks=[research_task, writing_task], # 绑定任务到团队
        process=Process.sequential, # 顺序执行任务
        llm=llm, # 将团队的默认 LLM 设置为指定模型
        verbose=True  # 设置详细程度以获取详细团队执行日志（布尔值）
    )

    # 执行团队任务
    print("## 正在运行使用 DS 的博客创建团队... ##")
    try:
        result = blog_creation_crew.kickoff()
        print("\n------------------\n")
        print("## 团队最终输出 ##")
        print(result)
    except Exception as e:
        print(f"\n发生了一个意外错误: {e}")


if __name__ == "__main__":
    main()

