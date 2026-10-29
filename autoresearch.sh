#!/usr/bin/env bash
set -euo pipefail

# Autoresearch Benchmark Entrypoint for Audio/Video Multimodal Handbook
# Workload: Runs deterministic technical evaluation of handbook content,
# hardware budget models, pipeline tools, and hands-on practice lab executions.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/tools/multimodal_tools:${SCRIPT_DIR}:${PYTHONPATH:-}"

python3 "${SCRIPT_DIR}/tools/multimodal_tools/eval_handbook.py"
