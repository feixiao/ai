## crewai 快速入门

## Install CrewAI
```shell
uv tool install crewai
```


## Generate Project
```shell
crewai create crew hello_crew
```

#### 项目结构
```text
.
├── knowledge                           # Directory for knowledge base
│   └── user_preference.txt
├── pyproject.toml
├── README.md
├── src
│   └── hello_crew
│       ├── __init__.py
│       ├── config
│       │   ├── agents.yaml             # Define your AI agents and their roles
│       │   └── tasks.yaml              # Set up agent tasks and workflows
│       ├── crew.py                     # Crew orchestration and coordination
│       ├── main.py 
│       └── tools
│           ├── __init__.py
│           └── custom_tool.py
└── tests
```
### Run your Crew
```shell
crewai install

# uv add <package-name>
crewai run
```