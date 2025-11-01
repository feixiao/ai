# LangChain入门

### 环境准备
```shell
pyenv virtualenv 3.12 llm
pyenv activate llm

pip install -r requirements.txt
```

#### 安装测试
```shell
python3 - <<'PY'
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
print("imports OK")
PY
```

#### 启动模型
```shell
ollama serve
ollama pull deepseek-r1:14b
ollama run deepseek-r1:14b
```