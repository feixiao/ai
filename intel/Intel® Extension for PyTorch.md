
##### 配置Python环境
```shell
conda create -n torch-intel python=3.10
conda activate torch-intel

python -m pip install torch==2.3.1+cxx11.abi torchvision==0.18.1+cxx11.abi torchaudio==2.3.1+cxx11.abi intel-extension-for-pytorch==2.3.110+xpu oneccl_bind_pt==2.3.100+xpu --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/
```

#### 参考资料
+ [《Intel® Extension for PyTorch》](https://intel.github.io/intel-extension-for-pytorch/)