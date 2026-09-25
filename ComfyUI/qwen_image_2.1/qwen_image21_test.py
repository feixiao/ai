# -*- coding: utf-8 -*-
"""
Qwen-Image-2.1 自动化测试入口套件
整合 LM Studio 智能提示词扩写、ComfyUI API 参数注入、生图调度与指标统计。
"""

import argparse
import copy
import json
import logging
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 引入同级扩写引擎
CURRENT_DIR = Path(__file__).parent.resolve()
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from prompt_expander import ExpandedPromptResult, LMStudioPromptExpander

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("QwenImageTest")


def parse_arguments(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """解析命令行参数。

    参数:
        argv: 参数列表，默认取 sys.argv[1:]
    返回值:
        包含所有配置项的命名空间对象
    """
    parser = argparse.ArgumentParser(
        description="Qwen-Image-2.1 本地自动化测试脚本 (集成 LM Studio 智能提示词扩写)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--desc", type=str, default="雨夜小巷里的机甲猫", help="用户极简描述输入")
    parser.add_argument(
        "--style",
        type=str,
        default="cinematic",
        choices=["cinematic", "photorealistic", "anime", "cyberpunk", "general"],
        help="画面风格预设",
    )
    parser.add_argument("--steps", type=int, default=24, help="采样迭代步数 (推荐 20-28)")
    parser.add_argument("--seed", type=int, default=-1, help="随机种子 (-1 表示随机生成)")
    parser.add_argument("--aspect", type=str, default=None, help="显式指定长宽比 (如 '1:1', '16:9', '3:4')")
    parser.add_argument(
        "--comfy-host",
        type=str,
        default="127.0.0.1:8188",
        help="ComfyUI 服务地址 (Comfy Desktop 默认为 8188，源码版默认为 8188)",
    )
    parser.add_argument("--lmstudio-host", type=str, default="127.0.0.1:1234", help="LM Studio 服务地址")
    parser.add_argument(
        "--llm-model",
        type=str,
        default=None,
        help="指定用于扩写的模型名称 (默认自动优先检测并选用 Qwen 系列大模型)",
    )
    parser.add_argument("--dry-run", action="store_true", help="仅执行扩写与工作流参数装配，不实际向 ComfyUI 发起生图")
    return parser.parse_args(argv)


def _normalize_host(host_str: str) -> str:
    """去除协议前缀，统一格式为 host:port。

    参数:
        host_str: 用户输入的主机字符串
    返回值:
        去除了协议头的主机与端口字符串
    """
    cleaned = host_str.strip()
    if cleaned.startswith("http://"):
        return cleaned[len("http://") :]
    if cleaned.startswith("https://"):
        return cleaned[len("https://") :]
    return cleaned


def check_system_readiness(comfy_url: str, lmstudio_url: str) -> Dict[str, bool]:
    """检测关键外部服务连通性。

    参数:
        comfy_url: ComfyUI 根地址
        lmstudio_url: LM Studio /v1 基础地址
    返回值:
        服务名称到连通状态的映射
    """
    status: Dict[str, bool] = {"comfyui": False, "lmstudio": False}
    normalized_comfy = _normalize_host(comfy_url)
    normalized_lm = _normalize_host(lmstudio_url)

    # 检测 ComfyUI
    try:
        req = urllib.request.Request(f"http://{normalized_comfy}/system_stats")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            if resp.status == 200:
                status["comfyui"] = True
    except Exception:
        status["comfyui"] = False

    # 检测 LM Studio
    try:
        req = urllib.request.Request(f"http://{normalized_lm}/v1/models")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            if resp.status == 200:
                status["lmstudio"] = True
    except Exception:
        status["lmstudio"] = False

    return status


def inject_workflow_parameters(
    workflow_template: Dict[str, object], prompt_res: ExpandedPromptResult, steps: int, seed: int
) -> Dict[str, object]:
    """将提示词扩写结果与采样参数深度注入到工作流字典中。

    参数:
        workflow_template: 原始 API 格式工作流字典
        prompt_res: 扩写结果对象
        steps: 采样步数
        seed: 随机种子
    返回值:
        完成参数装配的新工作流字典
    """
    workflow: Dict[str, object] = copy.deepcopy(workflow_template)

    # 遍历节点注入参数
    for node_id, node_raw in workflow.items():
        if not isinstance(node_raw, dict):
            continue
        node: Dict[str, object] = node_raw
        class_type = str(node.get("class_type", ""))
        inputs = node.get("inputs", {})
        if not isinstance(inputs, dict):
            continue

        meta = node.get("_meta", {})
        title = ""
        if isinstance(meta, dict):
            title = str(meta.get("title", "")).lower()

        # 注入正向提示词
        if class_type == "CLIPTextEncode" and ("positive" in title or node_id == "4"):
            inputs["text"] = prompt_res.positive_prompt

        # 注入负向提示词
        elif class_type == "CLIPTextEncode" and ("negative" in title or node_id == "5"):
            inputs["text"] = prompt_res.negative_prompt

        # 注入分辨率
        elif class_type in ("EmptyLatentImage", "EmptyQwenImageLayeredLatentImage"):
            inputs["width"] = prompt_res.width
            inputs["height"] = prompt_res.height

        # 注入采样参数
        elif class_type == "KSampler":
            inputs["steps"] = steps
            inputs["seed"] = seed

    return workflow


def submit_comfyui_prompt(comfy_host: str, workflow_dict: Dict[str, object]) -> Optional[str]:
    """向 ComfyUI 提交推理任务。

    参数:
        comfy_host: ComfyUI 主机地址
        workflow_dict: 待执行的工作流 JSON 对象
    返回值:
        任务 Prompt ID，提交失败则返回 None
    """
    url = f"http://{comfy_host}/prompt"
    payload = json.dumps({"prompt": workflow_dict}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            response_payload = json.loads(resp.read().decode("utf-8"))
            return str(response_payload.get("prompt_id"))
    except urllib.error.HTTPError as http_error:
        error_body = ""
        try:
            error_body = http_error.read().decode("utf-8")
            err_json = json.loads(error_body)
            if "node_errors" in err_json:
                logger.error(f"ComfyUI 节点错误 (缺少模型文件或缺少自定义节点): {err_json['node_errors']}")
            elif "error" in err_json:
                logger.error(f"ComfyUI 拒绝任务: {err_json['error']}")
            else:
                logger.error(f"ComfyUI 拒绝任务: {error_body}")
        except Exception:
            logger.error(f"向 ComfyUI 提交任务遭遇 HTTP {http_error.code}: {http_error.reason}")
        return None
    except Exception as error:
        logger.error(f"向 ComfyUI 提交任务失败: {error}")
        return None


def wait_and_download_image(
    comfy_host: str, prompt_id: str, output_dir: Path, timeout_seconds: float = 300.0
) -> List[Path]:
    """轮询任务历史记录并在完成后下载图像。

    参数:
        comfy_host: ComfyUI 服务地址
        prompt_id: 任务标识符
        output_dir: 产物保存目录
        timeout_seconds: 最大等待超时时间
    返回值:
        下载保存的图片路径列表
    """
    history_url = f"http://{comfy_host}/history/{prompt_id}"
    start_time = time.time()
    logger.info(f"等待 ComfyUI 任务渲染中 (ID: {prompt_id}) ...")

    output_files: List[Path] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    while time.time() - start_time < timeout_seconds:
        try:
            req = urllib.request.Request(history_url)
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                history_payload = json.loads(resp.read().decode("utf-8"))
                if prompt_id in history_payload:
                    prompt_data = history_payload[prompt_id]
                    outputs = prompt_data.get("outputs", {})
                    # 查找图像输出节点
                    for node_id, node_output in outputs.items():
                        images = node_output.get("images", [])
                        for img in images:
                            filename = img.get("filename")
                            subfolder = img.get("subfolder", "")
                            img_type = img.get("type", "output")
                            query_params = urllib.parse.urlencode(
                                {"filename": filename, "subfolder": subfolder, "type": img_type}
                            )
                            view_url = f"http://{comfy_host}/view?{query_params}"

                            dest_path = output_dir / f"{int(time.time())}_{prompt_id[:8]}_{filename}"
                            urllib.request.urlretrieve(view_url, str(dest_path))
                            logger.info(f"生成图片已下载: {dest_path}")
                            output_files.append(dest_path)
                    return output_files
        except Exception as error:
            logger.debug(f"轮询历史状态重试: {error}")
        time.sleep(2.0)

    logger.warning("任务等待超时，未能获取最终产物")
    return output_files


def main(argv: Optional[List[str]] = None) -> int:
    """主执行逻辑。

    参数:
        argv: 命令行入参
    返回值:
        状态码 (0 表示成功)
    """
    args = parse_arguments(argv)
    output_dir = CURRENT_DIR / "output"
    workflow_path = CURRENT_DIR / "workflows" / "qwen_image_2.1_api.json"

    print("=" * 70)
    print("🚀 Qwen-Image-2.1 本地测试套件启动")
    print(f"📝 原始描述: {args.desc}")
    print(f"🎨 风格预设: {args.style}")
    print(f"⚙️ 采样步数: {args.steps}")
    print("=" * 70)

    # 1. 检查工作流模板
    if not workflow_path.exists():
        logger.error(f"找不到 API 工作流模板: {workflow_path}")
        return 1
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_template = json.load(f)

    comfy_host = _normalize_host(args.comfy_host)
    lmstudio_host = _normalize_host(args.lmstudio_host)

    # 2. 检查外部服务连通性
    services = check_system_readiness(comfy_host, lmstudio_host)
    print(f"📡 连通性检查:")
    print(f"   · LM Studio ({lmstudio_host}): {'✅ 在线' if services['lmstudio'] else '⚠️ 离线 (将启用本地规则兜底)'}")
    print(f"   · ComfyUI   ({comfy_host}):   {'✅ 在线' if services['comfyui'] else '❌ 离线'}")

    # 3. 提示词扩写
    print("\n🔍 正在进行智能提示词扩写...")
    expand_start = time.time()
    expander = LMStudioPromptExpander(base_url=f"http://{lmstudio_host}/v1", preferred_model=args.llm_model)
    prompt_result = expander.expand(user_text=args.desc, style_preset=args.style, target_aspect=args.aspect)
    expand_duration = time.time() - expand_start

    print("-" * 70)
    print(f"✨ 扩写耗时: {expand_duration:.2f}s (引擎: {prompt_result.model_used})")
    print(f"📐 推荐尺寸: {prompt_result.width}x{prompt_result.height} ({prompt_result.aspect_ratio})")
    print(f"🌟 正向提示词:\n   {prompt_result.positive_prompt}")
    print(f"🛡️ 负向提示词:\n   {prompt_result.negative_prompt}")
    print("-" * 70)

    # 4. 生成随机种子与组装参数
    chosen_seed = random.randint(1, 2**31 - 1) if args.seed == -1 else args.seed
    injected_workflow = inject_workflow_parameters(
        workflow_template=workflow_template, prompt_res=prompt_result, steps=args.steps, seed=chosen_seed
    )

    # 5. 若为 dry-run 模式，直接保存测试组装结果并退出
    if args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        dry_run_path = output_dir / "dry_run_workflow.json"
        with open(dry_run_path, "w", encoding="utf-8") as f:
            json.dump(injected_workflow, f, ensure_ascii=False, indent=2)
        print(f"\n[DRY-RUN] 测试工作流组装完成，已保存至: {dry_run_path}")
        return 0

    # 6. 正式提交 ComfyUI
    if not services["comfyui"]:
        print(f"\n❌ 错误: ComfyUI 服务 ({comfy_host}) 未响应，无法派发生图任务。")
        print("💡 排查建议:")
        print("   1. 如果使用 Comfy Desktop: 桌面端主面板需点击实例的【启动/Open】以启动 Python 后端 (默认端口 8188)")
        print("   2. 如果使用开源源码版: 可通过 --comfy-host 127.0.0.1:8188 指定 8188 端口")
        print("   3. 命令行直接启动实例: /Users/frank/ComfyUI/.venv/bin/python /Users/frank/ComfyUI-Installs/ComfyUI/ComfyUI/main.py --port 8188")
        return 2

    print("\n📦 正在推送任务至 ComfyUI...")
    gen_start = time.time()
    prompt_id = submit_comfyui_prompt(args.comfy_host, injected_workflow)
    if not prompt_id:
        return 3

    output_images = wait_and_download_image(args.comfy_host, prompt_id, output_dir)
    gen_duration = time.time() - gen_start

    print("=" * 70)
    print(f"🎉 任务完成! 生图总耗时: {gen_duration:.2f}s")
    for img_path in output_images:
        print(f"🖼️ 产物位置: {img_path}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
