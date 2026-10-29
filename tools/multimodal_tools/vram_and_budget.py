#!/usr/bin/env python3
"""
VRAM and compute budget estimator for Audio/Video multimodal models.
Target devices: Mac Studio (Apple Silicon UMA) & Pixel 10 (Tensor G5 Edge).
Deterministic, zero external dependencies.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class MultimodalModelSpec:
    name: str
    modality: str  # 'vision-language', 'audio-asr', 'audio-tts', 'video-generation'
    params_billion: float
    context_tokens: int
    default_dtype: str  # 'fp16', 'int8', 'int4'

# Model registry covering key multimodal models discussed in the handbook
MODEL_REGISTRY: Dict[str, MultimodalModelSpec] = {
    "qwen2.5-vl-3b": MultimodalModelSpec("qwen2.5-vl-3b", "vision-language", 3.0, 8192, "int4"),
    "qwen2.5-vl-7b": MultimodalModelSpec("qwen2.5-vl-7b", "vision-language", 7.0, 8192, "int4"),
    "minicpm-v-2.6": MultimodalModelSpec("minicpm-v-2.6", "vision-language", 2.4, 4096, "int4"),
    "smolvlm-2b": MultimodalModelSpec("smolvlm-2b", "vision-language", 2.2, 4096, "int4"),
    "whisper-large-v3-turbo": MultimodalModelSpec("whisper-large-v3-turbo", "audio-asr", 0.8, 448, "fp16"),
    "whisper-base": MultimodalModelSpec("whisper-base", "audio-asr", 0.074, 448, "fp16"),
    "kokoro-tts": MultimodalModelSpec("kokoro-tts", "audio-tts", 0.082, 512, "fp16"),
    "chattts": MultimodalModelSpec("chattts", "audio-tts", 0.2, 1024, "fp16"),
}

# Target hardware specifications
HARDWARE_PROFILES = {
    "mac_studio_m2_max_64g": {
        "device_type": "desktop_edge_hub",
        "total_ram_gb": 64.0,
        "uma_bandwidth_gbs": 400.0,
        "max_recommended_vram_gb": 48.0,  # OS & app reserved 16GB
        "accelerators": ["Metal GPU", "Apple Neural Engine (ANE)", "VideoToolbox 4K/8K Decoders"],
    },
    "mac_studio_m4_ultra_128g": {
        "device_type": "desktop_edge_hub",
        "total_ram_gb": 128.0,
        "uma_bandwidth_gbs": 800.0,
        "max_recommended_vram_gb": 104.0,
        "accelerators": ["Metal GPU", "ANE", "VideoToolbox"],
    },
    "pixel_10_tensor_g5": {
        "device_type": "mobile_edge_node",
        "total_ram_gb": 16.0,
        "uma_bandwidth_gbs": 64.0,
        "max_recommended_vram_gb": 4.5,  # Strict mobile OS headroom
        "accelerators": ["Edge TPU (NPU)", "Mali/Custom GPU", "LiteRT / MediaPipe"],
    },
}

def estimate_inference_memory_gb(params_b: float, precision: str, video_frames: int = 16) -> Dict[str, float]:
    """
    Calculate model weight memory, activation overhead (including video patch tokens),
    and total working memory in GB.
    """
    bytes_per_param = {
        "fp16": 2.0,
        "bf16": 2.0,
        "int8": 1.0,
        "int4": 0.5,
    }.get(precision.lower(), 0.5)

    weight_gb = params_b * bytes_per_param
    # Video visual token activation overhead: approx 256 tokens per frame, 4KB per token state
    visual_activation_gb = (video_frames * 256 * 4096 * 2) / (1024 ** 3)
    kv_cache_gb = 0.5 if precision == "int4" else 1.2
    runtime_overhead_gb = 0.4  # Metal or LiteRT runtime context

    total_gb = weight_gb + visual_activation_gb + kv_cache_gb + runtime_overhead_gb
    return {
        "weight_gb": round(weight_gb, 2),
        "activation_and_kv_gb": round(visual_activation_gb + kv_cache_gb, 2),
        "runtime_overhead_gb": round(runtime_overhead_gb, 2),
        "total_gb": round(total_gb, 2),
    }

def estimate_lora_finetune_memory_gb(params_b: float, base_precision: str = "int4", rank: int = 16) -> Dict[str, float]:
    """
    QLoRA memory estimation on Apple Silicon:
    Base model (frozen INT4) + LoRA trainable weights (FP16) + Gradients + AdamW optimizer + Activations
    """
    base_weight_gb = params_b * (0.5 if base_precision == "int4" else 2.0)
    # Trainable params for rank r=16 is roughly 0.5% - 1.5% of total params
    trainable_ratio = 0.01 if rank <= 16 else 0.025
    trainable_params_b = params_b * trainable_ratio

    lora_weights_gb = trainable_params_b * 2.0
    gradients_gb = trainable_params_b * 2.0
    optimizer_gb = trainable_params_b * 4.0  # 8-bit AdamW is ~4 bytes/param, 16-bit is ~8 bytes
    activations_gb = 1.8  # Sequence length 2048, batch size 2

    total_gb = base_weight_gb + lora_weights_gb + gradients_gb + optimizer_gb + activations_gb
    return {
        "base_model_frozen_gb": round(base_weight_gb, 2),
        "lora_trainable_gb": round(lora_weights_gb, 2),
        "optimizer_and_grad_gb": round(optimizer_gb + gradients_gb, 2),
        "activation_gb": round(activations_gb, 2),
        "total_training_gb": round(total_gb, 2),
    }

def check_hardware_feasibility(model_id: str, device_key: str, task: str = "inference") -> Dict[str, Any]:
    """
    Evaluate if a model can run or be fine-tuned on the given hardware.
    """
    if model_id not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model: {model_id}")
    if device_key not in HARDWARE_PROFILES:
        raise ValueError(f"Unknown hardware: {device_key}")

    model = MODEL_REGISTRY[model_id]
    hw = HARDWARE_PROFILES[device_key]

    if task == "inference":
        budget = estimate_inference_memory_gb(model.params_billion, model.default_dtype)
        required_gb = budget["total_gb"]
    elif task == "finetune":
        budget = estimate_lora_finetune_memory_gb(model.params_billion)
        required_gb = budget["total_training_gb"]
    else:
        raise ValueError(f"Unsupported task: {task}")

    max_allowed = hw["max_recommended_vram_gb"]
    feasible = required_gb <= max_allowed

    recommendation = "Optimal"
    if not feasible:
        recommendation = "OOM_Risk: Exceeds device memory headroom"
    elif device_key.startswith("pixel") and required_gb > 3.0:
        recommendation = "Tight: Monitor thermal throttling and passive heat"

    return {
        "model": model.name,
        "device": device_key,
        "task": task,
        "required_gb": required_gb,
        "device_max_vram_gb": max_allowed,
        "feasible": feasible,
        "recommendation": recommendation,
        "breakdown": budget,
    }

def run_budget_benchmark():
    """Deterministic test suite for budget validation."""
    # Test 1: Pixel 10 running Qwen2.5-VL-3B INT4
    p1 = check_hardware_feasibility("qwen2.5-vl-3b", "pixel_10_tensor_g5", "inference")
    assert p1["feasible"] is True, f"Pixel 10 should run Qwen2.5-VL-3B INT4: {p1}"

    # Test 2: Pixel 10 trying to finetune 7B (Must fail/flag infeasible)
    p2 = check_hardware_feasibility("qwen2.5-vl-7b", "pixel_10_tensor_g5", "finetune")
    assert p2["feasible"] is False, f"Pixel 10 must not finetune 7B: {p2}"

    # Test 3: Mac Studio M2 Max running 7B QLoRA finetuning
    m1 = check_hardware_feasibility("qwen2.5-vl-7b", "mac_studio_m2_max_64g", "finetune")
    assert m1["feasible"] is True, f"Mac Studio 64G should easily finetune 7B QLoRA: {m1}"

    # Test 4: Whisper Base on Pixel 10
    p3 = check_hardware_feasibility("whisper-base", "pixel_10_tensor_g5", "inference")
    assert p3["feasible"] is True

    print("Budget estimator test suite: ALL PASSED")

if __name__ == "__main__":
    run_budget_benchmark()
