##### 在Intel GPU上运行Ollama
```shell
mkdir ollama && cd ollma 
conda activate llm-cpp
init-ollama

export OLLAMA_NUM_GPU=999
export no_proxy=localhost,127.0.0.1
export ZES_ENABLE_SYSMAN=1
source /opt/intel/oneapi/setvars.sh
export SYCL_CACHE_PERSISTENT=1
./ollama serve

# 后台启动
nohup ./ollama serve & 

# export  OLLAMA_HOST=0.0.0.0
# ./ollama serve


# 使用
export OLLAMA_NUM_GPU=999
export no_proxy=localhost,127.0.0.1
export ZES_ENABLE_SYSMAN=1
source /opt/intel/oneapi/setvars.sh
export SYCL_CACHE_PERSISTENT=1


./ollama pull dolphin-phi:latest

# crash 问题没有解决（实际测试跟模型有关）
./ollama run llama3.1
```

#### 安装Open WebUI
```shell
# Ollama在Docker部署
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main



docker run -dit --restart always -p 3000:8080 \
    -e OLLAMA_BASE_URL=http://10.10.120.107:11434 \
    -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
```


#### 参考资料
+ [《Run Ollama with IPEX-LLM on Intel GPU》](https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Quickstart/ollama_quickstart.md)
+ [《Run Open WebUI with Intel GPU》](https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Quickstart/open_webui_with_ollama_quickstart.md)