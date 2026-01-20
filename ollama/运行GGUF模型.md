## Ollama部署GGUF模型


### 工具准备
```shell
pip install modelscope
```

### 下载模型
```shell
modelscope download --model Qwen/Qwen3-Embedding-8B-GGUF --local_dir ./models/Qwen3-Embedding-8B-GGUF
```



#### ollama直接运行GGUF模型
+ Modelfile 示例
```shell
# 指定本地GGUF模型文件的路径
FROM /path/to/your/model.gguf
# 设置系统提示词，定义模型角色
SYSTEM "你是一个有用的AI助手。"
# 调整参数，例如控制生成创造性的温度参数
PARAMETER temperature 0.7
```
+ 运行
```shell
ollama create my-model -f ./Modelfile
ollama run my-model
```