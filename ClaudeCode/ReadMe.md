## Use your LM Studio Models in Claude Code


#### 模型介绍
+ ANTHROPIC_MODEL 默认场景使用经济模型
+ ANTHROPIC_DEFAULT_OPUS_MODEL 最复杂任务（如架构设计）使用推理模型 
+ ANTHROPIC_DEFAULT_SONNET_MODEL 日常编码使用经济模型 
+ ANTHROPIC_DEFAULT_HAIKU_MODEL 简单任务使用经济模型
+ CLAUDE_CODE_SUBAGENT_MODEL 子代理任务使用经济模型


#### 设置claude code的模型路径
```shell
# 替换为你的模型路径
# 写入环境变量
export ANTHROPIC_BASE_URL=http://localhost:1234
export ANTHROPIC_AUTH_TOKEN=lmstudio
```




### 切换模型
```shell
claude --model openai/gpt-oss-20b
claude --model qwopus3.5-27b-v3
```

### 参考配置
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:1234/v1"
    "ANTHROPIC_AUTH_TOKEN": "local-model",
    "API_TIMEOUT_MS": "3000000"
  },
  "companyAnnouncements": [
  ]
}
```


### GUI配置
+ [cc-switcher](https://github.com/farion1231/cc-switcher)cc-switcher: A GUI tool to switch between different models in Claude Code.


#### 参考资料
+ [Use your LM Studio Models in Claude Code](https://lmstudio.ai/blog/claudecode)