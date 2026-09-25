# -*- coding: utf-8 -*-
"""
ComfyUI LMStudio 提示词扩写自定义节点测试
"""
import sys
from pathlib import Path

# 添加自定义节点路径与扩写引擎路径
custom_node_dir = Path(__file__).parent.parent / "custom_nodes" / "ComfyUI-LMStudio-Prompt"
parent_dir = Path(__file__).parent.parent

sys.path.insert(0, str(custom_node_dir.resolve()))
sys.path.insert(0, str(parent_dir.resolve()))

from lmstudio_prompt_node import LMStudioPromptExpanderNode


def test_node_specification() -> None:
    """测试节点输入输出类型定义与 ComfyUI 规范一致。"""
    inputs = LMStudioPromptExpanderNode.INPUT_TYPES()
    assert "required" in inputs
    assert "user_short_desc" in inputs["required"]
    assert "style_preset" in inputs["required"]
    assert "temperature" in inputs["required"]

    assert LMStudioPromptExpanderNode.RETURN_TYPES == ("STRING", "STRING", "INT", "INT")
    assert LMStudioPromptExpanderNode.RETURN_NAMES == ("positive_prompt", "negative_prompt", "width", "height")


def test_node_execution_fallback() -> None:
    """测试节点在服务离线状态下的降级执行与输出解包。"""
    node = LMStudioPromptExpanderNode()
    pos, neg, w, h = node.expand_prompt(
        user_short_desc="未来都市飞行汽车",
        style_preset="cyberpunk",
        lmstudio_host="127.0.0.1:59999",
        aspect_ratio="16:9",
    )
    assert isinstance(pos, str) and len(pos) > 0
    assert isinstance(neg, str) and len(neg) > 0
    assert w == 1280
    assert h == 768
