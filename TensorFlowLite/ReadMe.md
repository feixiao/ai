## TensorFlowLite

#### 安装 tensorflow

##### OSX

```shell
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
bash Miniforge3-MacOSX-arm64.sh

# 添加到bash_profile
source ~/miniforge3/bin/activate
# conda create -n py39 python=3.9
# conda activate py39 # conda deactivate

conda create -n tf_env python=3.8
conda activate tf_env

conda config --add channels http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels http://mirrors.ustc.edu.cn/anaconda/pkgs/main/
conda config --add channels http://mirrors.ustc.edu.cn/anaconda/pkgs/free/
conda config --add channels http://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels http://mirrors.ustc.edu.cn/anaconda/cloud/msys2/
conda config --add channels http://mirrors.ustc.edu.cn/anaconda/cloud/bioconda/
conda config --add channels http://mirrors.ustc.edu.cn/anaconda/cloud/menpo/
conda config --set show_channel_urls yes

conda update --all --yes

conda install tensorflow

# 测试
python3 tf.py

# 存在问题： platform is already registered with name: "METAL"
# 待解决


# fixed err
# module compiled against API version 0x10 but this version of numpy is 0xf
python3 -m  pip install numpy --upgrade

```

##### Ubuntu

```shell
# anaconda
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh
bash Anaconda3-2023.03-1-Linux-x86_64.sh

# 升级
#conda install conda=23.5.0
conda create -n "py39" python=3.9
# 激活子环境
conda activate "py39"  #  conda deactivate

conda config --add channels http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels http://mirrors.ustc.edu.cn/anaconda/pkgs/main/
conda config --add channels http://mirrors.ustc.edu.cn/anaconda/pkgs/free/
conda config --add channels http://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels http://mirrors.ustc.edu.cn/anaconda/cloud/msys2/
conda config --add channels http://mirrors.ustc.edu.cn/anaconda/cloud/bioconda/
conda config --add channels http://mirrors.ustc.edu.cn/anaconda/cloud/menpo/
conda config --set show_channel_urls yes

conda update --all --yes
conda install -c conda-forge tensorflow

conda run tf.py
```

#### 参考资料

- [《Apple MacBook M1 Anaconda 安装 Tensorflow》](https://zhuanlan.zhihu.com/p/445535362)

* [macOS M1 安装运行 TensorFlow](https://www.pimspeak.com/macos-m1-install-tensorflow-speed-test.html)
