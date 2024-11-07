#### ComfyUI 部署与测试 FLUX.1
##### 安装 HuggingFace下载工具，使用镜像下载速度明显加快：
```shell
export HF_ENDPOINT="https://hf-mirror.com"
pip install -U huggingface_hub hf-transfer
```
##### 下载 HuggingFace 脚本
```shell
export HG_TOKEN="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"
huggingface-cli download --token ${HG_TOKEN} black-forest-labs/FLUX.1-dev --local-dir FLUX.1-dev --include "flux1-dev.safetensors" 

huggingface-cli download --token ${HG_TOKEN}  black-forest-labs/FLUX.1-dev --local-dir FLUX.1-dev --include "ae.safetensors"

huggingface-cli download --token ${HG_TOKEN}  stabilityai/stable-diffusion-3-medium --local-dir stable-diffusion-3-medium 
```

##### 下载模型
```shell
git clone https://gitee.com/hf-models/stable-diffusion-3-medium.git

cd stable-diffusion-3-medium

# 
git lfs pull

```

##### 配置模型
```shell

export ComfyUI=/Users/frank/forbuild/ComfyUI-0.2.4
${ComfyUI}/models/unet/flux1-dev.safetensors
${ComfyUI}/models/vae/ae.safetensors

# 来自stable-diffusion-3-medium
${ComfyUI}/models/clip/clip_l.safetensors
${ComfyUI}/models/clip/t5xxl_fp16.safetensors
```

#### 导入对应的工作流
https://comfyui-wiki.com/zh-CN/tutorial/advanced/flux1-comfyui-guide-workflow-and-examples.zh-CN

#### 参考资料
+ [《使用 ComfyUI 部署与测试 FLUX.1 图像生成模型 教程》](https://blog.csdn.net/caroline_wendy/article/details/141201307)