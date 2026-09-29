# -*- coding: utf-8 -*-
"""提示词增强引擎的单元测试 (不依赖 LM Studio, 全部走规则兜底分支)。"""

import pytest

from prompt_enhancer import (
    ASPECT_RESOLUTIONS,
    BASE_NEGATIVE_PROMPT,
    DEFAULT_FPS,
    STYLE_PRESETS,
    EnhancedVideoPrompt,
    LMStudioVideoPromptEnhancer,
    frames_for_duration,
    guess_aspect,
    normalize_resolution,
)

#: 指向一个几乎必然不可用的端口, 保证走规则兜底
OFFLINE_BASE_URL = "http://127.0.0.1:59999/v1"


@pytest.fixture()
def offline_enhancer() -> LMStudioVideoPromptEnhancer:
    """返回一个连不上 LM Studio 的增强器 (超时设短以便快速失败)。"""
    return LMStudioVideoPromptEnhancer(base_url=OFFLINE_BASE_URL, timeout=1.0)


# --------------------------------------------------------------------------- #
# 帧数与分辨率换算
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "duration, fps, expected",
    [
        (5.0, 24, 121),   # 官方默认: 5 秒 x 24fps
        (2.5, 24, 61),
        (1.0, 24, 25),
        (1 / 24, 24, 1),  # 退化到单帧
        (10.0, 24, 241),
    ],
)
def test_frames_for_duration(duration, fps, expected):
    """帧数必须满足 length = 4n + 1 的模型约束。"""
    result = frames_for_duration(duration, fps)
    assert result == expected
    assert (result - 1) % 4 == 0


def test_frames_for_duration_handles_bad_fps():
    """非法帧率应回退到默认帧率而不是抛异常。"""
    assert frames_for_duration(5.0, 0) == frames_for_duration(5.0, DEFAULT_FPS)


@pytest.mark.parametrize(
    "raw, expected",
    [((1280, 720), (1280, 720)), ((1000, 700), (992, 688)), ((5, 5), (16, 16))],
)
def test_normalize_resolution_aligns_to_16(raw, expected):
    """分辨率必须向下对齐到 16 的整数倍 (VAE 下采样倍率)。"""
    width, height = normalize_resolution(*raw)
    assert (width, height) == expected
    assert width % 16 == 0 and height % 16 == 0


@pytest.mark.parametrize(
    "size, expected_label",
    [((1280, 720), "16:9"), ((720, 1280), "9:16"), ((960, 960), "1:1"), ((960, 720), "4:3")],
)
def test_guess_aspect(size, expected_label):
    """长宽比推断应与标准档位匹配。"""
    assert guess_aspect(*size) == expected_label


# --------------------------------------------------------------------------- #
# 扩写主流程 (规则兜底)
# --------------------------------------------------------------------------- #
def test_expand_falls_back_to_rules_when_offline(offline_enhancer):
    """LM Studio 不可用时必须降级为规则扩写且不抛异常。"""
    result = offline_enhancer.expand(user_text="雨夜霓虹街道上的机甲猫", style_preset="cyberpunk")

    assert isinstance(result, EnhancedVideoPrompt)
    assert result.model_used == "heuristic-rules"
    assert "机甲猫" in result.positive_prompt          # 保留用户描述本体
    assert result.negative_prompt == BASE_NEGATIVE_PROMPT
    assert "neon" in result.positive_prompt.lower()      # 注入 cyberpunk 镜头/光照词汇
    assert len(result.positive_prompt) > len("雨夜霓虹街道上的机甲猫")


def test_expand_applies_style_and_aspect(offline_enhancer):
    """风格与长宽比参数必须生效。"""
    result = offline_enhancer.expand(
        user_text="雪山之巅的日出", style_preset="nature", target_aspect="9:16"
    )
    assert result.style == "nature"
    assert result.aspect_ratio == "9:16"
    assert (result.width, result.height) == ASPECT_RESOLUTIONS["9:16"]
    assert "aerial" in result.positive_prompt.lower()


def test_expand_respects_size_override(offline_enhancer):
    """显式 --size 应覆盖长宽比推导, 并对齐到 16 的倍数。"""
    result = offline_enhancer.expand(
        user_text="实验室中的机械臂", style_preset="cinematic", size_override="1000x700"
    )
    assert (result.width, result.height) == (992, 688)


def test_expand_computes_length_from_duration(offline_enhancer):
    """时长应正确换算为帧数。"""
    result = offline_enhancer.expand(user_text="海浪拍岸", duration=2.5, fps=24)
    assert result.length == 61
    assert result.fps == 24


def test_expand_unknown_style_falls_back_to_general(offline_enhancer):
    """未知风格名应回退到 general 而不是 KeyError。"""
    result = offline_enhancer.expand(user_text="猫", style_preset="does-not-exist")
    assert result.style == "general"


def test_expand_unknown_aspect_falls_back_to_16_9(offline_enhancer):
    """未知长宽比应回退到 16:9。"""
    result = offline_enhancer.expand(user_text="猫", target_aspect="42:1")
    assert result.aspect_ratio == "16:9"


def test_all_style_presets_have_required_keys():
    """每个风格预设都必须包含 camera / light / motion 三段模板。"""
    for name, preset in STYLE_PRESETS.items():
        for key in ("camera", "light", "motion"):
            assert preset.get(key), f"风格 {name} 缺少 {key}"


# --------------------------------------------------------------------------- #
# 模型发现
# --------------------------------------------------------------------------- #
def test_list_models_returns_empty_when_offline(offline_enhancer):
    """离线时模型列表应为空而非抛异常。"""
    assert offline_enhancer.list_models() == []


def test_pick_model_returns_none_when_offline(offline_enhancer):
    """离线时无法选出模型, 应返回 None 以触发规则兜底。"""
    assert offline_enhancer.pick_model() is None


def test_pick_model_prefers_explicit_choice(offline_enhancer):
    """显式指定的模型名应被直接采纳 (不依赖服务在线)。"""
    enhancer = LMStudioVideoPromptEnhancer(
        base_url=OFFLINE_BASE_URL, preferred_model="qwen3-vl-8b", timeout=1.0
    )
    assert enhancer.pick_model() == "qwen3-vl-8b"
