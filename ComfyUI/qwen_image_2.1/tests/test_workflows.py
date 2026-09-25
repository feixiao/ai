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
        data = json.load(f)

    # 验证是否为节点字典映射结构
    assert isinstance(data, dict), "API 工作流顶层必须为字典映射"

    # 查找关键节点类型
    class_types = [node.get("class_type") for node in data.values() if isinstance(node, dict)]
    assert any("UnetLoaderGGUF" in ct or "UNETLoader" in ct for ct in class_types), "需包含扩散模型加载节点"
    assert any("CLIPLoaderGGUF" in ct or "CLIPLoader" in ct for ct in class_types), "需包含文本编码加载节点"
    assert "VAELoader" in class_types, "需包含 VAE 加载节点"
    assert "CLIPTextEncode" in class_types, "需包含文本编码节点"
    assert "KSampler" in class_types, "需包含采样器节点"
    assert "SaveImage" in class_types, "需包含图像保存节点"


def test_canvas_workflow_structure() -> None:
    """验证 Web 画布工作流符合 ComfyUI 画布格式。"""
    canvas_path = Path("ComfyUI/qwen_image_2.1/workflows/qwen_image_2.1_t2i_canvas.json")
    assert canvas_path.exists(), "画布工作流文件必须存在"

    with open(canvas_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "nodes" in data and isinstance(data["nodes"], list), "画布工作流必须包含 nodes 列表"
    assert "links" in data and isinstance(data["links"], list), "画布工作流必须包含 links 列表"
