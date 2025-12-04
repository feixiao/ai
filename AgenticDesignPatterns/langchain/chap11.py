"""
动手代码示例 - 迭代 2
为了说明目标设定和监控模式，我们有一个使用 LangChain 和 OpenAI API 的例子：

目标：构建一个 AI 代理，可以根据指定的目标为指定的用例编写代码：
- 接受一个编码问题（用例）作为代码或输入。
- 接受一个目标列表（例如，“简单的”、“经过测试的”、“处理边缘情况”）作为代码或输入。
- 使用一个 LLM（如 GPT-4o）来生成和优化 Python 代码，直到目标达成。（我最多使用 5 次迭代，这也可以基于设定的目标）
- 为了检查我们是否达到了目标，我要求 LLM 来判断
  并只回答 True 或 False，这样更容易停止迭代。
- 将最终代码保存在一个 .py 文件中，文件名清晰并带有头部注释。
"""

import os
import random
import re
from pathlib import Path
from typing import Optional

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
    # 本地 Ollama 模型（例如 deepseek-r1:14b）。注意：该模型不支持 tools。
    from langchain_ollama import ChatOllama

    name = model_name or os.getenv("LLM_MODEL") or "deepseek-r1:14b"
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




# --- 实用工具函数 ---

def generate_prompt(
    use_case: str, goals: list[str], previous_code: str = "",
    feedback: str = ""
) -> str:
    print("为代码生成构建提示...")
    base_prompt = f"""
你是一个 AI 编码代理。你的工作是根据以下用例编写 Python 代码：

用例：{use_case}

你的目标是：
{chr(10).join(f"- {g.strip()}" for g in goals)}
"""
    if previous_code:
        print("将之前的代码添加到提示中以进行优化。")
        base_prompt += f"\n先前生成的代码：\n{previous_code}"
    if feedback:
        print("包含用于修订的反馈。")
        base_prompt += f"\n关于上一版本的反馈：\n{feedback}\n"

    base_prompt += "\n请仅返回修订后的 Python 代码。不要在代码之外包含注释或解释。"
    return base_prompt

def get_code_feedback(code: str, goals: list[str]) -> str:
    print("根据目标评估代码...")
    feedback_prompt = f"""
你是一名 Python 代码审查员。下面显示了一个代码片段。基于以下目标：

{chr(10).join(f"- {g.strip()}" for g in goals)}

请评论这段代码并确定目标是否已满足。如果需要改进清晰度、简单性、正确性、边缘情况处理或测试覆盖率，请提及。

代码：
{code}
"""
    return llm.invoke(feedback_prompt)

def goals_met(feedback_text: str, goals: list[str]) -> bool:
    """
    使用 LLM 评估基于反馈文本是否已满足目标。
    返回 True 或 False（从 LLM 输出中解析）。
    """
    review_prompt = f"""
你是一名 AI 审查员。

以下是目标：
{chr(10).join(f"- {g.strip()}" for g in goals)}

以下是关于代码的反馈：
\"\"\"
{feedback_text}
\"\"\"

根据上面的反馈，目标是否已满足？
只用一个词回答：True 或 False。
"""
    response = llm.invoke(review_prompt).content.strip().lower()
    return response == "true"

def clean_code_block(code: str) -> str:
    lines = code.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return"\n".join(lines).strip()

def add_comment_header(code: str, use_case: str) -> str:
    comment = f"# 此 Python 程序实现了以下用例：\n# {use_case.strip()}\n"
    return comment + "\n" + code

def to_snake_case(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    return re.sub(r"\s+", "_", text.strip().lower())

def save_code_to_file(code: str, use_case: str) -> str:
    print("正在将最终代码保存到文件...")

    summary_prompt = (
        f"将以下用例总结成一个单独的小写单词或短语，"
        f"不超过10个字符，适合用作Python文件名：\n\n{use_case}"
    )
    raw_summary = llm.invoke(summary_prompt).content.strip()
    short_name = re.sub(r"[^a-zA-Z0-9_]", "", raw_summary.replace(" ", "_").lower())[:10]

    random_suffix = str(random.randint(1000, 9999))
    filename = f"{short_name}_{random_suffix}.py"
    filepath = Path.cwd() / filename

    with open(filepath, "w") as f:
        f.write(code)

    print(f"代码已保存到：{filepath}")
    return str(filepath)

# --- 主要代理函数 ---

def run_code_agent(use_case: str, goals_input: str, max_iterations: int = 5) -> str:
    goals = [g.strip() for g in goals_input.split(",")]

    print(f"\n用例：{use_case}")
    print("目标：")
    for g in goals:
        print(f"- {g}")

    previous_code = ""
    feedback = ""

    for i in range(max_iterations):
        print(f"\n=== ☑ 迭代 {i + 1} of {max_iterations} ===")
        prompt = generate_prompt(use_case, goals, previous_code,
                                 feedback if isinstance(feedback, str) else feedback.content)

        print("正在生成代码...")
        code_response = llm.invoke(prompt)
        raw_code = code_response.content.strip()
        code = clean_code_block(raw_code)
        print("\n 生成的代码：\n" + "-" * 50 + f"\n{code}\n" + "-" * 50)

        print("\n提交代码进行反馈审查...")
        feedback = get_code_feedback(code, goals)
        feedback_text = feedback.content.strip()
        print("\n收到的反馈：\n" + "-" * 50 + f"\n{feedback_text}\n" + "-" * 50)

        if goals_met(feedback_text, goals):
            print("☑ LLM 确认目标已满足。停止迭代。")
            break

        print("目标未完全满足。准备下一次迭代...")
        previous_code = code

    final_code = add_comment_header(code, use_case)
    return save_code_to_file(final_code, use_case)

# --- CLI 测试运行 ---

if __name__ == "__main__":
    print("\n欢迎来到 AI 代码生成代理")

    # 示例 1
    use_case_input = "编写代码以查找给定正整数的二进制间距"
    goals_input = "代码易于理解，功能正确，处理全面的边缘情况，仅接受正整数输入，并用少量示例打印结果"
    run_code_agent(use_case_input, goals_input)

    # 示例 2
    # use_case_input = "编写代码以计算当前目录及其所有嵌套子目录中的文件数量，并打印总数"
    # goals_input = (
    #     "代码易于理解，功能正确，处理全面的边缘情况，忽略性能建议，"
    #     "忽略像 unittest 或 pytest 这样的测试套件使用建议"
    # )
    # run_code_agent(use_case_input, goals_input)

    # 示例 3
    # use_case_input = "编写代码，接受一个 word doc 或 docx 文件的命令行输入，打开它并计算其中的单词和字符数，并打印所有内容"
    # goals_input = "代码易于理解，功能正确，处理边缘情况"
    # run_code_agent(use_case_input, goals_input)