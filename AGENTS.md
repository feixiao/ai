# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Repository Overview

This repository is a hands-on AI engineering knowledge base and practice playground covering **Agentic Workflows**, **Multi-Agent Frameworks**, **Coding Agent CLIs**, **Local LLM Inference**, and **Multimodal Generative AI** (Image, Video, Audio).

## Architecture & Module Structure

- `LangChain/`: Progressive LangChain examples (`ex01` basic QA ~ `ex06` parallel execution and output parsing).
- `autogenbench/`: AutoGen agent benchmarking and evaluation.
- `crewai/`: CrewAI projects (`hello_crew`) configuring role-playing agents, task definitions, and tool integration via `uv` / `crewai` CLI.
- `helloagent/`: Minimal agent and function calling examples using `hello-agents`.
- `ComfyUI/` & `media/`: Generative AI workflows (Wan2.2, Flux, Z-Image-Turbo, SadTalker, TTS), JSON workflow definitions, benchmark scripts, and Apple Silicon / Mac Studio deployment guides.
- `intel/` & `ollama/`: Local inference setups, Intel Arc GPU (IPEX-LLM) configurations, and Ollama/ModelScope model guides.
- `Codex/`: Configuration patterns and environment settings for connecting Codex with local models (LM Studio / Ollama).
- `LMStudio/`: Remote connection guides, Tailscale/WireGuard peer-to-peer setup, and headless access patterns for LM Studio local LLM server.
- `CodeBuddy/`: Skills and Agents migration, deployment scripts, and guides for Tencent CodeBuddy CLI.
- `Antigravity/`: Skills and Agents migration, deployment scripts (`install.sh`), and CLI best practices for Google Antigravity (`agy` / Gemini).
- `Gemini/`: Deep dive guides and practical toolkits for Google Gemini ecosystem (1M+ context window, Deep Research, NotebookLM Pro, Jules code agent, Gemini Spark, Google Flow/Veo video, and 5TB cloud AI asset hub).
- `OpenCode/`: Configuration patterns, deployment scripts (`install.sh`), and LM Studio local model integration for OpenCode CLI.
- `PiAgent/`: Configuration patterns, deployment scripts (`install.sh`), Google Gemini Pro integration, and reverse proxy/gateway setups for Pi Agent (`pi` / `pi-coding-agent`).
- `omp/`: Configuration patterns, deployment scripts (`install.sh`), multi-model roles, and local gateway integration for omp (oh-my-pi) Coding Agent CLI.
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

### Running LangChain

```bash
# LangChain examples
pip install -r LangChain/requirements.txt
python LangChain/ex01.py
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

- **Model Compatibility**: When working with local LLMs that lack native tool-calling capabilities (e.g. `deepseek-r1`), use structured JSON prompting and lightweight decision chains rather than relying on native tool APIs (see `LangChain/ex06.py` or `helloagent/chap00.py`).
- **Provider Switching**: Scripts typically support switching between `ollama` and `openai` via factory helpers (`build_model(provider, model_name)`) and environment variables (`LLM_MODEL`, `OPENAI_API_KEY`).
