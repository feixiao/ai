### TTS
#### mozilla TTS
```shell
docker pull synesthesiam/mozilla-tts

# 使用默认
tts --text "Text for TTS" --out_path output/path/speech.wav
```
#### coqui-ai/TTS （网站待关闭状态）
```shell
# https://github.com/idiap/coqui-ai-TTS 三方修改版本
pip install coqui-tts

# no matching manifest for linux/arm64/v8 in the manifest list entries
docker pull ghcr.io/coqui-ai/tts-cpu --platform linux/amd64 

# M1 Pro 运行成功
docker run --name tts --rm --platform linux/amd64 -it -p 5002:5002 \
    --entrypoint /bin/bash ghcr.io/coqui-ai/tts-cpu 

# 浏览器访问
```
##### 模型声音
```shell
# 查看全部模型
tts --list_models
# 查看信息
tts --model_info_by_name tts_models/zh-CN/baker/tacotron2-DDC-GST

# 转换
tts --text "知是行之始，行是知之成。" --out_path aaa.wav --model_name tts_models/zh-CN/baker/tacotron2-DDC-GST
```
+ [模型声音Demo](https://mbarnig.github.io/TTS-Models-Comparison/)
+ [模型下载](https://github.com/coqui-ai/TTS/releases/tag/v0.6.1_models)


#### Parler-TTS






### 参考
+ [《TTS》](https://github.com/mozilla/TTS)
+ [《docker-mozillatts》](https://github.com/synesthesiam/docker-mozillatts)
+ [《语音合成工具Coqui TTS安装及体验》](https://blog.csdn.net/tangyin025/article/details/129525878)