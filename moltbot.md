## moltbot 对接

#### 安装
+ [clawbot](https://github.com/xianyu110/clawbot)

### 对接飞书(不需要公网节点)
+ [Moltbot](https://cloud.tencent.com/developer/article/2625073)


### 对接discard(不需要公网节点)
+ [Moltbot](https://cloud.tencent.com/developer/article/2625092)

##### 老版本
```shell
clawdbot gateway --port 18789

clawdbot onboard

export OPENROUTER_API_KEY=""
clawdbot onboard --auth-choice apiKey --token-provider openrouter --token "$OPENROUTER_API_KEY"
```





#### 参考资料
+ [《开源AI助手接入Discord》](https://zhuanlan.zhihu.com/p/1999598055972947248)
+ [clawbot老版本](https://github.com/xianyu110/clawbot)
+ [对接飞书](https://cloud.tencent.com/developer/article/2625073)
+ [对接discard](https://cloud.tencent.com/developer/article/2625092)