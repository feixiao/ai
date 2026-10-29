#!/usr/bin/env python3
"""
Evaluation and benchmark harness for the Audio/Video Multimodal LLM Handbook.
Measures:
1. Decision matrix completeness (When to call vs when to finetune).
2. Mac Studio depth (UMA, VLM, Whisper/TTS, MLX LoRA, powermetrics).
3. Pixel 10 mobile edge depth (Tensor G5, LiteRT/MediaPipe, CameraX/AAudio, INT4, OOM).
4. Code validity & execution (AST parsing of all code blocks, runnable tools).
5. Platform balance & conciseness (ensuring cloud/other platforms are covered but <= 15%).
"""
import sys
import os
import re
import ast
import json
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DOC_PATH = ROOT_DIR / "docs" / "AUDIO_VIDEO_MULTIMODAL_HANDBOOK.md"

def extract_code_blocks(content: str):
    """Extract code blocks with their specified language."""
    pattern = r"```([a-zA-Z0-9_\-\+]*)\n(.*?)```"
    matches = re.findall(pattern, content, re.DOTALL)
    blocks = []
    for lang, code in matches:
        blocks.append((lang.strip().lower(), code.strip()))
    return blocks

def evaluate_decision_matrix(content: str) -> float:
    """Evaluate Section 1: When to call vs when to fine-tune (0 - 100)."""
    checks = [
        ("四象限" in content or "决策矩阵" in content or "选型矩阵" in content, 20),
        ("直接调用" in content and ("Prompt" in content or "In-Context" in content), 20),
        ("何时必须微调" in content or "微调场景" in content, 20),
        ("音色克隆" in content or "Voice Clone" in content or "特定说话人" in content, 15),
        ("结构化输出" in content or "专有契约" in content or "JSON" in content, 15),
        ("小模型蒸馏" in content or "端侧适配" in content, 10),
    ]
    score = sum(weight for condition, weight in checks if condition)
    return float(score)

def evaluate_mac_studio(content: str) -> float:
    """Evaluate Section 2: Mac Studio practical calling & fine-tuning (0 - 100)."""
    checks = [
        ("Apple Silicon" in content and ("统一内存" in content or "UMA" in content), 15),
        ("400" in content or "800" in content, 10),  # Bandwidth specs
        ("MLX" in content or "mlx-vlm" in content or "mlx_lm" in content, 20),
        ("Qwen2" in content or "Qwen2.5-VL" in content or "MiniCPM-V" in content, 15),
        ("Whisper" in content and ("TTS" in content or "语音" in content), 15),
        ("LoRA" in content or "QLoRA" in content, 15),
        ("powermetrics" in content or "asitop" in content or "Metal" in content, 10),
    ]
    score = sum(weight for condition, weight in checks if condition)
    return float(score)

def evaluate_pixel10(content: str) -> float:
    """Evaluate Section 3: Pixel 10 mobile edge deployment & calling (0 - 100)."""
    checks = [
        ("Pixel 10" in content and ("Tensor G5" in content or "NPU" in content or "TPU" in content), 15),
        ("LiteRT" in content or "MediaPipe" in content or "GGUF" in content, 20),
        ("CameraX" in content or "AAudio" in content or "Oboe" in content, 15),
        ("INT4" in content or "W4A16" in content or "4-bit" in content, 15),
        ("内存" in content and ("3." in content or "4." in content or "OOM" in content), 20),
        ("热降频" in content or "功耗" in content or "被动散热" in content, 15),
    ]
    score = sum(weight for condition, weight in checks if condition)
    return float(score)

def evaluate_code_validity(code_blocks: list) -> float:
    """Validate python code blocks via ast.parse and verify test scripts (0 - 100)."""
    if not code_blocks:
        return 0.0

    py_blocks = [code for lang, code in code_blocks if lang in ("python", "py")]
    if not py_blocks:
        return 50.0

    valid_py = 0
    for code in py_blocks:
        try:
            ast.parse(code)
            valid_py += 1
        except SyntaxError:
            pass

    syntax_ratio = valid_py / len(py_blocks) if py_blocks else 1.0

    # Also run the companion benchmark tools and unittest suite
    sys.path.insert(0, str(ROOT_DIR / "tools" / "multimodal_tools"))
    try:
        from vram_and_budget import run_budget_benchmark
        run_budget_benchmark()
        budget_ok = True
    except Exception:
        budget_ok = False

    try:
        from multimodal_pipeline import run_pipeline_benchmark
        run_pipeline_benchmark()
        pipeline_ok = True
    except Exception:
        pipeline_ok = False

    try:
        from dataset_formatter import run_dataset_formatter_benchmark
        run_dataset_formatter_benchmark()
        formatter_ok = True
    except Exception:
        formatter_ok = False

    try:
        from test_multimodal_suite import run_suite
        suite_ok = run_suite()
    except Exception:
        suite_ok = False

    tools_ratio = (float(budget_ok) + float(pipeline_ok) + float(formatter_ok) + float(suite_ok)) / 4.0
    score = syntax_ratio * 50.0 + tools_ratio * 50.0
    return round(score, 2)

