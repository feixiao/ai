## Use your LM Studio Models in Claude Code


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