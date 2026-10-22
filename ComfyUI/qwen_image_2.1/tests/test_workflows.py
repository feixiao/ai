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
    assert "UC" in unet_node["inputs"].get("unet_name", ""), "必须采用 Qwen-Image-2.1 的 UC (Uncensored 非限制) 版本"
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
    assert any("UC" in str(val) for val in canvas_unet.get("widgets_values", [])), "画布必须采用 UC 非限制版本"
    canvas_sampler = next(
        node for node in canvas_payload["nodes"]
        if node.get("type") == "KSampler"
    )
    assert 1.0 in canvas_sampler.get("widgets_values", []), "画布默认采样器 CFG 应为 1.0"


def test_edit_api_workflow_structure() -> None:
    """验证图像修改与角色防漂移 API 工作流模板结构符合规范。"""
    workflow_path = Path("ComfyUI/qwen_image_2.1/workflows/qwen_image_2.1_edit_api.json")
    assert workflow_path.exists(), "编辑 API 工作流模板文件必须存在"

    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_payload = json.load(f)

    assert isinstance(workflow_payload, dict), "API 工作流顶层必须为字典映射"

    class_types = [node.get("class_type") for node in workflow_payload.values() if isinstance(node, dict)]
    assert "LoadImage" in class_types, "需包含原图输入节点 (LoadImage)"
    assert "VAEEncode" in class_types, "需包含原图隐空间编码节点 (VAEEncode)"
    assert "KSampler" in class_types, "需包含采样器节点 (KSampler)"
    assert "VAEDecode" in class_types, "需包含解码节点 (VAEDecode)"
    assert "SaveImage" in class_types, "需包含图像保存节点 (SaveImage)"

    unet_node = next(
        node for node in workflow_payload.values()
        if isinstance(node, dict) and node.get("class_type") in ("UnetLoaderGGUF", "UNETLoader")
    )
    assert "UC" in unet_node["inputs"].get("unet_name", ""), "编辑 API 工作流必须采用 UC 非限制模型"

    # 验证 VAEEncode 节点连接至 LoadImage 和 VAELoader
    vae_encode_node = next(
        node for node in workflow_payload.values()
        if isinstance(node, dict) and node.get("class_type") == "VAEEncode"
    )
    assert vae_encode_node["inputs"]["pixels"][0] == "10", "VAE 编码节点必须以 LoadImage (节点10) 为像素输入"
    assert vae_encode_node["inputs"]["vae"][0] == "3", "VAE 编码节点必须连接专用 VAE"

    # 验证采样器默认去噪强度适中 (0.45 ~ 0.60) 确保角色不偏移
    sampler_node = next(
        node for node in workflow_payload.values()
        if isinstance(node, dict) and node.get("class_type") == "KSampler"
    )
    denoise_val = sampler_node["inputs"].get("denoise")
    assert denoise_val is not None and 0.45 <= denoise_val <= 0.65, f"采样器 denoise 应为 0.45~0.65，实测: {denoise_val}"
    assert sampler_node["inputs"]["latent_image"][0] == "6", "采样器必须从原图的 VAEEncode 节点读取 latent"


def test_edit_canvas_workflow_structure() -> None:
    """验证图像修改与角色防漂移 Web 画布工作流结构。"""
    canvas_path = Path("ComfyUI/qwen_image_2.1/workflows/qwen_image_2.1_edit_canvas.json")
    assert canvas_path.exists(), "画布工作流文件必须存在"

    with open(canvas_path, "r", encoding="utf-8") as f:
        canvas_payload = json.load(f)

    assert "nodes" in canvas_payload and isinstance(canvas_payload["nodes"], list)
    node_types = [node.get("type") for node in canvas_payload["nodes"]]
    assert "LoadImage" in node_types
    assert "VAEEncode" in node_types
    assert "CLIPTextEncode" in node_types
    assert "KSampler" in node_types
    assert "ImageScaleToTotalPixels" in node_types
    canvas_sampler = next(
        node for node in canvas_payload["nodes"]
        if node.get("type") == "KSampler"
    )
    assert 0.55 in canvas_sampler.get("widgets_values", []), "画布默认采样器 denoise 应为 0.55 锁定角色防漂移"

    canvas_unet = next(
        node for node in canvas_payload["nodes"]
        if node.get("type") in ("UnetLoaderGGUF", "UNETLoader")
    )
    assert any("UC" in str(val) for val in canvas_unet.get("widgets_values", [])), "编辑画布必须采用 UC 非限制版本"


def test_edit_ai_canvas_workflow_structure() -> None:
    """验证包含 AI 扩写节点的进阶画布工作流结构。"""
    canvas_path = Path("ComfyUI/qwen_image_2.1/workflows/qwen_image_2.1_edit_ai_canvas.json")
    assert canvas_path.exists(), "AI 画布工作流文件必须存在"

    with open(canvas_path, "r", encoding="utf-8") as f:
        canvas_payload = json.load(f)

    node_types = [node.get("type") for node in canvas_payload["nodes"]]
    assert any("LMStudioPromptExpander" in str(nt) for nt in node_types), "需包含 LM Studio 扩写节点"
    assert "LoadImage" in node_types
    assert "VAEEncode" in node_types


def test_native_edit_api_workflow_structure() -> None:
    """验证官方 Qwen 2.1 原生多参考图编辑工作流模板结构。"""
    native_path = Path("ComfyUI/qwen_image_2.1/workflows/qwen_image_2.1_native_edit_api.json")
    assert native_path.exists(), "原生编辑 API 工作流模板文件必须存在"

    with open(native_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    class_types = [node.get("class_type") for node in payload.values() if isinstance(node, dict)]
    assert "TextEncodeQwenImage21" in class_types
    assert "LoadImage" in class_types

    unet_node = next(
        node for node in payload.values()
        if isinstance(node, dict) and node.get("class_type") in ("UnetLoaderGGUF", "UNETLoader")
    )
    assert "UC" in unet_node["inputs"].get("unet_name", ""), "原生编辑工作流必须采用 UC 非限制模型"