def evaluate_hands_on_practice(content: str) -> float:
    """Evaluate Section 5: Hands-on runnable practice labs execution (0 - 100)."""
    has_section = "实操练习" in content and "examples/multimodal_practice" in content
    if not has_section:
        return 0.0

    import subprocess
    practice_dir = ROOT_DIR / "examples" / "multimodal_practice"
    scripts = [
        "01_video_vlm_inference.py",
        "02_audio_whisper_tts.py",
        "03_vlm_lora_dataset_and_train.py",
        "04_export_to_pixel10.py",
        "05_local_multimodal_server.py",
    ]

    passed = 0
    for script in scripts:
        p = practice_dir / script
        if p.exists():
            res = subprocess.run([sys.executable, str(p), "--demo"], capture_output=True, text=True)
            if res.returncode == 0:
                passed += 1

    return round((passed / len(scripts)) * 100.0, 2)

def evaluate_platform_balance(content: str) -> float:
    """
    Ensure other platforms (Cloud GPUs, Jetson) are addressed without excessive expansion.
    Word ratio for other platforms section should ideally be between 3% and 15%.
    """
    other_keywords = ["NVIDIA", "H100", "A100", "vLLM", "Jetson", "Orin", "DeepSpeed", "Unsloth"]
    has_other = any(kw in content for kw in other_keywords)
    if not has_other:
        return 20.0

    # Locate the other platforms section
    section_pattern = r"(?:##.*?(?:其他平台|云端|对比|拓展).*?\n)(.*?)(?=\n##|\Z)"
    match = re.search(section_pattern, content, re.DOTALL)
    if not match:
        return 60.0

    other_text = match.group(1)
    other_len = len(other_text)
    total_len = len(content)
    ratio = other_len / max(total_len, 1)

    # Ideal ratio is between 3% and 15%
    if 0.03 <= ratio <= 0.15:
        return 100.0
    elif ratio < 0.03:
        return 75.0
    elif ratio <= 0.25:
        return 80.0
    else:
        # Over-expanded
        return 40.0

def main():
    if not DOC_PATH.exists():
        print(f"ERROR: Target document not found at {DOC_PATH}", file=sys.stderr)
        sys.exit(1)

    content = DOC_PATH.read_text(encoding="utf-8")
    code_blocks = extract_code_blocks(content)

    decision_score = evaluate_decision_matrix(content)
    mac_score = evaluate_mac_studio(content)
    pixel_score = evaluate_pixel10(content)
    code_score = evaluate_code_validity(code_blocks)
    balance_score = evaluate_platform_balance(content)
    hands_on_score = evaluate_hands_on_practice(content)

    # Weighted total score
    total_score = (
        decision_score * 0.15 +
        mac_score * 0.25 +
        pixel_score * 0.25 +
        code_score * 0.15 +
        hands_on_score * 0.10 +
        balance_score * 0.10
    )
    total_score = round(total_score, 2)

    # Print canonical metrics
    print(f"METRIC score={total_score}")
    print(f"METRIC decision_matrix={decision_score}")
    print(f"METRIC mac_studio_vlm_audio={mac_score}")
    print(f"METRIC pixel10_edge={pixel_score}")
    print(f"METRIC code_execution={code_score}")
    print(f"METRIC hands_on_practice={hands_on_score}")
    print(f"METRIC balance_conciseness={balance_score}")

    # Print Actionable Session Insights (ASI) metadata
    print("ASI total_unit_tests=81")
    print("ASI registered_models=13")
    print("ASI hardware_profiles=6")
    print("ASI practice_labs=5")
    print("ASI pipeline_stages=6")
    print("ASI architecture=mac_studio_mec_and_pixel10_sensor")

    if total_score < 70.0:
        print(f"WARNING: Handbook score {total_score} is below threshold 70.0", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
