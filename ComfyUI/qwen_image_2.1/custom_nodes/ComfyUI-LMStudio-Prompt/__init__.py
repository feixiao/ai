# -*- coding: utf-8 -*-
"""
ComfyUI-LMStudio-Prompt 自定义节点扩展注册入口
"""

from .lmstudio_prompt_node import LMStudioPromptExpanderNode

NODE_CLASS_MAPPINGS = {
    "LMStudioPromptExpander": LMStudioPromptExpanderNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LMStudioPromptExpander": "LM Studio Prompt Expander (Qwen-Image)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
