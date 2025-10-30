# 安装 OpenAI SDK：pip install openai
from openai import OpenAI

# pip install openai
# 创建 API 客户端
client = OpenAI(api_key="sk-xxxxxxxxxxxxxxxxxxxx", base_url="https://api.deepseek.com")

# 调用 deepseek-chat 模型
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "什么是CNN神经网络?"},
    ],
    stream=False  # 设置为 True 可启用流式输出
)

# 输出响应内容
print(response.choices[0].message.content)