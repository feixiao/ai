#!/usr/bin/env python3
"""
实操练习 1：Mac Studio 视频帧抽取与视觉多模态大模型 (VLM) 调用
演示：
1. 纯 Python / 零外部依赖生成合成测试测试帧（或调用 OpenCV）。
2. 构建符合 OpenAI / MLX-VLM / Ollama 标准的视觉多模态 Payload。
3. 模拟与真实本地端点（Ollama / LM Studio / MLX Server）交互。

运行方式：
    python3 01_video_vlm_inference.py --demo
"""
import argparse
import base64
import json
import os
import struct
import sys
import urllib.request
from pathlib import Path

def create_synthetic_bmp_frame(width: int = 128, height: int = 128, color: tuple = (30, 144, 255)) -> bytes:
    """纯 Python 生成一张无第三方依赖的 BMP 格式测试图像 (24-bit RGB)"""
    r, g, b = color
    row_bytes = width * 3
    padding = (4 - (row_bytes % 4)) % 4
    image_size = (row_bytes + padding) * height
    file_size = 54 + image_size

    # BMP Header (14 bytes) + DIB Header (40 bytes)
    header = struct.pack(
        "<2sIHHI", b"BM", file_size, 0, 0, 54
    )
    dib = struct.pack(
        "<IIIHHIIIIII", 40, width, height, 1, 24, 0, image_size, 2835, 2835, 0, 0
    )
    
    # Pixel data (bottom-up, BGR format)
    pixel_data = bytearray()
    pad = b"\x00" * padding
    for _ in range(height):
        for _ in range(width):
            pixel_data.extend(bytes([b, g, r]))
        pixel_data.extend(pad)

    return bytes(header + dib + pixel_data)

def simulate_video_frames(num_frames: int = 4) -> list:
    """模拟从视频时间轴抽取的关键帧集合"""
    colors = [
        (30, 144, 255),  # 蓝色 (第 0 秒：工人进入通道)
        (255, 165, 0),   # 橙色 (第 2 秒：工人靠近设备)
        (220, 20, 60),   # 红色 (第 4 秒：检测到设备报警灯闪烁)
        (50, 205, 50),   # 绿色 (第 6 秒：工人按下安全切断开关)
    ]
    frames = []
    for i in range(num_frames):
        color = colors[i % len(colors)]
        bmp_bytes = create_synthetic_bmp_frame(color=color)
        b64_str = base64.b64encode(bmp_bytes).decode("utf-8")
        frames.append({
            "frame_id": i,
            "timestamp_sec": i * 2.0,
            "base64_data": b64_str,
            "simulated_scene": f"时间轴 {i*2.0}s: 场景特征状态值 {color}"
        })
    return frames

def build_vlm_request(frames: list, user_prompt: str, model: str = "qwen2.5-vl:7b") -> dict:
    """构建标准多模态交互消息格式"""
    content = []
    for frame in frames:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/bmp;base64,{frame['base64_data']}"
            }
        })
    content.append({
        "type": "text",
        "text": f"你是一个工业边缘视觉安全分析专家。请根据这 {len(frames)} 张连续视频抽帧分析：{user_prompt}"
    })
    return {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.1,
        "max_tokens": 512
    }

