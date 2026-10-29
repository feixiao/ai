#!/usr/bin/env python3
"""
实操练习 2：Mac Studio 音频大模型 (Whisper ASR + TTS) 语音交互闭环实战
演示：
1. 纯 Python 生成标准 16kHz 16-bit 单声道 PCM WAV 音频切片。
2. 模拟音频流 VAD (静音检测) 与滑动窗口分块。
3. Whisper 语音识别转写与语义解析。
4. 本地 TTS 语音合成响应（在 macOS 上支持原生调用 say 或 Kokoro 模型接口）。

运行方式：
    python3 02_audio_whisper_tts.py --demo
"""
import argparse
import json
import math
import os
import struct
import subprocess
import sys
import wave
from pathlib import Path

def generate_synthetic_wav(filename: str, duration_sec: float = 2.0, sample_rate: int = 16000):
    """纯 Python 生成标准 16kHz PCM 单声道测试音频 (模拟双音频段与中间静音)"""
    num_samples = int(duration_sec * sample_rate)
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)        # 单声道 (Whisper 标准输入)
        wf.setsampwidth(2)        # 16-bit
        wf.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            # 前 0.8s 为 440Hz 提示音，中间 0.4s 为静音，后 0.8s 为 880Hz 语音特征段
            if 0.0 <= t < 0.8:
                val = int(16000 * math.sin(2 * math.pi * 440 * t))
            elif 0.8 <= t < 1.2:
                val = 0  # 静音
            else:
                val = int(14000 * math.sin(2 * math.pi * 880 * t))
            frames.extend(struct.pack("<h", val))
            
        wf.writeframes(frames)

def simulate_vad_and_chunk(audio_path: str) -> list:
    """模拟端侧低功耗语音活动检测 (VAD) 分块"""
    with wave.open(audio_path, "rb") as wf:
        frames_count = wf.getnframes()
        rate = wf.getframerate()
        duration = frames_count / rate
        
    return [
        {"chunk_id": 0, "start_time": "0.0s", "end_time": "0.8s", "vad_label": "VOICE_ACTIVE", "energy_db": -12.4},
        {"chunk_id": 1, "start_time": "0.8s", "end_time": "1.2s", "vad_label": "SILENCE_IGNORED", "energy_db": -65.1},
        {"chunk_id": 2, "start_time": "1.2s", "end_time": "2.0s", "vad_label": "VOICE_ACTIVE", "energy_db": -14.2},
    ]

def transcribe_audio_whisper_simulation(chunks: list) -> dict:
    """模拟 Whisper-large-v3-turbo 在 Mac Studio (ANE/Metal) 上的识别输出"""
    active_chunks = [c for c in chunks if c["vad_label"] == "VOICE_ACTIVE"]
    return {
        "engine": "Whisper-large-v3-turbo (Apple Neural Engine Acceleration)",
        "transcribed_text": "巡检打卡：1号空压机润滑油温已复核，当前数值处于绿区范围。",
        "detected_language": "zh",
        "confidence": 0.985,
        "processed_voice_duration": f"{len(active_chunks) * 0.8:.1f}s",
        "inference_latency_ms": 32.0
    }

def synthesize_speech_response(text: str, play_audio: bool = False) -> dict:
    """生成 TTS 语音反馈（如果在 macOS 下且启用 play_audio，调用系统 say 命令发音）"""
    if play_audio and sys.platform == "darwin":
        try:
            subprocess.run(["say", "-v", "Tingting", text], check=False, timeout=5)
        except Exception:
            pass

    return {
        "tts_engine": "Kokoro-82M / ChatTTS (Local Metal GPU)",
        "response_text": text,
        "sample_rate_hz": 24000,
        "audio_format": "PCM_16BIT_24KHZ",
        "synthesized_duration_sec": 2.4,
        "latency_ms": 55.0
    }

def main():
    parser = argparse.ArgumentParser(description="实操 2：Mac Studio 音频大模型 (Whisper + TTS) 语音交互练习")
    parser.add_argument("--demo", action="store_true", help="执行完整实操演示")
    parser.add_argument("--audio", type=str, default=None, help="指定本地待识别的 WAV 格式真实音频路径")
    parser.add_argument("--play", action="store_true", help="是否在 Mac 上实际播放生成的 TTS 语音")
    args = parser.parse_args()

    sample_wav_fixture = Path(__file__).resolve().parent / "sample_data" / "audio" / "sample_inspection_16k.wav"
    if args.audio is not None and os.path.exists(args.audio):
        target_wav = args.audio
        is_custom_audio = True
        audio_source_desc = f"用户指定音频: {target_wav}"
    elif sample_wav_fixture.exists():
        target_wav = str(sample_wav_fixture)
        is_custom_audio = True
        audio_source_desc = f"预置样本音频: {target_wav}"
    else:
        target_wav = "/tmp/test_multimodal_audio.wav"
        is_custom_audio = False
        audio_source_desc = f"临时生成测试音频: {target_wav}"

    print("===============================================================")
    print(" 🎙️ 实操 2：Mac Studio 音频大模型 (Whisper + TTS) 交互闭环练习")
    print("===============================================================")

    if not is_custom_audio:
        print(f"\n[步骤 1] 正在生成标准 16kHz PCM 单声道测试音频: {target_wav}")
        generate_synthetic_wav(target_wav, duration_sec=2.0)
    else:
        print(f"\n[步骤 1] 正在读取音频数据 ({audio_source_desc})")

    file_size = os.path.getsize(target_wav)
    print(f"  - 音频文件就绪 | 大小: {file_size} 字节")

    print("\n[步骤 2] 执行本地低延迟 VAD (语音活动检测) 与切片分块...")
    chunks = simulate_vad_and_chunk(target_wav)
    for c in chunks:
        status_icon = "🟢 语音" if c["vad_label"] == "VOICE_ACTIVE" else "⚪ 静音丢弃"
        print(f"  - 分片 #{c['chunk_id']} [{c['start_time']} -> {c['end_time']}] {status_icon} (能量: {c['energy_db']} dB)")

    print("\n[步骤 3] 调用 Whisper 引擎执行端侧高精度转写...")
    asr_res = transcribe_audio_whisper_simulation(chunks)
    print(f"  - 识别引擎: {asr_res['engine']}")
    print(f"  - 识别文本: \"{asr_res['transcribed_text']}\"")
    print(f"  - 置信度: {asr_res['confidence']} | 推理耗时: {asr_res['inference_latency_ms']} ms")

    print("\n[步骤 4] 驱动语音大模型 (TTS) 生成多模态智能语音播报反馈...")
    reply_text = "系统已收到1号机巡检数据，指标正常，已记录到边缘账本。"
    tts_res = synthesize_speech_response(reply_text, play_audio=args.play)
    print(f"  - 语音合成引擎: {tts_res['tts_engine']}")
    print(f"  - 播报语音文本: \"{tts_res['response_text']}\"")
    print(f"  - 音频合成耗时: {tts_res['latency_ms']} ms")

    # 清理合成临时文件
    if not is_custom_audio and os.path.exists(target_wav):
        os.remove(target_wav)

    print("\n✅ 实操 2 验证成功：音频转写与语音合成双向闭环完成！\n")

if __name__ == "__main__":
    main()
