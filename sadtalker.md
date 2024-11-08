#### 下载模型和配置
https://gitee.com/frank2020/sad-talker 项目地址

##### 部署
```shell
#  conda remove --name sadtalker --all
conda create -n sadtalker python=3.10
conda activate sadtalker

# 清华源没有tb-nightly包
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple

# install pytorch 2.0
pip install torch torchvision torchaudio
pip install ffmpeg
pip install -r requirements.txt
#pip install dlib # macOS needs to install the original dlib.
#pip install opencv-python tqdm safetensors scipy scikit-image kornia    
#pip install pydub
#pip uninstall numpy && pip install numpy==2.0.0

# https://nuowa.net/386 No module named 'torchvision.transforms.functional_tensor'

# 下载模型
./scripts/download_models.sh

# 测试内容 SadTalker-0.0.2-rc/examples

#export KMP_DUPLICATE_LIB_OK=TRUE
#export PYTORCH_ENABLE_MPS_FALLBACK=1

python inference.py --driven_audio examples/driven_audio//chinese_news.wav \
                    --source_image examples/source_image/art_0.png \
                    --result_dir examples/test.mp4 \
                    --still \
                    --preprocess full \
                    --enhancer gfpgan 

# 方法二 
# https://docs.coqui.ai/en/latest/installation.html
# pip install tts # 参考https://gitee.com/frank2020/tts 放弃
pip install coqui-tts
export HF_ENDPOINT="https://hf-mirror.com"
python app_sadtalker.py

# 浏览器访问
http://127.0.0.1:7860/

```

##### Intel平台
```shell
conda activate torch-intel
# 清华源没有tb-nightly包
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
pip install -r requirements.txt

export KMP_DUPLICATE_LIB_OK=TRUE
export OCL_ICD_VENDORS=/etc/OpenCL/vendors
python inference.py --driven_audio examples/driven_audio//chinese_news.wav \
                    --source_image examples/source_image/art_0.png \
                    --result_dir examples/test.mp4 \
                    --still \
                    --preprocess full \
                    --enhancer gfpgan 
```


###### ComfyUI方式
```shell
# https://github.com/OpenTalker/SadTalker/releases/tag/v0.0.2-rc
export ComfyUI_PATH=/Users/frank/forbuild/ComfyUI-0.2.4

# 模型和配置拷贝到下面路径
${ComfyUI_PATH}/models/checkpoints/
```

#### 参考资料
+ [《SadTalker》](https://github.com/OpenTalker/SadTalker) SadTalker
+ [《Comfyui-SadTalker》](https://github.com/haomole/Comfyui-SadTalker) Comfyui-SadTalker
