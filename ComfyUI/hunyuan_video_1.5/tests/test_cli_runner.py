# -*- coding: utf-8 -*-
"""CLI 参数解析、参数注入与前置校验的单元测试 (纯离线, 不发起任何网络请求)。"""

import json
from pathlib import Path

import pytest

from hunyuan_video15_test import (
    MODEL_MATRIX,
    OFFICIAL_PRESETS,
    _normalize_host,
    check_model_files,
    inject_workflow_parameters,
    parse_arguments,
)
from prompt_enhancer import EnhancedVideoPrompt

WORKFLOW_DIR = Path(__file__).resolve().parent.parent / "workflows"


@pytest.fixture()
def t2v_template() -> dict:
    return json.loads((WORKFLOW_DIR / "hunyuan_video_1.5_t2v_api.json").read_text(encoding="utf-8"))


@pytest.fixture()
def i2v_template() -> dict:
    return json.loads((WORKFLOW_DIR / "hunyuan_video_1.5_i2v_api.json").read_text(encoding="utf-8"))


@pytest.fixture()
def sample_prompt() -> EnhancedVideoPrompt:
    return EnhancedVideoPrompt(
        positive_prompt="A mecha cat strides through neon rain",
        negative_prompt="blurry, low quality",
        width=960,
        height=544,
        length=61,
        fps=24,
        duration=2.5,
        aspect_ratio="21:9",
        style="cyberpunk",
    )


# --------------------------------------------------------------------------- #
# 参数解析
# --------------------------------------------------------------------------- #
def test_parse_arguments_defaults():
    """默认参数应与官方快速验证档一致。"""
    args = parse_arguments([])
    assert args.mode == "t2v"
    assert args.model_size == "720p"
    assert args.steps == 20
    assert args.fps == 24
    assert args.cfg is None and args.shift is None  # 未指定时按官方预设填充
    assert args.seed == -1
    assert args.comfy_host == "127.0.0.1:8188"
    assert args.dry_run is False


def test_parse_arguments_overrides():
    """命令行覆盖项应被正确解析。"""
    args = parse_arguments(
        ["--mode", "i2v", "--image", "/tmp/a.png", "--duration", "2.5",
         "--size", "960x544", "--steps", "10", "--cfg", "1.0", "--shift", "9",
         "--model-size", "480p", "--seed", "42", "--no-enhance", "--dry-run"]
    )
    assert args.mode == "i2v"
    assert args.image == "/tmp/a.png"
    assert args.duration == 2.5
    assert args.size == "960x544"
    assert args.steps == 10
    assert (args.cfg, args.shift) == (1.0, 9.0)
    assert args.model_size == "480p"
    assert args.seed == 42
    assert args.no_enhance and args.dry_run


def test_parse_arguments_rejects_unknown_mode():
    """非法 mode 应触发 SystemExit。"""
    with pytest.raises(SystemExit):
        parse_arguments(["--mode", "t3v"])


@pytest.mark.parametrize(
    "raw, expected",
    [("127.0.0.1:8188", "127.0.0.1:8188"),
     ("http://127.0.0.1:8188", "127.0.0.1:8188"),
     ("https://host:8188", "host:8188"),
     (" host:8188 ", "host:8188")],
)
def test_normalize_host(raw, expected):
    """主机地址应去掉协议前缀与空白。"""
    assert _normalize_host(raw) == expected


# --------------------------------------------------------------------------- #
# 参数注入
# --------------------------------------------------------------------------- #
def test_inject_t2v_sets_all_parameters(t2v_template, sample_prompt):
    """T2V 注入: 模型 / 提示词 / 采样 / 分辨率帧数 / 输出前缀 全部生效。"""
    wf = inject_workflow_parameters(
        workflow_template=t2v_template, prompt_res=sample_prompt, mode="t2v",
        model_size="720p", steps=12, seed=12345, cfg=6.0, shift=7.0,
        filename_prefix="video/custom",
    )

    assert wf["3"]["inputs"]["unet_name"] == MODEL_MATRIX["t2v"]["720p"]
    assert wf["4"]["inputs"]["text"] == sample_prompt.positive_prompt
    assert wf["5"]["inputs"]["text"] == sample_prompt.negative_prompt
    assert wf["7"]["inputs"]["steps"] == 12
    assert wf["9"]["inputs"]["noise_seed"] == 12345
    assert wf["10"]["inputs"]["cfg"] == 6.0
    assert wf["6"]["inputs"]["shift"] == 7.0
    assert wf["14"]["inputs"]["filename_prefix"] == "video/custom"
    # T2V 的尺寸落在 #15 EmptyHunyuanVideo15Latent
    assert wf["15"]["class_type"] == "EmptyHunyuanVideo15Latent"
    assert wf["15"]["inputs"]["width"] == 960
    assert wf["15"]["inputs"]["height"] == 544
    assert wf["15"]["inputs"]["length"] == 61


