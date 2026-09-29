# -*- coding: utf-8 -*-
"""HunyuanVideo 1.5 API 工作流的离线结构校验。

不依赖运行中的 ComfyUI, 仅验证:
  - JSON 可解析
  - 每个节点具备 class_type 与 inputs
  - 所有 [node_id, slot] 连线指向存在的上游节点
  - 关键节点与关键模型文件名齐备
"""

import json
from pathlib import Path

import pytest

WORKFLOW_DIR = Path(__file__).resolve().parent.parent / "workflows"

T2V = WORKFLOW_DIR / "hunyuan_video_1.5_t2v_api.json"
I2V = WORKFLOW_DIR / "hunyuan_video_1.5_i2v_api.json"

#: 工作流必备的节点类型
REQUIRED_CLASS_TYPES = {
    "DualCLIPLoader",
    "VAELoader",
    "UNETLoader",
    "CLIPTextEncode",
    "ModelSamplingSD3",
    "BasicScheduler",
    "KSamplerSelect",
    "RandomNoise",
    "CFGGuider",
    "SamplerCustomAdvanced",
    "VAEDecode",
    "CreateVideo",
    "SaveVideo",
}

TEXT_ENCODER = "qwen_2.5_vl_7b_fp8_scaled.safetensors"
GLYPH_ENCODER = "byt5_small_glyphxl_fp16.safetensors"
VAE_FILE = "hunyuanvideo15_vae_fp16.safetensors"


def load(path: Path) -> dict:
    """读取工作流 JSON。"""
    assert path.exists(), f"工作流缺失: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def t2v() -> dict:
    return load(T2V)


@pytest.fixture(scope="module")
def i2v() -> dict:
    return load(I2V)


@pytest.mark.parametrize("path", [T2V, I2V])
def test_json_is_parseable(path):
    """工作流必须是合法 JSON 且非空。"""
    wf = load(path)
    assert isinstance(wf, dict) and wf, f"{path.name} 应为非空字典"


@pytest.mark.parametrize("fixture_name", ["t2v", "i2v"])
def test_all_nodes_have_class_type_and_inputs(fixture_name, request):
    """每个节点都必须声明 class_type 与 inputs 字典。"""
    wf = request.getfixturevalue(fixture_name)
    for node_id, node in wf.items():
        assert isinstance(node, dict), f"节点 {node_id} 应为字典"
        assert node.get("class_type"), f"节点 {node_id} 缺少 class_type"
        assert isinstance(node.get("inputs"), dict), f"节点 {node_id} 缺少 inputs 字典"


@pytest.mark.parametrize("fixture_name", ["t2v", "i2v"])
def test_links_point_to_existing_nodes(fixture_name, request):
    """所有连线 [node_id, slot] 必须指向工作流内存在的节点。"""
    wf = request.getfixturevalue(fixture_name)
    for node_id, node in wf.items():
        for key, value in node["inputs"].items():
            if isinstance(value, list) and len(value) == 2:
                target, slot = value
                assert isinstance(target, str), f"节点 {node_id}.{key} 连线目标应为字符串"
                assert isinstance(slot, int), f"节点 {node_id}.{key} 槽位应为整数"
                assert target in wf, f"节点 {node_id}.{key} 指向不存在的节点 {target}"
                assert slot >= 0, f"节点 {node_id}.{key} 槽位不能为负"


@pytest.mark.parametrize("fixture_name", ["t2v", "i2v"])
def test_required_class_types_present(fixture_name, request):
    """必备节点类型必须齐全。"""
    wf = request.getfixturevalue(fixture_name)
    present = {node["class_type"] for node in wf.values()}
    missing = REQUIRED_CLASS_TYPES - present
    assert not missing, f"缺少必备节点类型: {sorted(missing)}"


