# -*- coding: utf-8 -*-
"""
ComfyUI 自定义节点：LMStudioPromptExpanderNode
在 ComfyUI 流程中直接将简短文本扩写为适用于 Qwen-Image-2.1 的高表现力提示词。
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 寻找同级或上级 prompt_expander 模块
CURRENT_DIR = Path(__file__).parent.resolve()
PARENT_DIR = CURRENT_DIR.parent.parent.resolve()
for path_to_add in (CURRENT_DIR, PARENT_DIR):
    if str(path_to_add) not in sys.path:
        sys.path.insert(0, str(path_to_add))

from prompt_expander import ExpandedPromptResult, LMStudioPromptExpander


class LMStudioPromptExpanderNode:
    """ComfyUI 画布节点：调用本地 LM Studio 扩写提示词。"""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, object]:
        """定义节点输入控件与数据类型。"""
        return {
            "required": {
                "user_short_desc": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "雨夜小巷里的机甲猫",
                    },
                ),
                "style_preset": (
                    ["cinematic", "photorealistic", "anime", "cyberpunk", "general"],
                    {"default": "cinematic"},
                ),
                "temperature": (
                    "FLOAT",
                    {"default": 0.7, "min": 0.0, "max": 1.5, "step": 0.05, "round": 0.01},
                ),
                "aspect_ratio": (
                    ["auto", "1:1", "16:9", "9:16", "4:3", "3:4"],
                    {"default": "auto"},
                ),
                "lmstudio_host": (
                    "STRING",
                    {"default": "127.0.0.1:1234"},
                ),
            }
        }

    RETURN_TYPES: Tuple[str, str, str, str] = ("STRING", "STRING", "INT", "INT")
    RETURN_NAMES: Tuple[str, str, str, str] = ("positive_prompt", "negative_prompt", "width", "height")
    FUNCTION: str = "expand_prompt"
    CATEGORY: str = "QwenImage/Prompt"

    def expand_prompt(
        self,
        user_short_desc: str,
        style_preset: str = "cinematic",
        temperature: float = 0.7,
        lmstudio_host: str = "127.0.0.1:1234",
        aspect_ratio: str = "auto",
    ) -> Tuple[str, str, int, int]:
        """执行扩写并返回各参数。

        参数:
            user_short_desc: 用户输入的极简短句
            style_preset: 风格预设名称
            temperature: 采样温度
            lmstudio_host: LM Studio 端口地址
            aspect_ratio: 指定或自动长宽比
        返回值:
            (正向提示词, 负向提示词, 建议宽度, 建议高度)
        """
        host = lmstudio_host.strip()
        if not host.startswith("http://") and not host.startswith("https://"):
            base_url = f"http://{host}/v1"
        else:
            base_url = f"{host}/v1"

        target_ratio: Optional[str] = None if aspect_ratio == "auto" else aspect_ratio

        expander = LMStudioPromptExpander(base_url=base_url)
        res: ExpandedPromptResult = expander.expand(
            user_text=user_short_desc,
            style_preset=style_preset,
            target_aspect=target_ratio,
            temperature=temperature,
        )

        return (res.positive_prompt, res.negative_prompt, res.width, res.height)
