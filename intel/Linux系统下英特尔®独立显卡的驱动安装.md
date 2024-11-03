#### 系统
Arc™系列独立显卡只支持Linux系统下的Ubuntu* 20.04与Ubuntu* 22.04两个版本，你需要确保当前系统版本符合要求。


#### 检查系统配置并开启RBAR功能
```shell
lspci -v |grep -A8 VGA
# 输出
Memory at 6000000000 (64-bit, prefetchable) [size=16G]
```

#### 安装OpenVINO工具套件
```shell
conda create --name openvino_env python=3.9
conda activate openvino_env

pip install "openvino-dev[ONNX,tensorflow2,caffe,kaldi,pytorch,mxnet]"
# pip install -U openvino==2024.3.0


# 下载并安装OpenVINO™ 开发工具套件
git clone https://github.com/openvinotoolkit/openvino.git

# 查看本地支持OpenVINO™ 的推理硬件列表
python3 openvino/samples/python/hello_query_device/hello_query_device.py

GPU.0 => FULL_DEVICE_NAME: Intel(R) UHD Graphics 770 (iGPU)
GPU.1 => FULL_DEVICE_NAME: Intel(R) Arc(TM) A770 Graphics (dGPU)
```

#### 测试ARC系列独立显卡的推理性能
```shell
wget https://huggingface.co/spaces/OpenVINO/HelloWorld/resolve/8a4d33c7b74125813bbe0f853b3614295cf6c7b1/v3-small_224_1.0_float.xml

wget https://huggingface.co/spaces/OpenVINO/HelloWorld/resolve/8a4d33c7b74125813bbe0f853b3614295cf6c7b1/v3-small_224_1.0_float.bin

benchmark_app --path_to_model  "v3-small_224_1.0_float.xml" -d  GPU.1 

```

#### 参考资料
+ [《Linux系统下英特尔®独立显卡的驱动安装》](https://blog.csdn.net/inteldevzone/article/details/130241925)