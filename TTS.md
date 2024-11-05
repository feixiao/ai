### TTS
#### mozilla TTS
```shell
docker pull synesthesiam/mozilla-tts

# 使用默认
tts --text "Text for TTS" --out_path output/path/speech.wav
```
#### coqui-ai/TTS
```shell
# https://github.com/idiap/coqui-ai-TTS 三方修改版本
https://gitee.com/frank2020/tts

# no matching manifest for linux/arm64/v8 in the manifest list entries
docker pull ghcr.io/coqui-ai/tts-cpu --platform linux/amd64 

# M1 Pro 运行成功
docker run --name tts --rm --platform linux/amd64 -it -p 5002:5002 \
    --entrypoint /bin/bash ghcr.io/coqui-ai/tts-cpu 

# 浏览器访问
```
### 声音克隆



### 参考
+ [《TTS》](https://github.com/mozilla/TTS)
+ [《docker-mozillatts》](https://github.com/synesthesiam/docker-mozillatts)
+ [《语音合成工具Coqui TTS安装及体验》](https://blog.csdn.net/tangyin025/article/details/129525878)