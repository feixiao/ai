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
ollama pull deepseek-r1:8b
ollama run deepseek-r1:8b
```


##### 例子
+ [ex01.py](ex01.py) 简单的问答
+ [ex02.py](ex02.py) 多步骤的问答
+ [ex03.py](ex03.py) 多模型的问答
+ [ex04.py](ex04.py) 链式调用
+ [ex05.py](ex05.py) 多任务并行
+ [ex06.py](ex06.py) 多任务并行 + 输出解析
