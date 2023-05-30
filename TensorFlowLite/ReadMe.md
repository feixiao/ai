## TensorFlowLite

#### 安装 tensorflow

##### OSX

```shell
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
bash Miniforge3-MacOSX-arm64.sh

source ~/.zshrc
conda create -n py39 python=3.9
conda activate py39

conda install -c apple tensorflow-deps==2.6.0
python3 -m pip install tensorflow-macos
python3 -m pip install tensorflow-metal

# 测试
python3 tf.py
```

##### Ubuntu

#### 参考资料

- [macOS M1 安装运行 TensorFlow](https://www.pimspeak.com/macos-m1-install-tensorflow-speed-test.html)
