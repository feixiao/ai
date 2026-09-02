[中文](./ReadMe.md)

# Use your LM Studio Models in Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: Shell](https://img.shields.io/badge/Language-Shell-blue.svg)](https://www.gnu.org/software/bash/)

This directory provides `claude-lm.sh`, an isolated, Keychain-safe wrapper with automatic configuration isolation and bidirectional session synchronization for connecting the official Claude Code CLI with local LLMs hosted on [LM Studio](https://lmstudio.ai/).

---

## 1. Prerequisites and Installation

### 1.1 Install Claude Code CLI

Ensure the official `claude` CLI is installed:

```bash
# Standard npm installation
npm install -g @anthropic-ai/claude-code

# Or using the official one-line script
curl -fsSL https://claude.ai/install.sh | bash
```

Verify installation:
```bash
which claude
# Typically outputs ~/.local/bin/claude or /usr/local/bin/claude
```

---

### 1.2 Install and Start LM Studio Local Server

1. Download and install [LM Studio](https://lmstudio.ai/) (Apple Silicon Mac build recommended).
2. Download desired models (such as `qwen3.8-27b-mlx@4bit`, `gemma-4-31b-it`, `mlx-qwopus3.5-9b-v3`).
3. Switch to the **Developer** tab (Local Server):
   - Click **Start Server**.
   - Default port is `1234` (`http://127.0.0.1:1234`).
   - Ensure **Enable CORS** is checked.

---

### 1.3 Install `clm` / `claude-lm` to System PATH (Recommended)

Copy the wrapper script and synchronization utility to `~/.local/bin` for system-wide access:

```bash
# Navigate to ClaudeCode directory
cd /Users/frank/wk/github/ai/ClaudeCode

# Make scripts executable
chmod +x claude-lm.sh sync_sessions.sh

# 1. Copy to ~/.local/bin
mkdir -p ~/.local/bin
cp claude-lm.sh ~/.local/bin/clm
cp claude-lm.sh ~/.local/bin/claude-lm
cp sync_sessions.sh ~/.local/bin/sync_sessions.sh

# 2. Grant execution permissions
chmod +x ~/.local/bin/clm ~/.local/bin/claude-lm ~/.local/bin/sync_sessions.sh

# 3. Verify installation
which clm
which claude-lm
```

> **Note**:
> 1. Ensure `~/.local/bin` is in your `PATH` (e.g. `export PATH="$HOME/.local/bin:$PATH"` in `~/.zshrc` or `~/.bashrc`).
> 2. If you modify `claude-lm.sh` in the repository, re-run the `cp` command to update the installed binaries.

---

## 2. Usage and Command Options

### 2.1 Basic Launch

```bash
# Launch with default Coder preset (qwen3.8-27b-mlx@4bit + gemma-4-31b-it + mlx-qwopus3.5-9b-v3)
clm

# Or use full command name
claude-lm
```

---

### 2.2 Switch Presets (`--preset`)

Four built-in presets are available for different workflows:

```bash
# 1. Coding preset (Default: 27B coder + 31B reasoning + 9B subagent)
clm --preset coder

# 2. Deep reasoning preset (31B gemma for architectural planning and complex logic)
clm --preset reasoning

# 3. Qwen family preset (qwen3.8-27b 4bit/8bit + qwopus3.5-9b)
clm --preset qwen

# 4. Gemma family preset (gemma-4-26b-a4b-it + gemma-4-31b-it)
clm --preset gemma
```

---

### 2.3 Single-Model Mode (`--single`)

Route all roles (Sonnet/Opus/Haiku/Subagents) to a single model to avoid VRAM model swapping:

```bash
# Route everything to qwen3.8-27b-mlx@4bit
clm --single qwen3.8-27b-mlx@4bit

# Route everything to gemma-4-31b-it
clm --single gemma-4-31b-it
```

---

### 2.4 Session Resume and Argument Passthrough

All standard Claude Code arguments are passed through directly:

```bash
# Resume latest session
clm --resume

# Resume specific session by UUID
clm --resume 2ce044f6-9934-4e69-b974-c6881e1764da

# Run in non-interactive print mode
clm -p "Write a FastAPI streaming chat endpoint"
```

---

## 3. Local Model Hierarchy & Role Mapping

Recommended model allocations on Apple Silicon (M-series / Mac Studio):

| Model Name | VRAM Footprint | Parameter Size | Recommended Role | Specialty / Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **`qwen3.8-27b-mlx@4bit`** | 16.1 GB | 27B | **`ANTHROPIC_DEFAULT_SONNET_MODEL`**<br>+ **Primary (`ANTHROPIC_MODEL`)** | Optimized for code generation and refactoring (4-bit balanced) |
| **`gemma-4-31b-it`** | 18.4 GB | 31B | **`ANTHROPIC_DEFAULT_OPUS_MODEL`** / **Fable** | Dense reasoning model for architectural design and complex logic |
| **`qwen3.8-27b-mlx@8bit`** | 29.5 GB | 27B | **`ANTHROPIC_DEFAULT_OPUS_MODEL`** (Optional) | High precision 8-bit Qwen model for math and reasoning |
| **`gemma-4-26b-a4b-it`** | 15.6 GB | 26B | **`ANTHROPIC_DEFAULT_SONNET_MODEL`** / **Haiku** | High throughput MoE model with fast inference |
| **`mlx-qwopus3.5-9b-v3`** | 9.5 GB | 9B | **`ANTHROPIC_DEFAULT_HAIKU_MODEL`**<br>+ **`CLAUDE_CODE_SUBAGENT_MODEL`** | MLX-optimized 9B model for low-latency subagent tasks |
| **`qwopus3.5-9b-v3`** | 6.0 GB | 9B | **`ANTHROPIC_DEFAULT_HAIKU_MODEL`**<br>+ **`CLAUDE_CODE_SUBAGENT_MODEL`** | Lightweight 6GB model with fast TTFT |

---

## 4. Environment Variables & Low-Level Settings

Key environment configurations applied by the wrapper:

```bash
# 1. LM Studio endpoint and proxy bypass
export NO_PROXY="127.0.0.1,localhost,$NO_PROXY"
export ANTHROPIC_BASE_URL="http://127.0.0.1:1234/v1"
export ANTHROPIC_API_KEY="lmstudio"

# 2. Model role routing
export ANTHROPIC_MODEL="qwen3.8-27b-mlx@4bit"
export ANTHROPIC_DEFAULT_MODEL="qwen3.8-27b-mlx@4bit"
export ANTHROPIC_DEFAULT_SONNET_MODEL="qwen3.8-27b-mlx@4bit"
export ANTHROPIC_DEFAULT_OPUS_MODEL="gemma-4-31b-it"
export ANTHROPIC_DEFAULT_FABLE_MODEL="gemma-4-31b-it"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="mlx-qwopus3.5-9b-v3"
export CLAUDE_CODE_SUBAGENT_MODEL="mlx-qwopus3.5-9b-v3"

# 3. Disable 1M suffix and connection/timeout tuning
export CLAUDE_CODE_DISABLE_1M_CONTEXT=1
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK=1
export CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1
export CLAUDE_STREAM_IDLE_TIMEOUT_MS=600000
export API_TIMEOUT_MS=3000000

# 4. Context compression tuning
unset DISABLE_COMPACT
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=100000
```

---

## 5. Bidirectional Session Sync (`sync_sessions.sh`)

To prevent local model runs from conflicting with official OAuth/Keychain state, configurations are stored in `~/.lmstudio/claude_config`.

`sync_sessions.sh` automatically synchronizes session history between `~/.claude` and `~/.lmstudio/claude_config` before launch and on exit:

```bash
# Manually sync official sessions to LM Studio configuration
./sync_sessions.sh

# Bidirectional sync (retains newer files on both ends)
./sync_sessions.sh -b

# Sync a single session by UUID
./sync_sessions.sh 2ce044f6-9934-4e69-b974-c6881e1764da
```

---

## 6. Troubleshooting

### 6.1 Error: `zsh: no such file or directory: /Users/.../claude-lmstudio.sh`
- **Cause**: The active terminal session still has a stale alias loaded in memory. Running `source ~/.zshrc` does not remove existing in-memory aliases.
- **Solution**:
  1. Clear the alias in your active shell:
     ```bash
     unalias claude-lm 2>/dev/null
     unalias clm 2>/dev/null
     ```
  2. Ensure old `alias claude-lm=...` lines are removed from `~/.zshrc`.
  3. Ensure `~/.local/bin` is in your `PATH`:
     ```bash
     export PATH="$HOME/.local/bin:$PATH"
     source ~/.zshrc
     ```
  4. Open a new terminal window or tab and run `clm` or `claude-lm`.

### 6.2 Error: `claude: command not found`
- Verify installation via `which claude`. If missing, install via `npm install -g @anthropic-ai/claude-code` or `curl -fsSL https://claude.ai/install.sh | bash`.

### 6.3 Connection Refused or Timeout
- Verify LM Studio local server is running on port `1234`.
- If using a custom port (e.g. `8000`), override via: `ANTHROPIC_BASE_URL="http://127.0.0.1:8000/v1" clm`.

### 6.4 Frequent VRAM Eviction / Swapping
- Keep only 1 primary model loaded in LM Studio and launch with `--single <model_name>`.
