# -*- coding: utf-8 -*-
"""
Qwen-Image-2.1 提示词智能扩写引擎
对接本地 LM Studio (默认端口 1234, OpenAI 兼容接口)，支持结构化扩写与本地启发式降级兜底。
"""

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PromptExpander")


@dataclass
class ExpandedPromptResult:
    """扩写结果数据结构，包含正向词、负向词、分辨率规格及元数据。"""

    positive_prompt: str
    negative_prompt: str
    aspect_ratio: str
    width: int
    height: int
    model_used: str
    is_fallback: bool


class LMStudioPromptExpander:
    """基于 LM Studio 本地大模型的提示词扩写引擎。"""

    # 预设通用负向提示词
    DEFAULT_NEGATIVE_PROMPT: str = (
        "blurry, out of focus, low quality, bad anatomy, deformed limbs, extra fingers, "
        "poorly drawn hands, missing fingers, low resolution, bad proportions, watermark, "
        "signature, text artifacts, oversaturated, ugly, cropped"
    )

    # 常见风格注入模版
    STYLE_MODIFIERS: Dict[str, str] = {
        "cinematic": "cinematic lighting, 35mm film still, dramatic atmosphere, depth of field, anamorphic lens flares, 8k resolution, highly detailed",
        "photorealistic": "hyperrealistic photograph, shot on Hasselblad, natural soft lighting, intricate textures, pore level detail, award-winning photography",
        "anime": "refined anime aesthetic, Makoto Shinkai style, vibrant harmonious colors, clean lineart, soft cel shading, high aesthetic quality",
        "cyberpunk": "cyberpunk genre, rainy night street, vibrant neon reflections, volumetric magenta and cyan lighting, intricate metallic mechanical components, futuristic high-tech",
        "general": "masterpiece, best quality, ultra-detailed, beautiful composition, rich contrast, balanced color grading",
    }

    # 长宽比与分辨率映射 (对齐 64 像素倍数，匹配 VAE 编解码约束)
    ASPECT_RATIO_PRESETS: Dict[str, Tuple[int, int]] = {
        "1:1": (1024, 1024),
        "16:9": (1280, 768),
        "9:16": (768, 1280),
        "4:3": (1152, 896),
        "3:4": (896, 1152),
    }

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:1234/v1",
        timeout_seconds: float = 60.0,
        preferred_model: Optional[str] = None,
    ) -> None:
        """初始化扩写引擎。

        参数:
            base_url: LM Studio 服务基础地址 (默认: http://127.0.0.1:1234/v1)
            timeout_seconds: 接口请求超时秒数 (默认 60.0s)
            preferred_model: 指定或偏好的模型名称
        """
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.preferred_model = preferred_model

    def detect_model(self) -> str:
        """探测当前 LM Studio 实例挂载的模型。优先选用 qwen3-vl，其次选用其他 Qwen 系列模型。

        返回值:
            模型 ID 字符串
        """
        if self.preferred_model:
            return self.preferred_model

        url = f"{self.base_url}/models"
        request = urllib.request.Request(url, headers={"User-Agent": "QwenImageExpander/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
                models = payload.get("data", [])
                if models and isinstance(models, list):
                    model_ids: List[str] = [
                        str(item["id"]) for item in models if isinstance(item, dict) and "id" in item
                    ]
                    # 优先级 1: 优先挑选视觉与多模态匹配的 qwen3-vl 模型
                    for model_id in model_ids:
                        if "qwen" in model_id.lower() and "vl" in model_id.lower():
                            return model_id
                    # 优先级 2: 挑选其他 Qwen 系列大模型
                    for model_id in model_ids:
                        if "qwen" in model_id.lower():
                            return model_id
                    # 优先级 3: 挑选首个可用模型
                    if model_ids:
                        return model_ids[0]
        except Exception as error:
            logger.warning(f"未能自动检测到 LM Studio 模型，原因: {error}")
        return "local-default-model"

    def _infer_dimensions(self, user_text: str, target_aspect: Optional[str]) -> Tuple[str, int, int]:
        """根据用户输入文本的关键词与显式指定推断目标长宽比与尺寸。

        参数:
            user_text: 用户原始文本
            target_aspect: 显式指定的长宽比 (如 '16:9', '3:4')
        返回值:
            (长宽比标签, 宽度, 高度)
        """
        if target_aspect and target_aspect in self.ASPECT_RATIO_PRESETS:
            dims = self.ASPECT_RATIO_PRESETS[target_aspect]
            return target_aspect, dims[0], dims[1]

        lower_text = user_text.lower()
        # 竖屏肖像相关词汇
        portrait_keywords = ["肖像", "半身", "全身", "立绘", "美女", "少女", "帅哥", "人像", "portrait", "standing"]
        # 横屏风景相关词汇
        landscape_keywords = ["风景", "全景", "雪山", "大海", "森林", "城市", "宽屏", "壁纸", "landscape", "panorama", "wallpaper"]

        if any(keyword in lower_text for keyword in portrait_keywords):
            ratio = "3:4"
        elif any(keyword in lower_text for keyword in landscape_keywords):
            ratio = "16:9"
        else:
            ratio = "1:1"

        width, height = self.ASPECT_RATIO_PRESETS[ratio]
        return ratio, width, height

    def _heuristic_fallback(
        self, user_text: str, style_preset: str, aspect_ratio: str, width: int, height: int
    ) -> ExpandedPromptResult:
        """当无法访问本地大模型时的本地启发式规则兜底。

        参数:
            user_text: 原始用户描述
            style_preset: 风格预设名称
            aspect_ratio: 长宽比
            width: 分辨率宽度
            height: 分辨率高度
        返回值:
            ExpandedPromptResult 结构体
        """
        logger.info(f"启用规则引擎对描述 [{user_text}] 执行本地降级扩写")
        style_keywords = self.STYLE_MODIFIERS.get(style_preset, self.STYLE_MODIFIERS["general"])
        effective_text = user_text.strip() if user_text.strip() else "subject"
        positive_prompt = (
            f"{effective_text}, highly detailed visual representation, focused subject composition, "
            f"{style_keywords}, masterpiece quality"
        )
        return ExpandedPromptResult(
            positive_prompt=positive_prompt,
            negative_prompt=self.DEFAULT_NEGATIVE_PROMPT,
            aspect_ratio=aspect_ratio,
            width=width,
            height=height,
            model_used="local-heuristic-rule-engine",
            is_fallback=True,
        )

    def expand(
        self,
        user_text: str,
        style_preset: str = "cinematic",
        target_aspect: Optional[str] = None,
        temperature: float = 0.7,
    ) -> ExpandedPromptResult:
        """主入口：将用户极简描述扩写为高表现力的生图提示词。

        参数:
            user_text: 简短自然语言输入 (中英文均可)
            style_preset: 目标视觉风格 (cinematic, photorealistic, anime, cyberpunk, general)
            target_aspect: 可选的固定长宽比
            temperature: 采样随机度温度 (0.0-1.5)
        返回值:
            完整的 ExpandedPromptResult
        """
        clean_text = user_text.strip()
        aspect_ratio, width, height = self._infer_dimensions(clean_text, target_aspect)
        style_description = self.STYLE_MODIFIERS.get(style_preset, self.STYLE_MODIFIERS["general"])

        active_model = self.detect_model()
        system_instruction = (
            "You are an expert prompt engineer specializing in Qwen-Image-2.1 and Qwen3-VL text-to-image models. "
            "Your task is to take a short, simple user prompt and expand it into a rich, detailed, photographic/artistic English prompt. "
            "Focus on: subject details, textures, environment, atmospheric lighting, spatial depth, and camera optics. "
            f"Style orientation: {style_preset} ({style_description}). "
            "Output ONLY the final expanded prompt text directly in one coherent English paragraph. "
            "Do not include explanations, quotation marks, prefixes, or markdown blocks."
        )

        chat_payload = {
            "model": active_model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Expand this into a visually rich image prompt: {clean_text}"},
            ],
            "temperature": max(0.0, min(1.5, temperature)),
            "max_tokens": 1024,
        }

        url = f"{self.base_url}/chat/completions"
        encoded_data = json.dumps(chat_payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=encoded_data,
            headers={"Content-Type": "application/json", "User-Agent": "QwenImageExpander/1.0"},
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                choices = response_data.get("choices", [])
                if choices and isinstance(choices, list):
                    first_choice = choices[0]
                    if isinstance(first_choice, dict) and "message" in first_choice:
                        message = first_choice["message"]
                        message_content = message.get("content", "").strip()
                        # 若 content 为空但存在思考内容 (reasoning_content)，尝试截取最后有效段落
                        if not message_content and "reasoning_content" in message:
                            reasoning = message["reasoning_content"].strip()
                            lines = [line.strip().strip('"') for line in reasoning.splitlines() if line.strip()]
                            if lines:
                                message_content = lines[-1]

                        if message_content:
                            return ExpandedPromptResult(
                                positive_prompt=message_content,
                                negative_prompt=self.DEFAULT_NEGATIVE_PROMPT,
                                aspect_ratio=aspect_ratio,
                                width=width,
                                height=height,
                                model_used=active_model,
                                is_fallback=False,
                            )
        except Exception as error:
            logger.warning(f"LM Studio 请求失败，触发自动降级: {error}")

        return self._heuristic_fallback(clean_text, style_preset, aspect_ratio, width, height)
