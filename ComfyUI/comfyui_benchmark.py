import time
import subprocess
import os

def run_benchmark(
    resolution=(512, 512), duration=4, fps=4, style="Cinematic Film", prompt="一只橘猫坐在窗台晒太阳，窗外是樱花飘落，柔焦镜头，胶片质感，暖色调", seed=None
):
    """
    启动 ComfyUI，自动推送 WAN2.2 测试任务，统计生成时长。
    需保证 ComfyUI 已安装好并支持 CoreML。
    """
    # 构造命令
    cmd = [
        "python", "main.py", "--cpu", "--disable-smart-memory", "--preview-method", "auto"
    ]
    # 可根据实际情况调整 main.py 路径
    cwd = os.path.expanduser("~/ComfyUI-CoreML")
    
    # 启动 ComfyUI
    print("[INFO] 启动 ComfyUI ...")
    proc = subprocess.Popen(cmd, cwd=cwd)
    time.sleep(10)  # 等待服务启动，可根据实际情况调整
    
    # 这里应调用 API 或自动化脚本推送测试任务
    # 示例仅做流程占位，实际需结合 ComfyUI API 或 Web 自动化
    print(f"[INFO] 推送测试任务：分辨率={resolution}, 时长={duration}s, 帧率={fps}, 风格={style}")
    start = time.time()
    # ...推送任务代码...
    time.sleep(15)  # 假定生成耗时
    end = time.time()
    print(f"[RESULT] 总耗时：{end - start:.2f} 秒")
    
    # 关闭 ComfyUI
    proc.terminate()
    print("[INFO] ComfyUI 已关闭")

if __name__ == "__main__":
    run_benchmark()