def test_inject_t2v_does_not_mutate_template(t2v_template, sample_prompt):
    """注入必须深拷贝, 不得污染原始模板。"""
    original_unet = t2v_template["3"]["inputs"]["unet_name"]
    inject_workflow_parameters(
        workflow_template=t2v_template, prompt_res=sample_prompt, mode="t2v",
        model_size="480p", steps=5, seed=1, cfg=1.0, shift=5.0,
    )
    assert t2v_template["3"]["inputs"]["unet_name"] == original_unet


def test_inject_i2v_sets_dimensions_and_start_image(i2v_template, sample_prompt):
    """I2V 注入: 尺寸落在 #18, 且起始帧文件名写入 #15 LoadImage。"""
    wf = inject_workflow_parameters(
        workflow_template=i2v_template, prompt_res=sample_prompt, mode="i2v",
        model_size="720p", steps=20, seed=7, cfg=6.0, shift=7.0,
        filename_prefix="video/i2v", start_image_name="uploaded_start.png",
    )

    assert wf["3"]["inputs"]["unet_name"] == MODEL_MATRIX["i2v"]["720p"]
    assert wf["18"]["class_type"] == "HunyuanVideo15ImageToVideo"
    assert wf["18"]["inputs"]["width"] == 960
    assert wf["18"]["inputs"]["height"] == 544
    assert wf["18"]["inputs"]["length"] == 61
    assert wf["15"]["class_type"] == "LoadImage"
    assert wf["15"]["inputs"]["image"] == "uploaded_start.png"


def test_inject_i2v_480p_swap(i2v_template, sample_prompt):
    """480p 档位应切换到对应的轻量权重。"""
    wf = inject_workflow_parameters(
        workflow_template=i2v_template, prompt_res=sample_prompt, mode="i2v",
        model_size="480p", steps=20, seed=7, cfg=6.0, shift=5.0,
    )
    assert wf["3"]["inputs"]["unet_name"] == "hunyuanvideo1.5_480p_i2v_fp16.safetensors"
    assert wf["6"]["inputs"]["shift"] == 5.0


def test_official_presets_cover_both_modes():
    """官方预设表必须覆盖 t2v/i2v x 720p/480p 四种组合。"""
    for mode in ("t2v", "i2v"):
        for size in ("720p", "480p"):
            key = f"{mode}-{size}"
            assert key in OFFICIAL_PRESETS, f"缺少预设 {key}"
            assert set(OFFICIAL_PRESETS[key]) == {"cfg", "shift", "steps"}


# --------------------------------------------------------------------------- #
# 模型前置校验
# --------------------------------------------------------------------------- #
def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"stub")


def test_check_model_files_detects_missing(tmp_path):
    """缺失模型应被完整列出, 且附带目标目录提示。"""
    ready, missing = check_model_files(str(tmp_path), mode="t2v", model_size="720p")
    assert ready is False
    assert len(missing) == 4
    assert any("qwen_2.5_vl_7b_fp8_scaled.safetensors" in m for m in missing)
    assert any("diffusion_models" in m for m in missing)


def test_check_model_files_passes_when_complete(tmp_path):
    """全部就位时应判定为就绪。"""
    for sub, name in [
        ("text_encoders", "qwen_2.5_vl_7b_fp8_scaled.safetensors"),
        ("text_encoders", "byt5_small_glyphxl_fp16.safetensors"),
        ("vae", "hunyuanvideo15_vae_fp16.safetensors"),
        ("diffusion_models", MODEL_MATRIX["t2v"]["720p"]),
    ]:
        _touch(tmp_path / sub / name)

    ready, missing = check_model_files(str(tmp_path), mode="t2v", model_size="720p")
    assert ready is True and missing == []


def test_check_model_files_i2v_also_requires_clip_vision(tmp_path):
    """I2V 额外需要 SigLIP 视觉编码器。"""
    for sub, name in [
        ("text_encoders", "qwen_2.5_vl_7b_fp8_scaled.safetensors"),
        ("text_encoders", "byt5_small_glyphxl_fp16.safetensors"),
        ("vae", "hunyuanvideo15_vae_fp16.safetensors"),
        ("diffusion_models", MODEL_MATRIX["i2v"]["720p"]),
    ]:
        _touch(tmp_path / sub / name)

    ready, missing = check_model_files(str(tmp_path), mode="i2v", model_size="720p")
    assert ready is False
    assert len(missing) == 1 and "sigclip_vision_patch14_384.safetensors" in missing[0]
