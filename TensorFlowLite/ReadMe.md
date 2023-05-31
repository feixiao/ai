## TensorFlowLite

#### 安装 tensorflow

##### OSX

```shell

# 现在有arm版本的anaconda
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-MacOSX-arm64.sh
bash Anaconda3-2023.03-1-MacOSX-arm64.sh

# 添加到环境变量
export PATH=${PATH}:~/anaconda3/bin

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


# conda config --set auto_activate_base false
# conda create -n py39 python=3.9
# conda activate py39 # conda deactivate

conda create -n tf_env python=3.8
conda activate tf_env
python3  # 验证版本， 类似 Python 3.8.16 | packaged by conda-forge |

conda install tensorflow

# 测试
python3 tf.py

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
