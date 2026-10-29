#!/usr/bin/env python3
"""
轻量客户端参考实现 (Minimal Client Example)
演示如何使用原生 Python (无需 pip install openai) 跨网络调用 Mac Studio 多模态网关。
支持健康探测、视觉时序抽帧问答 (Chat Completion) 以及音频转写 (ASR)。

运行方式：
    python3 client_example.py --server http://127.0.0.1:8000
    python3 client_example.py --demo
"""
import argparse
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

def check_server_reachable(server_url: str, timeout: float = 2.0) -> bool:
    """快速探测远程 Mac Studio 多模态网关端口是否连通"""
    try:
        url = f"{server_url.rstrip('/')}/health"
        req = urllib.request.Request(url, headers={"Connection": "close"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False

def get_server_health(server_url: str) -> dict:
    """探测 Mac Studio 边缘算力服务运行状态与统一内存"""
    url = f"{server_url.rstrip('/')}/health"
    req = urllib.request.Request(url, headers={"Connection": "close"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))

def chat_multimodal_vision(server_url: str, prompt: str, image_paths: list = None) -> str:
    """向 Mac Studio 网关发送时序视觉图像帧并获取结构化分析"""
    url = f"{server_url.rstrip('/')}/v1/chat/completions"
    content = []

    if image_paths:
        for p in image_paths:
            if os.path.exists(p):
                b64 = base64.b64encode(Path(p).read_bytes()).decode("utf-8")
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/bmp;base64,{b64}"}
                })

    content.append({"type": "text", "text": prompt})

    payload = {
        "model": "qwen2.5-vl-7b",
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.1
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Connection": "close"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

def transcribe_audio_file(server_url: str, audio_path: str = None) -> str:
    """向 Mac Studio 网关发送音频字节并获取 Whisper 转写文本"""
    url = f"{server_url.rstrip('/')}/v1/audio/transcriptions"
    audio_bytes = b"dummy_audio_pcm"
    if audio_path and os.path.exists(audio_path):
        audio_bytes = Path(audio_path).read_bytes()

    req = urllib.request.Request(
        url,
        data=audio_bytes,
        headers={"Content-Type": "application/octet-stream", "Connection": "close"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("text", "")

def main():
    parser = argparse.ArgumentParser(description="多模态网关轻量客户端调用示例")
    parser.add_argument("--server", type=str, default="http://127.0.0.1:8000", help="Mac Studio 网关地址")
    parser.add_argument("--demo", action="store_true", help="演示模式 (自动启动微服务并联调)")
    args = parser.parse_args()

    server_url = args.server
    server = None

    if args.demo:
        import socket, threading, time
        from http.server import HTTPServer
        import importlib.util
        srv_file = Path(__file__).resolve().parent / "05_local_multimodal_server.py"
        spec = importlib.util.spec_from_file_location("srv", str(srv_file))
        srv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(srv)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        server = HTTPServer(("127.0.0.1", port), srv.MultimodalAPIHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        time.sleep(0.05)
        server_url = f"http://127.0.0.1:{port}"

    try:
        print(f"===============================================================")
        print(f" 📡 连接 Mac Studio 多模态网关: {server_url}")
        print(f"===============================================================")

        # 1. 健康探测
        print("\n[1] 正在请求 /health 检查硬件状态...")
        health = get_server_health(server_url)
        print("  - 服务状态:", health.get("status"))
        print("  - 硬件画像:", health.get("hardware_profile"))
        print("  - 加速硬件:", health.get("accelerators"))

        # 2. 视觉抽帧问答
        sample_frames = list(Path(__file__).resolve().parent.glob("sample_data/frames/*.bmp"))[:2]
        frame_paths = [str(f) for f in sample_frames]
        print(f"\n[2] 正在请求 /v1/chat/completions (携带 {len(frame_paths)} 张样本抽帧)...")
        reply = chat_multimodal_vision(server_url, "核查画面作业规范与设备状态", frame_paths)
        print("  - 网关分析输出:")
        for l in reply.split("\n"):
            print(f"    {l}")

        # 3. 音频转写
        sample_audio = Path(__file__).resolve().parent / "sample_data" / "audio" / "sample_inspection_16k.wav"
        print(f"\n[3] 正在请求 /v1/audio/transcriptions (音频: {sample_audio.name})...")
        transcript = transcribe_audio_file(server_url, str(sample_audio) if sample_audio.exists() else None)
        print(f"  - Whisper 转写结果: \"{transcript}\"")

        print("\n✅ 客户端端到端调用圆满完成！\n")
    finally:
        if server:
            server.shutdown()
            server.server_close()

if __name__ == "__main__":
    main()
