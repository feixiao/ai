# 安装 OpenAI SDK：pip install openai
from openai import OpenAI

# 使用 Ollama 本地部署的 deepseek-chat 模型 
# pip install openai
# ollama run  deepseek-r1:32b

# 创建 API 客户端

dpApiKey="ollama" #随便写的，没有生成apikey
client = OpenAI(api_key=dpApiKey, base_url="http://localhost:11434/v1")

# 调用 deepseek-chat 模型
response = client.chat.completions.create(
    model="deepseek-r1:32b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "什么是CNN神经网络?"},
    ],
    stream=False  # 设置为 True 可启用流式输出
)

# 输出响应内容
print(response.choices[0].message.content)