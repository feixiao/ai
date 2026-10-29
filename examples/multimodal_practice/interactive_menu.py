#!/usr/bin/env python3
"""
交互式控制台菜单 (Interactive CLI Menu)
用于一站式体验音视频多模态大模型的 4 套实操练习与算力核算工具。
支持交互式键盘输入与命令行快速调用 (--choice 1-7)。
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TOOLS_DIR = BASE_DIR.parent.parent / "tools" / "multimodal_tools"
PYTHON_BIN = sys.executable

MENU_ITEMS = [
    ("1", "实操 1：Mac Studio 视频抽帧与视觉大模型 (Qwen2.5-VL) 批处理调用", ["01_video_vlm_inference.py", "--demo"]),
    ("2", "实操 2：Mac Studio 音频大模型 (Whisper ASR + TTS) 语音交互闭环", ["02_audio_whisper_tts.py", "--demo"]),
    ("3", "实操 3：Mac Studio 多模态 LoRA 结构化微调与数学梯度下降仿真", ["03_vlm_lora_dataset_and_train.py", "--demo"]),
    ("4", "实操 4：Pixel 10 4-bit 量化导出与端侧 LiteRT/GGUF 内存防爆校验", ["04_export_to_pixel10.py", "--demo"]),
    ("5", "实操 5：Mac Studio 本地 OpenAI 兼容多模态 HTTP API 网关自测", ["05_local_multimodal_server.py", "--demo"]),
    ("6", "🚀 一键串行运行全部 6 套实操练习流水线", ["run_all_labs.sh"]),
    ("7", "🔍 执行宿主机环境与 UMA 统一内存硬件探测", ["probe_env"]),
    ("8", "📊 打开多模态模型显存与算力预算估算器 (vram_and_budget)", ["vram_budget"]),
    ("9", "📈 查看音视频多模态技术雷达与基准全景看板 (benchmark_summary)", ["benchmark_summary"]),
    ("10", "📡 运行原生轻量客户端调用参考实现 (client_example)", ["client_example.py", "--demo"]),
]

def probe_hardware_environment():
    """打印当前机器的芯片、内存与多模态加速器探测结果"""
    print("\n==================================================================")
    print("🔍 宿主机硬件环境与多模态加速能力探测")
    print("==================================================================")
    import platform
    print(f"  - 操作系统: {platform.system()} ({platform.machine()})")
    print(f"  - Python 版本: {platform.python_version()} ({sys.executable})")

    if platform.system() == "Darwin":
        try:
            brand = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
            mem_bytes = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).decode().strip())
            mem_gb = mem_bytes / (1024 ** 3)
            print(f"  - Apple Silicon 芯片: {brand}")
            print(f"  - 统一内存 (UMA): {mem_gb:.1f} GB")
            print("  - 加速硬件: Apple Neural Engine (ANE) + Metal GPU 支持")
        except Exception as e:
            print(f"  - Apple Silicon 信息获取提示: {e}")

    for tool in ["ffmpeg", "ollama"]:
        p = subprocess.run(["which", tool], capture_output=True, text=True)
        if p.returncode == 0:
            print(f"  - 可选工具 [{tool}]: 已安装 ({p.stdout.strip()})")
        else:
            print(f"  - 可选工具 [{tool}]: 未检测到 (内置纯 Python 仿真引擎无缝承载)")
    print("==================================================================\n")

def run_choice(choice: str):
    """根据选择执行对应任务"""
    if choice == "0" or choice.lower() in ("q", "quit", "exit"):
        print("👋 已退出多模态练习控制台。")
        return False

    for key, title, cmd in MENU_ITEMS:
        if choice == key:
            print(f"\n▶️ 正在启动 [{key}] {title} ...\n")
            if cmd == ["probe_env"]:
                probe_hardware_environment()
            elif cmd == ["vram_budget"]:
                vram_script = TOOLS_DIR / "vram_and_budget.py"
                subprocess.run([PYTHON_BIN, str(vram_script), "--list-models"])
                subprocess.run([PYTHON_BIN, str(vram_script), "--model", "qwen2.5-vl-3b", "--device", "pixel_10_tensor_g5"])
            elif cmd == ["benchmark_summary"]:
                summary_script = TOOLS_DIR / "benchmark_summary.py"
                subprocess.run([PYTHON_BIN, str(summary_script)])
            elif cmd == ["run_all_labs.sh"]:
                sh_script = BASE_DIR / "run_all_labs.sh"
                subprocess.run(["bash", str(sh_script)])
            else:
                target_script = BASE_DIR / cmd[0]
                full_cmd = [PYTHON_BIN, str(target_script)] + cmd[1:]
                subprocess.run(full_cmd)
            return True

    print(f"⚠️ 无效选项: {choice}，请输入 0~10 之间的数字。")
    return True

def print_menu():
    print("\n==================================================================")
    print(" 🎬 2026 音视频多模态大模型实操练习控制台 (Mac Studio & Pixel 10)")
    print("==================================================================")
    for key, title, _ in MENU_ITEMS:
        print(f" [{key:>2}] {title}")
    print(" [ 0] 退出")
    print("------------------------------------------------------------------")

def main():
    parser = argparse.ArgumentParser(description="音视频多模态实操练习交互式控制台")
    parser.add_argument("--choice", type=str, default=None, choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], help="直接执行指定编号任务")
    parser.add_argument("--demo", action="store_true", help="演示模式：直接运行一键流水线 (选项 6)")
    args = parser.parse_args()

    if args.demo:
        run_choice("6")
        return

    if args.choice is not None:
        run_choice(args.choice)
        return

    # 交互模式
    if not sys.stdin.isatty():
        # 非交互式终端环境，直接执行全部流水线
        run_choice("6")
        return

    while True:
        print_menu()
        try:
            user_input = input("请输入选项编号 [0-10]: ").strip()
            cont = run_choice(user_input)
            if not cont:
                break
        except (KeyboardInterrupt, EOFError):
            print("\n👋 已退出。")
            break

if __name__ == "__main__":
    main()
