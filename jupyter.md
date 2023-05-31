## jupyter 安装和部署

#### 安装 jupyterlab

- [conda 安装参考](./TensorFlowLite/ReadMe.md)

```shell

conda activate "py39"
conda install jupyter
pip install notebook
nohup jupyter-notebook --no-browser --port=8888 &

# 浏览器访问
http://10.8.113.165:8888/?token=93bf46aa3a87f1f62f6fe0bf879e2017065bbdb78d59698f

# 本机
```

#### 参考资料

- [《使用本地浏览器连接远程服务器上 Jupyter Notebook》](https://zhuanlan.zhihu.com/p/401178362)
