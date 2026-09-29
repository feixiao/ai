# -*- coding: utf-8 -*-
"""
HunyuanVideo 1.5 视频提示词增强引擎

与原 Qwen-Image 系列的 prompt_expander 不同, 视频生成对提示词的诉求侧重于
**时间维度**: 镜头运动、主体动作的起承转合、光影随时间的变化。

本模块提供两级能力:
1. 优先调用本地 LM Studio (OpenAI 兼容 /v1/chat/completions) 中已挂载的
   Qwen 系列多模态大模型, 把一句中文极简描述扩写为影视级英文视频提示词;
2. LM Studio 离线或超时时, 自动降级为内置的启发式规则库 (0 依赖, 0 显存),
   按风格模板补齐镜头运动与材质光照词汇, 保证流水线不中断。
"""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("HunyuanVideo15PromptEnhancer")

# --------------------------------------------------------------------------- #
# 分辨率与时长约束
# --------------------------------------------------------------------------- #

#: HunyuanVideo 1.5 官方推荐分辨率档位 (宽高均为 16 的整数倍)
ASPECT_RESOLUTIONS: Dict[str, Tuple[int, int]] = {
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "1:1": (960, 960),
    "4:3": (960, 720),
    "3:4": (720, 960),
    "21:9": (1280, 544),
}

#: 视频模型在 Apple Silicon 上极耗算力, 默认 5 秒 (24fps x 121 帧)
DEFAULT_FPS = 24
DEFAULT_DURATION = 5.0

#: 通用负向提示词 (视频场景: 强调时序稳定性与画质)
BASE_NEGATIVE_PROMPT = (
    "blurry, low quality, worst quality, jitter, flicker, temporal inconsistency, "
    "flickering frames, distorted anatomy, extra limbs, deformed hands, warping, "
    "watermark, signature, text, logo, oversaturated, overexposed, static image"
)

#: 风格预设 -> (镜头语言模版, 光照与质感模版)
STYLE_PRESETS: Dict[str, Dict[str, str]] = {
    "cinematic": {
        "camera": "smooth cinematic dolly-in followed by a slow orbit, shallow depth of field, 24mm anamorphic lens",
        "light": "dramatic volumetric lighting, golden rim light, film grain, teal-and-orange color grading",
        "motion": "the subject moves with deliberate, weighty momentum, background parallax reveals depth",
    },
    "photorealistic": {
        "camera": "handheld documentary camera, subtle natural shake, realistic focal length",
        "light": "natural daylight, physically accurate shadows, true-to-life skin and material response",
        "motion": "candid lifelike motion, clothing and hair react naturally to movement and wind",
    },
    "anime": {
        "camera": "dynamic anime-style camera pan with speed lines, punchy perspective shifts",
        "light": "vivid cel-shaded highlights, saturated color palette, crisp line art",
        "motion": "expressive exaggerated motion, snappy timing, flowing hair and fabric trails",
    },
    "cyberpunk": {
        "camera": "low-angle tracking shot through a neon-lit street, reflections sliding across wet ground",
        "light": "neon cyan and magenta practical lights, heavy bloom, volumetric haze, chromatic aberration",
        "motion": "rain streaks and holographic signage flicker as the subject strides forward",
    },
    "nature": {
        "camera": "slow aerial drone push-in revealing the landscape, gentle parallax",
        "light": "soft atmospheric haze, warm sunbeams through foliage, natural color science",
        "motion": "leaves, water and clouds drift continuously, wildlife moves with organic rhythm",
    },
    "general": {
        "camera": "steady medium shot with a gentle push-in",
        "light": "balanced natural lighting, clear and pleasant rendering",
        "motion": "the subject performs a continuous, easily readable action",
    },
}

#: 规则扩写时按风格补充的通用尾缀
RULE_SUFFIX = (
    "highly detailed, sharp focus, stable camera, consistent lighting across frames, "
    "temporal coherence, smooth motion, 720p"
)

_LLM_SYSTEM_PROMPT = (
    "You are a professional video-generation prompt engineer for the HunyuanVideo 1.5 "
    "text-to-video model.\n"
    "Rewrite the user's short idea into ONE single English paragraph (60-120 words) that "
    "works well for video generation.\n"
    "Requirements:\n"
    "1. Describe the subject and scene vividly (material, texture, colors, environment).\n"
    "2. Explicitly describe MOTION and its temporal evolution (what happens, in what order).\n"
    "3. Specify camera language (shot size, camera movement, lens).\n"
    "4. Specify lighting and atmosphere.\n"
    "5. Output ONLY the English prompt paragraph. No preamble, no explanation, no quotes, "
    "no markdown, no Chinese."
)


