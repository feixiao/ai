## moltbot 对接

#### 安装
+ [clawbot](https://github.com/xianyu110/clawbot)
```shell
curl -fsSL https://openclaw.ai/install.sh | bash

openclaw onboard

openclaw gateway --port 18789

# .openclaw/agents/main/agent/auth-profiles.json
openclaw onboard --auth-choice apiKey --token-provider openrouter --token "$OPENROUTER_API_KEY"
```

#### 测试key

```shell
export OPENROUTER_API_KEY=""
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek/deepseek-chat-v3-0324:free", "messages": [{"role": "user", "content": "Hello"}]}'
```

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

#### 配置邮箱
```shell
openclaw plugins install https://github.com/lamelas/himalaya.git
```


#### 推荐Skill
+ 1. self-improving-agent 自我迭代/主动代理。让Agent记住错误、自我优化、越来越聪明。
+ 2. tavily-search (或 tavily-web-search) 联网搜索（Tavily API优化版）。没这个Agent就是“井底之蛙”，查不了实时信息。
+ 3. summarize 总结URL、PDF、图片、YouTube、音频。快速消化信息，新手研究东西时超级省力。
+ 4. find-skills 让Agent自己去ClawHub搜并推荐/安装技能。解决“不知道装什么”的最大痛点，新手最友好
+ 5. ontology 或 agent-memory / memory 结构化记忆/知识图谱。让Agent真正“记住你”、跨对话连贯，不再健忘。新手交互体验提升巨大。
+ 6. proactive-agent (或 proactive-agent-1-2-4 等版本) 增加主动性，能自己规划、迭代任务。让Agent从“被动回答”变成“主动帮忙”。
+ 7. skill-vetter / security-audit 或类似安全扫描 安装前扫描技能代码、防恶意。新手安全第一，装这个后再放心装别的。

#### 参考资料
+ [《开源AI助手接入Discord》](https://zhuanlan.zhihu.com/p/1999598055972947248)
+ [《clawbot老版本](https://github.com/xianyu110/clawbot)
+ [《对接飞书》](https://cloud.tencent.com/developer/article/2625073)
+ [《对接discard》](https://cloud.tencent.com/developer/article/2625092)
+ [《如何为 OpenClaw 配置 NVIDIA 免费模型》](https://www.openclawai.cv/zh/blog/nvidia-free-model-openclaw-config)
+ [《最适合新手安装的10个小龙虾🦞 skills来了！》](https://mp.weixin.qq.com/s/4lUgy1nW41-6jxoRKdszeQ)