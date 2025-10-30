
# 提示链

from openai import OpenAI

# 使用 Ollama 本地部署的 deepseek-chat 模型 
# pip install openai
# ollama run  deepseek-r1:32b

# 创建 API 客户端

dpApiKey="ollama" #随便写的，没有生成apikey
client = OpenAI(api_key=dpApiKey, base_url="http://localhost:11434/v1")
