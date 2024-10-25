## PyTorch 快速入门

#### 安装

```shell
conda create -n torch-gpuprivate python=3.9
conda activate torch-gpuprivate

pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu 
# conda create -n torch-gpuprivate python=3.9


# https://pytorch.org/
pip3 install torch torchvision torchaudio
```

#### 测试

```python
import torch
print(torch.__version__)
print(torch.cuda.is_available())
```



#### 参考资料
+ [《Accelerated PyTorch training on Mac》](https://developer.apple.com/metal/pytorch/)