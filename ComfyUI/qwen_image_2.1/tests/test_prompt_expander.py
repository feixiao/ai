# -*- coding: utf-8 -*-
"""
提示词扩写引擎单元测试
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# 保证父级目录在模块搜索路径中
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompt_expander import LMStudioPromptExpander, ExpandedPromptResult


def test_heuristic_fallback_when_lmstudio_offline() -> None:
    """测试当 LM Studio 服务离线时，引擎应回退到本地启发式模板并成功返回结构化提示词。"""
    expander = LMStudioPromptExpander(base_url="http://127.0.0.1:59999/v1", timeout_seconds=1.0)
    result = expander.expand(user_text="赛博朋克机甲猫", style_preset="cyberpunk")

    assert isinstance(result, ExpandedPromptResult)
    assert result.is_fallback is True
    assert "cyberpunk" in result.positive_prompt.lower()
    assert len(result.negative_prompt) > 0
    assert result.width % 64 == 0
    assert result.height % 64 == 0


def test_aspect_ratio_inference() -> None:
    """测试长宽比与分辨率尺寸推断逻辑。"""
    expander = LMStudioPromptExpander(base_url="http://127.0.0.1:59999/v1", timeout_seconds=1.0)
    # 宽屏风景测试
    landscape_res = expander.expand("辽阔壮丽的雪山日落全景", style_preset="cinematic")
    assert landscape_res.width > landscape_res.height

    # 竖屏肖像测试
    portrait_res = expander.expand("穿着晚礼服的少女半身肖像特写", style_preset="photorealistic")
    assert portrait_res.height > portrait_res.width


@patch("urllib.request.urlopen")
def test_lmstudio_successful_expansion(mock_urlopen: MagicMock) -> None:
    """测试通过模拟 LM Studio 正常响应返回扩写结果。"""
    mock_models_response = MagicMock()
    mock_models_response.read.return_value = b'{"data": [{"id": "mock-qwen-model"}]}'
    mock_models_response.__enter__.return_value = mock_models_response

    mock_chat_response = MagicMock()
    mock_chat_response.read.return_value = b'''{
        "choices": [{
            "message": {
                "content": "A high-tech mechanical feline perched on wet neon-lit pavement, highly detailed metallic joints, glowing cyan optic sensors, rain reflections, 8k resolution, cinematic lighting."
            }
        }]
    }'''
    mock_chat_response.__enter__.return_value = mock_chat_response

    mock_urlopen.side_effect = [mock_models_response, mock_chat_response]

    expander = LMStudioPromptExpander(base_url="http://127.0.0.1:1234/v1")
    result = expander.expand("赛博朋克猫", style_preset="cyberpunk")

    assert result.is_fallback is False
    assert "mechanical feline" in result.positive_prompt
    assert result.model_used == "mock-qwen-model"


@patch("urllib.request.urlopen")
def test_detect_model_prioritizes_qwen(mock_urlopen: MagicMock) -> None:
    """测试探测模型时，如果存在多个模型，优先选择 Qwen 系列大模型。"""
    mock_models_response = MagicMock()
    mock_models_response.read.return_value = b'''{
        "data": [
            {"id": "google/gemma-4-26b-a4b-qat"},
            {"id": "qwen3.8-27b-mlx"},
            {"id": "qwen/qwen3-vl-8b"}
        ]
    }'''
    mock_models_response.__enter__.return_value = mock_models_response
    mock_urlopen.return_value = mock_models_response

    expander = LMStudioPromptExpander(base_url="http://127.0.0.1:1234/v1")
    detected = expander.detect_model()
    assert "qwen" in detected.lower()