@dataclass
class EnhancedVideoPrompt:
    """提示词增强结果与视频参数的结构化载体。"""

    positive_prompt: str
    negative_prompt: str = BASE_NEGATIVE_PROMPT
    width: int = 1280
    height: int = 720
    length: int = 121
    fps: int = DEFAULT_FPS
    duration: float = DEFAULT_DURATION
    aspect_ratio: str = "16:9"
    style: str = "cinematic"
    model_used: str = "heuristic-rules"
    tags: List[str] = field(default_factory=list)

    @property
    def resolution(self) -> str:
        """返回形如 '1280x720' 的分辨率字符串。"""
        return f"{self.width}x{self.height}"


def frames_for_duration(duration: float, fps: int) -> int:
    """把秒数换算为 HunyuanVideo 1.5 合法帧数 (满足 length = 4n + 1)。

    参数:
        duration: 目标时长 (秒)
        fps: 帧率
    返回值:
        合法帧数, 至少为 1
    """
    if fps <= 0:
        fps = DEFAULT_FPS
    raw = duration * fps
    blocks = int(round(raw / 4.0))
    return max(1, blocks * 4 + 1)


def normalize_resolution(width: int, height: int) -> Tuple[int, int]:
    """把任意分辨率向下对齐到 16 的整数倍 (HunyuanVideo 1.5 的 VAE 下采样倍率)。"""
    return (max(16, (width // 16) * 16), max(16, (height // 16) * 16))


def guess_aspect(width: int, height: int) -> str:
    """根据宽高推断最接近的标准长宽比标签。"""
    if height == 0:
        return "16:9"
    ratio = width / height
    best, best_delta = "16:9", float("inf")
    for label, (w, h) in ASPECT_RESOLUTIONS.items():
        delta = abs(ratio - w / h)
        if delta < best_delta:
            best, best_delta = label, delta
    return best


def _clean_llm_output(text: str) -> str:
    """清洗大模型输出: 去掉 markdown 包裹、引号与前缀说明。"""
    cleaned = text.strip()
    cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip().strip('"').strip("'").strip()
    # 去掉常见的 "Prompt:" / "Here is..." 前缀
    cleaned = re.sub(r"^(prompt|english prompt)\s*[:：]\s*", "", cleaned, flags=re.IGNORECASE)
    return " ".join(cleaned.split())


class LMStudioVideoPromptEnhancer:
    """基于本地 LM Studio 的视频提示词增强器 (带规则兜底)。"""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:1234/v1",
        preferred_model: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        """初始化增强器。

        参数:
            base_url: LM Studio 的 OpenAI 兼容地址 (以 /v1 结尾)
            preferred_model: 手动指定扩写模型名, 为空则自动优选 Qwen 系列
            timeout: 单次 HTTP 请求超时秒数
        """
        self.base_url = base_url.rstrip("/")
        self.preferred_model = preferred_model
        self.timeout = timeout

    # ------------------------------------------------------------------ #
    # 模型发现
    # ------------------------------------------------------------------ #
    def list_models(self) -> List[str]:
        """查询 LM Studio 当前已挂载的模型列表, 服务不可用时返回空列表。"""
        try:
            req = urllib.request.Request(f"{self.base_url}/models")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            return [str(m.get("id", "")) for m in payload.get("data", []) if m.get("id")]
        except Exception as error:  # noqa: BLE001 - 任何网络异常都视为离线
            logger.debug(f"LM Studio 模型列表获取失败: {error}")
            return []

    def pick_model(self) -> Optional[str]:
        """按优先级挑选扩写模型: 手动指定 > qwen3-vl > qwen > 任意可用模型。"""
        if self.preferred_model:
            return self.preferred_model
        models = self.list_models()
        if not models:
            return None
        for keyword in ("qwen3-vl", "qwen2.5-vl", "qwen3", "qwen2.5", "qwen"):
            for name in models:
                if keyword in name.lower():
                    return name
        return models[0]

    # ------------------------------------------------------------------ #
    # 主流程
    # ------------------------------------------------------------------ #
    def expand(
        self,
        user_text: str,
        style_preset: str = "cinematic",
        target_aspect: Optional[str] = None,
        duration: float = DEFAULT_DURATION,
        fps: int = DEFAULT_FPS,
        size_override: Optional[str] = None,
    ) -> EnhancedVideoPrompt:
        """执行扩写并组装完整的视频参数。

        参数:
            user_text: 用户的中文/英文极简描述
            style_preset: 风格预设键名 (见 STYLE_PRESETS)
            target_aspect: 显式指定长宽比标签, 如 '16:9'
            duration: 目标时长 (秒)
            fps: 帧率
            size_override: 显式指定分辨率, 如 '1280x720'
        返回值:
            EnhancedVideoPrompt 实例
        """
        style = style_preset if style_preset in STYLE_PRESETS else "general"
        aspect = target_aspect if target_aspect in ASPECT_RESOLUTIONS else "16:9"

        # 1) 解析分辨率
        if size_override and "x" in size_override.lower():
            try:
                raw_w, raw_h = size_override.lower().split("x", 1)
                width, height = normalize_resolution(int(raw_w), int(raw_h))
                aspect = guess_aspect(width, height)
            except (ValueError, TypeError):
                width, height = ASPECT_RESOLUTIONS[aspect]
        else:
            width, height = ASPECT_RESOLUTIONS[aspect]

        # 2) 解析帧数
        length = frames_for_duration(duration, fps)

        # 3) 扩写提示词 (LLM 优先, 规则兜底)
        model_name = self.pick_model()
        positive: Optional[str] = None
        used = "heuristic-rules"
        if model_name:
            positive = self._expand_via_llm(user_text, style, model_name)
            if positive:
                used = model_name
        if not positive:
            positive = self._expand_via_rules(user_text, style)

        return EnhancedVideoPrompt(
            positive_prompt=positive,
            negative_prompt=BASE_NEGATIVE_PROMPT,
            width=width,
            height=height,
            length=length,
            fps=fps,
            duration=duration,
            aspect_ratio=aspect,
            style=style,
            model_used=used,
            tags=[style, aspect],
        )

    # ------------------------------------------------------------------ #
    # LLM 分支
    # ------------------------------------------------------------------ #
    def _expand_via_llm(self, user_text: str, style: str, model_name: str) -> Optional[str]:
        """调用 LM Studio 进行扩写; 失败返回 None 以触发规则兜底。"""
        preset = STYLE_PRESETS[style]
        user_payload = (
            f"Style preset: {style}\n"
            f"Camera language to respect: {preset['camera']}\n"
            f"Lighting to respect: {preset['light']}\n"
            f"Motion guidance: {preset['motion']}\n\n"
            f"User idea: {user_text}"
        )
        body = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": _LLM_SYSTEM_PROMPT},
                {"role": "user", "content": user_payload},
            ],
            "temperature": 0.7,
            "max_tokens": 400,
            "stream": False,
        }
        try:
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            content = payload["choices"][0]["message"]["content"]
            cleaned = _clean_llm_output(content)
            if len(cleaned) < 10:
                logger.warning("LM Studio 返回内容过短, 回退到规则扩写")
                return None
            logger.info(f"LLM 扩写成功 (模型: {model_name}, 长度: {len(cleaned)} 字符)")
            return cleaned
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError, TimeoutError) as error:
            logger.warning(f"LM Studio 扩写失败 ({error}), 回退到内置规则库")
            return None
        except Exception as error:  # noqa: BLE001
            logger.warning(f"LM Studio 扩写异常 ({error}), 回退到内置规则库")
            return None

    # ------------------------------------------------------------------ #
    # 规则分支
    # ------------------------------------------------------------------ #
    def _expand_via_rules(self, user_text: str, style: str) -> str:
        """无大模型时, 用风格模板 + 描述本体拼装英文视频提示词。"""
        preset = STYLE_PRESETS[style]
        core = user_text.strip().rstrip("。.!！? ")
        parts = [
            f"{core}",
            "The scene is rendered with rich, physically plausible detail.",
            f"Camera: {preset['camera']}.",
            f"Lighting: {preset['light']}.",
            f"Motion: {preset['motion']}.",
            RULE_SUFFIX + ".",
        ]
        return " ".join(part.strip() for part in parts if part.strip())
