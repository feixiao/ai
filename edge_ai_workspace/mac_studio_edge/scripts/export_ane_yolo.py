import os
import sys
import subprocess
from ultralytics import YOLO

def main():
    models_dir = os.path.abspath("../models")
    os.makedirs(models_dir, exist_ok=True)
    
    print("=== [Mac Studio ANE] 阶段 1: 载入预训练 YOLOv8n / YOLO11n ===")
    model = YOLO("yolov8n.pt")  # 经典高兼容端侧轻量模型

    print("=== [Mac Studio ANE] 阶段 2: 导出为针对 ANE 优化的 Core ML 格式 ===")
    # 关键参数:
    # - format='coreml': 产出 .mlpackage
    # - nms=True: 将 NMS 算子固化进模型，ANE 直接硬解坐标，无需 CPU 参与
    # - imgsz=640: 静态 Shape 640x640 (64对齐)
    exported_path = model.export(
        format="coreml",
        nms=True,
        imgsz=640
    )
    print(f"Core ML Package 导出成功: {exported_path}")

    # 阶段 3: 使用 macOS 原生 xcrun 工具链预编译为 .mlmodelc 运行时二进制
    mlmodelc_target = os.path.join(models_dir, "yolov8n.mlmodelc")
    print(f"=== [Mac Studio ANE] 阶段 3: 执行 xcrun 预编译生成二进制运行时 ===")
    cmd = ["xcrun", "coremlcompiler", "compile", exported_path, models_dir]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"预编译完成！ANE 原生二进制位于: {mlmodelc_target}")
    else:
        print(f"xcrun 编译警告: {res.stderr}")

if __name__ == "__main__":
    main()
