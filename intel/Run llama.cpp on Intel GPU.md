
##### 配置Python环境
```shell
conda create -n llm-cpp python=3.11
conda activate llm-cpp

pip install dpcpp-cpp-rt==2024.0.2 mkl-dpcpp==2024.0.0 onednn==2024.0.0 # install oneapi
pip install --pre --upgrade 'ipex-llm[cpp]'

mkdir llama-cpp && cd llama-cpp
init-llama-cpp # init-ollama 区别
```


##### Runtime Configuration
```shell
source /opt/intel/oneapi/setvars.sh
export SYCL_CACHE_PERSISTENT=1
export SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1
# [optional] if you want to run on single GPU, use below command to limit GPU may improve performance
export ONEAPI_DEVICE_SELECTOR=level_zero:0


./main -m mistral-7b-instruct-v0.1.Q4_0.gguf -n 32 --prompt "Once upon a time, there existed a little girl who liked to have adventures. She wanted to go to places and meet new people, and have fun" -t 8 -e -ngl 99 --color

```




#### 参考资料
+ [《Run llama.cpp with IPEX-LLM on Intel GPU》](https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Quickstart/llama_cpp_quickstart.md)
+ [《Run Llama 3 on Intel GPU using llama.cpp and ollama with IPEX-LLM》](https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Quickstart/llama3_llamacpp_ollama_quickstart.md)
+ [《Run Ollama with IPEX-LLM on Intel GPU》](https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Quickstart/ollama_quickstart.md)