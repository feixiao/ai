ComfyUI 是一个为 Stable Diffusion 专门设计的基于节点的图形用户界面（GUI）。它使用户能够通过链接不同的块（称为节点）来构建复杂的图像生成工作流程。这些节点可以包括各种任务，如加载检查点模型、输入提示、指定采样器等。

它实际上就是一个比较专业的 Stable Diffusion 运行界面，只不过是节点式的。这种节点式界面其实广泛的存在于各种专业的生产力工具中，例如 Blender、虚幻引擎、达芬奇等。


#### 环境准备
##### PyTorch for Mac with GPU support
```shell
conda create -n torch-gpuprivate python=3.9
conda activate torch-gpuprivate

# Accelerated PyTorch training on Mac
conda install pytorch torchvision torchaudio -c pytorch-nightly
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.1
```
##### 安装包
+   [comfy](https://www.comfy.org/zh-cn/download)

#### ComfyUI
```shell

# 路径 /Users/frank/forbuild/ComfyUI-0.2.4
cd ComfyUI-0.2.4 
pip install -r requirements.txt

# 运行
python main.py

# 浏览器访问 http://127.0.0.1:8188
```

#### 使用

+ Download a checkpoint file. Maybe Stable Diffusion v1.5. Place the file under ComfyUI/models/checkpoints.
+ Refresh the ComfyUI.
+ Click **Load Default button** to use the default workflow.
+ In the Load Checkpoint node, select the checkpoint file you just downloaded.
+ Click **Queue Prompt** and watch your image generated. Play around with the prompts to generate different images.


#### 模型安装
+ [《使用 ComfyUI 部署与测试 FLUX.1 图像生成模型 教程》](https://blog.csdn.net/caroline_wendy/article/details/141201307)

#### 参考资料
+ [《安装》](https://docs.comfy.org/get_started/manual_install#mac-arm-silicon)
+ [《ComfyUI 入门教程》](https://www.uisdc.com/comfyui-3)
+ [《Quick Start》](https://docs.comfy.org/get_started/gettingstarted)
+ [《ComfyUI Stable Diffusion Installation for Apple Silicon (M1/M2/M3)》](https://medium.com/@ingridwickstevens/comfyui-stable-diffusion-installation-for-apple-silicon-m1-m2-m3-a7bd78e86495)
+ [《ComfyUI-MuseTalk》](https://github.com/chaojie/ComfyUI-MuseTalk)