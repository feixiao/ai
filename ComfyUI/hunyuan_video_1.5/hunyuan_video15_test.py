# -*- coding: utf-8 -*-
"""
HunyuanVideo 1.5 自动化测试入口套件 (Apple Silicon / ComfyUI 原生)

整合:
  - LM Studio 智能视频提示词扩写 (时序 / 镜头语言 / 光影)
  - ComfyUI API 参数注入 (分辨率、帧数、步数、CFG、shift、种子)
  - 图生视频的起始帧自动上传 (POST /upload/image)
  - 任务调度、进度轮询与 mp4 产物落盘

典型用法:
    python hunyuan_video15_test.py --desc "雨夜霓虹街道上的机甲猫缓步前行"
    python hunyuan_video15_test.py --mode i2v --image ./assets/robot.png --desc "机器人转头看向镜头"
    python hunyuan_video15_test.py --desc "..." --size 1280x720 --duration 5 --steps 20 --dry-run
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import mimetypes
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CURRENT_DIR = Path(__file__).parent.resolve()
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from prompt_enhancer import (  # noqa: E402
    DEFAULT_DURATION,
    DEFAULT_FPS,
    EnhancedVideoPrompt,
    LMStudioVideoPromptEnhancer,
    frames_for_duration,
    normalize_resolution,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HunyuanVideo15Test")

#: 默认 ComfyUI 模型根目录 (Comfy Desktop)
DEFAULT_COMFY_MODELS = "/Users/frank/ComfyUI/models"

#: 720p / 480p 档位对应的扩散模型文件名 (mode -> size -> filename)
MODEL_MATRIX: Dict[str, Dict[str, str]] = {
    "t2v": {
        "720p": "hunyuanvideo1.5_720p_t2v_fp16.safetensors",
        "480p": "hunyuanvideo1.5_480p_t2v_fp16.safetensors",
    },
    "i2v": {
        "720p": "hunyuanvideo1.5_720p_i2v_fp16.safetensors",
        "480p": "hunyuanvideo1.5_480p_i2v_fp16.safetensors",
    },
}

#: 官方推荐采样参数 (见内置模板 MarkdownNote)
OFFICIAL_PRESETS: Dict[str, Dict[str, float]] = {
    "t2v-720p": {"cfg": 6.0, "shift": 7.0, "steps": 50},
    "i2v-720p": {"cfg": 6.0, "shift": 7.0, "steps": 50},
    "t2v-480p": {"cfg": 6.0, "shift": 5.0, "steps": 50},
    "i2v-480p": {"cfg": 6.0, "shift": 5.0, "steps": 50},
}


# --------------------------------------------------------------------------- #
# 命令行参数
# --------------------------------------------------------------------------- #
def parse_arguments(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="HunyuanVideo 1.5 本地自动化测试脚本 (集成 LM Studio 视频提示词扩写)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--mode", choices=["t2v", "i2v"], default="t2v", help="生成模式: 文生视频 / 图生视频")
    parser.add_argument("--desc", type=str, default="雨夜霓虹街道上, 一只机甲猫抖落雨水后缓步向前", help="用户极简描述输入")
    parser.add_argument("--image", type=str, default=None, help="图生视频 (i2v) 的起始帧图片路径")
    parser.add_argument(
        "--style",
        choices=["cinematic", "photorealistic", "anime", "cyberpunk", "nature", "general"],
        default="cinematic",
        help="影片风格预设",
    )
    parser.add_argument("--size", type=str, default=None, help="显式分辨率, 如 '1280x720'; 默认按长宽比自动推导")
    parser.add_argument("--aspect", type=str, default="16:9", help="长宽比 (16:9 / 9:16 / 1:1 / 4:3 / 3:4)")
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION, help="视频时长 (秒)")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help="帧率")
    parser.add_argument("--model-size", choices=["720p", "480p"], default="720p", help="模型档位 (480p 更快)")
    parser.add_argument("--steps", type=int, default=20, help="采样步数 (官方 50 步, 默认 20 步快速验证)")
    parser.add_argument("--cfg", type=float, default=None, help="CFG 引导系数 (默认按官方预设)")
    parser.add_argument("--shift", type=float, default=None, help="ModelSamplingSD3 shift (默认按官方预设)")
    parser.add_argument("--seed", type=int, default=-1, help="随机种子 (-1 表示随机)")
    parser.add_argument("--comfy-host", type=str, default="127.0.0.1:8188", help="ComfyUI 服务地址")
    parser.add_argument("--lmstudio-host", type=str, default="127.0.0.1:1234", help="LM Studio 服务地址")
    parser.add_argument("--llm-model", type=str, default=None, help="指定扩写模型名 (默认自动优选 Qwen 系列)")
    parser.add_argument("--no-enhance", action="store_true", help="关闭大模型扩写, 直接使用 --desc 原文")
    parser.add_argument("--comfy-models", type=str, default=DEFAULT_COMFY_MODELS, help="ComfyUI 模型根目录 (用于前置文件校验)")
    parser.add_argument("--output", type=str, default=None, help="产物输出目录 (默认 ./output)")
    parser.add_argument("--dry-run", action="store_true", help="仅组装并校验工作流, 不提交生成")
    parser.add_argument("--timeout", type=float, default=3600.0, help="等待生成完成的最大秒数")
    parser.add_argument("--poll-interval", type=float, default=5.0, help="进度轮询间隔秒数")
    return parser.parse_args(argv)


def _normalize_host(host_str: str) -> str:
    """去除协议前缀, 统一为 host:port。"""
    cleaned = host_str.strip()
    for prefix in ("http://", "https://"):
        if cleaned.startswith(prefix):
            return cleaned[len(prefix) :]
    return cleaned


# --------------------------------------------------------------------------- #
# 前置校验
# --------------------------------------------------------------------------- #
def check_system_readiness(comfy_host: str, lmstudio_host: str) -> Dict[str, bool]:
    """探测 ComfyUI 与 LM Studio 的连通性。"""
    status = {"comfyui": False, "lmstudio": False}
    try:
        with urllib.request.urlopen(f"http://{comfy_host}/system_stats", timeout=2.0) as resp:
            status["comfyui"] = resp.status == 200
    except Exception:  # noqa: BLE001
        status["comfyui"] = False
    try:
        with urllib.request.urlopen(f"http://{lmstudio_host}/v1/models", timeout=2.0) as resp:
            status["lmstudio"] = resp.status == 200
    except Exception:  # noqa: BLE001
        status["lmstudio"] = False
    return status


def check_model_files(models_root: str, mode: str, model_size: str) -> Tuple[bool, List[str]]:
    """校验工作流所需的模型文件是否已就位。

    参数:
        models_root: ComfyUI 的 models 目录
        mode: t2v / i2v
        model_size: 720p / 480p
    返回值:
        (是否全部就绪, 缺失文件的人类可读描述列表)
    """
    root = Path(models_root)
    required = [
        (root / "text_encoders" / "qwen_2.5_vl_7b_fp8_scaled.safetensors", "text_encoders"),
        (root / "text_encoders" / "byt5_small_glyphxl_fp16.safetensors", "text_encoders"),
        (root / "vae" / "hunyuanvideo15_vae_fp16.safetensors", "vae"),
        (root / "diffusion_models" / MODEL_MATRIX[mode][model_size], "diffusion_models"),
    ]
    if mode == "i2v":
        required.append((root / "clip_vision" / "sigclip_vision_patch14_384.safetensors", "clip_vision"))

    missing = [f"{path.name}  (应放入 models/{sub}/)" for path, sub in required if not path.exists()]
    return (len(missing) == 0, missing)


# --------------------------------------------------------------------------- #
# 参数注入
# --------------------------------------------------------------------------- #
def inject_workflow_parameters(
    workflow_template: Dict[str, object],
    prompt_res: EnhancedVideoPrompt,
    mode: str,
    model_size: str,
    steps: int,
    seed: int,
    cfg: float,
    shift: float,
    filename_prefix: Optional[str] = None,
    start_image_name: Optional[str] = None,
) -> Dict[str, object]:
    """把扩写结果与采样参数注入 API 格式工作流。

    参数:
        workflow_template: 原始 API 工作流字典
        prompt_res: 提示词与视频参数
        mode: t2v / i2v
        model_size: 720p / 480p
        steps: 采样步数
        seed: 随机种子
        cfg: CFG 引导系数
        shift: ModelSamplingSD3 shift
        filename_prefix: 覆盖输出文件名前缀
        start_image_name: i2v 起始帧在 ComfyUI input 目录中的文件名
    返回值:
        注入完成的新工作流字典
    """
    workflow: Dict[str, object] = copy.deepcopy(workflow_template)

    def node(node_id: str) -> Optional[Dict[str, object]]:
        raw = workflow.get(node_id)
        return raw if isinstance(raw, dict) else None

    # 1) 扩散模型档位
    unet = node("3")
    if unet is not None and isinstance(unet.get("inputs"), dict):
        unet["inputs"]["unet_name"] = MODEL_MATRIX[mode][model_size]

    # 2) 提示词
    positive = node("4")
    if positive is not None and isinstance(positive.get("inputs"), dict):
        positive["inputs"]["text"] = prompt_res.positive_prompt
    negative = node("5")
    if negative is not None and isinstance(negative.get("inputs"), dict):
        negative["inputs"]["text"] = prompt_res.negative_prompt

    # 3) 采样调度
    sampler = node("7")
    if sampler is not None and isinstance(sampler.get("inputs"), dict):
        sampler["inputs"]["steps"] = steps
        sampler["inputs"]["denoise"] = 1.0
    noise = node("9")
    if noise is not None and isinstance(noise.get("inputs"), dict):
        noise["inputs"]["noise_seed"] = seed
    guider = node("10")
    if guider is not None and isinstance(guider.get("inputs"), dict):
        guider["inputs"]["cfg"] = cfg
    sampling = node("6")
    if sampling is not None and isinstance(sampling.get("inputs"), dict):
        sampling["inputs"]["shift"] = shift

    # 4) 分辨率与帧数 (t2v 用 #15 EmptyHunyuanVideo15Latent, i2v 用 #18 HunyuanVideo15ImageToVideo)
    latent_node = node("15") if mode == "t2v" else node("18")
    if latent_node is not None and isinstance(latent_node.get("inputs"), dict):
        latent_node["inputs"]["width"] = prompt_res.width
        latent_node["inputs"]["height"] = prompt_res.height
        latent_node["inputs"]["length"] = prompt_res.length
        latent_node["inputs"]["batch_size"] = 1

    # 5) i2v 起始帧
    if mode == "i2v":
        loader = node("15")  # i2v 中 #15 是 LoadImage
        if loader is not None and start_image_name and isinstance(loader.get("inputs"), dict):
            loader["inputs"]["image"] = start_image_name

    # 6) 输出前缀
    saver = node("14")
    if saver is not None and filename_prefix and isinstance(saver.get("inputs"), dict):
        saver["inputs"]["filename_prefix"] = filename_prefix

    return workflow


# --------------------------------------------------------------------------- #
# ComfyUI HTTP 交互
# --------------------------------------------------------------------------- #
def upload_image(comfy_host: str, image_path: Path) -> Optional[str]:
    """把本地图片上传到 ComfyUI 的 input 目录, 返回可被 LoadImage 引用的文件名。"""
    boundary = f"----HunyuanVideo15{uuid.uuid4().hex}"
    mime = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
    payload = image_path.read_bytes()

    body = bytearray()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="image"; filename="{image_path.name}"\r\n'.encode()
    body += f"Content-Type: {mime}\r\n\r\n".encode()
    body += payload
    body += f"\r\n--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n'
    body += f"--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"http://{comfy_host}/upload/image",
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60.0) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        name = result.get("name")
        subfolder = result.get("subfolder") or ""
        full = f"{subfolder}/{name}" if subfolder else name
        logger.info(f"起始帧上传成功: {full}")
        return full
    except urllib.error.HTTPError as error:
        logger.error(f"起始帧上传失败 HTTP {error.code}: {error.read().decode('utf-8', 'ignore')[:300]}")
        return None
    except Exception as error:  # noqa: BLE001
        logger.error(f"起始帧上传异常: {error}")
        return None


def submit_comfyui_prompt(comfy_host: str, workflow_dict: Dict[str, object]) -> Optional[str]:
    """向 ComfyUI 提交任务, 返回 prompt_id。"""
    url = f"http://{comfy_host}/prompt"
    payload = json.dumps({"prompt": workflow_dict}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30.0) as resp:
            return str(json.loads(resp.read().decode("utf-8")).get("prompt_id"))
    except urllib.error.HTTPError as http_error:
        try:
            err_json = json.loads(http_error.read().decode("utf-8"))
            if "node_errors" in err_json:
                logger.error("ComfyUI 节点校验失败 (模型缺失 / 输入非法):")
                for nid, info in err_json["node_errors"].items():
                    logger.error(f"   节点 {nid}: {info}")
            elif "error" in err_json:
                logger.error(f"ComfyUI 拒绝任务: {err_json['error']}")
        except Exception:  # noqa: BLE001
            logger.error(f"向 ComfyUI 提交任务遭遇 HTTP {http_error.code}: {http_error.reason}")
        return None
    except Exception as error:  # noqa: BLE001
        logger.error(f"向 ComfyUI 提交任务失败: {error}")
        return None


def wait_and_download_video(
    comfy_host: str,
    prompt_id: str,
    output_dir: Path,
    timeout_seconds: float = 3600.0,
    poll_interval: float = 5.0,
) -> Tuple[bool, List[Path]]:
    """轮询任务历史, 任务结束后下载视频产物。

    参数:
        comfy_host: ComfyUI 地址
        prompt_id: 任务 ID
        output_dir: 本地保存目录
        timeout_seconds: 最大等待时间
        poll_interval: 轮询间隔
    返回值:
        (是否成功, 已下载的文件路径列表)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    start = time.time()
    downloaded: List[Path] = []
    logger.info(f"等待 ComfyUI 渲染中 (ID: {prompt_id}) ...")

    while time.time() - start < timeout_seconds:
        try:
            with urllib.request.urlopen(f"http://{comfy_host}/history/{prompt_id}", timeout=10.0) as resp:
                history = json.loads(resp.read().decode("utf-8"))
        except Exception as error:  # noqa: BLE001
            logger.debug(f"轮询重试: {error}")
            time.sleep(poll_interval)
            continue

        if prompt_id not in history:
            elapsed = time.time() - start
            logger.info(f"  渲染中... 已等待 {elapsed:6.0f}s")
            time.sleep(poll_interval)
            continue

        entry = history[prompt_id]
        status = entry.get("status", {})
        if isinstance(status, dict) and status.get("status_str") == "error":
            logger.error(f"ComfyUI 任务执行失败 (ID: {prompt_id}):")
            for msg in status.get("messages", []):
                logger.error(f"   {msg}")
            return False, downloaded

        for node_id, node_output in (entry.get("outputs") or {}).items():
            # SaveVideo 通过 ui.PreviewVideo 落地, history 中以 "images" 键返回
            for key in ("videos", "gifs", "images"):
                for item in node_output.get(key, []) or []:
                    filename = item.get("filename")
                    if not filename:
                        continue
                    params = urllib.parse.urlencode(
                        {
                            "filename": filename,
                            "subfolder": item.get("subfolder", ""),
                            "type": item.get("type", "output"),
                        }
                    )
                    dest = output_dir / f"{int(time.time())}_{prompt_id[:8]}_{filename}"
                    urllib.request.urlretrieve(f"http://{comfy_host}/view?{params}", str(dest))
                    logger.info(f"产物已下载: {dest}")
                    downloaded.append(dest)
        return True, downloaded

    logger.warning("等待超时, 未获取到产物")
    return False, downloaded


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def main(argv: Optional[List[str]] = None) -> int:
    """主执行逻辑, 返回进程退出码 (0 表示成功)。"""
    args = parse_arguments(argv)
    output_dir = Path(args.output).resolve() if args.output else CURRENT_DIR / "output"
    workflow_path = CURRENT_DIR / "workflows" / f"hunyuan_video_1.5_{args.mode}_api.json"

    preset = OFFICIAL_PRESETS[f"{args.mode}-{args.model_size}"]
    cfg = args.cfg if args.cfg is not None else preset["cfg"]
    shift = args.shift if args.shift is not None else preset["shift"]

    print("=" * 72)
    print("🚀 HunyuanVideo 1.5 本地测试套件")
    print(f"📝 原始描述 : {args.desc}")
    print(f"🎬 模式档位 : {args.mode} / {args.model_size}")
    print(f"🎨 风格预设 : {args.style}")
    print(f"⚙️  采样配置 : steps={args.steps}, cfg={cfg}, shift={shift}")
    print(f"⏱️  时长帧率 : {args.duration}s @ {args.fps}fps "
          f"→ {frames_for_duration(args.duration, args.fps)} 帧")
    print("=" * 72)

    # 1) 工作流模板
    if not workflow_path.exists():
        logger.error(f"找不到 API 工作流模板: {workflow_path}")
        return 1
    workflow_template = json.loads(workflow_path.read_text(encoding="utf-8"))

    comfy_host = _normalize_host(args.comfy_host)
    lm_host = _normalize_host(args.lmstudio_host)

    # 2) 服务连通性
    services = check_system_readiness(comfy_host, lm_host)
    print("📡 连通性检查:")
    print(f"   · ComfyUI   ({comfy_host}): {'✅ 在线' if services['comfyui'] else '❌ 离线'}")
    print(f"   · LM Studio ({lm_host}): {'✅ 在线' if services['lmstudio'] else '⚠️ 离线 (启用规则兜底扩写)'}")

    # 3) 模型文件前置校验
    ready, missing = check_model_files(args.comfy_models, args.mode, args.model_size)
    if not ready:
        if args.dry_run:
            print(f"\n⚠️  dry-run 模式: 检测到 {len(missing)} 个模型文件缺失, 仅做工作流装配校验:")
            for item in missing:
                print(f"   · {item}")
            print("   → 正式生成前请执行 ./download_models.sh")
        else:
            print(f"\n❌ 缺少 {len(missing)} 个模型文件, 请先执行 ./download_models.sh:")
            for item in missing:
                print(f"   · {item}")
            return 5
    else:
        print(f"📦 模型文件校验: ✅ 全部就位 ({args.comfy_models})")

    # 4) 提示词扩写
    chosen_seed = random.randint(1, 2**48) if args.seed == -1 else args.seed
    if args.no_enhance:
        prompt_res = EnhancedVideoPrompt(
            positive_prompt=args.desc,
            width=1280, height=720, length=frames_for_duration(args.duration, args.fps),
            fps=args.fps, duration=args.duration, style=args.style, model_used="disabled",
        )
        if args.size and "x" in args.size.lower():
            w, h = (int(v) for v in args.size.lower().split("x", 1))
            prompt_res.width, prompt_res.height = normalize_resolution(w, h)
    else:
        print("\n🔍 正在进行智能视频提示词扩写...")
        started = time.time()
        enhancer = LMStudioVideoPromptEnhancer(
            base_url=f"http://{lm_host}/v1", preferred_model=args.llm_model
        )
        prompt_res = enhancer.expand(
            user_text=args.desc,
            style_preset=args.style,
            target_aspect=args.aspect,
            duration=args.duration,
            fps=args.fps,
            size_override=args.size,
        )
        print(f"✨ 扩写耗时: {time.time() - started:.2f}s (引擎: {prompt_res.model_used})")

    print("-" * 72)
    print(f"📐 分辨率   : {prompt_res.resolution} ({prompt_res.aspect_ratio})")
    print(f"🎞️  帧数     : {prompt_res.length}")
    print(f"🌟 正向提示词:\n   {prompt_res.positive_prompt}")
    print(f"🛡️  负向提示词:\n   {prompt_res.negative_prompt}")
    print("-" * 72)

    # 5) i2v 起始帧上传
    start_image_name: Optional[str] = None
    if args.mode == "i2v":
        if not args.image:
            logger.error("i2v 模式必须通过 --image 指定起始帧图片")
            return 1
        image_path = Path(args.image).expanduser().resolve()
        if not image_path.exists():
            logger.error(f"起始帧图片不存在: {image_path}")
            return 1
        if not services["comfyui"]:
            logger.error("ComfyUI 离线, 无法上传起始帧")
            return 2
        start_image_name = upload_image(comfy_host, image_path)
        if not start_image_name:
            return 6

    # 6) 注入参数
    prefix = f"video/hunyuan_video_1.5_{args.mode}_{args.model_size}"
    injected = inject_workflow_parameters(
        workflow_template=workflow_template,
        prompt_res=prompt_res,
        mode=args.mode,
        model_size=args.model_size,
        steps=args.steps,
        seed=chosen_seed,
        cfg=cfg,
        shift=shift,
        filename_prefix=prefix,
        start_image_name=start_image_name,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        dry_path = output_dir / f"dry_run_{args.mode}.json"
        dry_path.write_text(json.dumps(injected, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[DRY-RUN] 工作流组装完成 → {dry_path}")
        print(f"[DRY-RUN] 随机种子: {chosen_seed}")
        return 0

    if not services["comfyui"]:
        print(f"\n❌ ComfyUI ({comfy_host}) 未响应, 无法派发任务。")
        print("💡 启动建议: /Users/frank/ComfyUI/.venv/bin/python "
              "/Users/frank/ComfyUI-Installs/ComfyUI/ComfyUI/main.py --port 8188")
        return 2

    # 7) 提交并等待
    print(f"\n📦 正在推送任务至 ComfyUI (seed={chosen_seed}) ...")
    gen_start = time.time()
    prompt_id = submit_comfyui_prompt(comfy_host, injected)
    if not prompt_id:
        return 3

    success, files = wait_and_download_video(
        comfy_host, prompt_id, output_dir,
        timeout_seconds=args.timeout, poll_interval=args.poll_interval,
    )
    elapsed = time.time() - gen_start

    report = {
        "prompt_id": prompt_id,
        "mode": args.mode,
        "model_size": args.model_size,
        "resolution": prompt_res.resolution,
        "length": prompt_res.length,
        "fps": prompt_res.fps,
        "steps": args.steps,
        "cfg": cfg,
        "shift": shift,
        "seed": chosen_seed,
        "engine": prompt_res.model_used,
        "elapsed_seconds": round(elapsed, 2),
        "success": bool(success and files),
        "artifacts": [str(p) for p in files],
    }
    (output_dir / f"report_{prompt_id[:8]}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("=" * 72)
    if success and files:
        print(f"🎉 生成完成! 总耗时: {elapsed:.1f}s ({elapsed / 60:.1f} 分钟)")
        for path in files:
            print(f"🎬 产物: {path}")
        print("=" * 72)
        return 0

    print(f"❌ 生成失败 (耗时 {elapsed:.1f}s, 产物 {len(files)} 个)")
    print("💡 排查建议:")
    print("   1. 报 'value not in list' → 模型未下载到位, 执行 ./download_models.sh")
    print("   2. 报 OOM / 内存不足 → 改用 --model-size 480p 或降低 --duration")
    print("   3. i2v 报找不到图片 → 确认 --image 路径正确且已上传成功")
    print("=" * 72)
    return 4


if __name__ == "__main__":
    sys.exit(main())
