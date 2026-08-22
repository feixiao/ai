# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository is a hands-on AI engineering knowledge base and practice playground covering **Agentic Design Patterns**, **Multi-Agent Frameworks**, **Local LLM Inference**, and **Multimodal Generative AI** (Image, Video, Audio).

## Architecture & Module Structure

- `AgenticDesignPatterns/`: Core implementations of foundational agent design patterns, implemented in two frameworks:
  - `langchain/`: Patterns implemented with LangChain & LCEL (`chap01` Prompt Chaining, `chap02` Routing, `chap03` Parallelization, `chap04` Reflection, `chap05` Tool Calling/ReAct, `chap06` Planning, `chap07` Multi-Agent Collaboration, `chap08` Memory Management, `chap11`).
  - `autogen/`: Patterns implemented with Microsoft AutoGen (`chap01` ~ `chap08`).
- `LangChain/`: Progressive LangChain examples (`ex01` basic QA ~ `ex06` parallel execution and output parsing).
- `autogen/` & `autogenbench/`: AutoGen agent workflows, AutoGen Studio UI prototyping, and agent benchmarking.
- `crewai/`: CrewAI projects (`hello_crew`) configuring role-playing agents, task definitions, and tool integration via `uv` / `crewai` CLI.
- `helloagent/`: Minimal agent and function calling examples using `hello-agents`.
- `ComfyUI/` & `media/`: Generative AI workflows (Wan2.2, Flux, Z-Image-Turbo, SadTalker, TTS), JSON workflow definitions, benchmark scripts, and Apple Silicon / Mac Studio deployment guides.
- `intel/` & `ollama/`: Local inference setups, Intel Arc GPU (IPEX-LLM) configurations, and Ollama/ModelScope model guides.
- `ClaudeCode/`: Configuration patterns and environment settings for connecting Claude Code with local models (LM Studio / Ollama).
- `TensorFlowLite/`, `PyTorch/`, `spleeter/`: Deep learning experiments and audio source separation scripts.

## Environment & Common Commands

### Python Virtual Environment

Most Python modules target Python 3.10–3.12:

```bash
# Recommended environment setup
pyenv virtualenv 3.12 llm
pyenv activate llm
```

### Local LLM Backends

Scripts generally default to local Ollama instances or OpenAI-compatible endpoints:

```bash
# Start Ollama service & download models
ollama serve
ollama pull deepseek-r1:14b
ollama pull deepseek-r1:8b

# Override model via environment variable when running scripts
export LLM_MODEL="deepseek-r1:14b"
```

### Running Agentic Design Patterns & LangChain

```bash
# LangChain examples
pip install -r LangChain/requirements.txt
python LangChain/ex01.py

# Agentic Design Patterns (LangChain)
cd AgenticDesignPatterns/langchain
pip install -r requirements.txt
python chap01.py

# Agentic Design Patterns (AutoGen)
cd AgenticDesignPatterns/autogen
python chap01.py
```

### Running CrewAI

```bash
cd crewai/hello_crew
crewai install
crewai run
```

### ComfyUI & Benchmarking

```bash
# Run ComfyUI generation benchmark
python ComfyUI/comfyui_benchmark.py
```

## Key Development Conventions

- **Model Compatibility**: When working with local LLMs that lack native tool-calling capabilities (e.g. `deepseek-r1`), use structured JSON prompting and lightweight decision chains rather than relying on native tool APIs (see `AgenticDesignPatterns/langchain/chap05.py`).
- **Provider Switching**: Scripts typically support switching between `ollama` and `openai` via factory helpers (`build_model(provider, model_name)`) and environment variables (`LLM_MODEL`, `OPENAI_API_KEY`).