def test_t2v_has_empty_latent_node(t2v):
    """T2V 工作流必须包含空潜变量节点以定义视频尺寸。"""
    types = [n["class_type"] for n in t2v.values()]
    assert "EmptyHunyuanVideo15Latent" in types

    latent = next(n for n in t2v.values() if n["class_type"] == "EmptyHunyuanVideo15Latent")
    assert latent["inputs"]["width"] % 16 == 0
    assert latent["inputs"]["height"] % 16 == 0
    # HunyuanVideo 1.5 的帧数约束为 4n + 1
    assert (latent["inputs"]["length"] - 1) % 4 == 0


def test_i2v_has_image_to_video_chain(i2v):
    """I2V 必须包含 LoadImage -> CLIPVisionEncode -> HunyuanVideo15ImageToVideo 链路。"""
    types = {n["class_type"] for n in i2v.values()}
    for expected in ("LoadImage", "CLIPVisionLoader", "CLIPVisionEncode", "HunyuanVideo15ImageToVideo"):
        assert expected in types, f"I2V 缺少节点 {expected}"

    i2v_node = next(n for n in i2v.values() if n["class_type"] == "HunyuanVideo15ImageToVideo")
    assert i2v_node["inputs"]["start_image"][0] in i2v
    assert i2v_node["inputs"]["clip_vision_output"][0] in i2v
    # 帧数约束
    assert (i2v_node["inputs"]["length"] - 1) % 4 == 0


@pytest.mark.parametrize("fixture_name", ["t2v", "i2v"])
def test_model_filenames_consistent(fixture_name, request):
    """文本编码器与 VAE 文件名在两条工作流中必须一致 (共用同一套权重)。"""
    wf = request.getfixturevalue(fixture_name)

    clip = next(n for n in wf.values() if n["class_type"] == "DualCLIPLoader")
    assert clip["inputs"]["clip_name1"] == TEXT_ENCODER
    assert clip["inputs"]["clip_name2"] == GLYPH_ENCODER
    assert clip["inputs"]["type"] == "hunyuan_video_15"

    vae = next(n for n in wf.values() if n["class_type"] == "VAELoader")
    assert vae["inputs"]["vae_name"] == VAE_FILE


def test_t2v_uses_t2v_checkpoint(t2v):
    """T2V 必须加载 720p T2V 权重。"""
    unet = next(n for n in t2v.values() if n["class_type"] == "UNETLoader")
    assert unet["inputs"]["unet_name"] == "hunyuanvideo1.5_720p_t2v_fp16.safetensors"


def test_i2v_uses_i2v_checkpoint(i2v):
    """I2V 必须加载 720p I2V 权重与 SigLIP 视觉编码器。"""
    unet = next(n for n in i2v.values() if n["class_type"] == "UNETLoader")
    assert unet["inputs"]["unet_name"] == "hunyuanvideo1.5_720p_i2v_fp16.safetensors"

    vision = next(n for n in i2v.values() if n["class_type"] == "CLIPVisionLoader")
    assert vision["inputs"]["clip_name"] == "sigclip_vision_patch14_384.safetensors"


@pytest.mark.parametrize("fixture_name", ["t2v", "i2v"])
def test_shift_matches_official_720p_preset(fixture_name, request):
    """720p 档位的 ModelSamplingSD3 shift 必须为 7.0 (官方推荐值)。"""
    wf = request.getfixturevalue(fixture_name)
    sampling = next(n for n in wf.values() if n["class_type"] == "ModelSamplingSD3")
    assert sampling["inputs"]["shift"] == 7.0


@pytest.mark.parametrize("fixture_name", ["t2v", "i2v"])
def test_decoded_frames_reach_save_video(fixture_name, request):
    """VAEDecode 必须把图像喂给 CreateVideo, 再交给 SaveVideo 落盘。"""
    wf = request.getfixturevalue(fixture_name)
    by_type = {}
    for node_id, node in wf.items():
        by_type.setdefault(node["class_type"], []).append(node_id)

    decode_id = by_type["VAEDecode"][0]
    create_id = by_type["CreateVideo"][0]
    save_id = by_type["SaveVideo"][0]

    assert wf[create_id]["inputs"]["images"] == [decode_id, 0]
    assert wf[save_id]["inputs"]["video"] == [create_id, 0]
