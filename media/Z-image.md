## Z-image
 Z-image 是一款基于 M1/M2 芯片的 Mac 电脑上运行的图像生成工具，支持 Stable Diffusion 模型，可以生成高质量的图像。 它的设计目标是为 Mac 用户提供一个高效、易用的图像生成解决方案，充分利用 Apple Silicon 的硬件优势。

### [Draw Things](https://zeeklog.com/macshi-yong-z-imagesheng-tu-jiao-cheng-draw-thingspei-zhi-fang-fa-yu-zhen-shi-ce-shi-xiao-guo-mac-xia-ru-he-shi-yong-z-image-turbo-cong-an-zhuang-dao-sheng-tu-de-wan-zheng-jiao-cheng/). 优先

+ 模型路径
```shell
～/Library/Containers/com.liuliu.draw-things/Data/Documents/Models

# qwen_3_vl_4b_instruct_q8p.ckpt
# z_image_turbo_1.0_q6p.ckpt
```

### 基于ComfyUI + GGUF 方案 
在 Mac 上基于ComfyUI + GGUF 方案部署 Z-Image-Turbo，并封装 OpenAI 兼容 API 的全过程。

3-bit 量化的 GGUF 版本模型，并将其作为 UNet 组件放置在特定的目录下。与传统的一体化模型不同，GGUF 方案需要我们将模型拆解，因此我还需要分别准备 Qwen-4B 的 CLIP 模型用于文本理解，以及 Flux 的 VAE 模型用于图像解码，这种模块化的加载方式虽然繁琐，但却是在 Mac 上跑通高性能模型的必经之路。

#### ComfyUI安装
+   [comfy](https://www.comfy.org/zh-cn/download)


#### 模型下载
+  [Z-Image-Turbo](https://huggingface.co/ZJ-NSC/Z-Image-Turbo)

#### 参考
+ [《Z-image的mac使用指南》](https://zjncs.github.io/2025/12/01/12-1-Z-image%E7%9A%84mac%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97/index.html)