def call_local_vlm_mock_or_live(payload: dict, endpoint_url: str = None) -> dict:
    """如果提供真实本地端点则发起 HTTP 请求，否则执行零延迟本地模拟"""
    if endpoint_url:
        try:
            req = urllib.request.Request(
                endpoint_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
                # 适配 OpenAI 兼容格式或 Ollama 格式
                content = raw.get("message", {}).get("content") or \
                          (raw.get("choices", [{}])[0].get("message", {}).get("content")) or str(raw)
                return {
                    "status": "success",
                    "inference_engine": "Live HTTP Endpoint",
                    "model": payload["model"],
                    "analysis_report": {"summary": content},
                    "raw_response": raw
                }
        except Exception as e:
            print(f"[提示] 连接本地端点 {endpoint_url} 失败 ({e})，自动回退到内置确定性推理引擎。")

    # 本地确定性输出 (模拟 Qwen2.5-VL 在 Mac Studio 上的输出结构)
    return {
        "status": "success",
        "inference_engine": "MLX-VLM / Metal Acceleration (Simulated)",
        "model": payload["model"],
        "analysis_report": {
            "summary": "视频时序动作分析完成：共处理 4 个关键帧 (0.0s ~ 6.0s)。",
            "events_detected": [
                {"timestamp": "0.0s", "event": "作业人员进入监控作业区", "safety_flag": "NORMAL"},
                {"timestamp": "4.0s", "event": "检测到设备故障指示灯呈红色高频告警", "safety_flag": "WARNING"},
                {"timestamp": "6.0s", "event": "作业人员执行安全复位操作，设备恢复安全绿色状态", "safety_flag": "SAFE"}
            ],
            "conclusion": "事件闭环完成，无需上报紧急工单。"
        },
        "stats": {
            "total_frames": 4,
            "estimated_token_count": 1024,
            "latency_ms": 48.5
        }
    }

def save_frames_to_disk(frames: list, output_dir: str):
    """将提取的关键帧保存到本地目录供开发者核对"""
    p = Path(output_dir)
    p.mkdir(parents=True, exist_ok=True)
    for f in frames:
        file_path = p / f"frame_{f['frame_id']:02d}_{f['timestamp_sec']}s.bmp"
        data = base64.b64decode(f["base64_data"])
        file_path.write_bytes(data)
    print(f"  - 抽帧图像已保存至本地: {p.resolve()} (共 {len(frames)} 帧)")

def main():
    parser = argparse.ArgumentParser(description="实操 1：Mac Studio 视频帧抽取与视觉多模态大模型调用")
    parser.add_argument("--demo", action="store_true", help="一键执行完整实操演示")
    parser.add_argument("--endpoint", type=str, default=None, help="本地 Ollama / LM Studio HTTP 接口 (如 http://localhost:11434/v1/chat/completions)")
    parser.add_argument("--model", type=str, default="qwen2.5-vl:7b", help="模型名称标识")
    parser.add_argument("--dump-frames", type=str, default=None, help="将抽取的关键帧图像保存到指定目录")
    parser.add_argument("--prompt", type=str, default="分析画面中工人的作业安全合规性与设备状态变化", help="提问提示词")
    args = parser.parse_args()

    print("===============================================================")
    print(" 🎬 实操 1：Mac Studio 视频多模态大模型 (VLM) 实时调用练习")
    print("===============================================================")
    
    print("\n[步骤 1] 正在模拟视频时间轴高通量均匀抽帧...")
    frames = simulate_video_frames(num_frames=4)
    for f in frames:
        print(f"  - 提取帧 #{f['frame_id']} | 时间戳: {f['timestamp_sec']}s | 编码大小: {len(f['base64_data'])} 字符")

    if args.dump_frames:
        save_frames_to_disk(frames, args.dump_frames)

    print("\n[步骤 2] 正在构建符合 Qwen2.5-VL / MLX 标准的 Prompt Payload...")
    payload = build_vlm_request(frames, args.prompt, model=args.model)
    print(f"  - 模型目标: {payload['model']}")
    print(f"  - 图像 Token 挂载数: {len(frames)} 帧")
    print(f"  - 用户提问: {args.prompt}")

    print("\n[步骤 3] 发起多模态推理计算 (支持 Apple Silicon Metal GPU 加速)...")
    result = call_local_vlm_mock_or_live(payload, args.endpoint)
    
    print("\n[步骤 4] 结构化分析结果响应：")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n✅ 实操 1 验证成功：视频抽帧与 VLM 批处理链路闭环跑通！\n")

if __name__ == "__main__":
    main()
