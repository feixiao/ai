# -*- coding: utf-8 -*-
"""
ComfyUI Qwen-Image-2.1 工作流结构校验测试
"""
import json
from pathlib import Path


def test_api_workflow_structure() -> None:
    """验证 API 工作流模板结构符合 ComfyUI API 规范且包含关键参数节点。"""
    workflow_path = Path("ComfyUI/qwen_image_2.1/workflows/qwen_image_2.1_api.json")
    assert workflow_path.exists(), "API 工作流模板文件必须存在"

    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_payload = json.load(f)

    # 验证是否为节点字典映射结构
    assert isinstance(workflow_payload, dict), "API 工作流顶层必须为字典映射"

    # 查找关键节点类型
    class_types = [node.get("class_type") for node in workflow_payload.values() if isinstance(node, dict)]
    assert any("UnetLoaderGGUF" in ct or "UNETLoader" in ct for ct in class_types), "需包含扩散模型加载节点"
    assert any("CLIPLoaderGGUF" in ct or "CLIPLoader" in ct for ct in class_types), "需包含文本编码加载节点"
    assert "VAELoader" in class_types, "需包含 VAE 加载节点"
    assert "CLIPTextEncode" in class_types, "需包含文本编码节点"
    assert "KSampler" in class_types, "需包含采样器节点"
    assert "SaveImage" in class_types, "需包含图像保存节点"

    # 验证默认 Unet 模型为高性价比的 Q4_K_M 量化版本
    unet_node = next(
        node for node in workflow_payload.values()
        if isinstance(node, dict) and node.get("class_type") in ("UnetLoaderGGUF", "UNETLoader")
    )
    assert "Q4_K_M" in unet_node["inputs"].get("unet_name", ""), "默认 Unet 需为 Q4_K_M 量化模型"

    # 验证采样器默认采用适合 Flow-Matching 的极速单前向模式 (CFG=1.0)
    sampler_node = next(
        node for node in workflow_payload.values()
        if isinstance(node, dict) and node.get("class_type") == "KSampler"
    )
    assert sampler_node["inputs"].get("cfg") == 1.0, "API 工作流采样器默认 CFG 应为 1.0"


def test_canvas_workflow_structure() -> None:
    """验证 Web 画布工作流符合 ComfyUI 画布格式。"""
    canvas_path = Path("ComfyUI/qwen_image_2.1/workflows/qwen_image_2.1_t2i_canvas.json")
    assert canvas_path.exists(), "画布工作流文件必须存在"

    with open(canvas_path, "r", encoding="utf-8") as f:
        canvas_payload = json.load(f)

    assert "nodes" in canvas_payload and isinstance(canvas_payload["nodes"], list), "画布工作流必须包含 nodes 列表"
    assert "links" in canvas_payload and isinstance(canvas_payload["links"], list), "画布工作流必须包含 links 列表"

    canvas_unet = next(
        node for node in canvas_payload["nodes"]
        if node.get("type") in ("UnetLoaderGGUF", "UNETLoader")
    )
    assert any("Q4_K_M" in str(val) for val in canvas_unet.get("widgets_values", [])), "画布默认 Unet 需为 Q4_K_M"

    canvas_sampler = next(
        node for node in canvas_payload["nodes"]
        if node.get("type") == "KSampler"
    )
    assert 1.0 in canvas_sampler.get("widgets_values", []), "画布默认采样器 CFG 应为 1.0"
