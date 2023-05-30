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
```shell
# anaconda
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh
bash Anaconda3-2023.03-1-Linux-x86_64.sh

conda create -n "py39" python=3.9
# 激活子环境
conda activate "py39"  #  conda deactivate

conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/msys2/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/

conda install tensorflow-gpu==2.6.0

conda run tf.py
```

#### 参考资料

- [macOS M1 安装运行 TensorFlow](https://www.pimspeak.com/macos-m1-install-tensorflow-speed-test.html)
