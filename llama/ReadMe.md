#### MacBook Pro(M芯片) 搭建DeepSeek R1运行环境(硬件加速)

#### 安装

```shell
brew install llama.cpp
```

#### 下载模型

+ DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
  + DeepSeek-R1:  公司 + 版本,深度求索公司发布的第1版模型
  + Distill-Llama: 训练方法 + 基础架构, 基于 Llama 架构蒸馏训练
  + 8B: 模型大小,约80亿参数
  + Q4_K_M: 量化策略,4-bit混合量化，中等粒度
  + .gguf: 文件格式,新一代统一模型格式(专为本地 CPU/GPU 推理设计，兼容 llama.cpp 等工具)

#### 模型选择建议

##### 量化等级建议：
+ **Q4_K_M** ：平衡精度与速度，最推荐普通用户
+ **Q5_K_M** ：精度更高，速度稍慢
    + **追求效果** → 选更大参数 + 更高精度（如`Qwen-14B-Q5_K_M`）
    + **追求速度/低资源** → 选蒸馏版 + 强量化（如`DeepSeek-Distill-7B-Q4_K_M`）

##### OSX平台选择建议
+ MacBook (内存 ≤ 16GB)​:   DeepSeek-R1:7B、Qwen:7B​ 的 Q4_K_M
+ 高端 Studio (内存 ≥ 64GB)​: DeepSeek-V3​ 等超大规模模型的量化版
+ 目前，MLX等专有格式的生态和优化成熟度不如GGUF

总的来说，在macOS上，Ollama和llama.cpp的性能差异对普通用户而言并不大，Ollama的自动化优化往往能提供更稳定可靠的体验。推荐从Ollama开始你的macOS大模型之旅，除非你有明确且强烈的理由需要直接驾驭llama.cpp。

##### ollama直接运行GGUF模型
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

#### 参考资料

+ [《MacBook Pro(M芯片) 搭建DeepSeek R1运行环境(硬件加速)》](https://blog.csdn.net/DevSeek/article/details/145523888)
