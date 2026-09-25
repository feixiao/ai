# -*- coding: utf-8 -*-
"""
Qwen-Image-2.1 命令行测试套件单元测试
"""
import json
import sys
from pathlib import Path

# 保证父级目录在模块搜索路径中
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompt_expander import ExpandedPromptResult
from qwen_image21_test import _normalize_host, inject_workflow_parameters, parse_arguments


def test_normalize_host() -> None:
    """测试主机地址协议前缀的标准化处理。"""
    assert _normalize_host("127.0.0.1:8188") == "127.0.0.1:8188"
    assert _normalize_host("http://127.0.0.1:8188") == "127.0.0.1:8188"
    assert _normalize_host("https://remote.server.com:8188") == "remote.server.com:8188"
    assert _normalize_host("  http://localhost:1234  ") == "localhost:1234"


def test_cli_argument_parsing() -> None:
    """测试命令行参数解析默认值与自定义参数。"""
    args = parse_arguments(["--desc", "森林里的小鹿", "--style", "cinematic", "--steps", "28", "--dry-run"])
    assert args.desc == "森林里的小鹿"
    assert args.style == "cinematic"
    assert args.steps == 28
    assert args.dry_run is True


def test_workflow_parameter_injection() -> None:
    """测试动态将扩写结果与采样参数正确注入到工作流字典中。"""
    workflow_path = Path("ComfyUI/qwen_image_2.1/workflows/qwen_image_2.1_api.json")
    with open(workflow_path, "r", encoding="utf-8") as f:
        template = json.load(f)

    prompt_res = ExpandedPromptResult(
        positive_prompt="A majestic deer in misty emerald forest",
        negative_prompt="blurry, distorted",
        aspect_ratio="16:9",
        width=1280,
        height=768,
        model_used="test-model",
        is_fallback=False,
    )

    injected = inject_workflow_parameters(template, prompt_res, steps=20, seed=12345)

    # 验证是否正向提示词节点被成功替换
    found_pos = False
    found_sampler = False
    found_latent = False

    for node in injected.values():
        if isinstance(node, dict):
            if node.get("class_type") == "CLIPTextEncode" and node["inputs"].get("text") == prompt_res.positive_prompt:
                found_pos = True
            if node.get("class_type") == "KSampler":
                if node["inputs"].get("steps") == 20 and node["inputs"].get("seed") == 12345:
                    found_sampler = True
            if node.get("class_type") in ("EmptyLatentImage", "EmptyQwenImageLayeredLatentImage"):
                if node["inputs"].get("width") == 1280 and node["inputs"].get("height") == 768:
                    found_latent = True

    assert found_pos, "正向提示词未成功注入"
    assert found_sampler, "采样参数未成功注入"
    assert found_latent, "分辨率未成功注入"
