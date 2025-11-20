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
    + .gguf: 文件格式,新一代统一模型格式

```shell
DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
```

#### 参考资料
+ [《MacBook Pro(M芯片) 搭建DeepSeek R1运行环境(硬件加速)》](https://blog.csdn.net/DevSeek/article/details/145523888)